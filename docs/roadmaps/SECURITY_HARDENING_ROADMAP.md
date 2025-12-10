# Security Hardening Roadmap for Dashboard

**Quick Reference for Implementation Priority**

## Critical Security Gaps (MUST DO - This Week)

### 1. OWASP Security Headers Middleware

**Why:** Prevents common attacks (clickjacking, MIME sniffing, XSS)

**File to Modify:** `SortNStoreDashboard.py`

**Code to Add:**
```python
# Add after app = Flask(__name__) initialization (around line 200):

@app.after_request
def set_security_headers(response):
    """Set security-related HTTP headers."""
    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable browser XSS filtering
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy - strict mode
    csp = (
        "default-src 'self'; "
        "script-src 'self' cdn.jsdelivr.net; "
        "style-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "upgrade-insecure-requests"
    )
    response.headers['Content-Security-Policy'] = csp
    
    # Force HTTPS in production
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Restrict browser features
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Disable unused APIs
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), '
        'payment=(), usb=(), magnetometer=(), '
        'gyroscope=(), accelerometer=()'
    )
    
    return response
```

**Testing:**
```bash
# Check headers with curl:
curl -i http://localhost:5000 | grep -E "X-Frame|X-Content|CSP|HSTS"

# Or use online: https://securityheaders.com (for production)
```

**Impact:** 🔴 CRITICAL - Blocks most common web attacks

---

### 2. Content Security Policy (CSP) Validation

**Note:** Already configured in headers above, but validate in templates

**File to Check:** `dash/dashboard_base.html`

**Required for CSP Compliance:**
- ✅ No inline `<script>` tags (all in separate files)
- ✅ No `javascript:` URLs in onclick handlers
- ✅ No `eval()` in JavaScript
- ✅ External scripts only from `cdn.jsdelivr.net`

**Check for Violations:**
```bash
# Search for inline scripts that would violate CSP:
grep -n "onclick=" dash/*.html
grep -n "<script>" dash/*.html | grep -v src=
grep -n "eval(" dash/dashboard_scripts.html
grep -n "javascript:" dash/*.html
```

**If Found, Refactor to:**
```html
<!-- ❌ WRONG (violates CSP) -->
<button onclick="deleteItem()">Delete</button>

<!-- ✅ CORRECT (use event listeners) -->
<button id="delete-btn">Delete</button>
<script>
document.getElementById('delete-btn').addEventListener('click', deleteItem);
</script>
```

**Impact:** 🔴 CRITICAL - Prevents inline code injection

---

### 3. Rate Limiting (Brute Force Protection)

**Why:** Prevents credential stuffing and DoS attacks

**Dependencies:** Add to `requirements.txt`:
```
flask-limiter>=4.0,<5
```

**File to Modify:** `SortNStoreDashboard.py`

**Code to Add:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize limiter (after creating Flask app, around line 220):
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use Redis for multi-server: "redis://localhost:6379"
)

# Apply to sensitive endpoints in your route blueprints:

# In SortNStoreDashboard/routes/login.py:
@routes_login.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Strict: brute force protection
def login():
    # ... existing code ...

# In SortNStoreDashboard/routes/organizer_control.py:
@routes_organizer_control.route('/api/organizer/enable', methods=['POST'])
@limiter.limit("30 per minute")  # Moderate: API operations
def enable_organizer():
    # ... existing code ...

# Apply globally to all API endpoints:
@app.before_request
def apply_api_limits():
    if request.path.startswith('/api/'):
        # API calls: 100 per minute per IP
        limiter.limit("100 per minute")(lambda: None)
```

**Testing:**
```bash
# Test rate limiting:
for i in {1..10}; do curl -X POST http://localhost:5000/login -d "user=test"; done
# After 5 requests, should receive 429 (Too Many Requests)
```

**Impact:** 🟠 HIGH - Stops brute force attacks

---

### 4. Error Handling & Info Leakage Prevention

**Why:** Don't expose internal errors, paths, or versions to attackers

**File to Modify:** `SortNStoreDashboard.py`

**Code to Add:**
```python
# Add error handlers (after app initialization):

@app.errorhandler(400)
def bad_request(error):
    app.logger.warning(f"Bad request: {request.path} from {request.remote_addr}")
    return jsonify({'error': 'Bad Request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    app.logger.warning(f"Unauthorized access: {request.path} from {request.remote_addr}")
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    app.logger.warning(f"Forbidden access: {request.path} from {request.remote_addr}")
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    # Log full error internally, don't expose to user
    app.logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({'error': 'Internal Server Error'}), 500

# Prevent Flask debug info leakage
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['TRAP_HTTP_EXCEPTIONS'] = True
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# Don't show stack traces in production
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
```

**Remove Debug Info from Templates:**
```html
<!-- ❌ REMOVE these from production -->
<!-- In dash/dashboard_base.html -->
<!-- Check for any debug/console output -->
<!-- Remove any error stack traces in templates -->
```

**Testing:**
```bash
# Should NOT return stack trace:
curl http://localhost:5000/nonexistent
# Should return: {"error": "Not Found"}

curl http://localhost:5000/api/invalid
# Should return: {"error": "Not Found"}
# NOT the full Flask error traceback
```

**Impact:** 🔴 CRITICAL - Prevents information disclosure

---

### 5. Security Event Logging

**Why:** Audit trail for incidents and compliance

**File to Create:** `SortNStoreDashboard/security_logger.py`

**Code:**
```python
"""Security event logging for audit trail."""

import logging
import os
from pathlib import Path

# Ensure logs directory exists
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# Create security logger
security_logger = logging.getLogger('sortnstore.security')
security_logger.setLevel(logging.INFO)

# File handler (persistent storage)
handler = logging.FileHandler(log_dir / 'security.log')
handler.setLevel(logging.INFO)

# Format with timestamp, level, and details
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
security_logger.addHandler(handler)

def log_auth_event(event_type, username, ip_address, success, details=None):
    """Log authentication events."""
    status = "SUCCESS" if success else "FAILURE"
    msg = f"AUTH_{event_type} | User: {username} | IP: {ip_address} | {status}"
    if details:
        msg += f" | Details: {details}"
    security_logger.info(msg)

def log_config_change(username, ip_address, change_type, old_value, new_value):
    """Log configuration changes."""
    msg = f"CONFIG_CHANGE | User: {username} | IP: {ip_address} | " \
          f"Type: {change_type} | Old: {old_value} | New: {new_value}"
    security_logger.info(msg)

def log_access_denial(username, ip_address, resource, reason):
    """Log access denial events."""
    msg = f"ACCESS_DENIED | User: {username} | IP: {ip_address} | " \
          f"Resource: {resource} | Reason: {reason}"
    security_logger.warning(msg)

def log_suspicious_activity(ip_address, activity_type, details):
    """Log suspicious activity for review."""
    msg = f"SUSPICIOUS_ACTIVITY | IP: {ip_address} | " \
          f"Type: {activity_type} | Details: {details}"
    security_logger.warning(msg)
```

**Usage in auth.py:**
```python
from SortNStoreDashboard.security_logger import log_auth_event, log_access_denial

# On successful login:
log_auth_event('LOGIN', username, request.remote_addr, True)

# On failed login:
log_auth_event('LOGIN', username, request.remote_addr, False, 'Invalid credentials')

# On access denial:
log_access_denial(current_user.username, request.remote_addr, 
                  request.path, 'Insufficient permissions')
```

**Testing:**
```bash
# Check logs are created:
tail -f logs/security.log

# Should show:
# 2025-12-10 15:30:45 - INFO - AUTH_LOGIN | User: admin | IP: 127.0.0.1 | SUCCESS
# 2025-12-10 15:31:20 - INFO - CONFIG_CHANGE | User: admin | IP: 127.0.0.1 | Type: routes | Old: {...} | New: {...}
```

**Impact:** 🟠 HIGH - Enables incident investigation

---

## High Priority (Do Next Week)

### 6. HTTPS Enforcement

**Production Requirement:** All traffic must be HTTPS

**File:** `SortNStoreDashboard.py`

```python
@app.before_request
def enforce_https():
    """Force HTTPS in production."""
    if os.environ.get('FLASK_ENV') == 'production':
        if not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
```

**Configuration:**
```bash
# Set in deployment environment:
export FLASK_ENV=production
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Use gunicorn with SSL in production:
gunicorn --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:443 SortNStoreDashboard:app
```

**Impact:** 🔴 CRITICAL for production

---

### 7. Secure Cookie Configuration

**Already Implemented:** Check in `SortNStoreDashboard.py`

**Verify These Settings Exist:**
```python
# Session cookie security (around line 242):
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# If not present, add them
```

**Testing:**
```bash
# Check cookie flags:
curl -v http://localhost:5000 2>&1 | grep -i "set-cookie"
# Should show: HttpOnly; SameSite=Lax
```

**Impact:** 🟠 HIGH - Prevents session hijacking

---

## Medium Priority (Polish)

### 8. Dependency Security Audits

**Automated Checking:**
```bash
# Install security checker
pip install safety pip-audit

# Run checks regularly
safety check
pip-audit

# Add to CI/CD pipeline
```

**Create Script:** `.github/workflows/security.yml`
```yaml
name: Security Check
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install safety
      - run: safety check
```

**Impact:** 🟡 MEDIUM - Ongoing vulnerability detection

---

### 9. Input Validation Best Practices

**Ensure All Routes Validate:**
```python
# ✅ GOOD - Validates input
@app.route('/api/config', methods=['POST'])
@requires_auth
def update_config():
    data = request.get_json()
    
    # Validate required fields
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    key = str(data['key']).strip()
    value = data['value']
    
    # Validate key is known
    if key not in ALLOWED_CONFIG_KEYS:
        return jsonify({'error': 'Invalid config key'}), 400
    
    # Type checking
    if key == 'memory_threshold_mb' and not isinstance(value, int):
        return jsonify({'error': 'memory_threshold_mb must be integer'}), 400
    
    # Save config...
```

**Impact:** 🟡 MEDIUM - Prevents injection attacks

---

## Implementation Timeline

**Week 1 (CRITICAL):**
- Day 1-2: Add OWASP headers + CSP
- Day 2-3: Implement rate limiting
- Day 4: Error handling + info leakage prevention
- Day 5: Security logging setup

**Week 2 (HIGH):**
- Day 1-2: HTTPS enforcement setup
- Day 3-4: Verify cookie security
- Day 5: Dependency audit

**Week 3+ (ONGOING):**
- Input validation audit
- Penetration testing (optional)
- Security training/documentation

---

## Testing Checklist

- [ ] OWASP headers present and correct
- [ ] CSP doesn't break functionality
- [ ] Rate limiting works without false positives
- [ ] Error handling doesn't leak information
- [ ] Security logging captures all events
- [ ] HTTPS works in production
- [ ] Cookies have correct flags
- [ ] Dependencies pass safety check
- [ ] No known vulnerabilities in stack

---

## Post-Implementation

### Monitor & Maintain

1. **Weekly:** Check security logs for suspicious activity
2. **Monthly:** Run `safety check` and `pip-audit`
3. **Quarterly:** Security audit review
4. **Yearly:** Penetration testing (optional)

### Documentation

After implementing these changes, document:
- [ ] Security headers explanation
- [ ] Rate limiting policies
- [ ] Incident response procedures
- [ ] Security logging retention policy
- [ ] Deployment security checklist

---

**Status:** Ready to Implement  
**Estimated Time:** 15-20 hours for critical items  
**Risk Reduction:** ~85% of common vulnerabilities
