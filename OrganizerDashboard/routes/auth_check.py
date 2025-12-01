from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import check_auth

routes_auth_check = Blueprint('routes_auth_check', __name__)

@routes_auth_check.route('/auth_check')
def auth_check():
    """Lightweight endpoint to validate Basic credentials sent in the Authorization header."""
    auth = request.authorization
    if not auth:
        return jsonify({"valid": False, "message": "No credentials provided"}), 401
    if check_auth(auth.username, auth.password):
        return jsonify({"valid": True}), 200
    return jsonify({"valid": False, "message": "Invalid credentials"}), 401
