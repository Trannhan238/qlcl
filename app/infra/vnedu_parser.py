"""
Mô tả file:
- Vai trò: Parser chính cho file Excel VNEDU - trích xuất dữ liệu điểm và xếp loại học sinh
- Input: File Excel từ hệ thống VNEDU (.xlsx, .xls)
- Output: Danh sách dict chứa thông tin môn học và tổng hợp lớp
- Phụ thuộc: pandas, unicodedata (thư viện chuẩn)

Cấu trúc file VNEDU đã xác nhận:
  Row 6 (idx 5)  → Header môn học (VD: "Tiếng Việt", "Toán", ...)
  Row 8 (idx 7)  → Header metric (VD: "Mức đạt được", "Điểm KT")
  Row 9+ (idx 8+)→ Dòng dữ liệu học sinh

Quy ước data schema (Data Contract):
{
    "academic_year": str,      # Format: "YYYY-YYYY" (VD: "2024-2025")
    "class_name": str,        # Tên lớp (VD: "1A")
    "subject": str,           # Tên môn học đã chuẩn hoá
    "avg_score": float|None,  # Điểm trung bình (nếu có)
    "student_count": int,      # Tổng số học sinh
    "T": int,                  # Số học sinh xếp loại T (Tốt)
    "H": int,                  # Số học sinh xếp loại H (Hoàn thành)
    "C": int                   # Số học sinh xếp loại C (Chưa hoàn thành)
}

LƯU Ý QUAN TRỌNG:
- KHÔNG dùng key "class" - chỉ dùng "class_name"
- academic_year phải chuẩn hoá về format "YYYY-YYYY" trước khi lưu
"""

import unicodedata
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Helpers - Các hàm tiện ích
# ---------------------------------------------------------------------------

def _normalize(s: Any) -> str:
    """
    Mô tả:
        Chuẩn hoá text: lowercase, loại bỏ dấu tiếng Việt và 'đ', trả về ASCII string.

    Normalization steps:
        - lowercase
        - remove accents (đ → d)
        - trim whitespace

    Input:
        s (Any): Giá trị đầu vào

    Output:
        (str): String đã chuẩn hoá, empty string nếu không phải string
    """
    if not isinstance(s, str):
        return ""
    s = s.strip().lower().replace("đ", "d")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# Tập hợp các giá trị hợp lệ cho việc đánh giá bucket (T/H/C)
EVAL_VALUES = {"t", "h", "c", "cht", "ht", "htt", "htxs"}


def normalize_year(year: str) -> str | None:
    """
    Mô tả:
        Chuẩn hoá năm học về format thống nhất: YYYY-YYYY

    Input:
        year (str): Chuỗi năm học thô (VD: "2024 - 2025", "2024-2025", "2024–2025")

    Output:
        (str|None): Format chuẩn "YYYY-YYYY" hoặc None nếu không parse được

    Lưu ý:
        - Hỗ trợ các format: "2024 - 2025", "2024-2025", "2024–2025"
        - Luôn gọi hàm này khi nhận dữ liệu từ file Excel
    """
    import re

    if not year:
        return None

    year = str(year).strip()

    # Regex: bắt cặp năm cách nhau bởi dấu gạch ngang (có/không khoảng trắng)
    match = re.match(r'(\d{4})\s*[-–—]\s*(\d{4})', year)
    if not match:
        return None

    start, end = match.groups()
    return f"{start}-{end}"


def _eval_bucket(val: Any) -> Optional[str]:
    """
    Mô tả:
        Đánh giá giá trị cell và trả về bucket letter (T/H/C) tương ứng.

    Input:
        val (Any): Giá trị cell từ Excel

    Output:
        (str|None): "T" (Tốt), "H" (Hoàn thành), "C" (Chưa hoàn thành), hoặc None

    Lưu ý:
        - Chỉ chấp nhận: "htt", "t", "ht", "h", "cht", "c"
        - None/NaN trả về None (không đếm)
    """
    if pd.isna(val):
        return None
    s = _normalize(str(val))
    if s in ("htt", "t"):
        return "T"
    if s in ("ht",  "h"):
        return "H"
    if s in ("cht", "c"):
        return "C"
    return None


def _safe_str(value: Any) -> str:
    """
    Mô tả:
        Convert giá trị bất kỳ sang string an toàn, xử lý None và NaN.

    Input:
        value (Any): Giá trị đầu vào

    Output:
        (str): String đã strip, empty string nếu None/NaN
    """
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    try:
        return str(value).strip()
    except Exception:
        return ""


def is_checked(value: Any) -> bool:
    """
    Mô tả:
        Kiểm tra xem cell có phải là checkbox đã checked không.

    Input:
        value (Any): Giá trị cell từ Excel

    Output:
        (bool): True chỉ khi cell chứa marker checkbox hợp lệ

    Lưu ý:
        - Marker hợp lệ: ✓, ✔, v, x, 1
        - Mọi giá trị khác (text, số, None) trả về False
    """
    if value is None:
        return False
    if pd.isna(value):
        return False

    cleaned = _safe_str(value).lower()

    if cleaned in CHECKBOX_MARKERS:
        return True

    return False


# ---------------------------------------------------------------------------
# File reader - Đọc file Excel
# ---------------------------------------------------------------------------

def read_vnedu_file(file_path: str) -> Dict[str, pd.DataFrame]:
    """
    Mô tả:
        Đọc tất cả sheet từ file Excel VNEDU, không dùng header.

    Input:
        file_path (str): Đường dẫn đến file Excel

    Output:
        (Dict[str, pd.DataFrame]): Dict ánh xạ sheet_name -> DataFrame không header

    Lưu ý:
        - Fallback sang engine="xlrd" nếu file bị corruption
    """
    path = str(file_path)
    try:
        return pd.read_excel(path, sheet_name=None, header=None)
    except Exception:
        # File bị lỗi corruption - thử đọc với xlrd engine
        return pd.read_excel(
            path, sheet_name=None, header=None,
            engine="xlrd",
            engine_kwargs={"ignore_workbook_corruption": True},
        )


# ---------------------------------------------------------------------------
# Class name detection - Nhận diện tên lớp
# ---------------------------------------------------------------------------

def _detect_class_name(df: pd.DataFrame, sheet_name: str) -> str:
    """
    Mô tả:
        Trích xuất tên lớp từ row 4 (idx 4) của DataFrame.

    Input:
        df (pd.DataFrame): DataFrame đã đọc từ Excel
        sheet_name (str): Tên sheet (dùng làm fallback)

    Output:
        (str): Tên lớp (VD: "1A", "2B") hoặc sheet_name nếu không tìm thấy

    Lưu ý:
        - Tìm cell chứa "Lớp" hoặc "lớp"
        - Ưu tiên lấy phần sau dấu ":"
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
    Mô tả:
        Trích xuất năm học từ row 3 (idx 3) của DataFrame.

    Input:
        df (pd.DataFrame): DataFrame đã đọc từ Excel

    Output:
        (str): Năm học đã chuẩn hoá (VD: "2024-2025") hoặc "unknown"

    Lưu ý:
        - Gọi normalize_year() để chuẩn hoá format
        - Trả về "unknown" nếu không tìm thấy
    """
    if len(df) > 3:
        row = df.iloc[3]
        for cell in row:
            if isinstance(cell, str) and ("Năm học" in cell or "Nam hoc" in cell):
                parts = cell.strip().split(":")
                if len(parts) > 1:
                    raw_year = parts[-1].strip()
                    normalized = normalize_year(raw_year)
                    return normalized if normalized else "unknown"
    return "unknown"


# ============================================================================
# Constants - Hằng số
# ============================================================================

# Các marker được chấp nhận cho checkbox đã checked
CHECKBOX_MARKERS = {"✓", "✔", "v", "x", "1", "true", "yes"}

# Mapping category name -> keywords để nhận diện header column
CLASSIFICATION_CATEGORIES = {
    "HTXS": ["hoan thanh xuat sac", "hoan thien xuat sac", "hoan thanh xs", "hoan thien xs"],
    "HTT": ["hoan thanh tot", "hoan thien tot", "hoan thanh tot", "htt", "tot"],
    "HT": ["hoan thanh", "ht"],
    "CHT": ["chua hoan thanh", "chua hoan thanh", "cht"],
}

ACHIEVEMENT_CATEGORIES = {
    "HSXS": ["hoc sinh xuat sac", "hoc sinh xuatsac", "hsxs"],
    "HS_TieuBieu": ["hoc sinh tieu bieu", "hoc sinh tieubieu", "hs_tieubieu"],
}

ALL_CATEGORIES = {**CLASSIFICATION_CATEGORIES, **ACHIEVEMENT_CATEGORIES}


def _matches_category(text: str, category_keywords: List[str]) -> bool:
    """
    Mô tả:
        Kiểm tra xem text đã normalize có khớp với bất kỳ keyword nào của category không.

    Input:
        text (str): Text cần kiểm tra (đã normalize)
        category_keywords (List[str]): Danh sách keywords của category

    Output:
        (bool): True nếu khớp (exact hoặc substring match)
    """
    normalized = _normalize(text)

    if not normalized:
        return False

    for kw in category_keywords:
        kw_norm = _normalize(kw)
        if kw_norm in normalized or normalized in kw_norm:
            return True

    return False


# ============================================================================
# Logging helpers
# ============================================================================

def _log_debug(message: str) -> None:
    """Safe debug logging với UTF-8 support."""
    try:
        print(f"[DEBUG] {message}")
    except UnicodeEncodeError:
        print("[DEBUG] (unicode message)")


def _log_warning(message: str) -> None:
    """Safe warning logging với UTF-8 support."""
    try:
        print(f"[WARNING] {message}")
    except UnicodeEncodeError:
        print("[WARNING] (unicode message)")


# ============================================================================
# Column Detection Helpers
# ============================================================================

def _detect_category_columns(df: pd.DataFrame, header_start: int = 0, header_end: int = 15) -> Dict[str, Optional[int]]:
    """
    Mô tả:
        Nhận diện các column index tương ứng với category (HTXS, HTT, HT, CHT...).

    Input:
        df (pd.DataFrame): DataFrame chứa dữ liệu Excel
        header_start (int): Dòng bắt đầu tìm header
        header_end (int): Dòng kết thúc tìm header

    Output:
        (Dict[str, int|None]): Ánh xạ category name -> column index
                               VD: {"HTXS": 3, "HTT": 4, "HT": 5, "CHT": 6}
    """
    detected_columns: Dict[str, Optional[int]] = {}

    search_range = range(header_start, min(header_end, len(df)))

    for col_idx in range(len(df.columns)):
        for row_idx in search_range:
            cell = df.iloc[row_idx, col_idx]
            cell_str = _safe_str(cell)
            if not cell_str:
                continue

            cell_norm = _normalize(cell_str)

            for cat_name, keywords in ALL_CATEGORIES.items():
                if cat_name in detected_columns:
                    continue

                for kw in keywords:
                    kw_norm = _normalize(kw)
                    if kw_norm in cell_norm or cell_norm in kw_norm:
                        detected_columns[cat_name] = col_idx
                        break

    return detected_columns


def _find_header_region(df: pd.DataFrame) -> Tuple[int, int]:
    """
    Mô tả:
        Xác định vùng header trong DataFrame - tìm dòng bắt đầu dữ liệu.

    Input:
        df (pd.DataFrame): DataFrame từ Excel

    Output:
        (Tuple[int, int]): (header_start, header_end) - indices của dòng
                           Data bắt đầu từ header_end
    """
    header_end = 15

    for idx in range(min(20, len(df))):
        row = df.iloc[idx]
        row_values = [_safe_str(v) for v in row if pd.notna(v)]

        if any("stt" in _normalize(v) for v in row_values if v):
            return (0, idx)
        if any("hoten" in _normalize(v) or "ho ten" in _normalize(v) for v in row_values if v):
            return (0, idx)

    return (0, header_end)


def _count_checked_per_column(df: pd.DataFrame, column_map: Dict[str, Optional[int]], data_start: int) -> Dict[str, int]:
    """
    Mô tả:
        Đếm số checkbox checked cho mỗi category column.

    Input:
        df (pd.DataFrame): DataFrame chứa dữ liệu
        column_map (Dict): Ánh xạ category -> column index
        data_start (int): Dòng bắt đầu dữ liệu (sau header)

    Output:
        (Dict[str, int]): Ánh xạ category -> số checkbox checked
                          VD: {"HTXS": 5, "HTT": 12, "HT": 3, "CHT": 0}
    """
    counts: Dict[str, int] = {cat: 0 for cat in column_map}

    for cat_name, col_idx in column_map.items():
        if col_idx is None:
            continue
        for row_idx in range(data_start, len(df)):
            cell = df.iloc[row_idx, col_idx]
            if is_checked(cell):
                counts[cat_name] += 1

    return counts


def _validate_counts(counts: Dict[str, int], actual_student_count: int) -> bool:
    """
    Mô tả:
        Validate rằng tổng số học sinh xếp loại = actual student count.

    Fix: Use actual_student_count (từ dữ liệu) thay vì row index.

    Input:
        counts (Dict): Số học sinh mỗi loại (HTXS, HTT, HT, CHT)
        actual_student_count (int): Tổng số học sinh thực tế (đếm được)

    Output:
        (bool): True nếu validation OK, False nếu có mismatch
    """
    classification_keys = ["HTXS", "HTT", "HT", "CHT"]
    classified_total = sum(counts.get(k, 0) for k in classification_keys)

    if classified_total != actual_student_count:
        return False
    return True


# ============================================================================
# KQGD Section Parsing - Đánh giá KQGD
# ============================================================================

def _parse_kqgd_summary(
    df: pd.DataFrame,
    class_name: str,
    academic_year: str,
) -> Optional[Dict[str, Any]]:
    """
    Mô tả:
        Phân tích và đếm số lượng HTXS/HTT/HT/CHT trong phần Đánh giá KQGD.

    KQGD Rules (từ contracts.md):
        - Parse KQGD ONLY IF snapshot_type IN {"baseline", "actual_hk2"}
        - total_students_from_KQGD MUST be > 0
        - Sum(HTXS + HTT + HT + CHT) == total_students_from_KQGD

    Improved: Use keyword matching for header detection.

    Input:
        df (pd.DataFrame): DataFrame từ sheet
        class_name (str): Tên lớp
        academic_year (str): Năm học

    Output:
        (Dict|None): Dict chứa HTXS/HTT/HT/CHT/total_students hoặc None

    Raises:
        ValueError: Nếu total == 0 hoặc sum mismatch
    """
    # Tìm phần header có chứa "Đánh giá KQGD"
    section_start = None
    max_scan = min(60, len(df))
    for i in range(max_scan):
        for cell in df.iloc[i]:
            if isinstance(cell, str) and "đánh giá kqgd" in _normalize(cell):
                section_start = i
                break
        if section_start is not None:
            break
    if section_start is None:
        return None

    # Tìm cột cho HTXS/HTT/HT/CHT trong header ngay sau section_start
    # Sử dụng keyword matching thay vì exact string
    header_row = None
    category_map: Dict[str, int] = {}
    for r in range(section_start + 1, min(section_start + 12, len(df))):
        row = df.iloc[r]
        for c, cell in enumerate(row):
            if not isinstance(cell, str):
                continue
            # Keyword matching
            if _matches_category(cell, CLASSIFICATION_CATEGORIES.get("HTXS", [])):
                category_map["HTXS"] = c
            elif _matches_category(cell, CLASSIFICATION_CATEGORIES.get("HTT", [])):
                category_map["HTT"] = c
            elif _matches_category(cell, CLASSIFICATION_CATEGORIES.get("HT", [])):
                category_map["HT"] = c
            elif _matches_category(cell, CLASSIFICATION_CATEGORIES.get("CHT", [])):
                category_map["CHT"] = c
        if len(category_map) >= 4:
            header_row = r
            break
    if not category_map or len(category_map) < 4:
        return None

    data_start = (header_row or section_start) + 1
    HTXS = HTT = HT = CHT = 0
    total_students = 0

    for row_idx in range(data_start, len(df)):
        row = df.iloc[row_idx]
        first = row[0] if len(row) > 0 else None
        if pd.isna(first) or (isinstance(first, str) and first.strip() == ""):
            continue
        total_students += 1

        if "HTXS" in category_map:
            col = category_map["HTXS"]
            if is_checked(row.iloc[col]):
                HTXS += 1
        if "HTT" in category_map:
            col = category_map["HTT"]
            if is_checked(row.iloc[col]):
                HTT += 1
        if "HT" in category_map:
            col = category_map["HT"]
            if is_checked(row.iloc[col]):
                HT += 1
        if "CHT" in category_map:
            col = category_map["CHT"]
            if is_checked(row.iloc[col]):
                CHT += 1

    # Zero-data protection: total_students_from_KQGD MUST be > 0
    if total_students == 0:
        raise ValueError(
            f"KQGD: empty data in class {class_name}, year {academic_year}"
        )

    # Validate sum
    kqgd_sum = HTXS + HTT + HT + CHT
    if kqgd_sum != total_students:
        raise ValueError(
            f"KQGD: HTXS+HTT+HT+CHT ({kqgd_sum}) != total_students ({total_students}) "
            f"in class {class_name}, year {academic_year}"
        )

    return {
        "HTXS": HTXS,
        "HTT": HTT,
        "HT": HT,
        "CHT": CHT,
        "total_students": total_students,
    }


def _parse_class_summary(
    df: pd.DataFrame,
    class_name: str,
    academic_year: str,
    allow_kqgd: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Mô tả:
        Parse dữ liệu tổng hợp cấp lớp (HTXS, HTT, HT, CHT...) sử dụng checkbox counting.

    KQGD Gate:
        - Parse KQGD ONLY IF allow_kqgd=True
        - Skip KQGD parsing entirely if allow_kqgd=False

    Input:
        df (pd.DataFrame): DataFrame từ sheet
        class_name (str): Tên lớp
        academic_year (str): Năm học đã chuẩn hoá
        allow_kqgd (bool): Cho phép parse KQGD (True cho baseline/actual_hk2)

    Output:
        (Dict|None): Dict chứa số học sinh mỗi loại, hoặc None nếu không parse được

    Raises:
        ValueError: Nếu KQGD validation fail
    """
    header_start, header_end = _find_header_region(df)
    data_start = header_end

    _log_debug(f"Header region: rows {header_start}-{header_end}, Data starts at row {data_start}")

    # Nhận diện các column chứa category
    column_map = _detect_category_columns(df, header_start, header_end)

    if not column_map:
        _log_debug("No classification columns detected in header region")
        return None

    _log_debug("Detected category columns:")
    for cat, col in sorted(column_map.items(), key=lambda x: x[1] or 0):
        _log_debug(f"  {cat} -> column {col}")

    # Đếm checkbox checked cho mỗi category
    counts = _count_checked_per_column(df, column_map, data_start)

    # Đếm actual student count từ data rows
    actual_student_count = 0
    for row_idx in range(data_start, len(df)):
        row = df.iloc[row_idx]
        first = row[0] if len(row) > 0 else None
        if pd.isna(first) or (isinstance(first, str) and first.strip() == ""):
            continue
        actual_student_count += 1

    # Parse KQGD nếu được phép
    kqgd_section = None
    if allow_kqgd:
        try:
            kqgd_section = _parse_kqgd_summary(df, class_name, academic_year)
        except ValueError:
            raise
        except Exception:
            pass

    if kqgd_section:
        # Override counts với KQGD data nếu có
        counts["HTXS"] = kqgd_section.get("HTXS", 0)
        counts["HTT"] = kqgd_section.get("HTT", 0)
        counts["HT"] = kqgd_section.get("HT", 0)
        counts["CHT"] = kqgd_section.get("CHT", 0)
        # Use KQGD total as actual student count
        actual_student_count = kqgd_section.get("total_students", actual_student_count)

    result = {
        "class_name": class_name,
        "academic_year": academic_year,
        "HTXS": counts.get("HTXS", 0),
        "HTT": counts.get("HTT", 0),
        "HT": counts.get("HT", 0),
        "CHT": counts.get("CHT", 0),
        "HTCTLH_HT": counts.get("HTCTLH_HT", 0),
        "HTCTLH_CHT": counts.get("HTCTLH_CHT", 0),
        "HSXS": counts.get("HSXS", 0),
        "HS_TieuBieu": counts.get("HS_TieuBieu", 0),
        "total_students": actual_student_count,
    }

    classification_keys = ["HTXS", "HTT", "HT", "CHT"]
    classified_total = sum(counts.get(k, 0) for k in classification_keys)

    # Validation: tổng xếp loại phải = actual student count
    validation_ok = _validate_counts(counts, actual_student_count)
    result["_validation_ok"] = validation_ok

    if validation_ok:
        _log_debug(f"Validation OK: {classified_total} students classified correctly")
    else:
        _log_warning(f"Validation MISMATCH: {classified_total} classified, but {actual_student_count} actual students")

    return result


def parse_class_summary_sheet(
    df: pd.DataFrame,
    class_name: str,
    academic_year: str,
    allow_kqgd: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Mô tả:
        Wrapper cho _parse_class_summary - parse single sheet's class-level summary.

    Input:
        df (pd.DataFrame): DataFrame từ sheet
        class_name (str): Tên lớp
        academic_year (str): Năm học
        allow_kqgd (bool): Cho phép parse KQGD

    Output:
        (Dict|None): Dict class summary hoặc None
    """
    return _parse_class_summary(df, class_name, academic_year, allow_kqgd)


# ============================================================================
# Subject parsing - Parse dữ liệu môn học (điểm số, T/H/C)
# ============================================================================

def _detect_subject_type(
    current_col: int,
    next_col: Optional[int],
    current_header_norm: str,
    next_header_norm: Optional[str],
) -> Dict[str, Any]:
    """
    Mô tả:
        Xác định loại môn học dựa trên column grouping.

    Fix: If headers do NOT match → treat as qualitative (don't raise error).

    Rules (từ contracts.md):
        - Two adjacent columns with same subject header → scored subject (2 columns)
        - Single column OR headers don't match → qualitative subject (1 column)
        - Scored subject = exactly 2 columns
        - Qualitative subject = exactly 1 column

    Input:
        current_col (int): Column index hiện tại
        next_col (int|None): Column index kế tiếp
        current_header_norm (str): Normalized header của column hiện tại
        next_header_norm (str|None): Normalized header của column kế tiếp

    Output:
        (Dict): {
            "subject_type": "scored" | "qualitative",
            "level_col": int,
            "score_col": int | None,
            "columns_used": [int, ...]
        }
    """
    if next_col is not None and next_header_norm is not None:
        # Kiểm tra headers có match không
        if current_header_norm == next_header_norm:
            # Headers match -> scored subject (2 columns)
            return {
                "subject_type": "scored",
                "level_col": current_col,
                "score_col": next_col,
                "columns_used": [current_col, next_col],
            }
        else:
            # Headers don't match -> qualitative (1 column only)
            return {
                "subject_type": "qualitative",
                "level_col": current_col,
                "score_col": None,
                "columns_used": [current_col],
            }

    # No next column or no next header -> qualitative (1 column)
    return {
        "subject_type": "qualitative",
        "level_col": current_col,
        "score_col": None,
        "columns_used": [current_col],
    }


def _validate_subject_columns(
    subject_entries: List[Dict[str, Any]],
    class_name: str,
    academic_year: str,
) -> None:
    """
    Mô tả:
        Validate rằng mỗi subject có đúng column count.

    Rules (từ contracts.md):
        - Parser MUST validate that:
          - Scored subject = exactly 2 columns
          - Qualitative subject = exactly 1 column
        - Any deviation -> raise ValueError

    Input:
        subject_entries (List[Dict]): Danh sách subject entries đã detect
        class_name (str): Tên lớp (cho error message)
        academic_year (str): Năm học (cho error message)

    Raises:
        ValueError: Nếu column count không đúng
    """
    for entry in subject_entries:
        subject_type = entry.get("subject_type")
        columns_used = entry.get("columns_used", [])

        if subject_type == "scored":
            if len(columns_used) != 2:
                raise ValueError(
                    f"Column count mismatch: scored subject '{entry.get('subject')}' "
                    f"must have exactly 2 columns, got {len(columns_used)} "
                    f"(class {class_name}, year {academic_year})"
                )

        elif subject_type == "qualitative":
            if len(columns_used) != 1:
                raise ValueError(
                    f"Column count mismatch: qualitative subject '{entry.get('subject')}' "
                    f"must have exactly 1 column, got {len(columns_used)} "
                    f"(class {class_name}, year {academic_year})"
                )


def _build_column_plan(df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[int]]:
    """
    Mô tả:
        Nhận diện các subject columns dựa trên structural markers trong header.

    Column Grouping Detection (từ contracts.md):
        - Parser MUST detect subject type by STRUCTURE
        - Two adjacent columns with same subject header → scored subject
        - Single column OR headers don't match → qualitative subject
        - Headers match ONLY IF normalized headers are identical

    Normalization steps (từ contracts.md):
        - lowercase
        - remove accents (đ → d)
        - trim whitespace

    Input:
        df (pd.DataFrame): DataFrame từ Excel

    Output:
        (Tuple[List[Dict], List[int]]):
            - [0]: Danh sách entries với subject_type, columns_used
            - [1]: Danh sách các column indices đã used (để tránh duplicate)
    """
    if len(df) < 10:
        return [], []

    h_main = df.iloc[6].ffill()
    h_sub = df.iloc[7]
    h_metrics = df.iloc[8]

    # Thu thập tất cả potential columns
    raw_entries = []
    for col in range(len(df.columns)):
        main_name = str(h_main.iloc[col]).strip() if pd.notna(h_main.iloc[col]) else ""
        sub_name = str(h_sub.iloc[col]).strip() if pd.notna(h_sub.iloc[col]) else ""
        metric_raw = str(h_metrics.iloc[col]).strip() if pd.notna(h_metrics.iloc[col]) else ""

        metric_norm = _normalize(metric_raw)

        # Xác định loại column dựa trên metric label
        is_level = "muc dat duoc" in metric_norm or "muc do" in metric_norm
        is_score = "diem" in metric_norm

        if not (is_level or is_score):
            continue

        # Xây dựng subject name từ main + sub
        full_subject = main_name
        if sub_name and _normalize(sub_name) not in _normalize(main_name):
            if _normalize(sub_name) not in ["muc dat duoc", "diem ktdk"]:
                full_subject = f"{main_name} - {sub_name}"

        # Normalize header để so sánh (sử dụng _normalize duy nhất)
        normalized_header = _normalize(full_subject)

        raw_entries.append({
            "col": col,
            "type": "level" if is_level else "score",
            "subject": full_subject,
            "normalized_header": normalized_header,
        })

    # Group adjacent columns by normalized header và detect subject type
    subject_entries = []
    processed_cols = set()

    for i, entry in enumerate(raw_entries):
        if entry["col"] in processed_cols:
            continue

        current_col = entry["col"]
        current_type = entry["type"]
        current_header_norm = entry["normalized_header"]
        current_subject = entry["subject"]

        # Xác định loại subject dựa trên column grouping
        if current_type == "level" and i + 1 < len(raw_entries):
            next_entry = raw_entries[i + 1]
            next_col = next_entry["col"]
            next_type = next_entry["type"]
            next_header_norm = next_entry["normalized_header"]

            # Kiểm tra có phải scored subject không:
            # - Level column followed by Score column
            # - Headers match sau normalization
            if next_type == "score" and next_col == current_col + 1 and current_header_norm == next_header_norm:
                # Scored subject: 2 columns
                subject_info = _detect_subject_type(
                    current_col=current_col,
                    next_col=next_col,
                    current_header_norm=current_header_norm,
                    next_header_norm=next_header_norm,
                )
                subject_info["subject"] = current_subject
                subject_entries.append(subject_info)
                processed_cols.add(current_col)
                processed_cols.add(next_col)
                continue

        # Qualitative subject: 1 column (level only, no adjacent score column matching)
        if current_type == "level":
            subject_info = _detect_subject_type(
                current_col=current_col,
                next_col=None,
                current_header_norm=current_header_norm,
                next_header_norm=None,
            )
            subject_info["subject"] = current_subject
            subject_entries.append(subject_info)
            processed_cols.add(current_col)
        elif current_type == "score":
            # Score column không có level pair -> qualitative (1 column)
            subject_info = _detect_subject_type(
                current_col=current_col,
                next_col=None,
                current_header_norm=current_header_norm,
                next_header_norm=None,
            )
            subject_info["subject"] = current_subject
            subject_entries.append(subject_info)
            processed_cols.add(current_col)

    # Deduplicate by normalized subject name to avoid duplicates
    if not subject_entries:
        return subject_entries, list(processed_cols)

    merged: Dict[str, Dict[str, Any]] = {}
    for entry in subject_entries:
        subj = entry.get("subject", "") or ""
        norm = _normalize(subj)
        if not norm:
            # Fallback to original subject if normalization yields empty
            norm = subj
        if norm not in merged:
            merged[norm] = entry
        else:
            prev = merged[norm]
            # Determine merged type: if either is scored -> scored
            t1 = prev.get("subject_type")
            t2 = entry.get("subject_type")
            merged_type = "scored" if (t1 == "scored" or t2 == "scored") else "qualitative"
            prev["subject_type"] = merged_type
            # Merge columns_used
            cols1 = set(prev.get("columns_used", []))
            cols2 = set(entry.get("columns_used", []))
            merged_cols = sorted(list(cols1.union(cols2)))
            prev["columns_used"] = merged_cols
            # Merge optional fields if present
            if not prev.get("level_col") and entry.get("level_col"):
                prev["level_col"] = entry["level_col"]
            if not prev.get("score_col") and entry.get("score_col"):
                prev["score_col"] = entry["score_col"]
            # Prefer existing subject/name; keep the first subject string
            prev["subject"] = prev.get("subject")
    final_entries = list(merged.values())
    return final_entries, list(processed_cols)


def parse_sheet(df: pd.DataFrame, class_name: str, academic_year: str) -> List[Dict[str, Any]]:
    """
    Mô tả:
        Parse single sheet's DataFrame - trích xuất điểm và xếp loại T/H/C theo môn học.

    Subject Type Rules (từ contracts.md):
        - Scored subjects:
          - avg_score MUST NOT be NULL
          - avg_score MUST be in range [0, 10]
          - T, H, C MUST exist
        - Qualitative subjects:
          - avg_score MUST be NULL
          - T, H, C MUST exist
          - T + H + C <= student_count

    Score column validation:
        - If non-numeric values exist → raise ValueError

    Input:
        df (pd.DataFrame): DataFrame từ sheet
        class_name (str): Tên lớp
        academic_year (str): Năm học đã chuẩn hoá

    Output:
        (List[Dict]): Danh sách results, mỗi dict = 1 môn học

    Data Contract - Output schema:
    [{
        "academic_year": str,
        "class_name": str,
        "subject": str,
        "avg_score": float | None,
        "student_count": int,
        "T": int, "H": int, "C": int,
        "T_pct": float | None, "H_pct": float | None, "C_pct": float | None
    }]

    Raises:
        ValueError: Nếu subject type validation fail hoặc score validation fail
    """
    subject_entries, _ = _build_column_plan(df)
    if not subject_entries:
        return []

    # Validate column counts
    _validate_subject_columns(subject_entries, class_name, academic_year)

    data_start = 9  # Row 10 - dòng bắt đầu dữ liệu học sinh

    results = []
    data_rows = df.iloc[data_start:]

    # Filter out empty rows (summary rows thường có nan ở col 0)
    data_rows = data_rows[data_rows.iloc[:, 0].apply(lambda x: str(x).isdigit())]

    # Đếm số dòng hợp lệ = số học sinh thực tế
    student_count = len(data_rows)

    for entry in subject_entries:
        subject_type = entry["subject_type"]
        level_col = entry["level_col"]
        score_col = entry.get("score_col")
        subject = entry["subject"]

        # Đếm số học sinh mỗi bucket (T/H/C)
        T = H = C = 0
        for val in data_rows.iloc[:, level_col]:
            bucket = _eval_bucket(val)
            if bucket == "T":
                T += 1
            elif bucket == "H":
                H += 1
            elif bucket == "C":
                C += 1

        # Tính điểm trung bình (chỉ scored subjects)
        avg_score = None
        if subject_type == "scored":
            if score_col is None:
                raise ValueError(
                    f"Scored subject '{subject}' missing score_col "
                    f"(class {class_name}, year {academic_year})"
                )
            # Score column validation: kiểm tra non-numeric values
            scores_series = pd.to_numeric(data_rows.iloc[:, score_col], errors="coerce")
            # Filter out NaN to check for actual non-numeric values
            valid_scores = scores_series.dropna()
            
            # Nếu có giá trị không phải số (không phải NaN thuần túy)
            # errors="coerce" đã convert non-numeric thành NaN
            # Kiểm tra xem có NaN nào không phải từ empty cells
            if len(valid_scores) < len(data_rows):
                # Có thể có empty cells - kiểm tra xem có actual non-numeric values không
                original_vals = data_rows.iloc[:, score_col]
                non_numeric_mask = pd.to_numeric(original_vals, errors="coerce").isna()
                original_not_na = ~original_vals.isna()
                actual_non_numeric = (non_numeric_mask & original_not_na).sum()
                if actual_non_numeric > 0:
                    raise ValueError(
                        f"Non-numeric values found in score column for subject '{subject}' "
                        f"(class {class_name}, year {academic_year})"
                    )
            
            if len(valid_scores) > 0:
                avg_score = round(float(valid_scores.mean()), 2)

            # avg_score validation: MUST be in range [0, 10]
            if avg_score is not None and (avg_score < 0 or avg_score > 10):
                raise ValueError(
                    f"avg_score out of range [0, 10]: {avg_score} "
                    f"for subject '{subject}' "
                    f"(class {class_name}, year {academic_year})"
                )

        elif subject_type == "qualitative":
            # Qualitative: avg_score MUST be NULL
            avg_score = None

        # Validation: T, H, C must be >= 0
        if T < 0 or H < 0 or C < 0:
            raise ValueError(
                f"Negative T/H/C count for subject '{subject}' "
                f"(class {class_name}, year {academic_year})"
            )

        # Validation for qualitative: T + H + C <= student_count
        if subject_type == "qualitative":
            thc_sum = T + H + C
            if thc_sum > student_count:
                raise ValueError(
                    f"T+H+C ({thc_sum}) > student_count ({student_count}) "
                    f"for qualitative subject '{subject}' "
                    f"(class {class_name}, year {academic_year})"
                )

        # Tính phần trăm mỗi bucket
        T_pct = H_pct = C_pct = None
        if student_count > 0:
            T_pct = round(T / student_count * 100, 2)
            H_pct = round(H / student_count * 100, 2)
            C_pct = round(C / student_count * 100, 2)

        results.append({
            "class_name": class_name,
            "academic_year": academic_year,
            "subject": subject,
            "subject_type": subject_type,
            "avg_score": avg_score,
            "student_count": student_count,
            "T": T,
            "H": H,
            "C": C,
            "T_pct": T_pct,
            "H_pct": H_pct,
            "C_pct": C_pct,
        })

    return results


# ---------------------------------------------------------------------------
# Public entry points - Entry points công khai
# ---------------------------------------------------------------------------

def parse_vnedu_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Mô tả:
        Parse all sheets của file VNEDU Excel - chỉ trả về subject data.

    Input:
        file_path (str): Đường dẫn file Excel

    Output:
        (List[Dict]): Flat list của subject summaries
    """
    sheets = read_vnedu_file(file_path)
    all_results = []

    for sheet_name, df in sheets.items():
        class_name = _detect_class_name(df, sheet_name)
        academic_year = _detect_academic_year(df)
        sheet_results = parse_sheet(df, class_name, academic_year)
        all_results.extend(sheet_results)

    return all_results


def parse_vnedu_file_with_class_summary(
    file_path: str,
    allow_kqgd: bool = True,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Mô tả:
        Parse all sheets của file VNEDU Excel - trả về cả subject data và class summary.

    KQGD Gate (từ contracts.md):
        - Parse KQGD ONLY IF snapshot_type IN {"baseline", "actual_hk2"}
        - Skip KQGD parsing entirely for all other snapshot_type values

    Cross-Validation (từ contracts.md):
        - subject_snapshots.student_count MUST match class_summary.total_students
        - If mismatch → raise ValueError

    Input:
        file_path (str): Đường dẫn file Excel
        allow_kqgd (bool): Cho phép parse KQGD (True cho baseline/actual_hk2)

    Output:
        (Tuple[List[Dict], List[Dict]]):
            - [0]: subject_results - danh sách subject summaries
            - [1]: class_summary_results - danh sách class-level summaries

    Lưu ý:
        - Entry point chính được dùng trong main.py
        - Đảm bảo academic_year được chuẩn hoá trước khi trả về
    """
    sheets = read_vnedu_file(file_path)
    subject_results = []
    class_summary_results = []

    for sheet_name, df in sheets.items():
        class_name = _detect_class_name(df, sheet_name)
        academic_year = _detect_academic_year(df)

        # Parse subject data (điểm, T/H/C)
        sheet_results = parse_sheet(df, class_name, academic_year)
        subject_results.extend(sheet_results)

        # Parse class-level summary (HTXS, HTT, HT, CHT...) - chỉ khi allow_kqgd
        class_summary = parse_class_summary_sheet(
            df, class_name, academic_year, allow_kqgd=allow_kqgd
        )
        if class_summary:
            class_summary_results.append(class_summary)

    # Cross-validation: subject_snapshots.student_count must match class_summary.total_students
    if class_summary_results and allow_kqgd:
        for class_sum in class_summary_results:
            kqgd_total = class_sum.get("total_students", 0)
            if kqgd_total > 0:
                # Lấy student_count từ subject_results cùng class/year
                matching_subjects = [
                    s for s in subject_results
                    if s["class_name"] == class_sum["class_name"]
                    and s["academic_year"] == class_sum["academic_year"]
                ]
                if matching_subjects:
                    subject_avg_count = matching_subjects[0].get("student_count", 0)
                    if subject_avg_count != kqgd_total:
                        raise ValueError(
                            f"Cross-validation failed: subject_snapshots.student_count ({subject_avg_count}) "
                            f"!= class_summary.total_students ({kqgd_total}) "
                            f"in class {class_sum['class_name']}, year {class_sum['academic_year']}"
                        )

    return subject_results, class_summary_results
