import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sacco_core.db import get_connection, init_database

if __name__ == "__main__":
    con = get_connection()
    init_database(con)
    con.close()
    print("✅ DuckDB schema ready at", os.getenv("AML_DB_PATH","./data/aml_database.duckdb"))
