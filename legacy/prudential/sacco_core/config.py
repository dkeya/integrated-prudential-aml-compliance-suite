# sacco_core/config.py
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError
import os

class AppConfig(BaseModel):
    title: str = "SACCO Pro"
    environment: str = "development"

class AuthConfig(BaseModel):
    provider: str = "built_in"
    otp_required: bool = False

class RBACConfig(BaseModel):
    roles: list = ["Admin", "Risk", "Collections", "Finance", "Auditor", "Board"]
    page_patterns: Dict[str, list]

class LimitsConfig(BaseModel):
    single_employer_share_max: float = 0.25
    liquidity_ratio_min: float = 0.10
    par30_trigger_max: float = 0.15
    par30_warning_min: float = 0.08      # ADD THIS LINE
    par30_caution_min: float = 0.05      # ADD THIS LINE

class NotificationConfig(BaseModel):
    email: Dict[str, Any]
    sms: Dict[str, Any]

class PolicyEngineConfig(BaseModel):
    schedule_cron: str = "*/15 * * * *"
    actions: list = ["email", "sms", "flag"]

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

class ConfigManager:
    def __init__(self, config_path: str = "configs/settings.yml"):
        self.config_path = Path(config_path)
        self.config = None
    
    def load_settings(self) -> RootConfig:
        """Load and validate configuration from YAML file"""
        if not self.config_path.exists():
            return self.get_default_config()
        
        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        
        try:
            self.config = RootConfig(**raw_config)
            return self.config
        except ValidationError as e:
            raise ValueError(f"Configuration validation error: {e}")
    
    def get_default_config(self) -> RootConfig:
        """Return default configuration"""
        return RootConfig(
            app=AppConfig(),
            auth=AuthConfig(),
            rbac=RBACConfig(
                page_patterns={
                    "Admin": ["*"],
                    "Risk": ["02*", "03*", "06*", "07*", "09*", "12*", "11A*", "14*"],
                    "Collections": ["13*", "13A*"],
                    "Finance": ["03*", "03A*", "05A*", "14*", "02*", "09*"],
                    "Auditor": ["05*", "05A*", "07*", "09*", "12*", "02*", "03*"],
                    "Board": ["01*", "14*", "05A*", "03A*"]
                }
            ),
            limits=LimitsConfig(),
            notif=NotificationConfig(
                email={"enabled": True, "from": "noreply@sacco.com"},
                sms={"provider": "africas_talking"}
            ),
            policy_engine=PolicyEngineConfig(),
            ecl=ECLConfig(
                lgd_floors={"secured": 0.25, "unsecured": 0.45}
            ),
            dividend=DividendConfig(),
            database=DatabaseConfig()
        )
    
    def save_settings(self, config: RootConfig):
        """Save configuration to YAML file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config.dict(), f, default_flow_style=False)

# Global configuration instance
_config_manager = ConfigManager()
_config_instance = None

def get_config() -> RootConfig:
    """
    Get the application configuration
    
    Returns:
        RootConfig: The application configuration
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = _config_manager.load_settings()
    return _config_instance

def reload_config() -> RootConfig:
    """
    Reload configuration from file
    
    Returns:
        RootConfig: The reloaded application configuration
    """
    global _config_instance
    _config_instance = _config_manager.load_settings()
    return _config_instance

def get_default_config() -> RootConfig:
    """
    Get default configuration
    
    Returns:
        RootConfig: Default configuration
    """
    return _config_manager.get_default_config()

def save_config(config: RootConfig):
    """
    Save configuration to file
    
    Args:
        config: Configuration to save
    """
    _config_manager.save_settings(config)
    global _config_instance
    _config_instance = config