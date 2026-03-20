"""
Mô tả file:
- Vai trò: Test unit cho module compare.py - kiểm tra logic so sánh
- Input: Các test cases định nghĩa sẵn
- Output: Kết quả test pass/fail
- Phụ thuộc: app.core.compare
"""

from app.core.compare import compare_metric, safe_subtract


def test_core_logic():
    """Test các hàm trong compare.py."""
    print("Testing safe_subtract...")
    assert safe_subtract(10.0, 5.0) == 5.0
    assert safe_subtract(None, 5.0) is None
    assert safe_subtract(10.0, None) is None
    assert safe_subtract(None, None) is None

    print("Testing compare_metric - Standard Case...")
    data = {
        "baseline": 6.0,
        "target": 8.0,
        "commitment": None,
        "actual_hk1": 7.5,
        "actual_hk2": None
    }
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
