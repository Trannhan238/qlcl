import sqlite3
from typing import Optional
from pathlib import Path

# Use a module-level variable to store the database path
DB_PATH = Path("sqms.db")

def set_db_path(path: str | Path):
    global DB_PATH
    DB_PATH = Path(path)

from contextlib import contextmanager

def get_connection() -> sqlite3.Connection:
    """Returns a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_db_session():
    """Provides a transactional scope around a series of operations and closes connection."""
    conn = get_connection()
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def init_db():
    """Initializes the database schema."""
    schema = """
    CREATE TABLE IF NOT EXISTS classes (
        id TEXT PRIMARY KEY,
        grade TEXT NOT NULL,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS metrics (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS snapshots (
        id TEXT PRIMARY KEY,
        class_id TEXT NOT NULL,
        metric_id TEXT NOT NULL,
        snapshot_type TEXT NOT NULL,
        value REAL NOT NULL,
        academic_year TEXT NOT NULL,
        FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
        FOREIGN KEY (metric_id) REFERENCES metrics(id) ON DELETE CASCADE,
        UNIQUE(class_id, metric_id, snapshot_type, academic_year)
    );
    
    -- Create indices for common queries
    CREATE INDEX IF NOT EXISTS idx_snapshots_class_metric ON snapshots(class_id, metric_id);
    """
    with get_db_session() as conn:
        conn.executescript(schema)
