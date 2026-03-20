"""
Repository interfaces (abstract base classes).

Nguyên tắc:
- Chỉ định nghĩa contract, không chứa implementation.
- Không phụ thuộc vào SQLite hay bất kỳ external library.
- Depends on: app.domain.models
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models import SubjectSnapshot, ClassSummary, SnapshotType


class SubjectSnapshotRepository(ABC):
    """Abstract repository cho SubjectSnapshot."""

    @abstractmethod
    def upsert(self, snapshot: SubjectSnapshot) -> None:
        """
        Insert hoặc update một subject snapshot.

        Args:
            snapshot: SubjectSnapshot instance
        """
        pass

    @abstractmethod
    def find_by_class_and_year(
        self,
        class_name: str,
        academic_year: str,
        snapshot_type: Optional[SnapshotType] = None
    ) -> List[SubjectSnapshot]:
        """
        Tìm tất cả subject snapshots theo class và year.

        Args:
            class_name: Tên lớp
            academic_year: Năm học
            snapshot_type: Lọc theo type (optional)

        Returns:
            List of SubjectSnapshot
        """
        pass

    @abstractmethod
    def find_all(self) -> List[SubjectSnapshot]:
        """Lấy tất cả records."""
        pass


class ClassSummaryRepository(ABC):
    """Abstract repository cho ClassSummary (KQGD)."""

    @abstractmethod
    def upsert(self, summary: ClassSummary) -> None:
        """
        Insert hoặc update một class summary.

        Args:
            summary: ClassSummary instance
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def find_all(self) -> List[ClassSummary]:
        """Lấy tất cả records."""
        pass
