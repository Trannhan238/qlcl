import sqlite3
from typing import List, Optional

from app.models.domain import ClassInfo, Metric, MetricSnapshot
from app.infra.database import get_db_session
from app.core.ports import AbstractClassRepository, AbstractMetricRepository, AbstractSnapshotRepository

class ClassRepository(AbstractClassRepository):
    def add(self, class_info: ClassInfo) -> None:
        with get_db_session() as conn:
            conn.execute(
                """
                INSERT INTO classes (id, grade, name)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    grade=excluded.grade,
                    name=excluded.name
                """,
                (class_info.id, class_info.grade, class_info.name)
            )

    def get(self, class_id: str) -> Optional[ClassInfo]:
        with get_db_session() as conn:
            row = conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
            if row:
                return ClassInfo(**dict(row))
        return None

    def get_all(self) -> List[ClassInfo]:
        with get_db_session() as conn:
            rows = conn.execute("SELECT * FROM classes").fetchall()
            return [ClassInfo(**dict(row)) for row in rows]

class MetricRepository(AbstractMetricRepository):
    def add(self, metric: Metric) -> None:
        with get_db_session() as conn:
            conn.execute(
                """
                INSERT INTO metrics (id, name, description)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description
                """,
                (metric.id, metric.name, metric.description)
            )

    def get(self, metric_id: str) -> Optional[Metric]:
        with get_db_session() as conn:
            row = conn.execute("SELECT * FROM metrics WHERE id = ?", (metric_id,)).fetchone()
            if row:
                return Metric(**dict(row))
        return None

    def get_all(self) -> List[Metric]:
        with get_db_session() as conn:
            rows = conn.execute("SELECT * FROM metrics").fetchall()
            return [Metric(**dict(row)) for row in rows]

class SnapshotRepository(AbstractSnapshotRepository):
    def add(self, snapshot: MetricSnapshot) -> None:
        with get_db_session() as conn:
            conn.execute(
                """
                INSERT INTO snapshots (id, class_id, metric_id, snapshot_type, value, academic_year)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(class_id, metric_id, snapshot_type, academic_year) DO UPDATE SET
                    value=excluded.value
                """,
                (snapshot.id, snapshot.class_id, snapshot.metric_id, snapshot.snapshot_type, snapshot.value, snapshot.academic_year)
            )

    def get_by_class_and_metric(self, class_id: str, metric_id: str, academic_year: Optional[str] = None) -> List[MetricSnapshot]:
        with get_db_session() as conn:
            query = "SELECT * FROM snapshots WHERE class_id = ? AND metric_id = ?"
            params = [class_id, metric_id]
            if academic_year:
                query += " AND academic_year = ?"
                params.append(academic_year)
            rows = conn.execute(query, tuple(params)).fetchall()
            return [MetricSnapshot(**dict(row)) for row in rows]

    def get_all_for_class(self, class_id: str, academic_year: Optional[str] = None) -> List[MetricSnapshot]:
        with get_db_session() as conn:
            query = "SELECT * FROM snapshots WHERE class_id = ?"
            params = [class_id]
            if academic_year:
                query += " AND academic_year = ?"
                params.append(academic_year)
            rows = conn.execute(query, tuple(params)).fetchall()
            return [MetricSnapshot(**dict(row)) for row in rows]
