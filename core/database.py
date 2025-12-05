"""
Shared database connection utilities.
This example uses SQLite, adjust it to your real DB setup.
"""

from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "sacco_compliance.db"

def get_db_connection():
    """Return a SQLite connection object."""
    conn = sqlite3.connect(DB_PATH)
    return conn
