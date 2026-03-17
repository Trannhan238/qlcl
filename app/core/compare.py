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

def choose_actual(data: Dict[str, Optional[float]]) -> Optional[float]:
    """Prefers actual_hk2. Falls back to actual_hk1."""
    if not is_missing(data.get("actual_hk2")):
        return data["actual_hk2"]
    return data.get("actual_hk1")

def compare_metric(data: Dict[str, Optional[float]]) -> Dict[str, Any]:
    """
    Compares the actual metrics against baselines, targets, and commitments.
    If no actual score is available (subject has no score column or NaN),
    returns trend='unknown' and status='unknown' immediately.
    """
    actual = choose_actual(data)

    # If no actual score available, short-circuit — no score comparison possible
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
