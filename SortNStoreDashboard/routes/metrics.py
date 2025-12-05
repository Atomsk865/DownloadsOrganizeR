from flask import Blueprint, jsonify
from SortNStoreDashboard.auth.auth import requires_right
import psutil
import time
from SortNStoreDashboard.helpers.helpers import service_running, find_organizer_proc

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
    
    # Get disk usage for root/C: drive
    try:
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        disk_percent = disk.percent
    except Exception:
        disk_used_gb = 0
        disk_total_gb = 0
        disk_percent = 0
    
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
        "disk_used_gb": disk_used_gb,
        "disk_total_gb": disk_total_gb,
        "disk_percent": disk_percent,
        "memory_percent": ram_pct,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "cached": False
    }
    _METRICS_CACHE["data"] = payload
    _METRICS_CACHE["ts"] = now
    return jsonify(payload)
