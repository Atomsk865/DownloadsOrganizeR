from flask import Blueprint, jsonify
import psutil

routes_tasks = Blueprint('routes_tasks', __name__)

@routes_tasks.route("/tasks")
def tasks():
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
    return jsonify(procs[:5])
