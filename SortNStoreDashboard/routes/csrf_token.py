"""CSRF token helper route for AJAX requests."""
from flask import Blueprint, jsonify
from flask_wtf.csrf import generate_csrf

routes_csrf = Blueprint('routes_csrf', __name__)

@routes_csrf.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """Return CSRF token for client-side AJAX requests."""
    return jsonify({'csrf_token': generate_csrf()})
