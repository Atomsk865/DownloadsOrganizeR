# Quick Start: Security Hardening (Next 3 Hours)

**Get the critical security items done fast**

## Step 1: Add OWASP Security Headers (20 minutes)

### File: `SortNStoreDashboard.py`

**Find this line (~line 240):**
```python
    # CSRF Protection
    csrf = CSRFProtect()
```

**Add this function RIGHT AFTER the app is created (around line 200):**

```python
@app.after_request
def set_security_headers(response):
    """OWASP-recommended security headers."""
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' cdn.jsdelivr.net; "
        "style-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "upgrade-insecure-requests"
    )
    
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), '
        'payment=(), usb=(), magnetometer=(), '
        'gyroscope=(), accelerometer=()'
    )
    
    return response
```

**Verify it works:**
```bash
curl -i http://localhost:5000 | grep -E "X-Frame|X-Content|CSP"
# Should show the headers above
```

---

## Step 2: Add Rate Limiting (30 minutes)

### 2a. Update `requirements.txt`

**Add this line:**
```
flask-limiter>=4.0,<5
```

**Install it:**
```bash
pip install flask-limiter>=4.0,<5
```

### 2b. Modify `SortNStoreDashboard.py`

**Find this section (around line 28):**
```python
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
```

**Add this import:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
```

**After creating the Flask app (around line 225), add:**
```python
# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
```

### 2c. Protect Login Endpoint

**Find your login route in `SortNStoreDashboard/routes/login.py`**

**Add decorator to the POST handler:**
```python
@routes_login.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Block brute force attempts
def login():
    # ... existing code ...
```

**Test it:**
```bash
# Try to login 6 times in 1 minute - 6th should be blocked
for i in {1..6}; do 
    echo "Attempt $i:"
    curl -X POST http://localhost:5000/login \
        -d "username=test&password=test" -w "\nStatus: %{http_code}\n"
done
# Last one should return 429 (Too Many Requests)
```

---

## Step 3: Better Error Handling (30 minutes)

### File: `SortNStoreDashboard.py`

**Add these error handlers (after the security headers function):**

```python
@app.errorhandler(400)
def bad_request(error):
    app.logger.warning(f"Bad request from {request.remote_addr}: {request.path}")
    return jsonify({'error': 'Bad Request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    app.logger.warning(f"Unauthorized access from {request.remote_addr}: {request.path}")
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    app.logger.warning(f"Forbidden access from {request.remote_addr}: {request.path}")
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({'error': 'Internal Server Error'}), 500

# Prevent exposing debug info
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['TRAP_HTTP_EXCEPTIONS'] = True
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
```

**Test it:**
```bash
# Should NOT show stack trace, just error message
curl http://localhost:5000/this-does-not-exist
# Returns: {"error": "Not Found"}

# Invalid API call
curl http://localhost:5000/api/invalid/endpoint
# Returns: {"error": "Not Found"}
```

---

## Step 4: Security Event Logging (40 minutes)

### Create new file: `SortNStoreDashboard/security_logger.py`

**Copy this:**
```python
"""Security event logging module."""

import logging
from pathlib import Path

# Setup logging directory
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# Create security logger
security_logger = logging.getLogger('sortnstore.security')
security_logger.setLevel(logging.INFO)

# File handler
handler = logging.FileHandler(log_dir / 'security.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
security_logger.addHandler(handler)

def log_auth_attempt(username, ip_address, success, method='unknown', details=''):
    """Log authentication attempts."""
    status = 'SUCCESS' if success else 'FAILURE'
    msg = f"AUTH_ATTEMPT | User: {username} | IP: {ip_address} | Method: {method} | {status}"
    if details:
        msg += f" | Details: {details}"
    security_logger.info(msg)

def log_config_change(username, ip_address, change_type, changes):
    """Log configuration changes."""
    msg = f"CONFIG_CHANGE | User: {username} | IP: {ip_address} | Type: {change_type} | Changes: {changes}"
    security_logger.info(msg)

def log_access_denied(username, ip_address, resource, reason):
    """Log access denials."""
    msg = f"ACCESS_DENIED | User: {username} | IP: {ip_address} | Resource: {resource} | Reason: {reason}"
    security_logger.warning(msg)

def log_suspicious_activity(ip_address, activity_type, details):
    """Log suspicious activity."""
    msg = f"SUSPICIOUS | IP: {ip_address} | Type: {activity_type} | Details: {details}"
    security_logger.warning(msg)
```

### Update `SortNStoreDashboard/routes/login.py`

**Find the login function and add logging:**

```python
from SortNStoreDashboard.security_logger import log_auth_attempt

@routes_login.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # ... validate credentials ...
    
    if credentials_valid:
        log_auth_attempt(username, request.remote_addr, True, 'form')
        # ... rest of login ...
    else:
        log_auth_attempt(username, request.remote_addr, False, 'form', 'Invalid credentials')
        # ... show error ...
```

**Test it:**
```bash
# Check logs after login attempts
tail -f logs/security.log

# Should show:
# 2025-12-10 15:30:45 - INFO - AUTH_ATTEMPT | User: admin | IP: 127.0.0.1 | Method: form | SUCCESS
# 2025-12-10 15:31:20 - INFO - AUTH_ATTEMPT | User: admin | IP: 127.0.0.1 | Method: form | FAILURE | Details: Invalid credentials
```

---

## Step 5: Verify Everything (20 minutes)

### Run these checks:

```bash
# 1. Check security headers
echo "=== Security Headers ==="
curl -s -I http://localhost:5000 | grep -E "X-|Content-Security|Strict-Transport"

# 2. Check rate limiting works
echo -e "\n=== Rate Limiting Test ==="
for i in {1..6}; do
    response=$(curl -s -w "\nStatus:%{http_code}" -X POST \
        http://localhost:5000/login -d "user=test")
    echo "Attempt $i: $(echo "$response" | tail -1)"
done

# 3. Check error handling
echo -e "\n=== Error Handling ==="
curl -s http://localhost:5000/nonexistent | grep -q "error" && echo "✓ Error responses working"

# 4. Check security logs
echo -e "\n=== Security Logs ==="
tail logs/security.log | head -5
```

---

## Verification Checklist

- [ ] Security headers present in response
- [ ] CSP header looks correct
- [ ] Rate limiting blocks after 5/minute
- [ ] Error responses don't show stack traces
- [ ] Security logs created in `logs/security.log`
- [ ] No errors in application logs
- [ ] Dashboard still loads normally
- [ ] Login still works (just protected)

---

## If Something Breaks

### Headers breaking styles
- Check CSP is correct: `style-src 'self' cdn.jsdelivr.net 'unsafe-inline'`
- Inline styles are blocked, need to move to CSS file

### Rate limiting too strict
- Adjust limits: `@limiter.limit("10 per minute")`
- Start loose, tighten later

### Error handlers returning wrong format
- Make sure you're returning JSON: `return jsonify({'error': '...'}), code`
- Check Content-Type header

### Logs not creating
- Create `logs/` directory manually: `mkdir logs`
- Check file permissions

---

## Production Checklist

Before going live:

- [ ] Security headers verified
- [ ] Rate limiting configured for your traffic
- [ ] Error handling tested
- [ ] Security logging working
- [ ] HTTPS enforced (add before_request in production)
- [ ] Dependencies updated: `pip install --upgrade flask-limiter`
- [ ] Logs rotated (don't let grow unbounded)
- [ ] Security logs backed up (archive.log.1, etc.)

---

## Next: Visual Improvements (Optional)

Once security is done, see `DASHBOARD_VISUAL_IMPROVEMENT_GUIDE.md` for making it look sleek.

---

## Timeline

- ✅ Step 1: 20 min
- ✅ Step 2: 30 min
- ✅ Step 3: 30 min
- ✅ Step 4: 40 min
- ✅ Step 5: 20 min

**Total: ~2.5 hours for critical security**

---

## Support

If you need help:
1. Check SECURITY_HARDENING_ROADMAP.md for details
2. Check DASHBOARD_ARCHITECTURE_ANALYSIS.md for context
3. Review your application logs: `logs/flask.log`
4. Check security logs: `logs/security.log`

---

**Ready to start? Go to Step 1!** ⬆️

You've got this. 3 hours and your dashboard is dramatically more secure.
