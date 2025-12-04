from flask import Blueprint, jsonify
import psutil
from OrganizerDashboard.cache import get_cache

routes_drives = Blueprint('routes_drives', __name__)

@routes_drives.route("/drives")
def drives():
    # Cache drive info for 30 seconds
    cache = get_cache()
    if cache:
        cached = cache.get('drives_info')
        if cached:
            return jsonify(cached)
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
    
    # Cache the result
    if cache:
        cache.set('drives_info', drives_info, timeout=30)
    
    return jsonify(drives_info)
