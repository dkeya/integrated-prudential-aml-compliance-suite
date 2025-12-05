# sacco_core/db.py
from __future__ import annotations
from pathlib import Path
import duckdb
import pandas as pd
from typing import Any, Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "aml_database.duckdb"

_CONN: Optional[duckdb.DuckDBPyConnection] = None

def get_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    global _CONN
    if _CONN is not None:
        return _CONN
    _CONN = duckdb.connect(str(DB_PATH), read_only=read_only)
    _CONN.execute("PRAGMA threads=4")
    _CONN.execute("PRAGMA memory_limit='1GB'")
    return _CONN

def init_database() -> None:
    get_connection()

def query(sql: str, params: Optional[Iterable[Any]] = None) -> pd.DataFrame:
    con = get_connection()
    if params is None:
        return con.execute(sql).fetch_df()
    return con.execute(sql, params).fetch_df()

def query_df(sql: str, params: Optional[Iterable[Any]] = None) -> pd.DataFrame:
    return query(sql, params)

def execute(sql: str, params: Optional[Iterable[Any]] = None) -> None:
    con = get_connection()
    if params is None:
        con.execute(sql)
    else:
        con.execute(sql, params)
