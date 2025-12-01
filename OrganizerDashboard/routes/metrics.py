from flask import Blueprint, jsonify
import psutil
import sys
from OrganizerDashboard.helpers.helpers import service_running, find_organizer_proc

routes_metrics = Blueprint('routes_metrics', __name__)

@routes_metrics.route("/metrics")
def metrics():
    running = service_running()
    mem_mb = 0.0
    cpu_pct = 0.0
    ram_pct = psutil.virtual_memory().percent
    proc = find_organizer_proc()
    if proc:
        try:
            cpu_pct = proc.cpu_percent(interval=0.2)
            mem_mb = proc.memory_info().rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return jsonify({
        "service_status": "Running" if running else "Stopped",
        "service_memory_mb": mem_mb,
        "total_memory_mb": psutil.virtual_memory().used / (1024 * 1024),
        "total_memory_gb": psutil.virtual_memory().total / (1024 * 1024 * 1024),
        "service_cpu_percent": cpu_pct,
        "total_cpu_percent": psutil.cpu_percent(interval=0.2),
        "ram_percent": ram_pct
    })
