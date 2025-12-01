import bcrypt
import json
import sys
from flask import Response, request
from functools import wraps

def initialize_password_hash():
    """Initialize the password hash using globals from OrganizerDashboard module."""
    main = sys.modules['__main__']
    
    if main.ADMIN_PASS_HASH is not None:
        return
    
    stored_hash = None
    try:
        stored_hash = main.config.get("dashboard_pass_hash")
    except Exception:
        stored_hash = None
    
    if stored_hash:
        main.ADMIN_PASS_HASH = stored_hash.encode('utf-8')
        return
    
    plain = main.config.get("dashboard_pass")
    if plain:
        main.ADMIN_PASS_HASH = bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt())
        try:
            main.config['dashboard_pass_hash'] = main.ADMIN_PASS_HASH.decode('utf-8')
            if 'dashboard_pass' in main.config:
                del main.config['dashboard_pass']
            with open(main.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(main.config, f, indent=4)
        except Exception:
            pass
        return
    
    main.ADMIN_PASS_HASH = bcrypt.hashpw(main.ADMIN_PASS.encode('utf-8'), bcrypt.gensalt())
    try:
        main.config['dashboard_user'] = main.ADMIN_USER
        main.config['dashboard_pass_hash'] = main.ADMIN_PASS_HASH.decode('utf-8')
        with open(main.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(main.config, f, indent=4)
    except Exception:
        pass

def check_auth(username, password):
    """Verify given username/password against stored admin user and hashed password."""
    main = sys.modules['__main__']
    
    if username != main.ADMIN_USER:
        return False
    if main.ADMIN_PASS_HASH is None:
        initialize_password_hash()
    if main.ADMIN_PASS_HASH is None:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), main.ADMIN_PASS_HASH)
    except Exception:
        return False

def authenticate():
    return Response(
        'Authentication required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
