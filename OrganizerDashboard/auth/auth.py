import bcrypt
import json
import sys
from flask import Response, request
from functools import wraps

def initialize_password_hash():
    """Initialize the password hash using globals from OrganizerDashboard module."""
    main = sys.modules['__main__']
    
    if main.ADMIN_PASS_HASH is not None:  # type: ignore
        return
    
    stored_hash = None
    try:
        stored_hash = main.config.get("dashboard_pass_hash")  # type: ignore
    except Exception:
        stored_hash = None
    
    if stored_hash:
        main.ADMIN_PASS_HASH = stored_hash.encode('utf-8')  # type: ignore
        return
    
    plain = main.config.get("dashboard_pass")  # type: ignore
    if plain:
        main.ADMIN_PASS_HASH = bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt())  # type: ignore
        try:
            main.config['dashboard_pass_hash'] = main.ADMIN_PASS_HASH.decode('utf-8')  # type: ignore
            if 'dashboard_pass' in main.config:  # type: ignore
                del main.config['dashboard_pass']  # type: ignore
            with open(main.CONFIG_FILE, 'w', encoding='utf-8') as f:  # type: ignore
                json.dump(main.config, f, indent=4)  # type: ignore
        except Exception:
            pass
        return
    
    main.ADMIN_PASS_HASH = bcrypt.hashpw(main.ADMIN_PASS.encode('utf-8'), bcrypt.gensalt())  # type: ignore
    try:
        main.config['dashboard_user'] = main.ADMIN_USER  # type: ignore
        main.config['dashboard_pass_hash'] = main.ADMIN_PASS_HASH.decode('utf-8')  # type: ignore
        with open(main.CONFIG_FILE, 'w', encoding='utf-8') as f:  # type: ignore
            json.dump(main.config, f, indent=4)  # type: ignore
    except Exception:
        pass

def check_auth(username, password):
    """Verify given username/password against stored admin user and hashed password."""
    main = sys.modules['__main__']
    
    if username != main.ADMIN_USER:  # type: ignore
        return False
    if main.ADMIN_PASS_HASH is None:  # type: ignore
        initialize_password_hash()
    if main.ADMIN_PASS_HASH is None:  # type: ignore
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), main.ADMIN_PASS_HASH)  # type: ignore
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
