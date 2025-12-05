"""
Audit and logging utilities for SACCO Compliance System.
"""

import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "app.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

audit_logger = logging.getLogger("sacco_compliance")

def log_event(user: str, action: str, module: str, details: dict | None = None):
    audit_logger.info(
        "user=%s | action=%s | module=%s | details=%s",
        user,
        action,
        module,
        details or {},
    )
