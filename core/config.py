# core/config.py
from dataclasses import dataclass

@dataclass
class LimitsConfig:
    # Prudential limits used in 01_Overview.py
    par30_trigger_max: float = 0.05   # 5% SASRA threshold
    par30_warning_min: float = 0.04   # 4% internal warning

@dataclass
class AppConfig:
    limits: LimitsConfig

class ConfigManager:
    """Simple config manager for the unified SACCO app."""

    def load_settings(self) -> AppConfig:
        # Later, you can load from YAML/DB; for now we return defaults
        return AppConfig(limits=LimitsConfig())

    def get_default_config(self) -> AppConfig:
        # Fallback used in app.py if loading fails
        return AppConfig(limits=LimitsConfig())
