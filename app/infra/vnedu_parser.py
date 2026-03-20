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

def _norm(s: Any) -> str:
    """
    Mô tả:
        Chuẩn hoá text: lowercase, loại bỏ dấu tiếng Việt và 'đ', trả về ASCII string.

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
    s = _norm(str(val))
    if s in ("htt", "t"):
        return "T"
    if s in ("ht",  "h"):
        return "H"
    if s in ("cht", "c"):
        return "C"
    return None


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
# Class-level summary parsing - Tổng hợp dữ liệu cấp lớp (HTXS, HTT, HT, CHT)
# ============================================================================
# Cấu trúc dữ liệu: CHECKBOX MATRIX (Ma trận checkbox)
# - Mỗi ROW = 1 học sinh
# - Mỗi COLUMN = 1 category (HTXS, HTT, HT, CHT...)
# - Cell chứa marker checkbox (✓, ✔, x, 1) hoặc blank
# - Đếm số checkbox được đánh dấu trên mỗi cột
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


def _normalize_text(text: str) -> str:
    """
    Mô tả:
        Chuẩn hoá text tiếng Việt để so sánh: lowercase, loại bỏ dấu, xử lý khoảng trắng.

    Input:
        text (str): Chuỗi đầu vào

    Output:
        (str): Text đã chuẩn hoá, ASCII-safe
    """
    if not text:
        return ""

    text = text.strip().lower()

    # Loại bỏ khoảng trắng thừa (multiple spaces/newlines -> single space)
    text = " ".join(text.split())

    # Thay thế đ -> d
    text = text.replace("đ", "d").replace("Đ", "D")

    # Loại bỏ Vietnamese diacritics bằng NFKD normalization
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))

    return ascii_text.strip()


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
    normalized = _normalize_text(text)

    if not normalized:
        return False

    for kw in category_keywords:
        kw_norm = _normalize_text(kw)
        # Match: keyword in text hoặc text in keyword
        if kw_norm in normalized or normalized in kw_norm:
            return True

    return False


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

    # Duyệt từng cell trong vùng header
    for col_idx in range(len(df.columns)):
        for row_idx in search_range:
            cell = df.iloc[row_idx, col_idx]
            cell_str = _safe_str(cell)
            if not cell_str:
                continue

            cell_norm = _normalize_text(cell_str)

            # Kiểm tra cell có chứa keyword của category nào không
            for cat_name, keywords in ALL_CATEGORIES.items():
                if cat_name in detected_columns:
                    continue

                for kw in keywords:
                    kw_norm = _normalize_text(kw)
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

        # Tìm dòng chứa "STT" hoặc "Họ tên" -> đó là dòng cuối cùng của header
        if any("stt" in _normalize_text(v) for v in row_values if v):
            return (0, idx)
        if any("hoten" in _normalize_text(v) or "ho ten" in _normalize_text(v) for v in row_values if v):
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


def _validate_counts(counts: Dict[str, int], total_students: int) -> bool:
    """
    Mô tả:
        Validate rằng tổng số học sinh xếp loại = total students.

    Input:
        counts (Dict): Số học sinh mỗi loại (HTXS, HTT, HT, CHT)
        total_students (int): Tổng số học sinh

    Output:
        (bool): True nếu validation OK, False nếu có mismatch

    Lưu ý:
        - Mismatch có thể do lỗi đếm checkbox hoặc dữ liệu Excel không chuẩn
    """
    classification_keys = ["HTXS", "HTT", "HT", "CHT"]
    classified_total = sum(counts.get(k, 0) for k in classification_keys)

    if classified_total != total_students:
        return False
    return True


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


def _parse_class_summary(df: pd.DataFrame, class_name: str, academic_year: str) -> Optional[Dict[str, Any]]:
    """
    Mô tả:
        Parse dữ liệu tổng hợp cấp lớp (HTXS, HTT, HT, CHT...) sử dụng checkbox counting.

    Algorithm:
        1. Xác định vùng header (dòng trước dữ liệu)
        2. Map column indices -> categories bằng matching header text
        3. Đếm checkbox markers trên mỗi category column
        4. Validate tổng matches student count

    Input:
        df (pd.DataFrame): DataFrame từ sheet
        class_name (str): Tên lớp
        academic_year (str): Năm học đã chuẩn hoá

    Output:
        (Dict|None): Dict chứa số học sinh mỗi loại, hoặc None nếu không parse được

    Data Contract - Output schema:
    {
        "class_name": str,
        "academic_year": str,
        "HTXS": int, "HTT": int, "HT": int, "CHT": int,
        "HSXS": int, "HS_TieuBieu": int,
        "_validation_ok": bool
    }
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
    }

    classification_keys = ["HTXS", "HTT", "HT", "CHT"]
    classified_total = sum(counts.get(k, 0) for k in classification_keys)

    # Validation: tổng xếp loại phải = số dòng dữ liệu
    validation_ok = _validate_counts(counts, data_start)
    result["_validation_ok"] = validation_ok

    if validation_ok:
        _log_debug(f"Validation OK: {classified_total} students classified correctly")
    else:
        _log_warning(f"Validation MISMATCH: {classified_total} classified, but {data_start} data rows")

    return result


def parse_class_summary_sheet(df: pd.DataFrame, class_name: str, academic_year: str) -> Optional[Dict[str, Any]]:
    """
    Mô tả:
        Wrapper cho _parse_class_summary - parse single sheet's class-level summary.

    Input:
        df (pd.DataFrame): DataFrame từ sheet
        class_name (str): Tên lớp
        academic_year (str): Năm học

    Output:
        (Dict|None): Dict class summary hoặc None
    """
    return _parse_class_summary(df, class_name, academic_year)


# ---------------------------------------------------------------------------
# Subject parsing - Parse dữ liệu môn học (điểm số, T/H/C)
# ---------------------------------------------------------------------------

def _build_column_plan(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Mô tả:
        Nhận diện các subject columns dựa trên structural markers trong header.

    Cấu trúc header đã xác nhận:
        idx 6 (Row 7)  → Main Subject/Section
        idx 7 (Row 8)  → Sub-Subject/Category
        idx 8 (Row 9)  → Metric Label ("Mức đạt được", "Điểm KTĐK")

    Rules:
        - "Mức đạt được" hoặc "Mức độ" -> đánh dấu column là level/bucket column
        - "Điểm" -> đánh dấu column là numeric score column

    Input:
        df (pd.DataFrame): DataFrame từ Excel

    Output:
        (List[Dict]): Danh sách entries, mỗi entry có {col, type, subject}
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

        # Xác định loại column dựa trên metric label
        is_level = "muc dat duoc" in metric_norm or "muc do" in metric_norm
        is_score = "diem" in metric_norm

        if not (is_level or is_score):
            continue

        # Xây dựng subject name từ main + sub
        full_subject = main_name
        if sub_name and _norm(sub_name) not in _norm(main_name):
            # Bỏ qua nếu sub_name là metric label
            if _norm(sub_name) not in ["muc dat duoc", "diem ktdk"]:
                full_subject = f"{main_name} - {sub_name}"

        if is_level:
            plan.append({"col": col, "type": "level", "subject": full_subject})
        elif is_score:
            plan.append({"col": col, "type": "score", "subject": full_subject})

    return plan


def parse_sheet(df: pd.DataFrame, class_name: str, academic_year: str) -> List[Dict[str, Any]]:
    """
    Mô tả:
        Parse single sheet's DataFrame - trích xuất điểm và xếp loại T/H/C theo môn học.

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
    """
    plan = _build_column_plan(df)
    if not plan:
        return []

    data_start = 9  # Row 10 - dòng bắt đầu dữ liệu học sinh

    # Group plan entries by subject name (1 môn có thể có level + score column)
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

    # Filter out empty rows (summary rows thường có nan ở col 0)
    data_rows = data_rows[data_rows.iloc[:, 0].apply(lambda x: str(x).isdigit())]

    # Đếm số dòng hợp lệ = số học sinh thực tế
    student_count = len(data_rows)

    for subj, cols in subjects.items():
        level_col = cols["level_col"]
        score_col = cols["score_col"]

        # Đếm số học sinh mỗi bucket (T/H/C)
        T = H = C = 0
        if level_col is not None:
            for val in data_rows.iloc[:, level_col]:
                bucket = _eval_bucket(val)
                if bucket == "T":
                    T += 1
                elif bucket == "H":
                    H += 1
                elif bucket == "C":
                    C += 1

        # Tính điểm trung bình (nếu có score column)
        avg_score = None
        if score_col is not None:
            scores = pd.to_numeric(data_rows.iloc[:, score_col], errors="coerce").dropna()
            if not scores.empty:
                avg_score = round(float(scores.mean()), 2)

        # Tính phần trăm mỗi bucket
        T_pct = H_pct = C_pct = None
        if student_count > 0:
            T_pct = round(T / student_count * 100, 2)
            H_pct = round(H / student_count * 100, 2)
            C_pct = round(C / student_count * 100, 2)

        results.append({
            "class_name":    class_name,
            "academic_year": academic_year,
            "subject":       subj,
            "avg_score":     avg_score,
            "student_count": student_count,
            "T":             T,
            "H":             H,
            "C":             C,
            "T_pct":         T_pct,
            "H_pct":         H_pct,
            "C_pct":         C_pct,
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


def parse_vnedu_file_with_class_summary(file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Mô tả:
        Parse all sheets của file VNEDU Excel - trả về cả subject data và class summary.

    Input:
        file_path (str): Đường dẫn file Excel

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

        # Parse class-level summary (HTXS, HTT, HT, CHT...)
        class_summary = parse_class_summary_sheet(df, class_name, academic_year)
        if class_summary:
            class_summary_results.append(class_summary)

    return subject_results, class_summary_results
