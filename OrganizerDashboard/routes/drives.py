from flask import Blueprint, jsonify
import psutil

routes_drives = Blueprint('routes_drives', __name__)

@routes_drives.route("/drives")
def drives():
    drives_info = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            drives_info.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            })
        except Exception:
            continue
    return jsonify(drives_info)
