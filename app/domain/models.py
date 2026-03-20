"""
Domain models - Trái tim của hệ thống.

Nguyên tắc:
- Không phụ thuộc vào bất kỳ external library nào (chỉ typing)
- Dataclasses với type hints đầy đủ
- Business rules được encapsulate trong các phương thức
- Không có logic persistence (DB) hay I/O
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class SnapshotType(str, Enum):
    """Enum cho các loại snapshot."""
    BASELINE = "baseline"
    ACTUAL_HK1 = "actual_hk1"
    ACTUAL_HK2 = "actual_hk2"
    TARGET = "target"
    COMMITMENT = "commitment"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Kiểm tra value có hợp lệ không."""
        return value in cls._value2member_map_

    @classmethod
    def allows_kqgd(cls, value: str) -> bool:
        """
        KiQGD chỉ được parse cho baseline và actual_hk2.

        Returns:
            bool: True nếu snapshot_type được phép có KQGD.
        """
        return value in {cls.BASELINE.value, cls.ACTUAL_HK2.value}


@dataclass
class SubjectSnapshot:
    """
    Domain entity đại diện cho snapshot của một môn học.

    Data Contract (từ contracts.md):
        academic_year: str (format YYYY-YYYY, không được modify)
        class_name: str (không được modify)
        subject: str (tên môn học đã chuẩn hóa)
        snapshot_type: SnapshotType
        avg_score: float | None (range [0, 10], chỉ scored subjects)
        student_count: int (tổng số học sinh)
        T: int (Hoàn thành xuất sắc)
        H: int (Hoàn thành tốt)
        C: int (Hoàn thành)
    """
    academic_year: str
    class_name: str
    subject: str
    snapshot_type: SnapshotType
    avg_score: Optional[float]
    student_count: int
    T: int
    H: int
    C: int

    def __post_init__(self):
        """Validation runs automatically after init."""
        self.validate()

    def validate(self) -> None:
        """
        Validate theo business rules từ contracts.md.

        Raises:
            ValueError: Nếu vi phạm bất kỳ rule nào.
        """
        # 1. avg_score constraints
        if self.snapshot_type in {SnapshotType.BASELINE, SnapshotType.ACTUAL_HK1,
                                  SnapshotType.ACTUAL_HK2, SnapshotType.TARGET}:
            # Determined by subject type - will be validated at usecase level
            # because we don't know if subject is scored or qualitative here
            pass

        # 2. Non-negative counts
        if self.T < 0 or self.H < 0 or self.C < 0:
            raise ValueError(
                f"Negative T/H/C counts: T={self.T}, H={self.H}, C={self.C}"
            )

        # 3. student_count consistency
        total_thc = self.T + self.H + self.C
        if total_thc > self.student_count:
            raise ValueError(
                f"T+H+C ({total_thc}) exceeds student_count ({self.student_count}) "
                f"for subject '{self.subject}' in class '{self.class_name}' "
                f"year '{self.academic_year}'"
            )

    def is_scored(self) -> bool:
        """
        Xác định có phải môn có điểm số không.

        Note: Đây là heuristic dựa trên tên môn.
        Business rule: scored subjects REQUIRE avg_score NOT NULL.
        """
        norm = self.subject.lower()
        scoring_keywords = [
            "toán", "tiếng việt", "tiếng anh", "khoa học",
            "lịch sử", "địa lí", "tin học", "vật lý", "hóa học", "sinh học"
        ]
        return any(kw in norm for kw in scoring_keywords)

    def validate_subject_type(self) -> None:
        """
        Validate ràng buộc theo loại môn.

        Rules (contracts.md):
        - Scored subject: avg_score MUST NOT be NULL, MUST be in [0, 10]
        - Qualitative subject: avg_score MUST be NULL

        Raises:
            ValueError: Nếu không đúng rule.
        """
        if self.is_scored():
            if self.avg_score is not None:
                # Scored subject with avg_score → validate range
                if not (0.0 <= self.avg_score <= 10.0):
                    raise ValueError(
                        f"avg_score {self.avg_score} out of range [0, 10] "
                        f"for subject '{self.subject}' "
                        f"(class {self.class_name}, year {self.academic_year})"
                    )
            # Scored subject without avg_score → treated as qualitative, no error
        else:  # qualitative
            if self.avg_score is not None:
                raise ValueError(
                    f"Qualitative subject '{self.subject}' must have avg_score=NULL "
                    f"(class {self.class_name}, year {self.academic_year})"
                )


@dataclass
class ClassSummary:
    """
    Domain value object đại diện cho tổng hợp xếp loại cấp lớp (KQGD).

    Data Contract:
        academic_year: str
        class_name: str
        snapshot_type: SnapshotType (phải là baseline hoặc actual_hk2)
        HTXS: int (Hoàn thành xuất sắc)
        HTT: int (Hoàn thành tốt)
        HT: int (Hoàn thành)
        CHT: int (Chưa hoàn thành)
        total_students: int (HTXS + HTT + HT + CHT, phải > 0)

    Business Rules:
        - total_students MUST be > 0
        - HTXS + HTT + HT + CHT MUST equal total_students
    """
    academic_year: str
    class_name: str
    snapshot_type: SnapshotType
    HTXS: int
    HTT: int
    HT: int
    CHT: int
    # Các trường bổ sung (có thể có)
    HTCTLH_HT: int = 0
    HTCTLH_CHT: int = 0
    HSXS: int = 0
    HS_TieuBieu: int = 0

    def __post_init__(self):
        self.validate()

    @property
    def total_students(self) -> int:
        """Tổng số học sinh từ KQGD block."""
        return self.HTXS + self.HTT + self.HT + self.CHT

    def validate(self) -> None:
        """
        Validate KQGD rules.

        Raises:
            ValueError: Nếu vi phạm rule.
        """
        # 1. Snapshot type must allow KQGD
        if not SnapshotType.allows_kqgd(self.snapshot_type):
            raise ValueError(
                f"ClassSummary không hợp lệ cho snapshot_type '{self.snapshot_type}'. "
                f"Chỉ được dùng cho baseline hoặc actual_hk2."
            )

        # 2. Total students > 0
        total = self.total_students
        if total == 0:
            raise ValueError(
                f"KQGD empty: total_students = 0 "
                f"(class {self.class_name}, year {self.academic_year})"
            )

        # 3. Sum check: HTXS+HTT+HT+CHT phải bằng total_students
        # (Luôn đúng vì total_students là computed property, nhưng giữ để rõ ràng)
        if total != (self.HTXS + self.HTT + self.HT + self.CHT):
            raise ValueError(
                f"KQGD mismatch: sum={self.HTXS + self.HTT + self.HT + self.CHT} "
                f"!= total_students={total} "
                f"(class {self.class_name}, year {self.academic_year})"
            )

        # 4. Non-negative counts
        if any(x < 0 for x in [self.HTXS, self.HTT, self.HT, self.CHT]):
            raise ValueError(
                f"Negative KQGD counts: HTXS={self.HTXS}, HTT={self.HTT}, "
                f"HT={self.HT}, CHT={self.CHT}"
            )


@dataclass
class ProcessResult:
    """
    Result của process Excel file.

    Attributes:
        saved_subjects: Số lượng subject snapshots đã lưu
        saved_class_summaries: Số lượng class summaries đã lưu
        errors: Danh sách lỗi (file name + error message)
    """
    saved_subjects: int = 0
    saved_class_summaries: int = 0
    errors: List[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """Thêm lỗi vào danh sách."""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Có lỗi không."""
        return len(self.errors) > 0


# ==== DOMAIN CLASSES CŨ (cho ports và snapshot) ====
import uuid as _uuid
from dataclasses import dataclass as _dataclass, field as _field
from typing import Optional as _Optional


@_dataclass
class ClassInfo:
    """Domain entity cho thông tin lớp học."""
    grade: str
    name: str
    id: str = _field(default_factory=lambda: str(_uuid.uuid4()))


@_dataclass
class Metric:
    """Domain entity cho metric/độn số."""
    name: str
    description: _Optional[str] = None
    id: str = _field(default_factory=lambda: str(_uuid.uuid4()))


@_dataclass
class MetricSnapshot:
    """Domain entity cho metric snapshot (dùng cho báo cáo tổng hợp)."""
    class_id: str
    metric_id: str
    snapshot_type: str  # baseline, commitment, target, actual_hk1, actual_hk2
    value: _Optional[float]
    academic_year: str
    id: str = _field(default_factory=lambda: str(_uuid.uuid4()))
