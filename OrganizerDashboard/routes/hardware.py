from flask import Blueprint, jsonify
import socket
import psutil
from OrganizerDashboard.helpers.helpers import get_windows_version, get_cpu_name, get_private_ip, get_public_ip

routes_hardware = Blueprint('routes_hardware', __name__)

@routes_hardware.route("/hardware")
def hardware():
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
    return jsonify(info)
