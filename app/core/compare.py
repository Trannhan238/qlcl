"""
Mô tả file:
- Vai trò: Module so sánh - tính toán delta, trend, và status giữa các snapshot
- Input: Dict chứa actual, baseline, target, commitment values
- Output: Dict chứa delta, trend, status
- Phụ thuộc: pandas, typing (standard library)

Quy ước:
- actual: Kết quả thực tế (từ file VNEDU import)
- baseline: Dữ liệu gốc của năm học trước
- target: Mục tiêu đặt ra cho năm học hiện tại
- commitment: Cam kết của giáo viên

Snapshot types:
- actual_hk1: Kết quả HK1
- actual_hk2: Kết quả HK2
- baseline: Dữ liệu năm trước (shifted lên 1 grade)
- target: Mục tiêu năm nay
- commitment: Cam kết GV
"""

from typing import Dict, Optional, Any


def is_missing(val: Any) -> bool:
    """
    Mô tả:
        Kiểm tra giá trị có phải là None hoặc NaN không.

    Input:
        val (Any): Giá trị cần kiểm tra

    Output:
        (bool): True nếu None hoặc NaN

    Lưu ý:
        - Hỗ trợ cả pandas NA và Python float NaN
        - Dùng cho safe operations
    """
    if val is None:
        return True
    try:
        import pandas as pd
        if pd.isna(val):
            return True
    except ImportError:
        import math
        if isinstance(val, float) and math.isnan(val):
            return True
    return False


def safe_subtract(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """
    Mô tả:
        Trừ an toàn: b từ a, trả về None nếu a hoặc b là None/NaN.

    Input:
        a (float|None): Số bị trừ
        b (float|None): Số trừ

    Output:
        (float|None): a - b, hoặc None nếu có giá trị missing
    """
    if is_missing(a) or is_missing(b):
        return None
    return a - b


def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """
    Mô tả:
        Chia an toàn, trả về None nếu mẫu số = 0 hoặc có giá trị missing.

    Input:
        numerator (float): Tử số
        denominator (float): Mẫu số

    Output:
        (float|None): numerator/denominator, hoặc None nếu invalid
    """
    if denominator == 0 or is_missing(numerator) or is_missing(denominator):
        return None
    return numerator / denominator


def compute_thc_percentages(T: int, H: int, C: int, student_count: int) -> Dict[str, Optional[float]]:
    """
    Mô tả:
        Tính phần trăm T/H/C dựa trên tổng số học sinh.

    Input:
        T (int): Số học sinh xếp loại T (Tốt)
        H (int): Số học sinh xếp loại H (Hoàn thành)
        C (int): Số học sinh xếp loại C (Chưa hoàn thành)
        student_count (int): Tổng số học sinh

    Output:
        (Dict): {"T_pct": float, "H_pct": float, "C_pct": float}
                Giá trị None nếu student_count <= 0

    Lưu ý:
        - Tổng T_pct + H_pct + C_pct = 100%
        - student_count phải > 0 để tính được
    """
    if student_count <= 0:
        return {"T_pct": None, "H_pct": None, "C_pct": None}

    return {
        "T_pct": round(T / student_count * 100, 2),
        "H_pct": round(H / student_count * 100, 2),
        "C_pct": round(C / student_count * 100, 2),
    }


def compare_metric(data: Dict[str, Optional[float]], selected_snapshot: str = "actual_hk2") -> Dict[str, Any]:
    """
    Mô tả:
        So sánh metrics giữa actual, baseline, target, và commitment.

    Logic:
        1. Nếu không có actual score -> return unknown ngay
        2. Tính delta: actual - baseline, actual - target, actual - commitment
        3. Xác định trend dựa trên delta baseline (tăng/giảm/equal)
        4. Xác định status dựa trên target (achieved/not_achieved)

    Input:
        data (Dict): Dict chứa các snapshot values
            VD: {"actual_hk2": 8.5, "baseline": 8.0, "target": 8.5, "commitment": 8.3}
        selected_snapshot (str): Key của snapshot để so sánh (default: "actual_hk2")

    Output:
        (Dict):
            {
                "actual": float,
                "delta_baseline": float|None,
                "delta_target": float|None,
                "delta_commitment": float|None,
                "trend": "increase"|"decrease"|"equal"|"unknown",
                "status": "achieved"|"not_achieved"|"unknown"
            }

    Lưu ý:
        - Trend so với baseline: tăng/giảm/equal
        - Status so với target: achieved/not_achieved
    """
    actual = data.get(selected_snapshot)

    # Không có actual score -> không so sánh được
    if is_missing(actual):
        return {
            "actual": None,
            "delta_baseline": None,
            "delta_target": None,
            "delta_commitment": None,
            "trend": "unknown",
            "status": "unknown",
        }

    baseline = data.get("baseline")
    target = data.get("target")
    commitment = data.get("commitment")

    # Tính các delta
    delta_baseline = safe_subtract(actual, baseline)
    delta_target = safe_subtract(actual, target)
    delta_commitment = safe_subtract(actual, commitment)

    # Xác định trend dựa trên baseline
    trend = "unknown"
    if delta_baseline is not None:
        if delta_baseline > 0:
            trend = "increase"
        elif delta_baseline < 0:
            trend = "decrease"
        else:
            trend = "equal"

    # Xác định status dựa trên target
    status = "unknown"
    if target is not None:
        status = "achieved" if actual >= target else "not_achieved"

    return {
        "actual": actual,
        "delta_baseline": delta_baseline,
        "delta_target": delta_target,
        "delta_commitment": delta_commitment,
        "trend": trend,
        "status": status,
    }


def compare_with_targets(
    actual_avg_score: Optional[float],
    actual_T_pct: Optional[float],
    actual_H_pct: Optional[float],
    actual_C_pct: Optional[float],
    target_avg_score: Optional[float] = None,
    target_T_pct: Optional[float] = None,
    target_H_pct: Optional[float] = None,
    target_C_pct: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Mô tả:
        So sánh kết quả thực tế với mục tiêu đã đặt ra.

    Logic đánh giá:
        - score_status: achieved nếu actual >= target
        - thc_status:
            - achieved: T tăng/giữ (delta >= 0) VÀ C giảm/không tăng (delta <= 0)
            - not_achieved: ngược lại
            - partial: có target nhưng không đủ dữ liệu để kết luận
            - unknown: không có target hoặc actual

    Input:
        actual_avg_score (float|None): Điểm trung bình thực tế
        actual_T_pct, actual_H_pct, actual_C_pct (float|None): Phần trăm THC thực tế
        target_* (float|None): Các mục tiêu tương ứng

    Output:
        (Dict):
            {
                "score_delta": float|None,
                "score_status": "achieved"|"not_achieved"|"unknown",
                "T_delta", "H_delta", "C_delta": float|None,
                "thc_status": "achieved"|"not_achieved"|"partial"|"unknown"
            }
    """
    # Tính các delta
    score_delta = safe_subtract(actual_avg_score, target_avg_score)

    T_delta = safe_subtract(actual_T_pct, target_T_pct)
    H_delta = safe_subtract(actual_H_pct, target_H_pct)
    C_delta = safe_subtract(actual_C_pct, target_C_pct)

    # Đánh giá điểm trung bình
    score_status = "unknown"
    if target_avg_score is not None and actual_avg_score is not None:
        score_status = "achieved" if actual_avg_score >= target_avg_score else "not_achieved"

    # Kiểm tra có đủ dữ liệu THC không
    has_thc_target = any(v is not None for v in [target_T_pct, target_H_pct, target_C_pct])
    has_thc_actual = all(v is not None for v in [actual_T_pct, actual_H_pct, actual_C_pct])

    # Đánh giá THC
    if not has_thc_target:
        thc_status = "unknown"
    elif not has_thc_actual:
        thc_status = "unknown"
    else:
        all_delta = [T_delta, H_delta, C_delta]
        if all(d is not None for d in all_delta):
            # Thành công: T tăng/giữ VÀ C không tăng
            if T_delta is not None and T_delta >= 0 and C_delta is not None and C_delta <= 0:
                thc_status = "achieved"
            else:
                thc_status = "not_achieved"
        else:
            thc_status = "partial"

    return {
        "score_delta": score_delta,
        "score_status": score_status,
        "T_delta": T_delta,
        "H_delta": H_delta,
        "C_delta": C_delta,
        "thc_status": thc_status,
    }
