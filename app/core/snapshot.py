from typing import List, Dict, Optional
from app.models.domain import MetricSnapshot

def get_metric_snapshots(snapshots: List[MetricSnapshot], metric_id: str) -> Dict[str, Optional[float]]:
    """
    Filters snapshots for a specific metric and arranges them by snapshot_type.
    """
    result = {
        "baseline": None,
        "commitment": None,
        "target": None,
        "actual_hk1": None,
        "actual_hk2": None
    }
    
    for snapshot in snapshots:
        if snapshot.metric_id == metric_id and snapshot.snapshot_type in result:
            result[snapshot.snapshot_type] = snapshot.value
            
    return result
