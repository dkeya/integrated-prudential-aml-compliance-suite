import uuid

def format_currency(x: float) -> str:
    return f"KES {x:,.0f}"

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def validate_data(df, required_cols: list[str]) -> list[str]:
    missing = [c for c in required_cols if c not in df.columns]
    return missing
