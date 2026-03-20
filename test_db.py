"""
Test database operations với repository mới.

Test:
- init_db
- SubjectSnapshotRepository upsert/find
- ClassSummaryRepository upsert/find
"""

from pathlib import Path
from app.db.connection import init_db
from app.repositories import SqliteSubjectSnapshotRepository, SqliteClassSummaryRepository
from app.domain.models import SubjectSnapshot, ClassSummary, SnapshotType


def test_db():
    # Setup test DB (sử dụng DB thật)
    init_db()
    print("Database initialized.")

    subject_repo = SqliteSubjectSnapshotRepository()
    class_summary_repo = SqliteClassSummaryRepository()

    # 1. Create SubjectSnapshot
    s1 = SubjectSnapshot(
        academic_year="2024-2025",
        class_name="10A1",
        subject="Toan",
        snapshot_type=SnapshotType.BASELINE,
        avg_score=7.5,
        student_count=30,
        T=10, H=15, C=5
    )
    subject_repo.upsert(s1)
    print("Upserted SubjectSnapshot")

    # 2. Create ClassSummary
    cs1 = ClassSummary(
        academic_year="2024-2025",
        class_name="10A1",
        snapshot_type=SnapshotType.BASELINE,
        HTXS=10, HTT=15, HT=5, CHT=0
    )
    class_summary_repo.upsert(cs1)
    print("Upserted ClassSummary")

    # 3. Verify Retrieval
    subjects = subject_repo.find_by_class_and_year("10A1", "2024-2025")
    print(f"Subjects: {subjects}")
    assert len(subjects) == 1
    assert subjects[0].subject == "Toan"

    summaries = class_summary_repo.find_by_class_and_year("10A1", "2024-2025")
    print(f"Summaries: {summaries}")
    # summaries trả về Optional, cần kiểm tra None
    assert summaries is not None
    assert summaries.HTXS == 10

    print("All tests passed!")


if __name__ == "__main__":
    test_db()
