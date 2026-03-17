import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px

from app.infra.vnedu_parser import parse_vnedu_file
from app.core.compare import compare_metric

# ── DB setup ──────────────────────────────────────────────────────────────────
DB_PATH = root_dir / "sqms.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subject_snapshots (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                class_name    TEXT NOT NULL,
                subject       TEXT NOT NULL,
                snapshot_type TEXT NOT NULL,
                avg_score     REAL,          -- NULL means no score column for this subject
                T             INTEGER NOT NULL DEFAULT 0,
                H             INTEGER NOT NULL DEFAULT 0,
                C             INTEGER NOT NULL DEFAULT 0,
                UNIQUE(academic_year, class_name, subject, snapshot_type)
            )
        """)

def upsert_subject(conn, academic_year, class_name, subject, snapshot_type, avg_score, T, H, C):
    conn.execute("""
        INSERT INTO subject_snapshots
            (academic_year, class_name, subject, snapshot_type, avg_score, T, H, C)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(academic_year, class_name, subject, snapshot_type)
        DO UPDATE SET
            avg_score = excluded.avg_score,
            T = excluded.T, H = excluded.H, C = excluded.C
    """, (academic_year, class_name, subject, snapshot_type, avg_score, T, H, C))

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Báo cáo Chất lượng Giáo dục (SQMS)", layout="wide")
init_db()

def main():
    st.title("Hệ thống Quản lý Chất lượng Giáo dục (SQMS)")

    # ── Sidebar: Upload ──────────────────────────────────────────────────────
    st.sidebar.header("Quản lý Dữ liệu")
    uploaded_file = st.sidebar.file_uploader(
        "Tải lên tệp Excel VNEDU (.xls, .xlsx)", type=["xls", "xlsx"]
    )
    
    label_map = {
        "actual_hk1": "Kết quả Thực tế HK1",
        "actual_hk2": "Kết quả Thực tế HK2",
        "baseline":   "Dữ liệu Đầu năm",
        "target":     "Chỉ tiêu Phấn đấu",
        "commitment": "Chỉ tiêu Cam kết"
    }

    snapshot_type = st.sidebar.selectbox(
        "Nhập dữ liệu dưới dạng:",
        options=list(label_map.keys()),
        format_func=lambda x: label_map[x]
    )

    if uploaded_file is not None:
        if st.sidebar.button("Xử lý & Lưu vào CSDL"):
            temp_path = root_dir / "temp_upload.xls"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                results = parse_vnedu_file(str(temp_path))
                with st.spinner(f"Đang lưu {len(results)} bản ghi..."):
                    with get_conn() as conn:
                        for r in results:
                            upsert_subject(
                                conn,
                                r["academic_year"], r["class"], r["subject"],
                                snapshot_type,
                                r["avg_score"],      # may be None
                                int(r["T"]), int(r["H"]), int(r["C"])
                            )
                st.sidebar.success(f"Đã nhập thành công {len(results)} môn học.")
                os.remove(temp_path)
            except Exception as e:
                st.sidebar.error(f"Lỗi nhập dữ liệu: {e}")
                if temp_path.exists():
                    os.remove(temp_path)

    # ── Filters ───────────────────────────────────────────────────────────────
    with get_conn() as conn:
        years = [r["academic_year"] for r in
                 conn.execute("SELECT DISTINCT academic_year FROM subject_snapshots ORDER BY academic_year DESC").fetchall()]
        classes = [r["class_name"] for r in
                   conn.execute("SELECT DISTINCT class_name FROM subject_snapshots ORDER BY class_name").fetchall()]

    if not years:
        st.info("Chưa có dữ liệu. Vui lòng tải lên tệp excel VNEDU từ thanh bên.")
        return

    st.header("Bảng Tổng hợp")
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Năm học:", years)
    with col2:
        selected_class = st.selectbox("Lớp:", classes)

    # ── Data query ────────────────────────────────────────────────────────────
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT subject, snapshot_type, avg_score, T, H, C
            FROM subject_snapshots
            WHERE academic_year = ? AND class_name = ?
            ORDER BY subject
        """, (selected_year, selected_class)).fetchall()

    if not rows:
        st.warning(f"Không có dữ liệu cho lớp {selected_class} / năm học {selected_year}.")
        return

    # Group by subject → collect snapshot_type data for compare_metric
    from collections import defaultdict
    subject_data: dict = defaultdict(lambda: {"T": 0, "H": 0, "C": 0, "score_data": {}})

    for r in rows:
        d = subject_data[r["subject"]]
        # Keep the latest snapshot's T/H/C (prefer selected snapshot_type)
        d["T"] = r["T"]
        d["H"] = r["H"]
        d["C"] = r["C"]
        # Build score_data dict for compare_metric
        if r["avg_score"] is not None:
            d["score_data"][r["snapshot_type"]] = r["avg_score"]

    # ── Build table ───────────────────────────────────────────────────────────
    trend_map = {
        "increase": "↗ Tăng",
        "decrease": "↘ Giảm",
        "equal":    "→ Không đổi",
        "unknown":  "-"
    }
    status_map = {
        "achieved":     "✅ Đạt",
        "not_achieved": "❌ Chưa đạt",
        "unknown":      "-"
    }

    table_rows = []
    for subject, d in subject_data.items():
        comp = compare_metric(d["score_data"])
        table_rows.append({
            "Môn học":        subject,
            "Điểm TB":        comp["actual"],
            "Tốt (T)":        d["T"],
            "Hoàn thành (H)": d["H"],
            "Chưa đạt (C)":   d["C"],
            "Chênh (Chỉ tiêu)": comp["delta_target"],
            "Xu hướng":       trend_map.get(comp["trend"], "-"),
            "Trạng thái":     status_map.get(comp["status"], "-"),
        })

    df = pd.DataFrame(table_rows)
    # Ensure numeric types for core data columns
    df["Điểm TB"] = pd.to_numeric(df["Điểm TB"], errors="coerce")
    df["Chênh (Chỉ tiêu)"] = pd.to_numeric(df["Chênh (Chỉ tiêu)"], errors="coerce")

    # Formatting for display only
    df_display = df.copy()
    for col in ["Điểm TB", "Chênh (Chỉ tiêu)"]:
        df_display[col] = df_display[col].round(2).astype("string").fillna("-")

    st.subheader(f"Chỉ số chất lượng — {selected_class} ({selected_year})")
    st.dataframe(df_display, width="stretch")

    # ── Charts ────────────────────────────────────────────────────────────────
    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Phân bố mức độ T / H / C")
        df_melt = df.melt(id_vars=["Môn học"], value_vars=["Tốt (T)", "Hoàn thành (H)", "Chưa đạt (C)"],
                          var_name="Mức độ", value_name="Số lượng")
        fig1 = px.bar(df_melt, x="Môn học", y="Số lượng", color="Mức độ", barmode="group",
                      color_discrete_map={"Tốt (T)": "#2ecc71", "Hoàn thành (H)": "#f1c40f", "Chưa đạt (C)": "#e74c3c"})
        st.plotly_chart(fig1, width="stretch")

    with c2:
        st.subheader("Điểm trung bình theo Môn học")
        # Use raw numeric df for charts to avoid label issues
        df_score = df.dropna(subset=["Điểm TB"]).copy()
        fig2 = px.bar(
            df_score, x="Môn học", y="Điểm TB", color="Trạng thái",
            color_discrete_map={"✅ Đạt": "#2ecc71", "❌ Chưa đạt": "#e74c3c", "-": "gray"}
        )
        st.plotly_chart(fig2, width="stretch")

if __name__ == "__main__":
    main()
