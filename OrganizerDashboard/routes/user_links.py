from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import requires_auth, requires_right
import sys

routes_user_links = Blueprint('routes_user_links', __name__)

@routes_user_links.route('/api/dashboard/links', methods=['GET'])
def get_links():
    @requires_auth
    def _inner():
        # Resolve current user
        from flask_login import current_user
        username = current_user.get_id() if current_user and current_user.is_authenticated else None
        main = sys.modules['__main__']
        dash_cfg = getattr(main, 'dashboard_config', {})
        user_links = dash_cfg.get('user_links', {})
        return jsonify({'links': user_links.get(username or '', [])})
    return _inner()

@routes_user_links.route('/api/dashboard/links', methods=['POST'])
def set_links():
    @requires_right('modify_layout')
    def _inner():
        data = request.get_json() or {}
        links = data.get('links')
        if not isinstance(links, list):
            return jsonify({'error': 'links must be a list of {label,url}'}), 400
        # Resolve current user
        from flask_login import current_user
        username = current_user.get_id() if current_user and current_user.is_authenticated else None
        if not username:
            return jsonify({'error': 'no user'}), 400
        main = sys.modules['__main__']
        dash_cfg = getattr(main, 'dashboard_config', {})
        user_links = dash_cfg.get('user_links', {})
        user_links[username] = [
            {'label': (item.get('label') or '').strip(), 'url': (item.get('url') or '').strip()}
            for item in links if isinstance(item, dict) and item.get('url')
        ]
        dash_cfg['user_links'] = user_links
        from OrganizerDashboard.routes.dashboard_config import _persist_dashboard_config
        _persist_dashboard_config(dash_cfg, main)
        return jsonify({'success': True})
    return _inner()
