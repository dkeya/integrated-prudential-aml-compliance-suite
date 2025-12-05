import os, json, time, hashlib, threading
from typing import Dict, Any, List
from pathlib import Path  # <-- fix: was missing

AUDIT_PATH = os.getenv("AML_AUDIT_PATH", "./data/audit_logs.jsonl")
_LOCK = threading.Lock()

def _prev_hash() -> str:
    if not os.path.exists(AUDIT_PATH) or os.path.getsize(AUDIT_PATH) == 0:
        return "0"*64
    with open(AUDIT_PATH, "rb") as f:
        try:
            f.seek(-2048, os.SEEK_END)
        except OSError:
            f.seek(0)
        tail = f.read().decode("utf-8", errors="ignore").splitlines()
    for line in reversed(tail):
        if line.strip():
            try:
                rec = json.loads(line)
                return rec.get("hash", "0"*64)
            except Exception:
                continue
    return "0"*64

def _compute_hash(payload: Dict[str, Any], prev_hash: str) -> str:
    m = hashlib.sha256()
    m.update(prev_hash.encode())
    m.update(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    return m.hexdigest()

def log_action(event: str, user: str, payload: Dict[str, Any]):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec = {"ts": ts, "event": event, "user": user, "payload": payload}
    with _LOCK:
        ph = _prev_hash()
        h = _compute_hash(rec, ph)
        rec["prev_hash"] = ph
        rec["hash"] = h
        os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
        with open(AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def log_page_access(page: str, user: str):
    log_action("page_view", user, {"page": page})

def get_audit_logs(n: int = 200) -> List[Dict[str, Any]]:
    if not os.path.exists(AUDIT_PATH):
        return []
    lines = Path(AUDIT_PATH).read_text(encoding="utf-8").splitlines()[-n:]
    out = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except Exception:
            pass
    return out
