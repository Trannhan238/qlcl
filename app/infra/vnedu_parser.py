"""
VNEDU Fixed-Structure Excel Parser
====================================
Parses VNEDU grade-summary Excel exports with the confirmed structure:
  Row 6 (idx 5)  → Subject headers (e.g. "Tiếng Việt", "Toán", ...)
  Row 8 (idx 7)  → Metric headers  (e.g. "Mức đạt được", "Điểm KT")
  Row 9+ (idx 8+)→ Student data rows

Does NOT rely on any heuristic detection. Structure is fixed.
"""

import unicodedata
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(s: Any) -> str:
    """Lowercase, strip accents and 'đ', return ASCII-safe string."""
    if not isinstance(s, str):
        return ""
    s = s.strip().lower().replace("đ", "d")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


EVAL_VALUES = {"t", "h", "c", "cht", "ht", "htt", "htxs"}


def _eval_bucket(val: Any) -> Optional[str]:
    """Return canonical bucket letter or None."""
    if pd.isna(val):
        return None
    s = _norm(str(val))
    if s in ("htt", "t"):   return "T"
    if s in ("ht",  "h"):   return "H"
    if s in ("cht", "c"):   return "C"
    return None


# ---------------------------------------------------------------------------
# File reader
# ---------------------------------------------------------------------------

def read_vnedu_file(file_path: str) -> Dict[str, pd.DataFrame]:
    """Read all sheets without headers, handling VNEDU corruption flag."""
    path = str(file_path)
    try:
        return pd.read_excel(path, sheet_name=None, header=None)
    except Exception:
        return pd.read_excel(
            path, sheet_name=None, header=None,
            engine="xlrd",
            engine_kwargs={"ignore_workbook_corruption": True},
        )


# ---------------------------------------------------------------------------
# Class name detection
# ---------------------------------------------------------------------------

def _detect_class_name(df: pd.DataFrame, sheet_name: str) -> str:
    """
    Look for class name specifically in row 4 (idx 4).
    """
    if len(df) > 4:
        row = df.iloc[4]
        for cell in row:
            if isinstance(cell, str) and ("Lớp" in cell or "lớp" in cell or "lop" in cell.lower()):
                parts = cell.strip().split(":")
                if len(parts) > 1:
                    return parts[-1].strip()
                tokens = cell.strip().split()
                if len(tokens) >= 2:
                    return tokens[-1]
    return sheet_name


def _detect_academic_year(df: pd.DataFrame) -> str:
    """
    Look for academic year specifically in row 3 (idx 3).
    """
    if len(df) > 3:
        row = df.iloc[3]
        for cell in row:
            if isinstance(cell, str) and ("Năm học" in cell or "Nam hoc" in cell):
                parts = cell.strip().split(":")
                if len(parts) > 1:
                    return parts[-1].strip()
    return "unknown"


def _build_column_plan(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detects subject columns based purely on structural markers:
      idx 6 (Row 7)  → Main Subject/Section
      idx 7 (Row 8)  → Sub-Subject/Category
      idx 8 (Row 9)  → Metric Label ("Mức đạt được", "Điểm KTĐK")
    """
    if len(df) < 10:
        return []

    h_main = df.iloc[6].ffill()
    h_sub  = df.iloc[7]
    h_metrics = df.iloc[8]

    plan = []
    for col in range(len(df.columns)):
        main_name = str(h_main.iloc[col]).strip() if pd.notna(h_main.iloc[col]) else ""
        sub_name  = str(h_sub.iloc[col]).strip() if pd.notna(h_sub.iloc[col]) else ""
        metric_raw = str(h_metrics.iloc[col]).strip() if pd.notna(h_metrics.iloc[col]) else ""

        metric_norm = _norm(metric_raw)

        # Rule 1: "Mức đạt được" or "Mức độ" marks a level/bucket column
        is_level = "muc dat duoc" in metric_norm or "muc do" in metric_norm
        # Rule 2: "Điểm" marks a numeric score column
        is_score = "diem" in metric_norm

        if not (is_level or is_score):
            continue

        # Construct subject name from structure
        # Use main name as base. If sub_name is present and distinct, append it.
        full_subject = main_name
        if sub_name and _norm(sub_name) not in _norm(main_name):
            # Also ignore purely metric labels in Row 8 if they leaked there
            if _norm(sub_name) not in ["muc dat duoc", "diem ktdk"]:
                full_subject = f"{main_name} - {sub_name}"

        if is_level:
            plan.append({"col": col, "type": "level", "subject": full_subject})
        elif is_score:
            plan.append({"col": col, "type": "score", "subject": full_subject})

    return plan

def parse_sheet(df: pd.DataFrame, class_name: str, academic_year: str) -> List[Dict[str, Any]]:
    """
    Parse a single sheet's DataFrame using the fixed VNEDU structure.
    Data starts at idx 9 (Row 10).
    """
    plan = _build_column_plan(df)
    if not plan:
        return []

    data_start = 9 # Row 10

    # Group plan entries by subject name
    subjects: Dict[str, Dict[str, Any]] = {}
    for entry in plan:
        subj = entry["subject"]
        if subj not in subjects:
            subjects[subj] = {"level_col": None, "score_col": None}
        if entry["type"] == "level":
            subjects[subj]["level_col"] = entry["col"]
        elif entry["type"] == "score":
            subjects[subj]["score_col"] = entry["col"]

    results = []
    data_rows = df.iloc[data_start:]
    
    # Filter out empty rows at the end (summary rows usually have nan in col 0)
    data_rows = data_rows[data_rows.iloc[:, 0].apply(lambda x: str(x).isdigit())]

    for subj, cols in subjects.items():
        level_col = cols["level_col"]
        score_col = cols["score_col"]

        T = H = C = 0
        if level_col is not None:
            for val in data_rows.iloc[:, level_col]:
                bucket = _eval_bucket(val)
                if bucket == "T": T += 1
                elif bucket == "H": H += 1
                elif bucket == "C": C += 1

        avg_score = None
        if score_col is not None:
            scores = pd.to_numeric(data_rows.iloc[:, score_col], errors="coerce").dropna()
            if not scores.empty:
                avg_score = round(float(scores.mean()), 2)

        results.append({
            "class":     class_name,
            "academic_year": academic_year,
            "subject":   subj,
            "avg_score": avg_score,
            "T": T,
            "H": H,
            "C": C,
        })

    return results


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse_vnedu_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse all sheets of a VNEDU Excel file.
    Returns a flat list of per-class, per-subject summary dicts.
    """
    sheets = read_vnedu_file(file_path)
    all_results = []

    for sheet_name, df in sheets.items():
        class_name = _detect_class_name(df, sheet_name)
        academic_year = _detect_academic_year(df)
        sheet_results = parse_sheet(df, class_name, academic_year)
        all_results.extend(sheet_results)

    return all_results
