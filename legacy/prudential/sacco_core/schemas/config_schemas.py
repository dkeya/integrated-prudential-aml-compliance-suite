# sacco_core/schemas/config_schemas.py
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class AppConfig(BaseModel):
    title: str = "SACCO Pro"
    environment: str = "development"

class AuthConfig(BaseModel):
    provider: str = "built_in"
    otp_required: bool = False

class RBACConfig(BaseModel):
    roles: List[str] = ["Admin", "Risk", "Collections", "Finance", "Auditor", "Board"]
    page_patterns: Dict[str, List[str]]

class LimitsConfig(BaseModel):
    single_employer_share_max: float = 0.25
    liquidity_ratio_min: float = 0.10
    par30_trigger_max: float = 0.15

class NotificationConfig(BaseModel):
    email: Dict[str, Any]
    sms: Dict[str, Any]

class PolicyEngineConfig(BaseModel):
    schedule_cron: str = "*/15 * * * *"
    actions: List[str] = ["email", "sms", "flag"]

class ECLConfig(BaseModel):
    lookback_months: int = 36
    min_obs_for_pd: int = 12
    lgd_floors: Dict[str, float]
    macro_overlays: bool = True

class DividendConfig(BaseModel):
    max_recommendation: float = 0.07
    par30_gate: float = 0.15
    liquidity_gate: float = 0.10

class DatabaseConfig(BaseModel):
    driver: str = "duckdb"
    path: str = "data/warehouse/sacco.duckdb"

class RootConfig(BaseModel):
    app: AppConfig
    auth: AuthConfig
    rbac: RBACConfig
    limits: LimitsConfig
    notif: NotificationConfig
    policy_engine: PolicyEngineConfig
    ecl: ECLConfig
    dividend: DividendConfig
    database: DatabaseConfig