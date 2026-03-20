import os
from pathlib import Path

def normalize_excel(file_path: str) -> str:
    if file_path.endswith('.xlsx'):
        return file_path
    if not file_path.endswith('.xls'):
        raise ValueError('Unsupported format')
    try:
        from win32com.client import Dispatch  # type: ignore
        excel = Dispatch('Excel.Application')
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(os.path.abspath(file_path))
        new_path = file_path.replace('.xls', '_normalized.xlsx')
        wb.SaveAs(os.path.abspath(new_path), FileFormat=51)
        wb.Close(False)
        excel.Quit()
        return new_path
    except Exception as e:
        raise RuntimeError(f'Failed to normalize Excel: {e}')

def validate_excel_structure(df) -> None:
    if df is None or not hasattr(df, 'shape'):
        raise ValueError('Invalid Excel structure: missing dataframe')
    rows = int(df.shape[0])
    if rows < 10:
        raise ValueError(f'Invalid Excel structure: expected at least 10 rows, got {rows}')

__all__ = ['normalize_excel', 'validate_excel_structure']
