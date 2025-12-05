from typing import List, Dict

AML_ROLES = {
    "AML_Officer": ["read","triage","file_drafts"],
    "Compliance_Manager": ["read","triage","approve","file"],
    "MLRO": ["read","approve","file","override","admin"],
    "Auditor": ["read","export"],
    "Staff": ["read_limited"]
}

_CURRENT_USER = {"name":"Demo User","roles":["AML_Officer"]}

def get_user_roles() -> List[str]:
    return _CURRENT_USER["roles"]

def enforce_role(allowed: List[str]) -> None:
    roles = set(get_user_roles())
    if not roles.intersection(set(allowed)):
        raise PermissionError("RBAC: insufficient privileges")

def set_demo_user(name: str, roles: List[str]):
    global _CURRENT_USER
    _CURRENT_USER = {"name": name, "roles": roles}
    return _CURRENT_USER
