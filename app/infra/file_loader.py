"""
File loader utilities: load Excel files với .xls conversion.

Responsibilities:
- Detect file format
- Convert .xls → .xlsx nếu cần (win32com)
- Read với pandas (openpyxl)
"""

import os
import tempfile
from pathlib import Path
from typing import Union, Dict, Optional, Any

import pandas as pd


def load_excel(
    file_path: Union[str, Path],
    sheet_name: Optional[Union[int, str, None]] = 0,
    **kwargs: Any
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Load Excel file, tự động convert .xls → .xlsx nếu cần.

    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name/index (int/str), hoặc None để đọc tất cả sheets
        **kwargs: Additional args cho pd.read_excel

    Returns:
        - DataFrame nếu sheet_name là int/str
        - Dict[sheet_name, DataFrame] nếu sheet_name=None
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Xác định engine mặc định
    default_engine = "openpyxl" if path.suffix.lower() == ".xlsx" else "xlrd"
    engine = kwargs.pop("engine", default_engine)

    # Case 1: .xlsx
    if path.suffix.lower() == ".xlsx":
        try:
            return pd.read_excel(str(path), sheet_name=sheet_name, header=None, engine=engine, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to read .xlsx file: {e}")

    # Case 2: .xls
    if path.suffix.lower() == ".xls":
        try:
            # Thử xlrd trước
            return pd.read_excel(str(path), sheet_name=sheet_name, header=None, engine="xlrd", **kwargs)
        except Exception:
            # Convert sang .xlsx
            xlsx_path = _convert_xls_to_xlsx(str(path))
            try:
                return pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None, engine="openpyxl", **kwargs)
            finally:
                if os.path.exists(xlsx_path):
                    os.remove(xlsx_path)

    raise ValueError(f"Unsupported file format: {path.suffix}. Only .xls and .xlsx are supported.")


def _convert_xls_to_xlsx(xls_path: str) -> str:
    """
    Convert .xls → .xlsx bằng win32com (Excel COM automation).

    Args:
        xls_path: Path to .xls file

    Returns:
        Path to temporary .xlsx file

    Raises:
        RuntimeError: Nếu conversion fail
    """
    try:
        from win32com.client import Dispatch  # type: ignore
        import pythoncom  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "win32com is required to convert .xls files. "
            "Install with: pip install pywin32"
        ) from e

    # Tạo temp file với suffix .xlsx
    temp_fd, temp_path = tempfile.mkstemp(suffix=".xlsx", prefix="vnedu_converted_")
    os.close(temp_fd)  # Close file descriptor, we'll use the path

    pythoncom.CoInitialize()
    try:
        excel = Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(os.path.abspath(xls_path))
        wb.SaveAs(os.path.abspath(temp_path), FileFormat=51)  # 51 = xlOpenXMLWorkbook (.xlsx)
        wb.Close(False)
        excel.Quit()
        return temp_path
    except Exception as e:
        # Cleanup nếu fail
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise RuntimeError(f"Failed to convert .xls to .xlsx: {e}")
    finally:
        pythoncom.CoUninitialize()


def normalize_excel(file_path: str) -> str:
    """
    DEPRECATED: Giữ lại để tương thích với code cũ.
    Use load_excel() instead.
    """
    return file_path
