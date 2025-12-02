from flask import Blueprint, render_template, request, jsonify, Response, redirect
import socket
import sys
import psutil
from OrganizerDashboard.helpers.helpers import (
    get_windows_version, get_cpu_name, get_private_ip, get_public_ip, service_running, find_organizer_proc, format_bytes, last_n_lines_normalized, load_dashboard_json
)
from OrganizerDashboard.auth.auth import requires_auth
import os
import platform
import json

routes_dashboard = Blueprint('routes_dashboard', __name__)

@routes_dashboard.route("/")
def dashboard():
    # Redirect to setup wizard if initial setup not completed
    try:
        import sys
        main = sys.modules['__main__']
        dash_cfg = getattr(main, 'dashboard_config', {})
        if not dash_cfg.get('setup_completed', False):
            return redirect('/setup')
    except Exception:
        pass
    dashboard_data = load_dashboard_json()
    return render_template(
        "dashboard.html",
        hostname=socket.gethostname(),
        os=get_windows_version(),
        cpu=get_cpu_name(),
        ram_gb=round(psutil.virtual_memory().total / (1024**3), 2),
        gpu=dashboard_data.get("gpu", "N/A"),
        private_ip=get_private_ip(),
        public_ip=get_public_ip(),
        upload_rate_kb=0,
        download_rate_kb=0,
        service_status="Running" if service_running() else "Stopped",
        service_memory_mb=0,
        service_cpu_percent=0,
        total_memory_mb=round(psutil.virtual_memory().used / (1024 * 1024), 2),
        total_memory_gb=round(psutil.virtual_memory().total / (1024 * 1024 * 1024), 2),
        total_cpu_percent=psutil.cpu_percent(interval=0.2),
        ram_percent=psutil.virtual_memory().percent,
        tasks=[],
        drives=[],
        memory_threshold=0,
        cpu_threshold=0,
        logs_dir="",
        stdout_log="",
        stderr_log="",
        is_windows=(sys.platform == "win32")
    )
