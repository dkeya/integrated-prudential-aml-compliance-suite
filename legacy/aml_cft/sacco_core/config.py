# sacco_core/config.py
from __future__ import annotations
import yaml
from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel, Field
from typing import Any, Union

CONFIG_PATH_DEFAULT = Path("./configs/aml_config.yml")

class FRC(BaseModel):
    str_deadline_days: int = 2
    str_threshold: int = 0
    ctr_threshold_kes: int = 1_900_000
    ctr_reporting_day: str = "friday"
    sanctions_freezing_hours: int = 24
    annual_report_due: str = "01-31"
    record_retention_years: int = 7

class RiskScoring(BaseModel):
    high_risk_threshold: float = 0.7
    medium_risk_threshold: float = 0.4
    weights: dict = Field(default_factory=lambda: {
        "transaction_behavior": 0.40, "pep_status": 0.30,
        "geography": 0.20, "product": 0.10
    })

class Monitoring(BaseModel):
    structuring_unit_kes: int = 150_000
    structuring_window_days: int = 7
    rapid_movement_days: int = 5
    unusual_activity_multiplier: float = 3.0
    odd_hours: list[int] = [0, 1, 2, 3, 4, 23]

class Email(BaseModel):
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    from_address: str | None = None
    use_tls: bool = True
    default_recipients: list[str] = Field(default_factory=list)

class Settings(BaseModel):
    version: str = "1.0"
    frc: FRC = FRC()
    risk_scoring: RiskScoring = RiskScoring()
    monitoring: Monitoring = Monitoring()
    email: Email = Email()

def _ensure_config_path(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        # Minimal default file
        try:
            payload = Settings().model_dump()  # pydantic v2
        except Exception:
            payload = Settings().dict()        # pydantic v1 fallback
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)

@lru_cache(maxsize=1)
def load_aml_config(path: str = str(CONFIG_PATH_DEFAULT)) -> Settings:
    p = Path(path)
    _ensure_config_path(p)
    with open(p, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    # If older file (without email), pydantic fills defaults
    return Settings(**raw)

def get_config() -> Settings:
    return load_aml_config()

def _model_to_dict(obj: Any) -> dict:
    if isinstance(obj, BaseModel):
        try:
            return obj.model_dump()  # pydantic v2
        except Exception:
            return obj.dict()        # pydantic v1
    if isinstance(obj, dict):
        return obj
    # last resort
    return dict(obj)

def save_aml_config(cfg: Union[Settings, dict], path: str = str(CONFIG_PATH_DEFAULT)) -> None:
    """
    Persist configuration to YAML and refresh the cached Settings.
    Accepts either a Settings model or a plain dict (backward compatible).
    """
    p = Path(path)
    _ensure_config_path(p)
    payload = _model_to_dict(cfg)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    load_aml_config.cache_clear()