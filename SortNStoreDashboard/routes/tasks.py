from flask import Blueprint, jsonify
import psutil
from SortNStoreDashboard.cache import get_cache

routes_tasks = Blueprint('routes_tasks', __name__)

@routes_tasks.route("/tasks")
def tasks():
    # Cache task list for 5 seconds
    cache = get_cache()
    if cache:
        cached = cache.get('top_tasks')
        if cached:
            return jsonify(cached)
    
    num_cpus = psutil.cpu_count(logical=True)
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
        try:
            cpu = proc.info['cpu_percent'] / num_cpus
            procs.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "user": proc.info['username'],
                "cpu": cpu,
                "mem": proc.info['memory_info'].rss / (1024*1024)
            })
        except Exception:
            continue
    procs.sort(key=lambda x: x['cpu'], reverse=True)
    top_tasks = procs[:5]
    
    # Cache for 5 seconds
    if cache:
        cache.set('top_tasks', top_tasks, timeout=5)
    
    return jsonify(top_tasks)
