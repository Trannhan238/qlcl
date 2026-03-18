from typing import Dict, Optional, Any

def is_missing(val: Any) -> bool:
    """Checks if a value is None or NaN."""
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
    """Safely subtracts b from a. Returns None if either is None."""
    if is_missing(a) or is_missing(b):
        return None
    return a - b

def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """Safely divides, returning None if denominator is zero or invalid."""
    if denominator == 0 or is_missing(numerator) or is_missing(denominator):
        return None
    return numerator / denominator

def compute_thc_percentages(T: int, H: int, C: int, student_count: int) -> Dict[str, Optional[float]]:
    """
    Compute T/H/C percentages based on actual student_count.
    Returns None for all values if student_count is 0 or invalid.
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
    Compares the metrics against baselines, targets, and commitments based on the user's selected snapshot view.
    If no score is available (subject has no score column or NaN) in the selected snapshot,
    returns trend='unknown' and status='unknown' immediately.
    """
    actual = data.get(selected_snapshot)

    # If no score available in the selected view, short-circuit
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

    # Compute deltas
    delta_baseline = safe_subtract(actual, baseline)
    delta_target = safe_subtract(actual, target)
    delta_commitment = safe_subtract(actual, commitment)

    # Determine trend based on baseline
    trend = "unknown"
    if delta_baseline is not None:
        if delta_baseline > 0:
            trend = "increase"
        elif delta_baseline < 0:
            trend = "decrease"
        else:
            trend = "equal"

    # Determine status based on target
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
    Compare actual results against planned targets.
    
    Returns:
        - score_delta: actual_avg_score - target_avg_score (or None)
        - T_delta, H_delta, C_delta: percentage deltas (or None if target not set)
        - score_status: "achieved" | "not_achieved" | "unknown"
        - thc_status: "achieved" | "not_achieved" | "partial" | "unknown"
    """
    score_delta = safe_subtract(actual_avg_score, target_avg_score)
    
    T_delta = safe_subtract(actual_T_pct, target_T_pct)
    H_delta = safe_subtract(actual_H_pct, target_H_pct)
    C_delta = safe_subtract(actual_C_pct, target_C_pct)
    
    score_status = "unknown"
    if target_avg_score is not None and actual_avg_score is not None:
        score_status = "achieved" if actual_avg_score >= target_avg_score else "not_achieved"
    
    has_thc_target = any(v is not None for v in [target_T_pct, target_H_pct, target_C_pct])
    has_thc_actual = all(v is not None for v in [actual_T_pct, actual_H_pct, actual_C_pct])
    
    if not has_thc_target:
        thc_status = "unknown"
    elif not has_thc_actual:
        thc_status = "unknown"
    else:
        all_delta = [T_delta, H_delta, C_delta]
        if all(d is not None for d in all_delta):
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
