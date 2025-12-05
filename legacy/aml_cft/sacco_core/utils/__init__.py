# sacco_core/utils/__init__.py
from __future__ import annotations
from time import time
from typing import Iterable, List, Optional
import pandas as pd

# Re-export the export helpers so `sacco_core.utils.export` works,
# and (optionally) callers can also do `from sacco_core.utils import df_to_csv_bytes`
from .export import df_to_csv_bytes, df_to_xlsx_bytes, export_buttons

def format_currency(val: Optional[float], currency: str = "KES") -> str:
    """Lightweight pretty currency formatter used around the app."""
    if val is None:
        return "—"
    try:
        return f"{currency} {float(val):,.0f}"
    except Exception:
        return str(val)

def generate_id(prefix: str = "ID") -> str:
    """Simple time-based ID (millisecond precision)."""
    return f"{prefix}{int(time()*1000)}"

def validate_data(df: pd.DataFrame, required_cols: Iterable[str]) -> List[str]:
    """Return missing columns from df (empty list if all present)."""
    cols = set(df.columns.astype(str).str.lower())
    missing = [c for c in required_cols if str(c).lower() not in cols]
    return missing

__all__ = [
    "df_to_csv_bytes", "df_to_xlsx_bytes", "export_buttons",
    "format_currency", "generate_id", "validate_data",
]
