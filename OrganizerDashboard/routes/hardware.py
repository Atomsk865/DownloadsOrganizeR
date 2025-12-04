from flask import Blueprint, jsonify
import socket
import psutil
from OrganizerDashboard.helpers.helpers import get_windows_version, get_cpu_name, get_private_ip, get_public_ip
from OrganizerDashboard.cache import get_cache

routes_hardware = Blueprint('routes_hardware', __name__)

@routes_hardware.route("/hardware")
def hardware():
    # Cache hardware info for 5 minutes (rarely changes)
    cache = get_cache()
    if cache:
        cached = cache.get('hardware_info')
        if cached:
            return jsonify(cached)
    from OrganizerDashboard.helpers.helpers import get_gpus
    gpus = get_gpus()
    gpu_display = gpus[0] if gpus else "N/A"
    
    info = {
        "hostname": socket.gethostname(),
        "os": get_windows_version(),
        "cpu": get_cpu_name(),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "gpu": gpu_display,
        "private_ip": get_private_ip(),
        "public_ip": get_public_ip()
    }
    
    # Cache hardware info for 5 minutes
    if cache:
        cache.set('hardware_info', info, timeout=300)
    
    return jsonify(info)
