"""
Adapter converters: chuyển đổi giữa dict (từ parser) và domain objects.

Nguyên tắc:
- Parser trả dict (không đổi).
- Adapter convert dict → domain object.
- Usecase chỉ làm việc với domain objects.
"""

from typing import List, Dict, Any, Optional

from app.domain.models import (
    SubjectSnapshot,
    ClassSummary,
    SnapshotType,
    ProcessResult
)


def normalize_subject_name(subject: str) -> Optional[str]:
    """
    Normalize subject name by stripping parent prefix and removing invalid entries.

    Rules:
    - "Nghệ thuật - Âm nhạc" → "Âm nhạc"
    - "Nghệ thuật - Mĩ thuật" → "Mĩ thuật"
    - "Nghệ thuật" → None (skip - not a real subject)
    - "Toán" → "Toán" (unchanged)

    Args:
        subject: Raw subject name from parser

    Returns:
        Normalized subject name, or None if subject should be skipped
    """
    if not subject:
        return None

    s = subject.strip()

    # Has sub-category: strip parent prefix
    if " - " in s:
        parts = s.split(" - ", 1)
        sub = parts[1].strip()
        return sub if sub else None

    # Standalone "Nghệ thuật": not a real subject
    if s.lower() == "nghệ thuật":
        return None

    return s


class ParserResultAdapter:
    """
    Adapter để convert parser output (dicts) sang domain objects.

    Parser hiện tại trả:
        List[Dict] cho subjects (parse_sheet)
        List[Dict] cho class_summary (_parse_kqgd_summary)

    Adapter chuyển thành:
        List[SubjectSnapshot]
        List[ClassSummary]
    """

    @staticmethod
    def to_subject_snapshots(dicts: List[Dict[str, Any]]) -> List[SubjectSnapshot]:
        """
        Convert parser subject dicts → SubjectSnapshot domain objects.

        Parser dict keys (từ parse_sheet):
            academic_year, class_name, subject, subject_type,
            avg_score (float|None), student_count,
            T, H, C, T_pct, H_pct, C_pct

        Note: subject_type là "scored" hoặc "qualitative", không phải snapshot_type.
        Snapshot_type sẽ được truyền từ usecase (vì parser không biết).

        Args:
            dicts: List of dicts từ parser

        Returns:
            List of SubjectSnapshot objects
        """
        snapshots = []
        for d in dicts:
            # Parser không có snapshot_type → cần được set từ usecase context
            snapshot_type = d.get("snapshot_type")
            if snapshot_type is None:
                raise ValueError(
                    f"Missing snapshot_type for subject '{d.get('subject')}' "
                    f"in class '{d.get('class_name')}'"
                )

            # Convert string enum to SnapshotType
            if isinstance(snapshot_type, str):
                snapshot_type = SnapshotType(snapshot_type)

            # Note: avg_score có thể None cho qualitative subjects
            # Validation sẽ happen trong SubjectSnapshot.__post_init__()
            snap = SubjectSnapshot(
                academic_year=d["academic_year"],
                class_name=d["class_name"],
                subject=d["subject"],
                snapshot_type=snapshot_type,
                avg_score=d.get("avg_score"),
                student_count=d.get("student_count", 0),
                T=d.get("T", 0),
                H=d.get("H", 0),
                C=d.get("C", 0)
            )
            snapshots.append(snap)
        return snapshots

    @staticmethod
    def to_class_summaries(dicts: List[Dict[str, Any]]) -> List[ClassSummary]:
        """
        Convert parser KQGD dicts → ClassSummary domain objects.

        Parser dict keys (từ _parse_kqgd_summary):
            academic_year, class_name,
            HTXS, HTT, HT, CHT, total_students

        Note: Parser không có snapshot_type → cần được set từ usecase.

        Args:
            dicts: List of dicts từ parser (often 1 per class)

        Returns:
            List of ClassSummary objects
        """
        summaries = []
        for d in dicts:
            snapshot_type = d.get("snapshot_type")
            if snapshot_type is None:
                raise ValueError(
                    f"Missing snapshot_type for class summary "
                    f"(class {d.get('class_name')}, year {d.get('academic_year')})"
                )

            if isinstance(snapshot_type, str):
                snapshot_type = SnapshotType(snapshot_type)

            summary = ClassSummary(
                academic_year=d["academic_year"],
                class_name=d["class_name"],
                snapshot_type=snapshot_type,
                HTXS=d.get("HTXS", 0),
                HTT=d.get("HTT", 0),
                HT=d.get("HT", 0),
                CHT=d.get("CHT", 0),
                # Các trường khác Parser không trả về (default 0)
                HTCTLH_HT=d.get("HTCTLH_HT", 0),
                HTCTLH_CHT=d.get("HTCTLH_CHT", 0),
                HSXS=d.get("HSXS", 0),
                HS_TieuBieu=d.get("HS_TieuBieu", 0)
            )
            summaries.append(summary)
        return summaries

    @staticmethod
    def convert_parser_output(
        subject_dicts: List[Dict[str, Any]],
        class_summary_dicts: List[Dict[str, Any]],
        snapshot_type: SnapshotType
    ) -> tuple[List[SubjectSnapshot], List[ClassSummary]]:
        """
        Helper: convert cả parser output cùng lúc.

        Args:
            subject_dicts: Parser subject results
            class_summary_dicts: Parser class summary results
            snapshot_type: SnapshotType để apply cho tất cả records

        Returns:
            (subject_snapshots, class_summaries)
        """
        # Inject snapshot_type vào từng dict trước khi convert
        for d in subject_dicts:
            d["snapshot_type"] = snapshot_type
        for d in class_summary_dicts:
            d["snapshot_type"] = snapshot_type

        # Normalize subject names and filter invalid entries
        normalized_subjects = []
        for d in subject_dicts:
            raw_name = d.get("subject", "")
            normalized = normalize_subject_name(raw_name)
            if normalized is None:
                continue  # skip invalid subjects (e.g. standalone "Nghệ thuật")
            d["subject"] = normalized
            normalized_subjects.append(d)

        subjects = ParserResultAdapter.to_subject_snapshots(normalized_subjects)
        summaries = ParserResultAdapter.to_class_summaries(class_summary_dicts)

        return subjects, summaries



