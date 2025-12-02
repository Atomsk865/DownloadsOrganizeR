from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, current_user, UserMixin
from OrganizerDashboard.auth.auth import check_auth

routes_login = Blueprint('routes_login', __name__)

class User(UserMixin):
    def __init__(self, username, role='viewer'):
        self.id = username
        self.role = role

def _resolve_role(username: str) -> str:
    try:
        from OrganizerDashboard.config_runtime import get_dashboard_config
        dash_cfg = get_dashboard_config()
        for u in dash_cfg.get('users', []):
            if u.get('username') == username:
                return u.get('role') or 'viewer'
        # Admin fallback
        import sys
        admin_user = getattr(sys.modules.get('__main__'), 'ADMIN_USER', 'admin')
        if username == admin_user:
            return 'admin'
    except Exception:
        pass
    return 'viewer'

@routes_login.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('routes_dashboard.dashboard'))
    return render_template('login.html')

@routes_login.route('/login', methods=['POST'])
def login_post():
    # Accept form or JSON
    username = request.form.get('username') or (request.json.get('username') if request.is_json else None)
    password = request.form.get('password') or (request.json.get('password') if request.is_json else None)
    if not username or not password:
        return render_template('login.html', error='Missing username or password'), 400
    if check_auth(username, password):
        role = _resolve_role(username)
        user = User(username, role)
        login_user(user)
        return redirect(url_for('routes_dashboard.dashboard'))
    return render_template('login.html', error='Invalid credentials'), 401

@routes_login.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('routes_login.login_page'))
