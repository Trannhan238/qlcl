import pandas as pd
import unicodedata
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

def _normalize_str(s: Any) -> str:
    """Removes accents, strips, and lowercases a string."""
    if pd.isna(s) or not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = s.replace('đ', 'd')
    nfkd = unicodedata.normalize('NFKD', s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def read_raw_excel(file_path: str) -> Dict[str, pd.DataFrame]:
    """Reads all sheets from an Excel file without assuming headers.
    Falls back to ignore_workbook_corruption for VNEDU-style exports.
    """
    try:
        return pd.read_excel(file_path, sheet_name=None, header=None)
    except Exception:
        # VNEDU XLS files are often exported with workbook corruption flags
        return pd.read_excel(
            file_path,
            sheet_name=None,
            header=None,
            engine="xlrd",
            engine_kwargs={"ignore_workbook_corruption": True}
        )

def detect_header_row(df: pd.DataFrame) -> int:
    """Finds the header row based on max non-empty cells or known keywords."""
    max_non_empty = 0
    best_row_idx = 0
    keywords = ["toan", "tieng viet", "htt", "ht", "cht", "mon hoc", "ho va ten"]
    
    for idx, row in df.iterrows():
        non_empty = row.count()
        row_str = " ".join([_normalize_str(x) for x in row if pd.notna(x)])
        
        for kw in keywords:
            if kw in row_str:
                return int(idx)
                
        if non_empty > max_non_empty:
            max_non_empty = non_empty
            best_row_idx = int(idx)
            
    return best_row_idx

def detect_tables(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Detects table blocks ignoring their specific type."""
    header_idx = detect_header_row(df)
    tables = []
    
    in_table = False
    start_row = 0
    
    # Analyze row by row below header
    for idx in range(header_idx + 1, len(df)):
        row = df.iloc[idx]
        is_empty = row.isna().all()
        
        if not is_empty and not in_table:
            in_table = True
            start_row = int(idx)
            
        elif is_empty and in_table:
            tables.append({
                "start_row": start_row,
                "end_row": int(idx) - 1,
                "type": "unknown"
            })
            in_table = False

    if in_table:
        tables.append({
            "start_row": start_row,
            "end_row": len(df) - 1,
            "type": "unknown"
        })
        
    # Fallback if no empty rows isolated the tables
    if not tables and len(df) > header_idx + 1:
        tables.append({
            "start_row": header_idx + 1,
            "end_row": len(df) - 1,
            "type": "unknown"
        })
        
    return tables

def extract_table(df: pd.DataFrame, table_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts normalized rows based on table bounds."""
    start_row = table_info["start_row"]
    end_row = table_info["end_row"]
    
    # Check if the first row of the block is a header
    first_row = df.iloc[start_row]
    first_row_str = " ".join([_normalize_str(x) for x in first_row if pd.notna(x)])
    
    # Try to find header directly above or use main sheet header
    header_idx = max(0, start_row - 1)
    if df.iloc[header_idx].isna().all():
        header_idx = detect_header_row(df)
        
    actual_start_row = start_row
    
    # Check if the start of our bound is actually a sub-header (common if first block)
    if actual_start_row <= end_row:
        first_data = df.iloc[actual_start_row].values
        has_numeric = any(isinstance(x, (int, float)) and not pd.isna(x) for x in first_data)
        if not has_numeric:
            actual_start_row += 1
            
    # Gather header rows: the main header, plus any subheaders leading up to actual data
    header_rows = [df.iloc[header_idx].values]
    for r in range(header_idx + 1, actual_start_row):
        header_rows.append(df.iloc[r].values)
        
    # Forward-fill merged cells in the top header row horizontally
    top_header = pd.Series(header_rows[0]).ffill().values
    
    headers = []
    for col_idx in range(len(top_header)):
        parts = []
        if pd.notna(top_header[col_idx]):
            parts.append(str(top_header[col_idx]).strip())
        
        # append any sub header parts
        if len(header_rows) > 1:
            for i in range(1, len(header_rows)):
                if pd.notna(header_rows[i][col_idx]):
                    parts.append(str(header_rows[i][col_idx]).strip())
            
        combined = " ".join(parts) if parts else f"col_{col_idx}"
        
        # Normalize: lowercase, no accents, spaces to underscores
        combined = _normalize_str(combined).replace(" ", "_")
        headers.append(combined)

    extracted = []

    for idx in range(actual_start_row, end_row + 1):
        row = df.iloc[idx].values
        
        for col_idx, cell_value in enumerate(row):
            if pd.notna(cell_value):
                # Resolve metric name
                h_name = headers[col_idx] if col_idx < len(headers) else f"col_{col_idx}"
                metric_name = h_name
                
                val = cell_value
                if isinstance(val, str):
                    val = val.strip()
                    try:
                        val = float(val)
                    except ValueError:
                        pass # Valid for evaluate metrics like HT, CHT
                        
                # 1. Ignore "muc_dat_duoc"
                if "muc_dat_duoc" in metric_name:
                    continue
                    
                # 2 & 3. Column-level classification
                metric_type = "unknown"
                if "diem" in metric_name:
                    metric_type = "score"
                elif str(val).lower() in ["ht", "htt", "cht", "htxs"]:
                    metric_type = "evaluation"
                    
                extracted.append({
                    "metric_name": metric_name,
                    "value": val,
                    "metric_type": metric_type
                })
                
    return extracted

def load_mapping_config() -> dict:
    config_path = Path("config/import_mapping.json")
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def map_to_metric_key(metric_name: str) -> Optional[str]:
    """Maps a raw column name to a standard metric_key using fuzzy matching."""
    mapping = load_mapping_config()
    norm_name = _normalize_str(metric_name)
    
    for key, aliases in mapping.items():
        if norm_name == _normalize_str(key):
            return key
            
        for alias in aliases:
            norm_alias = _normalize_str(alias)
            if norm_alias in norm_name or norm_name in norm_alias:
                return key
                
    return None
