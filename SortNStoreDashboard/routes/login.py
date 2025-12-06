from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, current_user, UserMixin, login_required
import bcrypt
from SortNStoreDashboard.auth.auth import check_auth

routes_login = Blueprint('routes_login', __name__)

class User(UserMixin):
    def __init__(self, username, role='viewer'):
        self.id = username
        self.role = role

def _resolve_role(username: str) -> str:
    try:
        from SortNStoreDashboard.config_runtime import get_dashboard_config
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
        # Remember login with persistent cookie
        remember = True
        try:
            # Accept optional 'remember' flag from form
            remember = request.form.get('remember', 'on').lower() in ('on', 'true', '1')
        except Exception:
            pass
        login_user(user, remember=remember)
        try:
            from SortNStoreDashboard.config_runtime import get_config
            cfg = get_config()
            if cfg.get('password_change_required'):
                return redirect(url_for('routes_login.force_change_password_page'))
        except Exception:
            pass
        return redirect(url_for('routes_dashboard.dashboard'))
    return render_template('login.html', error='Invalid credentials'), 401

@routes_login.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('routes_login.login_page'))


@routes_login.route('/force-change-password', methods=['GET'])
@login_required
def force_change_password_page():
    try:
        from SortNStoreDashboard.config_runtime import get_config
        cfg = get_config()
        if not cfg.get('password_change_required'):
            return redirect(url_for('routes_dashboard.dashboard'))
    except Exception:
        return redirect(url_for('routes_dashboard.dashboard'))
    return render_template('force_password_change.html', error=None)


@routes_login.route('/force-change-password', methods=['POST'])
@login_required
def force_change_password_post():
    new_password = request.form.get('new_password') or (request.json.get('new_password') if request.is_json else None)
    confirm = request.form.get('confirm_password') or (request.json.get('confirm_password') if request.is_json else None)
    if not new_password:
        return render_template('force_password_change.html', error='New password required'), 400
    if new_password != confirm:
        return render_template('force_password_change.html', error='Passwords do not match'), 400
    try:
        from SortNStoreDashboard.routes.setup import _validate_password
        err = _validate_password(new_password)
        if err:
            return render_template('force_password_change.html', error=err), 400
    except Exception:
        # Fallback minimal validation
        if len(new_password) < 8:
            return render_template('force_password_change.html', error='Password must be at least 8 characters'), 400

    try:
        from SortNStoreDashboard.config_runtime import get_config, get_dashboard_config, save_config, save_dashboard_config
        import SortNStoreDashboard
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cfg = get_config()
        admin_user = cfg.get('dashboard_user', 'admin')
        cfg['dashboard_user'] = admin_user
        cfg['dashboard_pass_hash'] = hashed
        cfg['password_change_required'] = False
        cfg.pop('dashboard_pass', None)
        save_config()

        dash_cfg = get_dashboard_config()
        updated = False
        for u in dash_cfg.get('users', []):
            if u.get('username') == admin_user:
                u['password_hash'] = hashed
                updated = True
                break
        if not updated:
            dash_cfg.setdefault('users', []).append({
                'username': admin_user,
                'role': 'admin',
                'password_hash': hashed
            })
        dash_cfg['password_change_required'] = False
        save_dashboard_config()

        SortNStoreDashboard.ADMIN_PASS_HASH = hashed.encode('utf-8')
        from SortNStoreDashboard.auth.auth import initialize_auth_manager
        initialize_auth_manager()

        return redirect(url_for('routes_dashboard.dashboard'))
    except Exception as e:
        return render_template('force_password_change.html', error=f'Failed to update password: {e}'), 500
