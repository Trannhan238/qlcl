"""
Database connection layer.

Chứa:
- DB_PATH: đường dẫn file SQLite
- get_conn(): factory tạo connection
- Các helper functions liên quan DB
"""

import sqlite3
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database path
DB_PATH = BASE_DIR / "data" / "sqms.db"


def get_conn() -> sqlite3.Connection:
    """
    Tạo kết nối SQLite mới với row_factory=sqlite3.Row.

    Returns:
        sqlite3.Connection đã configure với row_factory
    
    Note:
        Tự động tạo thư mục data nếu chưa tồn tại.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    Kiểm tra table có tồn tại trong database không.

    Args:
        conn: SQLite connection
        table_name: Tên table cần kiểm tra

    Returns:
        True nếu table tồn tại
    """
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cur.fetchone() is not None


def migrate_db():
    """
    Migration database - thêm columns thiếu và chuẩn hoá academic_year.

    Logic:
        1. Thêm student_count, avg_score vào subject_snapshots nếu chưa có
        2. Chuẩn hoá format academic_year: "2024 - 2025" -> "2024-2025"
    """
    conn = get_conn()
    try:
        if table_exists(conn, "subject_snapshots"):
            columns = {row[1] for row in conn.execute("PRAGMA table_info(subject_snapshots)").fetchall()}
            if "student_count" not in columns:
                conn.execute("ALTER TABLE subject_snapshots ADD COLUMN student_count INTEGER")
            if "avg_score" not in columns:
                conn.execute("ALTER TABLE subject_snapshots ADD COLUMN avg_score REAL")
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
    """Khởi tạo tất cả tables."""
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


# Các alias functions để tương thích với main.py cũ
def init_teacher_commitments():
    """Khởi tạo bảng teacher_commitments (alias)."""
    init_db()  # đã包含


def init_student_achievements():
    """Khởi tạo bảng student_achievements (alias)."""
    init_db()


def init_class_summary():
    """Khởi tạo bảng class_summary (alias)."""
    init_db()
