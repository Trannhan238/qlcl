"""
Use case: Process Excel file và lưu vào database.

Chứa business logic cho việc:
- Parse Excel file
- Validate dữ liệu
- Deduplicate subjects
- Generate targets (nếu baseline)
- Persist vào database

Không phụ thuộc vào UI (Streamlit).
"""

from typing import List, Tuple, Optional
import uuid
from pathlib import Path

from app.domain.models import (
    SubjectSnapshot,
    ClassSummary,
    SnapshotType,
    ProcessResult
)
from app.domain.adapters import ParserResultAdapter
from app.repositories import (
    SubjectSnapshotRepository,
    ClassSummaryRepository
)
from app.infra.vnedu_parser import parse_vnedu_file_with_class_summary


class ProcessExcelUseCase:
    """
    Use case cho việc xử lý file Excel và lưu dữ liệu.

    Args:
        subject_repo: Repository để lưu subject snapshots
        class_summary_repo: Repository để lưu class summaries
    """

    def __init__(
        self,
        subject_repo: SubjectSnapshotRepository,
        class_summary_repo: ClassSummaryRepository
    ):
        self.subject_repo = subject_repo
        self.class_summary_repo = class_summary_repo

    def execute(
        self,
        file_path: str,
        snapshot_type: SnapshotType,
        score_delta: Optional[float] = None
    ) -> ProcessResult:
        """
        Execute use case.

        Args:
            file_path: Path to Excel file
            snapshot_type: Loại snapshot (baseline, actual_hk1, actual_hk2, target)
            score_delta: Delta điểm để generate targets (chỉ dùng cho baseline)

        Returns:
            ProcessResult với stats và errors
        """
        result = ProcessResult()

        try:
            # 1. Parse file
            allow_kqgd = SnapshotType.allows_kqgd(snapshot_type.value)
            parser_func = parse_vnedu_file_with_class_summary
            subject_dicts, class_summary_dicts = parser_func(
                file_path,
                allow_kqgd=allow_kqgd
            )

            # Safety: discard class summaries if snapshot_type doesn't allow KQGD
            if not allow_kqgd:
                class_summary_dicts = []

            # 2. Convert to domain objects
            subjects, summaries = ParserResultAdapter.convert_parser_output(
                subject_dicts,
                class_summary_dicts,
                snapshot_type
            )

            # 3. Validate subjects (business rules)
            for subj in subjects:
                try:
                    subj.validate()
                except ValueError as e:
                    result.add_error(f"Validation error for subject '{subj.subject}': {e}")
                    continue

            # 4. Deduplicate subjects (group by normalized subject name)
            deduped_subjects = self._deduplicate_subjects(subjects)

            # 5. Generate targets nếu baseline + có score_delta
            targets = []
            if snapshot_type == SnapshotType.BASELINE and score_delta is not None:
                targets = self._generate_targets(deduped_subjects, score_delta)
                # Targets cũng là subjects, thêm vào danh sách
                deduped_subjects.extend(targets)

            # 6. Persist to database
            saved_subjects = 0
            saved_summaries = 0

            for subj in deduped_subjects:
                try:
                    self.subject_repo.upsert(subj)
                    saved_subjects += 1
                except Exception as e:
                    result.add_error(f"Failed to save subject '{subj.subject}': {e}")

            for summary in summaries:
                try:
                    self.class_summary_repo.upsert(summary)
                    saved_summaries += 1
                except Exception as e:
                    result.add_error(
                        f"Failed to save class summary for {summary.class_name}: {e}"
                    )

            result.saved_subjects = saved_subjects
            result.saved_class_summaries = saved_summaries

        except Exception as e:
            result.add_error(f"Critical error: {e}")

        return result

    def _deduplicate_subjects(
        self,
        subjects: List[SubjectSnapshot]
    ) -> List[SubjectSnapshot]:
        """
        Deduplicate subjects bằng cách group theo (academic_year, class_name, snapshot_type, normalized_subject).

        Logic từ main.py:group (line 693-743):
        - Group by normalized subject name
        - Sum T, H, C
        - Weighted average cho avg_score

        Args:
            subjects: List of SubjectSnapshot objects (có thể duplicate)

        Returns:
            List[SubjectSnapshot] đã deduplicate
        """
        from app.infra.vnedu_parser import _normalize

        groups = {}
        for subj in subjects:
            key = (
                subj.academic_year,
                subj.class_name,
                subj.snapshot_type,
                _normalize(subj.subject)
            )
            if key not in groups:
                groups[key] = {
                    "academic_year": subj.academic_year,
                    "class_name": subj.class_name,
                    "subject": subj.subject,  # Giữ nguyên subject string (không normalized)
                    "snapshot_type": subj.snapshot_type,
                    "T": 0,
                    "H": 0,
                    "C": 0,
                    "avg_score_sum": 0.0,
                    "avg_count": 0,
                    "student_count": subj.student_count,
                }
            g = groups[key]
            g["T"] += subj.T
            g["H"] += subj.H
            g["C"] += subj.C
            if subj.avg_score is not None:
                g["avg_score_sum"] += subj.avg_score
                g["avg_count"] += 1
            if subj.student_count and (
                g["student_count"] is None or subj.student_count > g["student_count"]
            ):
                g["student_count"] = subj.student_count

        # Build deduped list
        deduped = []
        for gr in groups.values():
            avg_final = None
            if gr["avg_count"] > 0:
                avg_final = round(gr["avg_score_sum"] / gr["avg_count"], 2)

            deduped.append(SubjectSnapshot(
                academic_year=gr["academic_year"],
                class_name=gr["class_name"],
                subject=gr["subject"],
                snapshot_type=gr["snapshot_type"],
                avg_score=avg_final,
                student_count=gr["student_count"] or 0,
                T=gr["T"],
                H=gr["H"],
                C=gr["C"]
            ))

        return deduped

    def _generate_targets(
        self,
        subjects: List[SubjectSnapshot],
        score_delta: float
    ) -> List[SubjectSnapshot]:
        """
        Generate target snapshots từ baseline subjects.

        Logic từ main.py:generate_target_from_baseline (line 522-569):
        - avg_score = baseline_avg + score_delta (clamp 0-10)
        - Giữ nguyên T, H, C
        - Snapshot type = TARGET
        - academic_year và class_name: giữ nguyên baseline (không shift ở usecase)

        Args:
            subjects: Baseline subject snapshots
            score_delta: Delta để apply (VD: 0.5)

        Returns:
            List of target SubjectSnapshot objects
        """
        targets = []
        for base in subjects:
            if base.avg_score is None:
                continue  # qualitative subjects không có target avg_score

            target_avg = base.avg_score + score_delta
            if target_avg > 10.0:
                target_avg = 10.0
            if target_avg < 0.0:
                target_avg = 0.0

            target = SubjectSnapshot(
                academic_year=base.academic_year,
                class_name=base.class_name,
                subject=base.subject,
                snapshot_type=SnapshotType.TARGET,
                avg_score=target_avg,
                student_count=base.student_count,
                T=base.T,
                H=base.H,
                C=base.C
            )
            targets.append(target)

        return targets
