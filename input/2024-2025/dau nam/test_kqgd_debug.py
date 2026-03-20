import os
import pandas as pd

FILE_PATH = "so_diem_tong_ket_khoi_khoi_4.xls"


# =============================
# 1. TRY READ XLS
# =============================
def read_file(path):
    try:
        df = pd.read_excel(path, header=None, engine="xlrd")
        print("✅ Read .xls OK")
        return df
    except Exception as e:
        print("❌ xlrd FAIL:", e)

        print("👉 Convert via Excel COM...")
        try:
            import win32com.client

            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            wb = excel.Workbooks.Open(os.path.abspath(path))

            new_path = path.replace(".xls", "_converted.xlsx")
            wb.SaveAs(os.path.abspath(new_path), FileFormat=51)

            wb.Close(False)
            excel.Quit()

            print("🔥 Converted:", new_path)

            df = pd.read_excel(new_path, header=None, engine="openpyxl")
            print("✅ Read converted .xlsx OK")
            return df

        except Exception as e2:
            print("💣 Convert FAIL:", e2)
            return None


# =============================
# 2. FIND KQGD COLUMNS (KEYWORD BASED)
# =============================
def find_kqgd_columns(df):
    def norm(x):
        return str(x).lower() if isinstance(x, str) else ""

    cols = {}

    for i in range(min(30, len(df))):
        row = df.iloc[i]

        for j, cell in enumerate(row):
            s = norm(cell)

            if "hoàn thành xuất sắc" in s or "xuat sac" in s:
                cols["HTXS"] = j

            elif "hoàn thành tốt" in s or ("tot" in s and "hoan thanh" in s):
                cols["HTT"] = j

            elif "chưa hoàn thành" in s:
                cols["CHT"] = j

            elif "hoàn thành" in s and "tot" not in s:
                cols["HT"] = j

    return cols


# =============================
# 3. DETECT STUDENT ROW
# =============================
def is_student_row(val):
    if pd.isna(val):
        return False
    return str(val).strip().isdigit()


# =============================
# 4. TICK DETECT
# =============================
def is_tick(val):
    if val is None:
        return False

    if isinstance(val, str):
        s = val.strip()
        return s in {"✓", "✔", "ü", "þ", "x", "X", "1","\uf0fc"}

    if isinstance(val, (int, float)):
        return val == 1

    return False


# =============================
# 5. DEBUG + COUNT
# =============================
def debug_and_count(df, cols):
    print("\n===== KQGD COLS =====")
    print(cols)

    if len(cols) < 4:
        print("💣 Không detect đủ cột KQGD")
        return

    print("\n===== SAMPLE DATA =====")

    sample_count = 0

    HTXS = HTT = HT = CHT = total = 0

    for i in range(len(df)):
        row = df.iloc[i]
        first = row[0] if len(row) > 0 else None

        if not is_student_row(first):
            continue

        total += 1

        data = {}
        for k, c in cols.items():
            if c < len(row):
                data[k] = repr(row[c])

        if sample_count < 5:
            print(f"ROW {i}: {data}")
            sample_count += 1

        counted = False

        if is_tick(row[cols["HTXS"]]):
            HTXS += 1
            counted = True
        elif is_tick(row[cols["HTT"]]):
            HTT += 1
            counted = True
        elif is_tick(row[cols["HT"]]):
            HT += 1
            counted = True
        elif is_tick(row[cols["CHT"]]):
            CHT += 1

    print("\n===== RESULT =====")
    print("TOTAL:", total)
    print("HTXS:", HTXS)
    print("HTT :", HTT)
    print("HT  :", HT)
    print("CHT :", CHT)
    print("SUM :", HTXS + HTT + HT + CHT)


# =============================
# MAIN
# =============================
if __name__ == "__main__":
    df = read_file(FILE_PATH)

    if df is None:
        exit()

    print("\n===== SHAPE =====")
    print(df.shape)

    cols = find_kqgd_columns(df)

    debug_and_count(df, cols)