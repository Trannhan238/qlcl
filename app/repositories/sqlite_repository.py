"""
SQLite implementation của repository interfaces.

Nguyên tắc:
- Chứa persistence logic (SQL queries, connections).
- Không chứa business logic.
- Depends on: app.domain.models, app.main (DB_PATH, get_conn)
"""

from typing import List, Optional

import sqlite3

from app.domain.models import SubjectSnapshot, ClassSummary, SnapshotType
from app.repositories.interfaces import SubjectSnapshotRepository, ClassSummaryRepository
from app.db.connection import get_conn


class SqliteSubjectSnapshotRepository(SubjectSnapshotRepository):
    """
    SQLite implementation cho SubjectSnapshotRepository.

    Note: Sử dụng connection từ main.get_conn().
    Repository KHÔNG tự tạo connection.
    """

    def upsert(self, snapshot: SubjectSnapshot) -> None:
        """
        Insert hoặc update subject snapshot.

        Dùng ON CONFLICT để upsert theo unique key:
        (academic_year, class_name, subject, snapshot_type)
        """
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO subject_snapshots (
                    academic_year, class_name, subject, snapshot_type,
                    avg_score, student_count, T, H, C
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(academic_year, class_name, subject, snapshot_type)
                DO UPDATE SET
                    avg_score=excluded.avg_score,
                    student_count=excluded.student_count,
                    T=excluded.T,
                    H=excluded.H,
                    C=excluded.C
            """, (
                snapshot.academic_year,
                snapshot.class_name,
                snapshot.subject,
                snapshot.snapshot_type.value,
                snapshot.avg_score,
                snapshot.student_count,
                snapshot.T,
                snapshot.H,
                snapshot.C
            ))

    def find_by_class_and_year(
        self,
        class_name: str,
        academic_year: str,
        snapshot_type: Optional[SnapshotType] = None
    ) -> List[SubjectSnapshot]:
        """
        Tìm subject snapshots theo class và year.

        Args:
            class_name: Tên lớp
            academic_year: Năm học
            snapshot_type: Lọc theo type (optional)

        Returns:
            List of SubjectSnapshot objects.
        """
        with get_conn() as conn:
            if snapshot_type:
                rows = conn.execute("""
                    SELECT * FROM subject_snapshots
                    WHERE class_name = ? AND academic_year = ? AND snapshot_type = ?
                    ORDER BY subject
                """, (class_name, academic_year, snapshot_type.value)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM subject_snapshots
                    WHERE class_name = ? AND academic_year = ?
                    ORDER BY subject
                """, (class_name, academic_year)).fetchall()

        return [self._row_to_subject(row) for row in rows]

    def find_all(self) -> List[SubjectSnapshot]:
        """Lấy tất cả subject snapshots."""
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM subject_snapshots ORDER BY academic_year, class_name").fetchall()
        return [self._row_to_subject(row) for row in rows]

    def _row_to_subject(self, row: sqlite3.Row) -> SubjectSnapshot:
        """
        Convert sqlite3.Row sang SubjectSnapshot.

        Args:
            row: sqlite3.Row từ database

        Returns:
            SubjectSnapshot instance
        """
        return SubjectSnapshot(
            academic_year=row["academic_year"],
            class_name=row["class_name"],
            subject=row["subject"],
            snapshot_type=SnapshotType(row["snapshot_type"]),
            avg_score=row["avg_score"],
            student_count=row["student_count"],
            T=row["T"],
            H=row["H"],
            C=row["C"]
        )


class SqliteClassSummaryRepository(ClassSummaryRepository):
    """
    SQLite implementation cho ClassSummaryRepository.
    """

    def upsert(self, summary: ClassSummary) -> None:
        """
        Insert hoặc update class summary.

        Unique key: (academic_year, class_name, snapshot_type)
        """
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO class_summary (
                    academic_year, class_name, snapshot_type,
                    HTXS, HTT, HT, CHT,
                    HTCTLH_HT, HTCTLH_CHT, HSXS, HS_TieuBieu
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(academic_year, class_name, snapshot_type)
                DO UPDATE SET
                    HTXS=excluded.HTXS,
                    HTT=excluded.HTT,
                    HT=excluded.HT,
                    CHT=excluded.CHT,
                    HTCTLH_HT=excluded.HTCTLH_HT,
                    HTCTLH_CHT=excluded.HTCTLH_CHT,
                    HSXS=excluded.HSXS,
                    HS_TieuBieu=excluded.HS_TieuBieu
            """, (
                summary.academic_year,
                summary.class_name,
                summary.snapshot_type.value,
                summary.HTXS,
                summary.HTT,
                summary.HT,
                summary.CHT,
                summary.HTCTLH_HT,
                summary.HTCTLH_CHT,
                summary.HSXS,
                summary.HS_TieuBieu
            ))

    def find_by_class_and_year(
        self,
        class_name: str,
        academic_year: str,
        snapshot_type: Optional[SnapshotType] = None
    ) -> Optional[ClassSummary]:
        """
        Tìm class summary theo class và year.

        Returns:
            ClassSummary hoặc None nếu không tìm thấy.
        """
        with get_conn() as conn:
            if snapshot_type:
                row = conn.execute("""
                    SELECT * FROM class_summary
                    WHERE class_name = ? AND academic_year = ? AND snapshot_type = ?
                """, (class_name, academic_year, snapshot_type.value)).fetchone()
            else:
                row = conn.execute("""
                    SELECT * FROM class_summary
                    WHERE class_name = ? AND academic_year = ?
                """, (class_name, academic_year)).fetchone()

            return self._row_to_summary(row) if row else None

    def find_all(self) -> List[ClassSummary]:
        """Lấy tất cả class summaries."""
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM class_summary ORDER BY academic_year, class_name").fetchall()
        return [self._row_to_summary(row) for row in rows]

    def _row_to_summary(self, row: sqlite3.Row) -> ClassSummary:
        """
        Convert sqlite3.Row sang ClassSummary.

        Args:
            row: sqlite3.Row từ database

        Returns:
            ClassSummary instance
        """
        return ClassSummary(
            academic_year=row["academic_year"],
            class_name=row["class_name"],
            snapshot_type=SnapshotType(row["snapshot_type"]),
            HTXS=row["HTXS"],
            HTT=row["HTT"],
            HT=row["HT"],
            CHT=row["CHT"],
            HTCTLH_HT=row["HTCTLH_HT"],
            HTCTLH_CHT=row["HTCTLH_CHT"],
            HSXS=row["HSXS"],
            HS_TieuBieu=row["HS_TieuBieu"]
        )
