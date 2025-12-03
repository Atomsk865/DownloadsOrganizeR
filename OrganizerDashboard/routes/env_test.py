from flask import Blueprint, render_template, jsonify
from OrganizerDashboard.auth.auth import requires_auth

routes_env = Blueprint('routes_env', __name__)


@routes_env.route('/env-test')
def env_test_page():
    return render_template('environment_test.html')


@routes_env.route('/api/env/ping')
def env_ping():
    return jsonify({"pong": True})
