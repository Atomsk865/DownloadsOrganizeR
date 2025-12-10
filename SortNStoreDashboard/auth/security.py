"""
Authentication security enforcement - rate limiting, lockout, and audit logging.

Implements:
- Per-IP and per-username failed login throttling
- Automatic lockout after threshold breaches
- Persistent state tracking across restarts
- Comprehensive audit logging with rotation
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from threading import Lock
import os

# Configuration
MAX_FAILED_ATTEMPTS_PER_IP = 5
MAX_FAILED_ATTEMPTS_PER_USER = 5
LOCKOUT_DURATION_SECONDS = 300  # 5 minutes
RATE_LIMIT_WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 10
AUDIT_LOG_MAX_ENTRIES = 10000
AUDIT_LOG_ROTATION_DAYS = 90

# State file paths
_config_dir = Path(__file__).parent.parent.parent / "config" / "json"
_config_dir.mkdir(parents=True, exist_ok=True)
AUTH_STATE_FILE = _config_dir / "auth_state.json"
AUDIT_LOG_FILE = _config_dir / "auth_audit.json"

# In-memory state with thread safety
_state_lock = Lock()
_auth_state: Dict = {
    "ip_failures": {},      # ip -> {"count": int, "first_attempt": timestamp, "locked_until": timestamp}
    "user_failures": {},    # username -> {"count": int, "first_attempt": timestamp, "locked_until": timestamp}
    "rate_limits": {}       # ip -> {"requests": [timestamps]}
}


def _load_state():
    """Load persistent auth state from disk."""
    global _auth_state
    if AUTH_STATE_FILE.exists():
        try:
            with AUTH_STATE_FILE.open('r') as f:
                loaded = json.load(f)
                # Clean expired entries on load
                now = time.time()
                for category in ["ip_failures", "user_failures"]:
                    if category in loaded:
                        loaded[category] = {
                            k: v for k, v in loaded[category].items()
                            if v.get("locked_until", 0) > now or v.get("first_attempt", 0) > now - LOCKOUT_DURATION_SECONDS
                        }
                _auth_state = loaded
        except Exception as e:
            print(f"Warning: Could not load auth state: {e}")


def _save_state():
    """Persist auth state to disk."""
    try:
        with AUTH_STATE_FILE.open('w') as f:
            json.dump(_auth_state, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save auth state: {e}")


def _get_client_ip() -> str:
    """Extract client IP from Flask request context."""
    try:
        from flask import request
        # Check X-Forwarded-For for proxied requests
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return request.remote_addr or "unknown"
    except Exception:
        return "unknown"


def check_rate_limit(ip: str) -> Tuple[bool, Optional[str]]:
    """
    Check if IP is within rate limit.
    
    Returns:
        (allowed: bool, reason: Optional[str])
    """
    with _state_lock:
        now = time.time()
        if ip not in _auth_state["rate_limits"]:
            _auth_state["rate_limits"][ip] = {"requests": []}
        
        # Clean old requests outside window
        requests = _auth_state["rate_limits"][ip]["requests"]
        requests = [ts for ts in requests if ts > now - RATE_LIMIT_WINDOW_SECONDS]
        _auth_state["rate_limits"][ip]["requests"] = requests
        
        if len(requests) >= MAX_REQUESTS_PER_WINDOW:
            return False, f"Rate limit exceeded: {len(requests)} requests in {RATE_LIMIT_WINDOW_SECONDS}s"
        
        # Record this request
        requests.append(now)
        return True, None


def is_ip_locked(ip: str) -> Tuple[bool, Optional[int]]:
    """
    Check if IP is currently locked out.
    
    Returns:
        (locked: bool, seconds_remaining: Optional[int])
    """
    with _state_lock:
        if ip not in _auth_state["ip_failures"]:
            return False, None
        
        entry = _auth_state["ip_failures"][ip]
        locked_until = entry.get("locked_until", 0)
        
        if locked_until > time.time():
            remaining = int(locked_until - time.time())
            return True, remaining
        
        # Expired lockout - clean up
        if locked_until > 0:
            del _auth_state["ip_failures"][ip]
            _save_state()
        
        return False, None


def is_user_locked(username: str) -> Tuple[bool, Optional[int]]:
    """
    Check if username is currently locked out.
    
    Returns:
        (locked: bool, seconds_remaining: Optional[int])
    """
    with _state_lock:
        if username not in _auth_state["user_failures"]:
            return False, None
        
        entry = _auth_state["user_failures"][username]
        locked_until = entry.get("locked_until", 0)
        
        if locked_until > time.time():
            remaining = int(locked_until - time.time())
            return True, remaining
        
        # Expired lockout - clean up
        if locked_until > 0:
            del _auth_state["user_failures"][username]
            _save_state()
        
        return False, None


def record_failed_login(username: str, ip: str, reason: str = "invalid_credentials"):
    """
    Record a failed login attempt and apply lockout if threshold exceeded.
    
    Args:
        username: Username that failed authentication
        ip: Client IP address
        reason: Failure reason (e.g., "invalid_credentials", "rate_limited")
    """
    with _state_lock:
        now = time.time()
        
        # Track IP failures
        if ip not in _auth_state["ip_failures"]:
            _auth_state["ip_failures"][ip] = {
                "count": 0,
                "first_attempt": now,
                "locked_until": 0
            }
        
        ip_entry = _auth_state["ip_failures"][ip]
        ip_entry["count"] += 1
        
        if ip_entry["count"] >= MAX_FAILED_ATTEMPTS_PER_IP:
            ip_entry["locked_until"] = now + LOCKOUT_DURATION_SECONDS
            audit_log("lockout", username, ip, f"IP locked: {ip_entry['count']} failed attempts")
        
        # Track username failures
        if username not in _auth_state["user_failures"]:
            _auth_state["user_failures"][username] = {
                "count": 0,
                "first_attempt": now,
                "locked_until": 0
            }
        
        user_entry = _auth_state["user_failures"][username]
        user_entry["count"] += 1
        
        if user_entry["count"] >= MAX_FAILED_ATTEMPTS_PER_USER:
            user_entry["locked_until"] = now + LOCKOUT_DURATION_SECONDS
            audit_log("lockout", username, ip, f"User locked: {user_entry['count']} failed attempts")
        
        _save_state()
    
    # Log the failure
    audit_log("failed_login", username, ip, reason)


def record_successful_login(username: str, ip: str):
    """
    Record successful login and reset failure counters.
    
    Args:
        username: Authenticated username
        ip: Client IP address
    """
    with _state_lock:
        # Clear failure counts for this IP and username
        if ip in _auth_state["ip_failures"]:
            del _auth_state["ip_failures"][ip]
        if username in _auth_state["user_failures"]:
            del _auth_state["user_failures"][username]
        _save_state()
    
    audit_log("successful_login", username, ip, "authenticated")


def audit_log(event_type: str, username: str, ip: str, details: str):
    """
    Append structured event to audit log with automatic rotation.
    
    Args:
        event_type: Event category (e.g., "successful_login", "failed_login", "lockout")
        username: Username involved
        ip: Client IP
        details: Additional context
    """
    try:
        # Load existing log
        events = []
        if AUDIT_LOG_FILE.exists():
            try:
                with AUDIT_LOG_FILE.open('r') as f:
                    data = json.load(f)
                    events = data.get("events", [])
            except Exception:
                events = []
        
        # Add new event
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "username": username,
            "ip": ip,
            "details": details
        }
        events.append(event)
        
        # Rotate old entries
        cutoff_date = datetime.utcnow() - timedelta(days=AUDIT_LOG_ROTATION_DAYS)
        events = [
            e for e in events
            if datetime.fromisoformat(e["timestamp"].replace("Z", "")) > cutoff_date
        ]
        
        # Enforce max entries
        if len(events) > AUDIT_LOG_MAX_ENTRIES:
            events = events[-AUDIT_LOG_MAX_ENTRIES:]
        
        # Save
        with AUDIT_LOG_FILE.open('w') as f:
            json.dump({"events": events}, f, indent=2)
    
    except Exception as e:
        print(f"Warning: Could not write to audit log: {e}")


def get_audit_log(limit: int = 100, event_type: Optional[str] = None) -> List[Dict]:
    """
    Retrieve recent audit log entries.
    
    Args:
        limit: Maximum number of entries to return
        event_type: Optional filter by event type
    
    Returns:
        List of audit log events (most recent first)
    """
    try:
        if not AUDIT_LOG_FILE.exists():
            return []
        
        with AUDIT_LOG_FILE.open('r') as f:
            data = json.load(f)
            events = data.get("events", [])
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]
        
        # Return most recent first
        return list(reversed(events[-limit:]))
    
    except Exception as e:
        print(f"Warning: Could not read audit log: {e}")
        return []


def reset_lockout(identifier: str, identifier_type: str = "username"):
    """
    Manually reset lockout for a user or IP (admin override).
    
    Args:
        identifier: Username or IP to unlock
        identifier_type: "username" or "ip"
    """
    with _state_lock:
        if identifier_type == "username" and identifier in _auth_state["user_failures"]:
            del _auth_state["user_failures"][identifier]
            audit_log("lockout_reset", identifier, "admin", "Manual unlock by administrator")
        elif identifier_type == "ip" and identifier in _auth_state["ip_failures"]:
            del _auth_state["ip_failures"][identifier]
            audit_log("lockout_reset", "N/A", identifier, "Manual IP unlock by administrator")
        _save_state()


def get_lockout_status() -> Dict:
    """
    Get current lockout status for monitoring.
    
    Returns:
        Dictionary with locked IPs and usernames
    """
    with _state_lock:
        now = time.time()
        locked_ips = {
            ip: {"locked_until": entry["locked_until"], "attempts": entry["count"]}
            for ip, entry in _auth_state["ip_failures"].items()
            if entry.get("locked_until", 0) > now
        }
        locked_users = {
            user: {"locked_until": entry["locked_until"], "attempts": entry["count"]}
            for user, entry in _auth_state["user_failures"].items()
            if entry.get("locked_until", 0) > now
        }
        return {
            "locked_ips": locked_ips,
            "locked_users": locked_users,
            "timestamp": now
        }


# Initialize on module load
_load_state()
