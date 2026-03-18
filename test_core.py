from app.core.snapshot import get_metric_snapshots
from app.core.compare import compare_metric, safe_subtract
from app.models.domain import MetricSnapshot

def test_core_logic():
    print("Testing safe_subtract...")
    assert safe_subtract(10.0, 5.0) == 5.0
    assert safe_subtract(None, 5.0) is None
    assert safe_subtract(10.0, None) is None
    assert safe_subtract(None, None) is None
    

    print("Testing get_metric_snapshots...")
    snapshots = [
        MetricSnapshot(class_id="c1", metric_id="m1", snapshot_type="baseline", value=6.0, academic_year="2025-2026"),
        MetricSnapshot(class_id="c1", metric_id="m1", snapshot_type="target", value=8.0, academic_year="2025-2026"),
        MetricSnapshot(class_id="c1", metric_id="m1", snapshot_type="actual_hk1", value=7.5, academic_year="2025-2026"),
        MetricSnapshot(class_id="c1", metric_id="m2", snapshot_type="baseline", value=9.0, academic_year="2025-2026") # Should be ignored
    ]
    
    data = get_metric_snapshots(snapshots, "m1")
    assert data["baseline"] == 6.0
    assert data["target"] == 8.0
    assert data["actual_hk1"] == 7.5
    assert data["actual_hk2"] is None
    assert data["commitment"] is None

    print("Testing compare_metric - Standard Case...")
    result1 = compare_metric(data, selected_snapshot="actual_hk1")
    assert result1["actual"] == 7.5
    assert result1["delta_baseline"] == 1.5
    assert result1["delta_target"] == -0.5
    assert result1["trend"] == "increase"
    assert result1["status"] == "not_achieved"
    print(result1)

    print("Testing compare_metric - Missing Actual...")
    data2 = {
        "baseline": 6.0,
        "target": 8.0,
        "commitment": None,
        "actual_hk1": None,
        "actual_hk2": None
    }
    result2 = compare_metric(data2)
    assert result2["actual"] is None
    assert result2["delta_baseline"] is None
    assert result2["trend"] == "unknown"
    assert result2["status"] == "unknown"
    print(result2)

    print("All core logic tests passed!")

if __name__ == "__main__":
    test_core_logic()
