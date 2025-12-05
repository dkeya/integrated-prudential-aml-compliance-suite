# sacco_core/db.py
import duckdb
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Any, Dict
import logging

class DatabaseManager:
    def __init__(self, config_path: str = "configs/settings.yml"):
        self.config_path = Path(config_path)
        self.connection = None
        self.driver = "duckdb"
        self.db_path = "data/warehouse/sacco.duckdb"
        
    def connect(self) -> Any:
        """Establish database connection"""
        try:
            if self.driver == "duckdb":
                # Ensure directory exists
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
                self.connection = duckdb.connect(self.db_path)
            elif self.driver == "sqlite":
                self.connection = sqlite3.connect(self.db_path)
            else:
                # PostgreSQL connection would go here
                pass
            
            self._initialize_tables()
            return self.connection
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise
    
    def _initialize_tables(self):
        """Initialize database tables"""
        if self.driver == "duckdb":
            self._init_duckdb_tables()
    
    def _init_duckdb_tables(self):
        """Initialize DuckDB tables"""
        # Loan states monthly table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS loan_states_monthly (
                loan_id VARCHAR,
                member_id VARCHAR,
                employer_id VARCHAR,
                product VARCHAR,
                origination_date DATE,
                month_end DATE,
                state VARCHAR,
                os_principal DECIMAL(15,2),
                days_past_due INTEGER,
                recoveries_cash DECIMAL(15,2),
                interest_accrued DECIMAL(15,2),
                charge_off_flag INTEGER,
                cure_flag INTEGER,
                PRIMARY KEY (loan_id, month_end)
            )
        """)
        
        # Members table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id VARCHAR PRIMARY KEY,
                join_date DATE,
                deposits_balance DECIMAL(15,2),
                shares_balance DECIMAL(15,2),
                channel VARCHAR,
                employer_id VARCHAR,
                phone VARCHAR,
                email VARCHAR
            )
        """)
        
        # Audit log table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP,
                user VARCHAR,
                role VARCHAR,
                action VARCHAR,
                object_type VARCHAR,
                object_id VARCHAR,
                payload_hash VARCHAR,
                ip VARCHAR,
                user_agent VARCHAR
            )
        """)
        
        # PTP promises table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS ptp_promises (
                promise_id VARCHAR PRIMARY KEY,
                loan_id VARCHAR,
                member_id VARCHAR,
                promised_date DATE,
                promised_amount DECIMAL(15,2),
                created_by VARCHAR,
                status VARCHAR,
                created_at TIMESTAMP
            )
        """)
    
    def load_csv_to_table(self, csv_path: str, table_name: str):
        """Load CSV data into table"""
        try:
            df = pd.read_csv(csv_path)
            self.connection.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.connection.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
            return True
        except Exception as e:
            logging.error(f"Failed to load {csv_path}: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        if params:
            return self.connection.execute(query, params).df()
        else:
            return self.connection.execute(query).df()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()