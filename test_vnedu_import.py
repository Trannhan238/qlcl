"""
Mô tả file:
- Vai trò: Validation script - kiểm tra parser với các file trong input/
- Input: File Excel trong thư mục input/
- Output: Kết quả validation cho từng file
- Phụ thuộc: app.infra.vnedu_parser

Chú ý:
- File sử dụng key "class_name" thay vì "class"
- Mỗi result cần có: subject, avg_score, T, H, C
"""

import sys
import io
from pathlib import Path

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app.infra.vnedu_parser import parse_vnedu_file  # noqa: E402

INPUT_DIR = Path("input")


def validate_result(result: dict) -> list:
    """
    Mô tả:
        Validate một kết quả parse - kiểm tra các rule violations.

    Rules:
        1. avg_score phải là float hoặc None
        2. avg_score phải trong range [0, 10]
        3. Phải có ít nhất 1 trong 4: avg_score, T, H, C

    Input:
        result (dict): Kết quả từ parser

    Output:
        (list): Danh sách warning strings
    """
    warnings = []
    score = result.get("avg_score")
    T, H, C = result.get("T", 0), result.get("H", 0), result.get("C", 0)

    # Rule 1: avg_score phải là float
    if score is not None and not isinstance(score, float):
        warnings.append(f"avg_score is not float: {score!r}")

    # Rule 2: avg_score range
    if score is not None and (score < 0 or score > 10):
        warnings.append(f"avg_score out of range [0,10]: {score}")

    # Rule 3: phải có data
    if T + H + C == 0 and score is None:
        warnings.append("No data at all for this subject")

    return warnings


def run():
    """
    Mô tả:
        Run validation trên tất cả file Excel trong input/.
    """
    files = sorted(INPUT_DIR.glob("*.xls")) + sorted(INPUT_DIR.glob("*.xlsx"))
    if not files:
        print("[ERROR] No .xls or .xlsx files found in input/")
        return

    grand_total = 0

    for file_path in files:
        print(f"\n{'='*60}")
        print(f"FILE: {file_path.name}")
        print(f"{'='*60}")

        try:
            results = parse_vnedu_file(str(file_path))
        except Exception as e:
            print(f"[ERROR] Failed to parse {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

        if not results:
            print("[!] No results extracted.")
            continue

        grand_total += len(results)
        print(f"[*] Extracted {len(results)} subject entries\n")

        any_warnings = False
        for r in results:
            warns = validate_result(r)
            flag = " [WARN]" if warns else ""
            print(
                f"  Class: {r['class_name']:<8} | Subject: {r['subject']:<20} | "
                f"AvgScore: {str(r['avg_score']):<6} | T={r['T']:>3}  H={r['H']:>3}  C={r['C']:>3}{flag}"
            )
            for w in warns:
                print(f"    ⚠ {w}")
                any_warnings = True

        if not any_warnings:
            print("\n  [OK] All validation rules passed.")

    print(f"\n{'='*60}")
    print(f"[*] TOTAL entries across all files: {grand_total}")
    print(f"{'='*60}")


if __name__ == "__main__":
    run()
