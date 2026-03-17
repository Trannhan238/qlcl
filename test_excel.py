import pandas as pd
from app.infra.excel_parser import detect_header_row, detect_tables, extract_table, map_to_metric_key

def test_excel_parsing():
    print("Testing map_to_metric_key...")
    assert map_to_metric_key("Môn Toán") == "toan"
    assert map_to_metric_key("Tiếng Việt") == "tieng_viet"
    assert map_to_metric_key("Năng Lực") == "nang_luc"
    assert map_to_metric_key("Random") is None

    print("Testing messy dataframe parsing...")
    data = [
        [None, "SỞ GDĐT TỈNH...", None, None],
        ["BẢNG KẾT QUẢ HỌC TẬP...", None, None, None],
        [None, None, None, None],
        ["STT", "Họ và tên", "Môn Toán", None], # Row 3: Top Header (Merged "Môn Toán" over two cols)
        [None, None, "Mức đạt được", "Điểm KT"], # Row 4: Sub Header
        [1, "Nguyen Van A", "HT", 9.0],          # Row 5: Score table
        [2, "Tran Thi B", "HTT", 10.0],
        [None, None, None, None],
        ["Năng lực", "Phẩm chất", None, None],       # Row 7: Maybe header for second table?
        ["HTT", "HT", None, None],                   # Row 8: Eval table
        ["HT", "CHT", None, None]
    ]
    df = pd.DataFrame(data)
    
    h_idx = detect_header_row(df)
    assert h_idx == 3, f"Expected 3, got {h_idx}"
    
    tables = detect_tables(df)
    print("Detected tables:", tables)
    assert len(tables) == 2, f"Expected 2 tables, found {len(tables)}"
    
    extracted1 = extract_table(df, tables[0])
    print("Extracted Table 1:", extracted1)
    
    # We should have exactly 6 items in table 1 because "muc_dat_duoc" columns (2 per row) are skipped
    assert len(extracted1) == 6
    
    # Check column types
    stt_item = next(x for x in extracted1 if x["metric_name"] == "stt")
    assert stt_item["metric_type"] == "unknown"
    
    diem_kt_item = next(x for x in extracted1 if x["metric_name"] == "mon_toan_diem_kt")
    assert diem_kt_item["metric_type"] == "score"

    extracted2 = extract_table(df, tables[1])
    print("Extracted Table 2:", extracted2)
    # Check evaluation type
    nang_luc_item = next(x for x in extracted2 if "nang_luc" in x["metric_name"])
    assert nang_luc_item["metric_type"] == "evaluation"
    
    print("Excel logic tests passed!")

if __name__ == "__main__":
    test_excel_parsing()
