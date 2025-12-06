# core/database.py
"""
Lightweight DatabaseManager for the unified SACCO app.

- Uses DuckDB by default (file-based, fast analytics)
- Can be extended later to support multiple tenants / external DBs
"""

from pathlib import Path
from typing import Optional, Any, Dict

import duckdb
import pandas as pd


class DatabaseManager:
    """Simple wrapper around DuckDB for the unified SACCO platform."""

    def __init__(self, db_path: Optional[str] = None):
        # Default location: <project_root>/data/warehouse/sacco.duckdb
        project_root = Path(__file__).parent.parent
        default_path = project_root / "data" / "warehouse" / "sacco.duckdb"

        self.db_path = Path(db_path) if db_path else default_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Return a live DuckDB connection (create it if needed)."""
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
        return self._conn

    def execute(self, sql: str, params: Optional[Dict[str, Any]] = None):
        """
        Execute a statement (CREATE TABLE, INSERT, etc.).
        Returns the DuckDB cursor.
        """
        conn = self.get_connection()
        if params:
            return conn.execute(sql, params)
        return conn.execute(sql)

    def query_df(self, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Run a SELECT query and return a pandas DataFrame.
        """
        conn = self.get_connection()
        if params:
            return conn.execute(sql, params).df()
        return conn.execute(sql).df()

    def close(self):
        """Close the connection if open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
