"""
Domain normalizers: business rules for transforming raw parsed data.

Principle:
- Parser extracts RAW data from Excel (no transformation)
- Normalizers apply BUSINESS RULES to raw data
- This separation keeps parser stable across policy changes
"""

from typing import Optional


def normalize_subject_name(subject: str) -> Optional[str]:
    """
    Normalize subject name by stripping parent prefix and removing invalid entries.

    Business rules:
    - "Nghệ thuật" is a parent group, not a real subject
    - Actual subjects are "Âm nhạc" and "Mĩ thuật"
    - Parent prefix is stripped, child name is kept

    Rules:
    - "Nghệ thuật - Âm nhạc" → "Âm nhạc"
    - "Nghệ thuật - Mĩ thuật" → "Mĩ thuật"
    - "Nghệ thuật" → None (invalid, skip)
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
