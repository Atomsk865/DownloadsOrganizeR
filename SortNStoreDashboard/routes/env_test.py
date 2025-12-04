from flask import Blueprint, render_template, jsonify
import subprocess
import sys
import os
from SortNStoreDashboard.auth.auth import requires_auth

routes_env = Blueprint('routes_env', __name__)


@routes_env.route('/env-test')
def env_test_page():
    return render_template('environment_test.html')


@routes_env.route('/api/env/ping')
def env_ping():
    return jsonify({"pong": True})


@routes_env.route('/env-test/run-tests', methods=['POST'])
def env_run_tests():
    """Run pytest in the workspace and return output."""
    try:
        # Prefer running tests/ directory; fallback to repository root
        cwd = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        cmd = [sys.executable, '-m', 'pytest', '-q']
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(timeout=120)
        return jsonify({
            'success': proc.returncode == 0,
            'exit_code': proc.returncode,
            'stdout': stdout,
            'stderr': stderr
        }), 200
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Test run timed out after 120s'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
