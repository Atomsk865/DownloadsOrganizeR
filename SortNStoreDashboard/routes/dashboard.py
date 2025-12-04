from flask import Blueprint, render_template, request, jsonify, Response, redirect
import socket
import sys
import psutil
from SortNStoreDashboard.helpers.helpers import (
    get_windows_version, get_cpu_name, get_private_ip, get_public_ip, service_running, find_organizer_proc, format_bytes, last_n_lines_normalized, load_dashboard_json
)
from SortNStoreDashboard.auth.auth import check_auth, authenticate, requires_auth
from flask_login import current_user
import os
import platform
import json

routes_dashboard = Blueprint('routes_dashboard', __name__)

@routes_dashboard.route("/")
def dashboard():
    """Dashboard root. If setup incomplete redirect to wizard; otherwise require auth."""
    # Use runtime config to check setup state
    try:
        from SortNStoreDashboard.config_runtime import get_dashboard_config, get_config
        dash_cfg = get_dashboard_config()
        # Stronger first-run detection: setup flag, missing users, or no stored admin hash
        cfg = get_config()
        users = dash_cfg.get('users') or []
        has_admin_hash = bool(cfg.get('dashboard_pass_hash'))
        if (not dash_cfg.get('setup_completed', False)) or (len(users) == 0) or (not has_admin_hash):
            return redirect('/setup')
    except Exception:
        pass

    # If session-authenticated, proceed; else redirect to login
    try:
        if current_user.is_authenticated:
            pass
        else:
            return redirect('/login')
    except Exception:
        return redirect('/login')

    dashboard_data = load_dashboard_json()
    
    # Get top processes by CPU
    top_processes = []
    try:
        num_cpus = psutil.cpu_count(logical=True)
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
            try:
                cpu = proc.info['cpu_percent'] / num_cpus if num_cpus else proc.info['cpu_percent']
                procs.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "user": proc.info.get('username', 'N/A'),
                    "cpu": cpu,
                    "mem": round(proc.info['memory_info'].rss / (1024*1024), 1)
                })
            except Exception:
                continue
        procs.sort(key=lambda x: x['cpu'], reverse=True)
        top_processes = procs[:5]
    except Exception:
        pass
    
    # Get drive information
    drives = []
    try:
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                drives.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "total": format_bytes(usage.total),
                    "used": format_bytes(usage.used),
                    "free": format_bytes(usage.free),
                    "percent": round(usage.percent, 1)
                })
            except Exception:
                continue
    except Exception:
        pass
    
    # Load config for settings display
    import OrganizerDashboard
    config = OrganizerDashboard.config
    
    # Get GPU info
    from SortNStoreDashboard.helpers.helpers import get_gpus
    gpus = get_gpus()
    gpu_display = gpus[0] if gpus else "N/A"
    
    # Derive basic client context from the request
    try:
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        client_ua = request.headers.get('User-Agent', '')
    except Exception:
        client_ip = ''
        client_ua = ''

    return render_template(
        "dashboard.html",
        hostname=socket.gethostname(),
        os=get_windows_version(),
        cpu=get_cpu_name(),
        ram_gb=round(psutil.virtual_memory().total / (1024**3), 2),
        gpu=gpu_display,
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
        top_processes=top_processes,
        drives=drives,
        memory_threshold=config.get('memory_threshold_mb', 200),
        cpu_threshold=config.get('cpu_threshold_percent', 60),
        logs_dir=config.get('logs_dir', ''),
        watch_folder=config.get('watch_folder', ''),
        stdout_log="",
        stderr_log="",
        is_windows=(sys.platform == "win32"),
        routes=json.dumps({}),
        custom_routes=json.dumps({}),
        client_ip=client_ip,
        client_ua=client_ua
    )

@routes_dashboard.route("/api/organizer/config", methods=["GET"])
@requires_auth
def get_organizer_config():
    """Return organizer configuration including routes and custom_routes."""
    import OrganizerDashboard
    config = OrganizerDashboard.config
    
    return jsonify({
        "routes": config.get("routes", {}),
        "custom_routes": config.get("custom_routes", {}),
        "tag_routes": config.get("tag_routes", {}),
        "memory_threshold_mb": config.get("memory_threshold_mb", 200),
        "cpu_threshold_percent": config.get("cpu_threshold_percent", 60),
        "logs_dir": config.get("logs_dir", ""),
        # Legacy single watch folder and new list for multi-folder support
        "watch_folder": config.get("watch_folder", ""),
        "watch_folders": config.get("watch_folders", []),
        # Feature flags and VirusTotal API key for UI gating
        "features": config.get("features", {}),
        "vt_api_key": config.get("vt_api_key") or config.get("virustotal_api_key") or ""
    })
