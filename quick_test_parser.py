"""Quick test for parser with flatten header."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))

from app.infra.vnedu_parser import parse_vnedu_file_with_class_summary

# Test với file .xls đầu tiên
test_file = "input/2024-2025/dau nam/so_diem_tong_ket_khoi_khoi_1.xls"
print(f"Testing: {test_file}")

try:
    subjects, summaries = parse_vnedu_file_with_class_summary(test_file, allow_kqgd=True)
    print(f"\nParsed {len(subjects)} subjects, {len(summaries)} class summaries")
    if subjects:
        print("\nFirst subject:")
        for k, v in subjects[0].items():
            print(f"  {k}: {v}")
    if summaries:
        print("\nFirst summary:")
        for k, v in summaries[0].items():
            print(f"  {k}: {v}")
except Exception as e:
    import traceback
    traceback.print_exc()
