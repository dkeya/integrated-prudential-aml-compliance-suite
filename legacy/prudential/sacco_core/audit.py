# sacco_core/audit.py
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st

class AuditLogger:
    def __init__(self, log_dir: str = "data/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _hash_pii(self, data: str) -> str:
        """Hash PII data for privacy"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _redact_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Redact PII from audit payload"""
        redacted = payload.copy()
        
        # Fields that might contain PII
        pii_fields = ['email', 'phone', 'first_name', 'last_name', 'national_id', 
                     'address', 'password', 'token']
        
        for field in pii_fields:
            if field in redacted:
                redacted[field] = self._hash_pii(str(redacted[field]))
        
        return redacted
    
    def log_action(self, user: str, role: str, action: str, object_type: str, 
                  object_id: Optional[str] = None, payload: Optional[Dict] = None,
                  ip: str = "127.0.0.1", user_agent: str = "streamlit"):
        """Log an auditable action"""
        timestamp = datetime.utcnow().isoformat()
        
        # Redact PII from payload
        safe_payload = self._redact_payload(payload) if payload else {}
        payload_hash = hashlib.sha256(
            json.dumps(safe_payload, sort_keys=True).encode()
        ).hexdigest()
        
        log_entry = {
            "timestamp": timestamp,
            "user": user,
            "role": role,
            "action": action,
            "object_type": object_type,
            "object_id": object_id,
            "payload_hash": payload_hash,
            "ip": ip,
            "user_agent": user_agent
        }
        
        # Write to JSONL file
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Also write to database if available
        self._log_to_database(log_entry)
    
    def _log_to_database(self, log_entry: Dict[str, Any]):
        """Log to database table"""
        try:
            # This would be implemented with the database manager
            pass
        except Exception as e:
            # Fallback to file logging only
            pass
    
    def log_login(self, user: str, role: str):
        """Log user login"""
        self.log_action(user, role, "login", "system")
    
    def log_logout(self, user: str, role: str):
        """Log user logout"""
        self.log_action(user, role, "logout", "system")
    
    def log_data_access(self, user: str, role: str, dataset: str, filters: Dict = None):
        """Log data access"""
        self.log_action(user, role, "data_access", dataset, payload=filters)
    
    def log_config_change(self, user: str, role: str, config_section: str, changes: Dict):
        """Log configuration changes"""
        self.log_action(user, role, "config_update", config_section, payload=changes)
    
    # ADD THIS METHOD TO FIX THE ERROR
    def log_event(self, user: str, action: str, module: str, details: Dict = None):
        """Log a custom event - added to fix enhanced pages"""
        payload = {
            "module": module,
            "action": action,
            "details": details or {}
        }
        self.log_action(user, "system", action, module, payload=payload)

# Create a global instance for easy access
_audit_logger = AuditLogger()

# Standalone function for easy importing
def audit_log(action: str, description: str, payload: Optional[Dict] = None):
    """
    Standalone audit logging function for easy use in pages
    
    Args:
        action: The action being performed (e.g., 'login', 'data_view', 'export')
        description: Human-readable description of the action
        payload: Additional data to log
    """
    try:
        # Get current user from session state
        user = st.session_state.get('username', 'unknown')
        role = st.session_state.get('role', 'unknown')
        
        _audit_logger.log_action(
            user=user,
            role=role,
            action=action,
            object_type="system",
            payload={
                "description": description,
                "details": payload or {}
            }
        )
    except Exception as e:
        # Silent fail for audit logging - don't break the app
        pass

# Convenience functions for common actions
def audit_login(username: str, role: str):
    """Log user login"""
    _audit_logger.log_login(username, role)

def audit_logout(username: str, role: str):
    """Log user logout"""
    _audit_logger.log_logout(username, role)

def audit_data_access(dataset: str, filters: Dict = None):
    """Log data access"""
    try:
        user = st.session_state.get('username', 'unknown')
        role = st.session_state.get('role', 'unknown')
        _audit_logger.log_data_access(user, role, dataset, filters)
    except Exception:
        pass

def audit_config_change(config_section: str, changes: Dict):
    """Log configuration changes"""
    try:
        user = st.session_state.get('username', 'unknown')
        role = st.session_state.get('role', 'unknown')
        _audit_logger.log_config_change(user, role, config_section, changes)
    except Exception:
        pass