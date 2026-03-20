"""
Mô tả file:
- Vai trò: Ứng dụng Streamlit chính - giao diện quản lý dữ liệu VNEDU
- Input: File Excel VNEDU, dữ liệu từ người dùng (cam kết GV, thành tích HS)
- Output: Dashboard hiển thị, lưu trữ SQLite
- Phụ thuộc: streamlit, pandas, plotly, app.infra.vnedu_parser, app.core.compare

Cấu trúc ứng dụng:
├── Sidebar: Upload file, chọn loại dữ liệu
├── Tab 1 (📊 Tổng hợp): Dashboard so sánh điểm, T/H/C theo môn học
├── Tab 2 (📝 Cam kết GV): Nhập và quản lý chỉ tiêu giáo viên
└── Tab 3 (🏆 Thành tích HS): Nhập và xem thành tích học sinh

Database Schema:
├── subject_snapshots: Điểm và T/H/C theo môn học
├── class_summary: Tổng hợp xếp loại cấp lớp (HTXS, HTT, HT, CHT)
├── teacher_commitments: Cam kết của giáo viên
└── student_achievements: Thành tích học sinh các cấp

Snapshot Types:
- actual_hk1, actual_hk2: Dữ liệu thực tế
- baseline: Dữ liệu năm trước (đã shift grade lên)
- target: Mục tiêu năm nay
- commitment: Cam kết giáo viên
"""

import sys
import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px

root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.infra.vnedu_parser import parse_vnedu_file_with_class_summary, normalize_year, _normalize  # noqa: E402
from app.core.compare import compare_metric, compare_with_targets, compute_thc_percentages  # noqa: E402

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE LAYER - Kết nối và quản lý SQLite
# ═══════════════════════════════════════════════════════════════════════════════

# Đường dẫn file SQLite (nằm cùng cấp với project root)
DB_PATH = root_dir / "sqms.db"


def get_conn() -> sqlite3.Connection:
    """
    Mô tả:
        Tạo kết nối SQLite mới với row_factory=sqlite3.Row.

    Output:
        (sqlite3.Connection): Connection đã configure

    Lưu ý:
        - Gọi close() sau khi dùng xong
        - Hoặc dùng context manager: with get_conn() as conn:
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    Mô tả:
        Kiểm tra table có tồn tại trong database không.

    Input:
        conn (sqlite3.Connection): Kết nối database
        table_name (str): Tên table cần kiểm tra

    Output:
        (bool): True nếu table tồn tại
    """
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cur.fetchone() is not None


def migrate_db():
    """
    Mô tả:
        Migration database - thêm columns thiếu và chuẩn hoá academic_year.

    Logic:
        1. Thêm student_count, avg_score vào subject_snapshots nếu chưa có
        2. Chuẩn hoá format academic_year: "2024 - 2025" -> "2024-2025"

    Lưu ý:
        - Dùng table_exists() để tránh crash khi table chưa tồn tại
        - Gọi sau init_db() trong main()
    """
    conn = get_conn()
    try:
        # Chỉ migrate nếu table tồn tại
        if table_exists(conn, "subject_snapshots"):
            # Thêm columns mới nếu thiếu (hỗ trợ old database)
            columns = {row[1] for row in conn.execute("PRAGMA table_info(subject_snapshots)").fetchall()}
            if "student_count" not in columns:
                conn.execute("ALTER TABLE subject_snapshots ADD COLUMN student_count INTEGER")
            if "avg_score" not in columns:
                conn.execute("ALTER TABLE subject_snapshots ADD COLUMN avg_score REAL")

            # Chuẩn hoá academic_year: loại bỏ khoảng trắng thừa
            conn.execute("UPDATE subject_snapshots SET academic_year = REPLACE(academic_year, ' - ', '-')")
            conn.execute("UPDATE subject_snapshots SET academic_year = REPLACE(academic_year, '  -  ', '-')")

        if table_exists(conn, "teacher_commitments"):
            conn.execute("UPDATE teacher_commitments SET academic_year = REPLACE(academic_year, ' - ', '-')")
            conn.execute("UPDATE teacher_commitments SET academic_year = REPLACE(academic_year, '  -  ', '-')")

        if table_exists(conn, "class_summary"):
            conn.execute("UPDATE class_summary SET academic_year = REPLACE(academic_year, ' - ', '-')")

        if table_exists(conn, "student_achievements"):
            conn.execute("UPDATE student_achievements SET academic_year = REPLACE(academic_year, ' - ', '-')")

        conn.commit()
    finally:
        conn.close()


def init_db():
    """
    Mô tả:
        Khởi tạo bảng subject_snapshots - lưu điểm và T/H/C theo môn học.

    Schema:
        - academic_year: Năm học (format: YYYY-YYYY)
        - class_name: Tên lớp (VD: "1A")
        - subject: Tên môn học
        - snapshot_type: Loại snapshot (actual_hk1, actual_hk2, baseline, target)
        - avg_score: Điểm trung bình
        - student_count: Tổng số học sinh
        - T, H, C: Số học sinh mỗi loại

    Data Contract - subject_snapshots:
        Key duy nhất: (academic_year, class_name, subject, snapshot_type)
    """
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subject_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                snapshot_type TEXT NOT NULL,
                avg_score REAL,
                student_count INTEGER,
                T INTEGER NOT NULL DEFAULT 0,
                H INTEGER NOT NULL DEFAULT 0,
                C INTEGER NOT NULL DEFAULT 0,
                UNIQUE(academic_year, class_name, subject, snapshot_type)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots ON subject_snapshots(academic_year, class_name)")


def init_teacher_commitments():
    """
    Mô tả:
        Khởi tạo bảng teacher_commitments - lưu cam kết của giáo viên.

    Schema:
        - avg_score_target: Mục tiêu điểm trung bình
        - T_pct_target, H_pct_target, C_pct_target: Mục tiêu phần trăm T/H/C
        - HTXS_target, HTT_target, HT_target, CHT_target: Mục tiêu xếp loại cấp lớp
    """
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS teacher_commitments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                avg_score_target REAL,
                T_pct_target REAL,
                H_pct_target REAL,
                C_pct_target REAL,
                HTXS_target INTEGER DEFAULT 0,
                HTT_target INTEGER DEFAULT 0,
                HT_target INTEGER DEFAULT 0,
                CHT_target INTEGER DEFAULT 0,
                UNIQUE(academic_year, class_name, subject)
            )
        """)


def init_student_achievements():
    """
    Mô tả:
        Khởi tạo bảng student_achievements - lưu thành tích học sinh.

    Schema:
        - category: Hạng mục (VD: "IOE", "Văn Toán Tuổi thơ")
        - level: Cấp độ (Xã, Quận/Huyện, Tỉnh/Thành phố, Quốc gia, Quốc tế)
        - quantity: Số lượng học sinh đạt giải/thành tích
    """
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS student_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                category TEXT NOT NULL,
                level TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                UNIQUE(academic_year, category, level)
            )
        """)


def init_class_summary():
    """
    Mô tả:
        Khởi tạo bảng class_summary - lưu tổng hợp xếp loại cấp lớp.

    Schema:
        - HTXS, HTT, HT, CHT: Số học sinh xếp loại từng cấp
        - HTCTLH_HT, HTCTLH_CHT: Học sinh hoàn thành/CTLH
        - HSXS, HS_TieuBieu: Học sinh xuất sắc, tiêu biểu
    """
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS class_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                class_name TEXT NOT NULL,
                snapshot_type TEXT NOT NULL,
                HTXS INTEGER DEFAULT 0,
                HTT INTEGER DEFAULT 0,
                HT INTEGER DEFAULT 0,
                CHT INTEGER DEFAULT 0,
                HTCTLH_HT INTEGER DEFAULT 0,
                HTCTLH_CHT INTEGER DEFAULT 0,
                HSXS INTEGER DEFAULT 0,
                HS_TieuBieu INTEGER DEFAULT 0,
                UNIQUE(academic_year, class_name, snapshot_type)
            )
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA ACCESS LAYER - CRUD operations
# ═══════════════════════════════════════════════════════════════════════════════

def upsert_subject(conn, academic_year, class_name, subject, snapshot_type, avg_score, student_count, T, H, C):
    """
    Mô tả:
        Insert hoặc update subject snapshot.

    Input:
        conn: SQLite connection
        academic_year (str): Năm học (format YYYY-YYYY)
        class_name (str): Tên lớp (KHÔNG dùng "class")
        subject (str): Tên môn học đã chuẩn hoá
        snapshot_type (str): Loại snapshot
        avg_score (float|None): Điểm TB
        student_count (int): Sĩ số
        T, H, C (int): Số học sinh mỗi loại

    Lưu ý:
        - ON CONFLICT: update nếu đã tồn tại (theo unique key)
        - Dùng class_name, KHÔNG dùng class
    """
    conn.execute("""
        INSERT INTO subject_snapshots (academic_year, class_name, subject, snapshot_type, avg_score, student_count, T, H, C)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(academic_year, class_name, subject, snapshot_type)
        DO UPDATE SET avg_score=excluded.avg_score, student_count=excluded.student_count,
                      T=excluded.T, H=excluded.H, C=excluded.C
    """, (academic_year, class_name, subject, snapshot_type, avg_score, student_count, T, H, C))


def upsert_class_summary(conn, academic_year, class_name, snapshot_type, HTXS=0, HTT=0, HT=0, CHT=0,
                          HTCTLH_HT=0, HTCTLH_CHT=0, HSXS=0, HS_TieuBieu=0):
    """
    Mô tả:
        Insert hoặc update class summary - tổng hợp xếp loại cấp lớp.

    Input:
        conn: SQLite connection
        academic_year, class_name, snapshot_type: Các trường identifier
        HTXS, HTT, HT, CHT: Số học sinh xếp loại
        HTCTLH_HT, HTCTLH_CHT: CTLH hoàn thành/CTLH
        HSXS, HS_TieuBieu: Học sinh xuất sắc, tiêu biểu
    """
    conn.execute("""
        INSERT INTO class_summary (academic_year, class_name, snapshot_type, HTXS, HTT, HT, CHT,
                                    HTCTLH_HT, HTCTLH_CHT, HSXS, HS_TieuBieu)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(academic_year, class_name, snapshot_type)
        DO UPDATE SET HTXS=excluded.HTXS, HTT=excluded.HTT, HT=excluded.HT, CHT=excluded.CHT,
                      HTCTLH_HT=excluded.HTCTLH_HT, HTCTLH_CHT=excluded.HTCTLH_CHT,
                      HSXS=excluded.HSXS, HS_TieuBieu=excluded.HS_TieuBieu
    """, (academic_year, class_name, snapshot_type, HTXS, HTT, HT, CHT, HTCTLH_HT, HTCTLH_CHT, HSXS, HS_TieuBieu))


def upsert_teacher_commitment(conn, academic_year, class_name, subject, avg_score_target=None,
                               T_pct_target=None, H_pct_target=None, C_pct_target=None,
                               HTXS_target=0, HTT_target=0, HT_target=0, CHT_target=0):
    """
    Mô tả:
        Insert hoặc update teacher commitment - cam kết của giáo viên.

    Input:
        conn: SQLite connection
        avg_score_target: Mục tiêu điểm TB
        T_pct_target, H_pct_target, C_pct_target: Mục tiêu phần trăm T/H/C (số tuyệt đối, không phải %)
        HTXS_target, HTT_target, HT_target, CHT_target: Mục tiêu số học sinh xếp loại
    """
    conn.execute("""
        INSERT INTO teacher_commitments (academic_year, class_name, subject, avg_score_target,
                                          T_pct_target, H_pct_target, C_pct_target,
                                          HTXS_target, HTT_target, HT_target, CHT_target)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(academic_year, class_name, subject)
        DO UPDATE SET avg_score_target=excluded.avg_score_target, T_pct_target=excluded.T_pct_target,
                      H_pct_target=excluded.H_pct_target, C_pct_target=excluded.C_pct_target,
                      HTXS_target=excluded.HTXS_target, HTT_target=excluded.HTT_target,
                      HT_target=excluded.HT_target, CHT_target=excluded.CHT_target
    """, (academic_year, class_name, subject, avg_score_target, T_pct_target, H_pct_target, C_pct_target,
          HTXS_target, HTT_target, HT_target, CHT_target))


def upsert_student_achievement(conn, academic_year, category, level, quantity):
    """
    Mô tả:
        Insert hoặc update student achievement.

    Input:
        conn: SQLite connection
        category (str): Hạng mục (VD: "IOE", "Văn Toán Tuổi thơ")
        level (str): Cấp độ (Xã, Quận/Huyện, Tỉnh/Thành phố, Quốc gia, Quốc tế)
        quantity (int): Số lượng
    """
    conn.execute("""
        INSERT INTO student_achievements (academic_year, category, level, quantity)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(academic_year, category, level)
        DO UPDATE SET quantity=excluded.quantity
    """, (academic_year, category, level, quantity))


def get_student_count(row) -> int:
    """
    Mô tả:
        Lấy sĩ số từ row - ưu tiên student_count, fallback bằng T+H+C.

    Input:
        row (sqlite3.Row hoặc dict): Row từ database

    Output:
        (int): Sĩ số lớp
    """
    try:
        sc = row["student_count"] if "student_count" in row.keys() else None
        return sc if sc is not None else (row["T"] + row["H"] + row["C"])
    except (KeyError, TypeError):
        return row["T"] + row["H"] + row["C"]


def get_achievements_summary(academic_year: str) -> pd.DataFrame:
    """
    Mô tả:
        Query achievements summary - pivot theo category và level.

    Input:
        academic_year (str): Năm học

    Output:
        (pd.DataFrame): DataFrame với columns: category, Xã, Quận/Huyện, Tỉnh/Thành phố, Quốc gia, Quốc tế, Tổng
    """
    return pd.read_sql("""
        SELECT category,
               SUM(CASE WHEN level='Xã' THEN quantity ELSE 0 END) as "Xã",
               SUM(CASE WHEN level='Quận/Huyện' THEN quantity ELSE 0 END) as "Quận/Huyện",
               SUM(CASE WHEN level='Tỉnh/Thành phố' THEN quantity ELSE 0 END) as "Tỉnh/Thành phố",
               SUM(CASE WHEN level='Quốc gia' THEN quantity ELSE 0 END) as "Quốc gia",
               SUM(CASE WHEN level='Quốc tế' THEN quantity ELSE 0 END) as "Quốc tế",
               SUM(quantity) as "Tổng"
        FROM student_achievements WHERE academic_year = ?
        GROUP BY category ORDER BY category
    """, get_conn(), params=(academic_year,))


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS - Các hằng số và mapping
# ═══════════════════════════════════════════════════════════════════════════════

# Các hạng mục thành tích học sinh
ACHIEVEMENT_CATEGORIES = [
    "Văn Toán Tuổi thơ", "Tin học trẻ", "IOE", "VioEdu",
    "Tiếng Anh", "Khoa học Kỹ thuật", "Hội thi Olympic", "Hội thi HSG", "Khác"
]

# Các cấp độ thành tích
ACHIEVEMENT_LEVELS = ["Xã", "Quận/Huyện", "Tỉnh/Thành phố", "Quốc gia", "Quốc tế"]

# Mapping snapshot_type -> label hiển thị
LABEL_MAP = {
    "actual_hk1": "Kết quả HK1",
    "actual_hk2": "Kết quả HK2",
    "baseline": "Dữ liệu Đầu năm",
    "target": "Chỉ tiêu Phấn đấu",
    "commitment": "Cam kết GV"
}


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - Các hàm tiện ích
# ═══════════════════════════════════════════════════════════════════════════════

def clamp_score(value: Optional[float]) -> Optional[float]:
    """
    Mô tả:
        Giới hạn giá trị điểm trong khoảng 0-10.

    Input:
        value (float|None): Điểm đầu vào

    Output:
        (float|None): Điểm đã clamp, hoặc None
    """
    if value is None:
        return None
    return max(0.0, min(10.0, value))


def parse_delta(delta_str: str) -> Optional[float]:
    """
    Mô tả:
        Parse delta string thành float.

    Input:
        delta_str (str): VD: "+0.5", "-0.3", "0.5"

    Output:
        (float|None): Giá trị delta, hoặc None nếu invalid
                     Chỉ chấp nhận range -1.0 đến 2.0

    Lưu ý:
        - Hỗ trợ dấu "+" và "-"
        - Replace "," bằng "." cho format Việt Nam
    """
    if not delta_str or not delta_str.strip():
        return None
    s = delta_str.strip().replace(",", ".")
    if s.startswith("+"):
        s = s[1:]
    try:
        value = float(s)
        # Validate range: -1.0 to 2.0
        if -1.0 <= value <= 2.0:
            return value
        return None
    except ValueError:
        return None


def increment_academic_year(year: str) -> Optional[str]:
    """
    Mô tả:
        Tăng năm học lên 1.

    Input:
        year (str): Năm học format YYYY-YYYY (VD: "2024-2025")

    Output:
        (str|None): Năm học tiếp theo (VD: "2025-2026")

    Lưu ý:
        - Yêu cầu start_year + 1 = end_year (đúng format)
        - VD: "2024-2025" -> "2025-2026" ✓
             "2024-2026" -> None (invalid)
    """
    import re
    if not year:
        return None
    match = re.match(r'^(\d{4})\s*[-–—]\s*(\d{4})$', year.strip())
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    return f"{start + 1}-{end + 1}" if end == start + 1 else None


def shift_class_name(class_name: str) -> Optional[str]:
    """
    Mô tả:
        Shift tên lớp lên 1 grade.

    Input:
        class_name (str): VD: "1A", "2B"

    Output:
        (str|None): Lớp sau khi shift (VD: "2A", "3B")
                    None nếu grade >= 5 (không có lớp 6)

    Lưu ý:
        - Grade 1-4 được shift lên (1->2, 2->3, 3->4, 4->5)
        - Grade 5 trở lên không shift (None)
    """
    import re
    if not class_name:
        return None
    match = re.match(r'^(\d+)\s*([A-Z]?)\s*$', class_name.strip())
    if not match:
        return None
    grade, suffix = int(match.group(1)), match.group(2) or ""
    return f"{grade + 1}{suffix}" if 1 <= grade < 5 else None


def generate_target_from_baseline(baseline_record: dict, score_delta: float) -> Optional[dict]:
    """
    Mô tả:
        Tạo target record từ baseline - dùng cho việc tự động tạo chỉ tiêu.

    Logic:
        1. Tính target_avg = baseline_avg + score_delta
        2. Giữ nguyên T/H/C từ baseline
        3. Update academic_year và class_name đã shifted

    Input:
        baseline_record (dict): Record baseline với keys:
            - academic_year_shifted: Năm học đã increment
            - class_shifted: Tên lớp đã shift
            - avg_score: Điểm TB gốc
            - T, H, C: Số học sinh mỗi loại
        score_delta (float): Delta điểm (VD: 0.5)

    Output:
        (dict|None): Target record, hoặc None nếu baseline không có avg_score

    Data Contract - Output:
        {
            "academic_year": str,    # Đã shift
            "class_name": str,      # Đã shift
            "subject": str,
            "snapshot_type": "target",
            "avg_score": float,
            "student_count": int,
            "T": int, "H": int, "C": int
        }
    """
    baseline_avg = baseline_record.get("avg_score")
    if baseline_avg is None:
        return None
    target_avg = clamp_score(baseline_avg + score_delta)
    student_count = baseline_record.get("student_count") or (baseline_record["T"] + baseline_record["H"] + baseline_record["C"])
    return {
        "academic_year": baseline_record.get("academic_year_shifted") or baseline_record["academic_year"],
        "class_name": baseline_record.get("class_shifted") or baseline_record["class_name"],
        "subject": baseline_record["subject"],
        "snapshot_type": "target",
        "avg_score": target_avg,
        "student_count": student_count,
        "T": baseline_record["T"],
        "H": baseline_record["H"],
        "C": baseline_record["C"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - Thanh bên upload và điều khiển
# ═══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    """
    Mô tả:
        Render sidebar - upload file và chọn loại dữ liệu.

    Output:
        (tuple): (files, snapshot_type, process_clicked, score_delta)

    Lưu ý:
        - Dùng session_state để reset uploader khi cần
        - score_delta chỉ có giá trị khi snapshot_type == "baseline"
    """
    st.sidebar.header("📤 Nhập liệu")

    # Reset uploader key khi cần
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    # Upload nhiều file Excel cùng lúc
    uploaded_files = st.sidebar.file_uploader(
        "Tải file Excel VNEDU",
        type=["xls", "xlsx"],
        accept_multiple_files=True,
        key=f"upload_{st.session_state.uploader_key}"
    )

    if uploaded_files:
        st.sidebar.caption(f"Đã chọn {len(uploaded_files)} tệp")

    # Chọn loại dữ liệu
    snapshot_type = st.sidebar.selectbox(
        "Loại dữ liệu",
        options=list(LABEL_MAP.keys()),
        format_func=lambda x: LABEL_MAP[x]
    )

    # Delta điểm chỉ hiển thị khi import baseline
    score_delta = None
    if snapshot_type == "baseline":
        delta_input = st.sidebar.text_input(
            "Tăng điểm TB",
            value="",
            placeholder="VD: +0.5",
            help="Tự động tạo chỉ tiêu từ baseline"
        )
        score_delta = parse_delta(delta_input)

    # Nút xử lý - disabled nếu chưa upload file
    process_clicked = st.sidebar.button("Xử lý & Lưu", type="primary", disabled=not uploaded_files)

    return uploaded_files, snapshot_type, process_clicked, score_delta


# ═══════════════════════════════════════════════════════════════════════════════
# PROCESS FILES - Xử lý file upload
# ═══════════════════════════════════════════════════════════════════════════════

def process_files(files, snapshot_type, score_delta):
    """
    Mô tả:
        Xử lý các file Excel đã upload - parse và lưu vào database.

    Logic:
        1. Parse từng file bằng vnedu_parser
        2. Nếu snapshot_type == "baseline": shift grade và tạo target
        3. Upsert vào database (subject_snapshots và class_summary)

    Input:
        files: List các uploaded files
        snapshot_type (str): Loại dữ liệu
        score_delta (float|None): Delta điểm cho target generation

    Lưu ý:
        - Baseline data được shift: lớp 1->2, năm +1
        - Target được tạo tự động nếu có score_delta
    """
    progress_bar = st.sidebar.progress(0)
    progress_text = st.sidebar.empty()

    all_subjects = []
    all_class_summary = []
    targets = []  # temporary targets generated from baseline (no shifting)
    errors = []

    # Parse từng file
    for idx, file in enumerate(files):
        progress_text.text(f"Đang xử lý {idx + 1}/{len(files)}: {file.name}")
        progress_bar.progress((idx + 1) / len(files))

        # Ghi file tạm để parse
        temp_path = root_dir / f"temp_{uuid.uuid4().hex}_{file.name}"
        try:
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            # Parse file Excel - KQGD gate enforcement
            allow_kqgd = snapshot_type in {"baseline", "actual_hk2"}
            subjects, class_data = parse_vnedu_file_with_class_summary(
                str(temp_path), allow_kqgd=allow_kqgd
            )
            # Normalize subject names will be handled later, before DB insert (uniformly for all snapshots)
            all_subjects.extend(subjects)
            if allow_kqgd:
                all_class_summary.extend(class_data)
            # Generate targets from baseline if requested (no shifting)
            if snapshot_type == "baseline" and score_delta is not None:
                for r in subjects:
                    tgt = generate_target_from_baseline(r, score_delta)
                    if tgt:
                        targets.append(tgt)
        except Exception as e:
            errors.append(f"{file.name}: {e}")
        finally:
            # Dọn file tạm
            if temp_path.exists():
                os.remove(temp_path)

    # Deduplicate by normalized subject name across same (academic_year, class, snapshot_type)
    deduped_subjects: List[Dict[str, Any]] = []
    if all_subjects:
        group: Dict[Tuple, Dict[str, Any]] = {}
        for r in all_subjects:
            acc_year = r.get("academic_year")
            cls = r.get("class_name")
            snap = r.get("snapshot_type", snapshot_type)
            subj = r.get("subject", "")
            norm = _normalize(subj)
            norm = " ".join(norm.split()) if norm else subj
            key = (acc_year, cls, snap, norm)
            if key not in group:
                group[key] = {
                    "academic_year": acc_year,
                    "class_name": cls,
                    "subject": norm,
                    "snapshot_type": snap,
                    "T": 0,
                    "H": 0,
                    "C": 0,
                    "avg_score_sum": 0.0,
                    "avg_count": 0,
                    "student_count": r.get("student_count"),
                }
            g = group[key]
            g["T"] += int(r.get("T") or 0)
            g["H"] += int(r.get("H") or 0)
            g["C"] += int(r.get("C") or 0)
            if r.get("avg_score") is not None:
                g["avg_score_sum"] += float(r["avg_score"])
                g["avg_count"] += 1
            sc = r.get("student_count")
            if sc is not None:
                if g["student_count"] is None or sc > g["student_count"]:
                    g["student_count"] = sc

        for gr in group.values():
            avg_final = None
            if gr["avg_count"] > 0:
                avg_final = round(gr["avg_score_sum"] / gr["avg_count"], 2)
            deduped_subjects.append({
                "academic_year": gr["academic_year"],
                "class_name": gr["class_name"],
                "subject": gr["subject"],
                "snapshot_type": gr["snapshot_type"],
                "avg_score": avg_final,
                "student_count": gr["student_count"],
                "T": gr["T"],
                "H": gr["H"],
                "C": gr["C"],
            })
    all_subjects = deduped_subjects

    # Lưu vào database
    saved_count = 0
    try:
        with get_conn() as conn:
            conn.execute("BEGIN TRANSACTION")
            for r in all_subjects:
                # Do not normalize here; normalization happens in grouping step
                snapshot_type_to_store = r.get("snapshot_type", snapshot_type)
                upsert_subject(conn, r["academic_year"], r["class_name"], r["subject"], snapshot_type_to_store,
                               r.get("avg_score"), r.get("student_count"), r["T"], r["H"], r["C"])
                saved_count += 1
            for cs in all_class_summary:
                snapshot_type_to_store_cs = cs.get("snapshot_type", snapshot_type)
                upsert_class_summary(conn, cs.get("academic_year", ""), cs.get("class_name", ""),
                                     snapshot_type_to_store_cs, cs.get("HTXS", 0), cs.get("HTT", 0),
                                     cs.get("HT", 0), cs.get("CHT", 0))
            conn.execute("COMMIT")
    except Exception as e:
        st.error(f"Lỗi lưu dữ liệu: {e}")
        return False

    progress_bar.empty()
    progress_text.empty()

    st.success(f"Đã lưu {saved_count} bản ghi")
    if errors:
        st.warning(f"Lỗi: {', '.join(errors)}")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD - Dashboard tổng hợp điểm và T/H/C
# ═══════════════════════════════════════════════════════════════════════════════

def render_dashboard():
    """
    Mô tả:
        Render dashboard - hiển thị điểm và T/H/C theo môn học.

    Features:
        - Filter theo năm học và lớp
        - Chọn loại snapshot để so sánh
        - Hiển thị bảng với delta, trạng thái đạt/chưa đạt
        - Charts: Phân bố T/H/C, Điểm TB

    Lưu ý:
        - Sĩ số (student_count) được đọc từ subject_snapshots
        - Trạng thái so với target: achieved/not_achieved/partial/unknown
    """
    with get_conn() as conn:
        years = [r["academic_year"] for r in conn.execute(
            "SELECT DISTINCT academic_year FROM subject_snapshots ORDER BY academic_year DESC").fetchall()]

    if not years:
        st.info("Chưa có dữ liệu. Vui lòng tải lên file Excel.")
        return

    # Filter: năm học và lớp
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Năm học", years, key="dash_year")
    with col2:
        with get_conn() as conn:
            classes = [r[0] for r in conn.execute(
                "SELECT DISTINCT class_name FROM subject_snapshots WHERE academic_year=? ORDER BY class_name",
                (selected_year,)).fetchall()]
        if not classes:
            st.info("Không có dữ liệu lớp")
            return
        selected_class = st.selectbox("Lớp", classes, key="dash_class")

    # Query dữ liệu
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM subject_snapshots WHERE academic_year=? AND class_name=? ORDER BY subject",
            (selected_year, selected_class)).fetchall()

    if not rows:
        st.info("Không có dữ liệu")
        return

    # Build data structure
    snapshot_types = list(set(r["snapshot_type"] for r in rows))
    selected_snapshot = st.selectbox("Xem kết quả", snapshot_types,
                                      format_func=lambda x: LABEL_MAP.get(x, x), key="dash_snap")

    # Khởi tạo data structure cho từng môn
    subjects = list(set(r["subject"] for r in rows))
    subject_data = {s: {"score_data": {}, "T_pct": None, "H_pct": None, "C_pct": None,
                        "target_score": None, "target_T_pct": None, "target_H_pct": None, "target_C_pct": None,
                        "student_count": 0} for s in subjects}

    # Populate data từ rows
    for r in rows:
        d = subject_data[r["subject"]]
        snap = r["snapshot_type"]

        # Lấy dữ liệu của snapshot được chọn
        if snap == selected_snapshot:
            d["student_count"] = get_student_count(r)
            d["T"], d["H"], d["C"] = r["T"], r["H"], r["C"]
            if d["student_count"] > 0:
                pct = compute_thc_percentages(r["T"], r["H"], r["C"], d["student_count"])
                d["T_pct"], d["H_pct"], d["C_pct"] = pct["T_pct"], pct["H_pct"], pct["C_pct"]

        # Thu thập score data và target/commitment data
        avg = r["avg_score"] if "avg_score" in r.keys() else None
        if avg is not None:
            d["score_data"][snap] = avg
        if snap in ("target", "commitment") and avg is not None:
            d["target_score"] = avg
            if get_student_count(r) > 0:
                pct = compute_thc_percentages(r["T"], r["H"], r["C"], get_student_count(r))
                d["target_T_pct"], d["target_H_pct"], d["target_C_pct"] = pct["T_pct"], pct["H_pct"], pct["C_pct"]

    # Mapping trạng thái cho display
    status_map = {"achieved": "✅ Đạt", "not_achieved": "❌ Chưa đạt", "partial": "⚠️ Một phần", "unknown": "-"}

    # Formatters
    def fmt_pct(v): return f"{v:.1f}%" if v is not None else "-"
    def fmt_delta(v): return f"{v:+.2f}" if v is not None else "-"

    # Build table rows
    table_rows = []
    for subj, d in subject_data.items():
        # So sánh điểm với target/commitment
        score_comp = compare_metric(d["score_data"], selected_snapshot)
        target_comp = compare_with_targets(
            d["T_pct"] if d["student_count"] > 0 else None,
            d["H_pct"] if d["student_count"] > 0 else None,
            d["C_pct"] if d["student_count"] > 0 else None,
            d["target_score"], d["target_T_pct"], d["target_H_pct"], d["target_C_pct"])
        table_rows.append({
            "Môn học": subj, "Điểm TB": score_comp["actual"],
            "Δ Điểm": fmt_delta(score_comp["delta_target"]),
            "T (%)": fmt_pct(d["T_pct"]), "H (%)": fmt_pct(d["H_pct"]), "C (%)": fmt_pct(d["C_pct"]),
            "Δ T%": fmt_delta(target_comp["T_delta"]), "Δ C%": fmt_delta(target_comp["C_delta"]),
            "Trạng thái": status_map.get(target_comp["score_status"], "-"),
        })

    # Hiển thị bảng
    df = pd.DataFrame(table_rows)
    st.dataframe(df, width="stretch", hide_index=True)

    # Charts
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Phân bố T/H/C")
        df_pct = df[df["T (%)"] != "-"].copy()
        if not df_pct.empty:
            df_melt = df_pct.melt(id_vars=["Môn học"], value_vars=["T (%)", "H (%)", "C (%)"],
                                   var_name="Mức", value_name="%")
            df_melt["%"] = df_melt["%"].str.rstrip("%").astype(float)
            fig = px.bar(df_melt, x="Môn học", y="%", color="Mức", barmode="group",
                         color_discrete_map={"T (%)": "#2ecc71", "H (%)": "#f1c40f", "C (%)": "#e74c3c"})
            st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Điểm TB")
        df_score = df.dropna(subset=["Điểm TB"]).copy()
        if not df_score.empty:
            fig = px.bar(df_score, x="Môn học", y="Điểm TB", color="Trạng thái",
                         color_discrete_map={"✅ Đạt": "#2ecc71", "❌ Chưa đạt": "#e74c3c", "-": "gray"})
            st.plotly_chart(fig, width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: TEACHER COMMITMENTS - Quản lý cam kết giáo viên
# ═══════════════════════════════════════════════════════════════════════════════

# Danh sách lớp mặc định (fallback khi không có data)
FALLBACK_CLASSES = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B", "5A"]

# Danh sách môn học chuẩn
CANONICAL_SUBJECTS = [
    "Toán", "Tiếng Việt", "Tiếng Anh", "Khoa học",
    "Lịch sử và Địa lí", "Tin học", "Tin học và Công nghệ",
    "Đạo đức", "Nghệ thuật - Âm nhạc", "Nghệ thuật - Mĩ thuật",
    "Hoạt động trải nghiệm", "Giáo dục thể chất"
]

# Keywords nhận diện môn có điểm số (scoring subjects)
SCORING_KEYWORDS = [
    "toan", "tieng viet", "tieng anh", "tieng ru", "tin hoc",
    "li su", "dia li", "khoa hoc", "vat ly", "hoa hoc", "sinh hoc",
    "cong nghe", "giai tri", "ngoai ngu"
]

# Keywords nhận diện môn nhận xét (comment-based)
COMMENT_KEYWORDS = [
    "dao duc", "nghe thuat", "am nhac", "mi thuat", "my thuat",
    "trai nghiem", "the chat", " GDTC", "sinh hoat", "shct"
]


def _normalize_subject(name: str) -> str:
    """
    Mô tả:
        Chuẩn hoá tên môn học - lowercase, loại bỏ dấu tiếng Việt.

    Input:
        name (str): Tên môn học thô

    Output:
        (str): Tên đã chuẩn hoá, ASCII-safe
    """
    import unicodedata
    if not name:
        return ""

    name = name.lower().strip()
    name = name.replace("đ", "d")
    nfkd = unicodedata.normalize("NFKD", name)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _map_to_canonical(name: str) -> str | None:
    """
    Mô tả:
        Map tên môn học raw về dạng chuẩn.

    Input:
        name (str): Tên môn từ database

    Output:
        (str|None): Tên chuẩn hoặc None nếu không nhận diện được
    """
    norm = _normalize_subject(name)

    # Priority order: longer/more specific matches FIRST
    if "lich su" in norm and "dia li" in norm:
        return "Lịch sử và Địa lí"
    if "tin hoc" in norm and "cong nghe" in norm:
        return "Tin học và Công nghệ"
    if "toan" in norm:
        return "Toán"
    if "tieng viet" in norm or "tv" in norm:
        return "Tiếng Việt"
    if "tieng anh" in norm:
        return "Tiếng Anh"
    if "khoa hoc" in norm or "tnxh" in norm:
        return "Khoa học"
    if "lich su" in norm:
        return "Lịch sử và Địa lí"
    if "dia li" in norm:
        return "Lịch sử và Địa lí"
    if "tin hoc" in norm:
        return "Tin học"
    if "cong nghe" in norm:
        return "Tin học và Công nghệ"
    if "dao duc" in norm or "đđ" in norm:
        return "Đạo đức"
    if "am nhac" in norm:
        return "Nghệ thuật - Âm nhạc"
    if "mi thuat" in norm or "my thuat" in norm:
        return "Nghệ thuật - Mĩ thuật"
    if "trai nghiem" in norm or "hđtn" in norm:
        return "Hoạt động trải nghiệm"
    if "the chat" in norm or "gdtc" in norm:
        return "Giáo dục thể chất"

    return None  # unknown → drop


def _is_scoring_subject(name: str) -> bool:
    """
    Mô tả:
        Kiểm tra môn học có điểm số hay không.

    Input:
        name (str): Tên môn học

    Output:
        (bool): True nếu là môn có điểm (Toán, TV, TA, KH...)
    """
    norm = _normalize_subject(name)
    return any(kw in norm for kw in SCORING_KEYWORDS)


def _is_comment_subject(name: str) -> bool:
    """
    Mô tả:
        Kiểm tra môn học có đánh giá bằng nhận xét không.

    Input:
        name (str): Tên môn học

    Output:
        (bool): True nếu là môn nhận xét (Đạo đức, Nghệ thuật...)
    """
    norm = _normalize_subject(name)
    return any(kw in norm for kw in COMMENT_KEYWORDS)


def _get_subject_type(name: str) -> str:
    """
    Mô tả:
        Xác định loại môn học: scoring hay comment.

    Input:
        name (str): Tên môn học

    Output:
        (str): "scoring" hoặc "comment"
    """
    if _is_scoring_subject(name):
        return "scoring"
    if _is_comment_subject(name):
        return "comment"
    return "comment"  # Default to comment


def render_commitments():
    """
    Mô tả:
        Render tab cam kết giáo viên - 3 sub-tabs:
        1. Nhập liệu: Form bulk input cho từng lớp
        2. Tải Excel: Import từ file
        3. Danh sách: Xem các cam kết đã lưu

    Features:
        - Auto-load danh sách lớp và môn từ database
        - Sĩ số được đọc read-only từ subject_snapshots
        - Tự động phân biệt môn điểm số / môn nhận xét
        - Validate T+H+C = sĩ số
    """
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📝 Nhập", "📤 Tải Excel", "📊 Danh sách"])

    with sub_tab1:
        st.subheader("Cam kết giáo viên")

        # Chọn năm học, lớp, sĩ số
        col1, col2, col3 = st.columns(3)

        with col1:
            year = st.selectbox("Năm học", ["2024-2025", "2025-2026", "2026-2027"], key="comm_year")

        with col2:
            # Load class list từ database
            class_options = FALLBACK_CLASSES
            try:
                with get_conn() as conn:
                    rows = conn.execute(
                        "SELECT DISTINCT class_name FROM subject_snapshots WHERE academic_year = ? ORDER BY class_name",
                        (year,)
                    ).fetchall()
                    if rows:
                        class_options = [r[0] for r in rows]
            except Exception:
                pass
            cls = st.selectbox("Lớp", class_options, key="comm_class")

        with col3:
            # Sĩ số được đọc read-only từ subject_snapshots
            class_size = 0
            try:
                with get_conn() as conn:
                    row = conn.execute(
                        "SELECT student_count FROM subject_snapshots WHERE academic_year = ? AND class_name = ? AND student_count IS NOT NULL LIMIT 1",
                        (year, cls)
                    ).fetchone()
                    if row and row[0]:
                        class_size = row[0]
            except Exception:
                pass

            if class_size == 0:
                st.text_input("Sĩ số lớp", value="?", disabled=True, key="comm_size")
                st.warning("Chưa có dữ liệu sĩ số. Import VNEDU trước.")
            else:
                st.text_input("Sĩ số lớp", value=str(class_size), disabled=True, key="comm_size")

        if not year or not cls:
            st.info("Vui lòng chọn Năm học và Lớp để tiếp tục")
            return

        # Load danh sách môn từ database
        raw_subjects = []
        try:
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT DISTINCT subject FROM subject_snapshots WHERE subject IS NOT NULL"
                ).fetchall()
                if rows:
                    raw_subjects = [r[0] for r in rows if r[0]]
        except Exception:
            pass

        # Normalize và map về canonical names
        normalized = []
        for s in raw_subjects:
            canon = _map_to_canonical(s)
            if canon:
                normalized.append(canon)

        # Dedupe và sort
        subject_list = sorted(set(normalized))

        # Merge với canonical list nếu có data
        if subject_list:
            all_subjects = sorted(set(subject_list) | set(CANONICAL_SUBJECTS))
            subject_list = all_subjects
        else:
            subject_list = CANONICAL_SUBJECTS
            st.warning("Chưa có dữ liệu VNEDU. Đang dùng danh sách môn mặc định.")

        st.divider()
        st.markdown(f"**Chỉ tiêu lớp {cls} — Năm học {year}**")

        # Header row
        h_cols = st.columns([3, 1, 1, 1, 1, 1])
        h_cols[0].markdown("**Môn học**")
        h_cols[1].markdown("**Loại**")
        h_cols[2].markdown("**Điểm TB**")
        h_cols[3].markdown("**T**")
        h_cols[4].markdown("**H**")
        h_cols[5].markdown("**C**")

        # Input form cho từng môn
        comm_inputs = {}
        for subj in subject_list:
            subj_type = _get_subject_type(subj)
            row = st.columns([3, 1, 1, 1, 1, 1])
            row[0].text(subj)

            # Badge hiển thị loại môn
            type_label = "📊 Điểm" if subj_type == "scoring" else "📝 Nhận xét"
            row[1].caption(type_label)

            comm_inputs[subj] = {"type": subj_type, "avg": None, "t": None, "h": None, "c": None}

            if subj_type == "scoring":
                # Môn có điểm: nhập điểm TB, T/H/C disabled
                avg_str = row[2].text_input("", key=f"avg_{subj}", label_visibility="collapsed", placeholder="-")
                try:
                    comm_inputs[subj]["avg"] = float(avg_str) if avg_str.strip() else None
                except ValueError:
                    comm_inputs[subj]["avg"] = None
                row[3].text("-")
                row[4].text("-")
                row[5].text("-")
            else:
                # Môn nhận xét: nhập T/H/C, điểm disabled
                row[2].text("-")
                for col_idx, key_suffix in [(3, "t"), (4, "h"), (5, "c")]:
                    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")
                    try:
                        comm_inputs[subj][key_suffix] = int(float(val_str)) if val_str.strip() else 0
                    except (ValueError, TypeError):
                        comm_inputs[subj][key_suffix] = 0

        st.markdown("---")

        # Lưu tất cả cam kết
        if st.button("💾 Lưu toàn bộ cam kết", type="primary"):
            saved = 0
            errors = []

            for subj, data in comm_inputs.items():
                subj_type = data["type"]
                avg = data["avg"]
                t = data["t"]
                h = data["h"]
                c = data["c"]

                if subj_type == "scoring":
                    # Validate điểm: 0-10
                    if avg is not None and (avg < 0 or avg > 10):
                        errors.append(f"{subj}: Điểm TB phải từ 0-10")
                        continue
                    try:
                        with get_conn() as conn:
                            upsert_teacher_commitment(conn, year, cls, subj, avg, None, None, None, 0, 0, 0, 0)
                            saved += 1
                    except Exception as e:
                        errors.append(f"{subj}: {e}")

                else:  # comment subject
                    # Validate T+H+C = sĩ số
                    total = (t or 0) + (h or 0) + (c or 0)
                    if total > 0 and total != class_size:
                        errors.append(f"{subj}: T+H+C ({total}) phải = sĩ số ({class_size})")
                        continue
                    if t is None and h is None and c is None:
                        continue  # Skip empty
                    try:
                        with get_conn() as conn:
                            upsert_teacher_commitment(conn, year, cls, subj, None, t, h, c, 0, 0, 0, 0)
                            saved += 1
                    except Exception as e:
                        errors.append(f"{subj}: {e}")

            for err in errors:
                st.error(err)

            if saved > 0:
                st.success(f"Đã lưu {saved} cam kết cho lớp {cls}")
                st.rerun()

    with sub_tab2:
        # Import từ Excel
        st.caption("File mẫu: cam_ket_giao_vien.xlsx")
        comm_file = st.file_uploader("Chọn file Excel", type=["xlsx", "xls"], key="comm_upload")
        if comm_file:
            df = pd.read_excel(comm_file)
            st.dataframe(df.head())
            if st.button("Xử lý", key="proc_comm"):
                with get_conn() as conn:
                    conn.execute("BEGIN TRANSACTION")
                    for _, row in df.iterrows():
                        raw_year = str(row.get("Năm học", ""))
                        normalized_year = normalize_year(raw_year) or raw_year
                        upsert_teacher_commitment(conn, normalized_year, str(row.get("Lớp", "")),
                                                   str(row.get("Môn", "")), row.get("Điểm TB"), row.get("T%"),
                                                   row.get("H%"), row.get("C%"), int(row.get("HTXS", 0) or 0),
                                                   int(row.get("HTT", 0) or 0), int(row.get("HT", 0) or 0),
                                                   int(row.get("CHT", 0) or 0))
                    conn.execute("COMMIT")
                st.success("Đã lưu dữ liệu")
                st.rerun()

    with sub_tab3:
        # Xem danh sách cam kết đã lưu
        with get_conn() as conn:
            years = [r[0] for r in conn.execute("SELECT DISTINCT academic_year FROM teacher_commitments ORDER BY academic_year DESC").fetchall()]
        if years:
            sel_year = st.selectbox("Năm học", years, key="comm_view_year")
            df_comm = pd.read_sql("SELECT class_name as 'Lớp', subject as 'Môn', avg_score_target as 'Điểm TB', "
                                   "T_pct_target as 'T%', H_pct_target as 'H%', C_pct_target as 'C%' "
                                   "FROM teacher_commitments WHERE academic_year=? ORDER BY class_name",
                                   get_conn(), params=(sel_year,))
            if not df_comm.empty:
                st.dataframe(df_comm, use_container_width=True, hide_index=True)
                st.caption(f"{len(df_comm)} cam kết")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: STUDENT ACHIEVEMENTS - Quản lý thành tích học sinh
# ═══════════════════════════════════════════════════════════════════════════════

def render_achievements():
    """
    Mô tả:
        Render tab thành tích học sinh - 3 sub-tabs:
        1. Nhập liệu: Form nhập thủ công
        2. Tải Excel: Import từ file
        3. Danh sách: Xem pivot table thành tích

    Features:
        - Pivot table: rows=categories, columns=levels
        - Metrics tổng hợp theo cấp
        - Bar chart trực quan
    """
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📝 Nhập", "📤 Tải Excel", "📊 Danh sách"])

    with sub_tab1:
        # Form nhập thủ công
        with st.form("achievement_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                year = st.selectbox("Năm học", ["2024-2025", "2025-2026", "2026-2027"], key="ach_year")
                category = st.selectbox("Hạng mục", ACHIEVEMENT_CATEGORIES)
            with c2:
                level = st.selectbox("Cấp độ", ACHIEVEMENT_LEVELS)
                quantity = st.number_input("Số lượng", 0, 10000, step=1)

            if st.form_submit_button("Lưu", type="primary") and year and category and level:
                try:
                    with get_conn() as conn:
                        upsert_student_achievement(conn, year, category, level, quantity)
                    st.success(f"Đã lưu: {category} - {level} = {quantity} HS")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    with sub_tab2:
        # Import từ Excel
        st.caption("File mẫu: thanh_tich_hoc_sinh.xlsx")
        ach_file = st.file_uploader("Chọn file Excel", type=["xlsx", "xls"], key="ach_upload")
        if ach_file:
            df = pd.read_excel(ach_file)
            st.dataframe(df.head())
            if st.button("Xử lý", key="proc_ach"):
                with get_conn() as conn:
                    conn.execute("BEGIN TRANSACTION")
                    for _, row in df.iterrows():
                        raw_year = str(row.get("Năm học", ""))
                        normalized_year = normalize_year(raw_year) or raw_year
                        upsert_student_achievement(conn, normalized_year, str(row.get("Hạng mục", "")),
                                                    str(row.get("Cấp độ", "")), int(row.get("Số lượng", 0) or 0))
                    conn.execute("COMMIT")
                st.success("Đã lưu dữ liệu")
                st.rerun()

    with sub_tab3:
        # Pivot table và chart
        with get_conn() as conn:
            years = [r[0] for r in conn.execute("SELECT DISTINCT academic_year FROM student_achievements ORDER BY academic_year DESC").fetchall()]
        if years:
            sel_year = st.selectbox("Năm học", years, key="ach_view_year")
            df_sum = get_achievements_summary(sel_year)
            if not df_sum.empty:
                st.dataframe(df_sum, use_container_width=True, hide_index=True)

                # Metrics theo cấp
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Xã", df_sum["Xã"].sum())
                c2.metric("Q.Huyện", df_sum["Quận/Huyện"].sum())
                c3.metric("Tỉnh", df_sum["Tỉnh/Thành phố"].sum())
                c4.metric("QGia", df_sum["Quốc gia"].sum())
                c5.metric("QTế", df_sum["Quốc tế"].sum())

                # Bar chart
                fig = px.bar(df_sum.melt(id_vars="category", var_name="Cấp độ", value_name="SL"),
                             x="category", y="SL", color="Cấp độ", barmode="group")
                st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN - Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Mô tả:
        Entry point chính của ứng dụng Streamlit.

    Execution order:
        1. init_db() - tạo tables
        2. migrate_db() - apply migrations
        3. init_*() - tạo các tables còn lại
        4. render UI components

    Lưu ý:
        - init_db() phải gọi TRƯỚC migrate_db()
        - migrate_db() dùng table_exists() nên an toàn với fresh DB
    """
    st.set_page_config(page_title="SQMS", layout="wide")

    # Khởi tạo database trước migration
    init_db()
    migrate_db()
    init_teacher_commitments()
    init_student_achievements()
    init_class_summary()

    st.title("Hệ thống Quản lý Chất lượng Giáo dục")

    # Sidebar
    files, snapshot_type, process_clicked, score_delta = render_sidebar()

    # Xử lý file khi click
    if process_clicked:
        process_files(files, snapshot_type, score_delta)

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 Tổng hợp", "📝 Cam kết GV", "🏆 Thành tích"])

    with tab1:
        render_dashboard()

    with tab2:
        render_commitments()

    with tab3:
        render_achievements()


if __name__ == "__main__":
    main()
