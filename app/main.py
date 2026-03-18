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
from app.core.compare import compare_metric, compare_with_targets, compute_thc_percentages

# ── DB setup ──────────────────────────────────────────────────────────────────
DB_PATH = root_dir / "sqms.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_table_columns(conn: sqlite3.Connection) -> set:
    """Get set of column names for subject_snapshots table."""
    cursor = conn.execute("PRAGMA table_info(subject_snapshots)")
    return {row[1] for row in cursor.fetchall()}

def migrate_db():
    """Migrate existing database to support new columns."""
    with get_conn() as conn:
        columns = get_table_columns(conn)
        
        if "student_count" not in columns:
            try:
                conn.execute("ALTER TABLE subject_snapshots ADD COLUMN student_count INTEGER")
            except sqlite3.Error as e:
                pass
        
        if "avg_score" not in columns:
            conn.execute("ALTER TABLE subject_snapshots ADD COLUMN avg_score REAL")

def get_student_count(row: sqlite3.Row) -> int:
    """Safely get student_count from row, fallback to T+H+C if column missing."""
    try:
        if "student_count" in row.keys():
            sc = row["student_count"]
            return sc if sc is not None else (row["T"] + row["H"] + row["C"])
        return row["T"] + row["H"] + row["C"]
    except (KeyError, TypeError):
        return row["T"] + row["H"] + row["C"]

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subject_snapshots (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                class_name    TEXT NOT NULL,
                subject       TEXT NOT NULL,
                snapshot_type TEXT NOT NULL,
                avg_score     REAL,
                student_count INTEGER,
                T             INTEGER NOT NULL DEFAULT 0,
                H             INTEGER NOT NULL DEFAULT 0,
                C             INTEGER NOT NULL DEFAULT 0,
                UNIQUE(academic_year, class_name, subject, snapshot_type)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_class_year 
            ON subject_snapshots(academic_year, class_name)
        """)

def upsert_subject(conn, academic_year, class_name, subject, snapshot_type, avg_score, student_count, T, H, C):
    conn.execute("""
        INSERT INTO subject_snapshots
            (academic_year, class_name, subject, snapshot_type, avg_score, student_count, T, H, C)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(academic_year, class_name, subject, snapshot_type)
        DO UPDATE SET
            avg_score = excluded.avg_score,
            student_count = excluded.student_count,
            T = excluded.T, H = excluded.H, C = excluded.C
    """, (academic_year, class_name, subject, snapshot_type, avg_score, student_count, T, H, C))

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Báo cáo Chất lượng Giáo dục (SQMS)", layout="wide")
init_db()
migrate_db()

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

    # Year override selector for semantic mismatch fix
    # When importing, user can select which academic year this data is FOR
    # (e.g., end-of-year 2024-2025 used as baseline for 2025-2026)
    st.sidebar.caption("Năm học áp dụng (mặc định: từ tệp)")
    year_override = st.sidebar.text_input(
        "Năm học áp dụng",
        value="",
        placeholder="VD: 2025-2026 (để trống = dùng năm từ tệp)",
        help="Để trống để dùng năm học từ tệp Excel. Nhập năm học để ghi đè (VD: năm cuối năm 2024-2025 làm baseline cho 2025-2026)"
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
                            # Override academic_year if user specified a target year
                            target_year = year_override.strip() if year_override.strip() else r["academic_year"]
                            upsert_subject(
                                conn,
                                target_year, r["class"], r["subject"],
                                snapshot_type,
                                r["avg_score"],
                                r.get("student_count"),
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
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_year = st.selectbox("Năm học:", years)
    with col2:
        selected_class = st.selectbox("Lớp:", classes)
    with col3:
        # Standardize the terminology for the view filter
        label_map_view = {
            "actual_hk1": "Kết quả Thực tế HK1",
            "actual_hk2": "Kết quả Thực tế HK2",
            "baseline":   "Dữ liệu Đầu năm",
            "target":     "Chỉ tiêu Phấn đấu",
            "commitment": "Chỉ tiêu Cam kết"
        }
        selected_snapshot = st.selectbox(
            "Xem dữ liệu của:", 
            options=["actual_hk1", "actual_hk2", "baseline", "target", "commitment"],
            format_func=lambda x: label_map_view.get(x, x),
            index=0
        )

    # ── Data query ────────────────────────────────────────────────────────────
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT subject, snapshot_type, avg_score, student_count, T, H, C
            FROM subject_snapshots
            WHERE academic_year = ? AND class_name = ?
            ORDER BY subject
        """, (selected_year, selected_class)).fetchall()

    if not rows:
        st.warning(f"Không có dữ liệu cho lớp {selected_class} / năm học {selected_year}.")
        return

    # Group by subject → collect data for comparison
    from collections import defaultdict
    subject_data: dict = defaultdict(lambda: {
        "student_count": 0, "T": 0, "H": 0, "C": 0,
        "T_pct": None, "H_pct": None, "C_pct": None,
        "score_data": {}, "target_score": None,
        "target_T_pct": None, "target_H_pct": None, "target_C_pct": None,
    })

    is_actual = selected_snapshot in ("actual_hk1", "actual_hk2")

    for r in rows:
        d = subject_data[r["subject"]]
        snapshot_type = r["snapshot_type"]
        student_count = get_student_count(r)
        
        if snapshot_type == selected_snapshot:
            d["student_count"] = student_count
            d["T"] = r["T"]
            d["H"] = r["H"]
            d["C"] = r["C"]
            if d["student_count"] > 0:
                pct = compute_thc_percentages(r["T"], r["H"], r["C"], d["student_count"])
                d["T_pct"] = pct["T_pct"]
                d["H_pct"] = pct["H_pct"]
                d["C_pct"] = pct["C_pct"]

        avg_score = r["avg_score"] if "avg_score" in r.keys() else None
        if avg_score is not None:
            d["score_data"][snapshot_type] = avg_score
        
        if snapshot_type in ("target", "commitment") and avg_score is not None:
            d["target_score"] = avg_score
            if student_count > 0:
                pct = compute_thc_percentages(r["T"], r["H"], r["C"], student_count)
                d["target_T_pct"] = pct["T_pct"]
                d["target_H_pct"] = pct["H_pct"]
                d["target_C_pct"] = pct["C_pct"]


    # ── Build table ───────────────────────────────────────────────────────────
    status_map = {
        "achieved":     "✅ Đạt",
        "not_achieved": "❌ Chưa đạt",
        "partial":      "⚠️ Một phần",
        "unknown":      "-"
    }

    table_rows = []
    for subject, d in subject_data.items():
        score_comp = compare_metric(d["score_data"], selected_snapshot)
        target_comp = compare_with_targets(
            d["T_pct"] if d["student_count"] > 0 else None,
            d["H_pct"] if d["student_count"] > 0 else None,
            d["C_pct"] if d["student_count"] > 0 else None,
            d["target_score"],
            d["target_T_pct"],
            d["target_H_pct"],
            d["target_C_pct"],
        )
        
        # Format percentage display
        def fmt_pct(val):
            if val is None:
                return "-"
            return f"{val:.1f}%"
        
        def fmt_delta(val):
            if val is None:
                return "-"
            sign = "+" if val > 0 else ""
            return f"{sign}{val:.2f}"
        
        table_rows.append({
            "Môn học":          subject,
            "Điểm TB":          score_comp["actual"],
            "Chênh Điểm":       fmt_delta(score_comp["delta_target"]),
            "T (%)":            fmt_pct(d["T_pct"]),
            "H (%)":            fmt_pct(d["H_pct"]),
            "C (%)":            fmt_pct(d["C_pct"]),
            "Chênh T%":         fmt_delta(target_comp["T_delta"]),
            "Chênh C%":         fmt_delta(target_comp["C_delta"]),
            "Trạng thái":       status_map.get(target_comp["score_status"], "-"),
        })

    df = pd.DataFrame(table_rows)
    df_numeric = df.copy()
    df_numeric["Điểm TB"] = pd.to_numeric(df_numeric["Điểm TB"], errors="coerce")

    st.subheader(f"Chỉ số chất lượng — {selected_class} ({selected_year})")
    st.dataframe(df, width="stretch")

    # ── Charts ────────────────────────────────────────────────────────────────
    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Phân bố mức độ T / H / C (%)")
        df_pct = df[df["T (%)"] != "-"].copy()
        if not df_pct.empty:
            df_melt = df_pct.melt(
                id_vars=["Môn học"], 
                value_vars=["T (%)", "H (%)", "C (%)"],
                var_name="Mức độ", value_name="Phần trăm"
            )
            df_melt["Phần trăm"] = df_melt["Phần trăm"].str.rstrip("%").astype(float)
            fig1 = px.bar(
                df_melt, x="Môn học", y="Phần trăm", color="Mức độ", barmode="group",
                color_discrete_map={"T (%)": "#2ecc71", "H (%)": "#f1c40f", "C (%)": "#e74c3c"}
            )
            st.plotly_chart(fig1, width="stretch")
        else:
            st.info("Không có dữ liệu T/H/C để hiển thị")

    with c2:
        st.subheader("Điểm trung bình theo Môn học")
        df_score = df.dropna(subset=["Điểm TB"]).copy()
        if not df_score.empty:
            fig2 = px.bar(
                df_score, x="Môn học", y="Điểm TB", color="Trạng thái",
                color_discrete_map={"✅ Đạt": "#2ecc71", "❌ Chưa đạt": "#e74c3c", "-": "gray"}
            )
            st.plotly_chart(fig2, width="stretch")
        else:
            st.info("Không có dữ liệu điểm để hiển thị")

if __name__ == "__main__":
    main()
