from flask import Blueprint, jsonify
from OrganizerDashboard.auth.auth import requires_right
import psutil
import time
from OrganizerDashboard.helpers.helpers import service_running, find_organizer_proc

routes_metrics = Blueprint('routes_metrics', __name__)

_METRICS_CACHE = {"data": None, "ts": 0.0}
_METRICS_TTL = 2.0  # seconds

@routes_metrics.route("/metrics")
@requires_right('view_metrics')
def metrics():
    now = time.time()
    if _METRICS_CACHE["data"] is not None and (now - _METRICS_CACHE["ts"]) < _METRICS_TTL:
        return jsonify(_METRICS_CACHE["data"])

    running = service_running()
    mem_mb = 0.0
    cpu_pct = 0.0
    ram = psutil.virtual_memory()
    ram_pct = ram.percent
    proc = find_organizer_proc()
    if proc:
        try:
            cpu_pct = proc.cpu_percent(interval=0.1)
            mem_mb = proc.memory_info().rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    payload = {
        "service_status": "Running" if running else "Stopped",
        "service_memory_mb": mem_mb,
        "total_memory_mb": ram.used / (1024 * 1024),
        "total_memory_gb": ram.total / (1024 * 1024 * 1024),
        "service_cpu_percent": cpu_pct,
        "total_cpu_percent": psutil.cpu_percent(interval=0.1),
        "ram_percent": ram_pct,
        "cached": False
    }
    _METRICS_CACHE["data"] = payload
    _METRICS_CACHE["ts"] = now
    return jsonify(payload)
