from flask import Blueprint, jsonify
import psutil
import time
from OrganizerDashboard.cache import get_cache

routes_network = Blueprint('routes_network', __name__)

last_net = psutil.net_io_counters()
last_time = time.time()

@routes_network.route("/network")
def network():
    # Cache network stats for 2 seconds
    cache = get_cache()
    if cache:
        cached = cache.get('network_stats')
        if cached:
            return jsonify(cached)
    
    global last_net, last_time
    now_net = psutil.net_io_counters()
    now_time = time.time()
    interval = now_time - last_time
    upload_rate_b = (now_net.bytes_sent - last_net.bytes_sent) / interval if interval > 0 else 0
    download_rate_b = (now_net.bytes_recv - last_net.bytes_recv) / interval if interval > 0 else 0
    last_net = now_net
    last_time = now_time
    upload_rate_kb = upload_rate_b / 1024
    download_rate_kb = download_rate_b / 1024
    upload_rate_mb = upload_rate_b / (1024 * 1024)
    download_rate_mb = download_rate_b / (1024 * 1024)
    
    stats = {
        "upload_rate_b": upload_rate_b,
        "download_rate_b": download_rate_b,
        "upload_rate_kb": upload_rate_kb,
        "download_rate_kb": download_rate_kb,
        "upload_rate_mb": upload_rate_mb,
        "download_rate_mb": download_rate_mb,
        "total_sent": now_net.bytes_sent,
        "total_recv": now_net.bytes_recv
    }
    
    # Cache for 2 seconds
    if cache:
        cache.set('network_stats', stats, timeout=2)
    
    return jsonify(stats)
