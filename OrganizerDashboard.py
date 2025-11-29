
import os
import json
import time
import psutil
import platform
import subprocess
import socket
from flask import Flask, render_template_string, request, redirect, Response, jsonify

SERVICE_NAME = "DownloadsOrganizer"
CONFIG_FILE = "organizer_config.json"
proc_cpu_cache = {}


# ---------- Load config or defaults ----------
DEFAULT_CONFIG = {
    "routes": {
        "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp", "heic"],
        "Music": ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"],
        "Videos": ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm"],
        "Documents": ["pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "ppt", "pptx", "csv"],
        "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2"],
        "Executables": ["exe", "msi", "bat", "cmd", "ps1"],
        "Shortcuts": ["lnk", "url"],
        "Scripts": ["py", "js", "html", "css", "json", "xml", "sh", "ts", "php"],
        "Fonts": ["ttf", "otf", "woff", "woff2"],
        "Logs": ["log"],
        "Other": []
    },
    "memory_threshold_mb": 200,
    "cpu_threshold_percent": 60,
    "logs_dir": r"C:\Scripts\service-logs"
}
config = DEFAULT_CONFIG.copy()
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        config.update(loaded)
    except Exception:
        pass

LOGS_DIR = config.get("logs_dir", DEFAULT_CONFIG["logs_dir"])
STDOUT_LOG = os.path.join(LOGS_DIR, "organizer_stdout.log")
STDERR_LOG = os.path.join(LOGS_DIR, "organizer_stderr.log")

app = Flask(__name__)

# ---------- HTML ----------

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Organizer Dashboard</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f7f9fa;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 1800px;
            margin: 24px auto;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 12px #0001;
            padding: 24px 18px 18px 18px;
        }
        h2, h4 { margin-top: 0; }
        .section { margin-bottom: 24px; }
        .card-row {
            display: flex;
            gap: 18px;
            margin-bottom: 12px;
        }
        .card {
            background: #f0f4f8;
            border-radius: 8px;
            padding: 14px 18px;
            flex: 1;
            min-width: 120px;
            text-align: center;
            box-shadow: 0 1px 4px #0001;
            position: relative;
        }
        .card b { font-size: 1.15em; }
        .usage-green { color: #1db954; font-weight: bold; }
        .usage-yellow { color: #ffb300; font-weight: bold; }
        .usage-orange { color: #ff7043; font-weight: bold; }
        .usage-red { color: #e53935; font-weight: bold; }
        .bg-green { background: #eafbe7 !important; }
        .bg-yellow { background: #fffbe6 !important; }
        .bg-orange { background: #fff3e0 !important; }
        .bg-red { background: #ffebee !important; }
        .config-table, .drives-table, .tasks-table, .hardware-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 12px;
        }
        .config-table th, .config-table td,
        .drives-table th, .drives-table td,
        .tasks-table th, .tasks-table td,
        .hardware-table th, .hardware-table td {
            border: 1px solid #e0e6ed;
            padding: 6px 10px;
            text-align: left;
        }
        .config-table th, .drives-table th, .tasks-table th, .hardware-table th {
            background: #f7f9fa;
        }
        .config-table input {
            width: 95%;
            padding: 2px 4px;
            border: 1px solid #d0d7de;
            border-radius: 3px;
        }
        .log-controls {
            margin-bottom: 6px;
        }
        .log-controls button {
            margin-right: 8px;
            padding: 4px 10px;
            border: none;
            border-radius: 4px;
            background: #e0e6ed;
            cursor: pointer;
            transition: background 0.2s;
        }
        .log-controls button:hover {
            background: #c9d6e3;
        }
        .logs-row {
            display: flex;
            gap: 24px;
        }
        .log-box {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        pre {
            background: #23272e;
            color: #e6e6e6;
            border-radius: 6px;
            padding: 14px;
            max-height: 420px;
            min-height: 200px;
            overflow-y: auto;
            font-size: 1.08em;
            line-height: 1.5;
        }
        .save-btn, .restart-btn {
            background: #1976d2;
            color: #fff;
            border: none;
            border-radius: 4px;
            padding: 7px 18px;
            font-size: 1em;
            cursor: pointer;
            margin-top: 10px;
            margin-bottom: 10px;
            transition: background 0.2s;
        }
        .save-btn:hover, .restart-btn:hover {
            background: #125ea7;
        }
        .row-flex {
            display: flex;
            gap: 24px;
        }
        .half {
            flex: 1;
            min-width: 0;
        }
        @media (max-width: 1200px) {
            .container { padding: 8px 1vw; }
            .card-row, .row-flex, .logs-row { flex-direction: column; gap: 10px; }
        }
        .top-actions {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
<div class="container">
    <h2>Organizer Service Dashboard</h2>
    <!-- Hardware Info Row -->
    <div class="section">
        <div class="card-row" id="hardware_cards">
            <div class="card" title="This PC's hostname.">
                Hostname<br><b id="hw_hostname">—</b>
            </div>
            <div class="card" title="Operating system and version.">
                OS<br><b id="hw_os">—</b>
            </div>
            <div class="card" title="Processor model and core count.">
                CPU<br><b id="hw_cpu">—</b>
            </div>
            <div class="card" title="Total installed RAM.">
                RAM<br><b id="hw_ram">—</b>
            </div>
            <div class="card" title="Graphics card(s) detected.">
                GPU<br><b id="hw_gpu">—</b>
            </div>
        </div>
    </div>
    <!-- Status Cards -->
    <div class="section">
        <div class="card-row">
            <div class="card" title="Shows if the Organizer service is running.">
                Service<br><b id="service_status">—</b>
            </div>
            <div class="card" title="Current memory used by the Organizer process.">
                Memory Usage<br><b id="memory_usage" class="usage-green">—</b>
            </div>
            <div class="card" title="Current CPU usage by the Organizer process.">
                CPU Usage<br><b id="cpu_usage" class="usage-green">—</b>
            </div>
            <div class="card" title="Overall system RAM usage.">
                RAM Usage<br><b id="ram_usage" class="usage-green">—</b>
            </div>
            <div class="card" title="Current upload and download speeds.">
                Network<br>
                <span style="font-size:0.95em;">
                    Up: <b id="network_up" class="usage-green">—</b><br>
                    Down: <b id="network_down" class="usage-green">—</b>
                </span>
            </div>
        </div>
        <div class="top-actions">
            <button class="restart-btn" type="button" onclick="restartService()">Restart Service</button>
        </div>
    </div>
    <div class="section row-flex">
        <div class="half">
            <h4>Drive Space</h4>
            <table id="drives_table" class="drives-table"></table>
        </div>
        <div class="half">
            <h4>Task Manager</h4>
            <table id="tasks_table" class="tasks-table"></table>
        </div>
    </div>
    <div class="section">
        <h4>Configuration</h4>
        <form method="POST" action="/update">
            <table class="config-table">
                <tr>
                    <th>Folder</th>
                    <th>Extensions (comma-separated)</th>
                    <th>Action</th>
                </tr>
                {% for folder, exts in routes.items() %}
                <tr>
                    <td><input name="folder_{{loop.index}}" value="{{folder}}" /></td>
                    <td><input name="exts_{{loop.index}}" value="{{ ','.join(exts) }}" /></td>
                    <td><button name="delete_{{loop.index}}" value="1">Delete</button></td>
                </tr>
                {% endfor %}
                <tr>
                    <td><input name="folder_new" placeholder="New folder" /></td>
                    <td><input name="exts_new" placeholder="ext1,ext2" /></td>
                    <td></td>
                </tr>
            </table>
            <div style="margin-bottom:8px;">
                Memory Threshold (MB): <input name="memory_threshold" value="{{ memory_threshold }}" size="4" />
                &nbsp; CPU Threshold (%): <input name="cpu_threshold" value="{{ cpu_threshold }}" size="3" />
                &nbsp; Logs Directory: <input name="logs_dir" value="{{ logs_dir }}" size="30" />
            </div>
            <button class="save-btn" type="submit">Save Configuration</button>
        </form>
    </div>
    <div class="section logs-row">
        <div class="log-box">
            <h4>Stdout (real-time)</h4>
            <div class="log-controls">
                <button onclick="clearLog('stdout')" type="button">Clear</button>
                <button onclick="pauseScroll('stdout')" type="button">Pause Auto-Scroll</button>
            </div>
            <pre id="stdout_log"></pre>
        </div>
        <div class="log-box">
            <h4>Stderr (real-time)</h4>
            <div class="log-controls">
                <button onclick="clearLog('stderr')" type="button">Clear</button>
                <button onclick="pauseScroll('stderr')" type="button">Pause Auto-Scroll</button>
            </div>
            <pre id="stderr_log"></pre>
        </div>
    </div>
</div>
<script>
function usageClass(percent) {
    if (percent < 60) return "usage-green";
    if (percent < 80) return "usage-yellow";
    if (percent < 90) return "usage-orange";
    return "usage-red";
}
function bgClass(percent) {
    if (percent < 60) return "bg-green";
    if (percent < 80) return "bg-yellow";
    if (percent < 90) return "bg-orange";
    return "bg-red";
}

let scrollPaused = {stdout: false, stderr: false};

function pauseScroll(which) {
    scrollPaused[which] = !scrollPaused[which];
    alert((scrollPaused[which] ? "Paused" : "Resumed") + " auto-scroll for " + which);
}

function clearLog(which) {
    fetch(`/clear_log/${which}`, {method: "POST"})
        .then(resp => {
            if (resp.ok) {
                document.getElementById(which + "_log").textContent = "";
            } else {
                alert("Failed to clear log file.");
            }
        });
}

function restartService() {
    fetch("/restart", {method: "POST"})
        .then(resp => {
            if (resp.ok) {
                alert("Service restart requested.");
            } else {
                alert("Failed to restart service.");
            }
        });
}

// Hardware info
function updateHardware() {
    fetch("/hardware").then(r => r.json()).then(data => {
        document.getElementById("hw_hostname").textContent = data.hostname || "—";
        document.getElementById("hw_os").textContent = data.os || "—";
        document.getElementById("hw_cpu").textContent = (data.cpu || "—") + (data.cpu_count ? ` (${data.cpu_count} cores)` : "");
        document.getElementById("hw_ram").textContent = data.ram_gb ? (data.ram_gb + " GB") : "—";
        document.getElementById("hw_gpu").textContent = (data.gpus && data.gpus.length) ? data.gpus.join(", ") : "—";
    });
}
updateHardware();

function updateStatus() {
    fetch("/metrics").then(r => r.json()).then(data => {
        document.getElementById("service_status").textContent = data.service_status;
        document.getElementById("memory_usage").textContent = data.memory_usage_mb.toFixed(1) + " MB";
        document.getElementById("cpu_usage").textContent = data.cpu_percent.toFixed(1) + " %";
        document.getElementById("ram_usage").textContent = data.ram_percent.toFixed(1) + " %";
        document.getElementById("cpu_usage").className = usageClass(data.cpu_percent);
        document.getElementById("ram_usage").className = usageClass(data.ram_percent);
        document.getElementById("memory_usage").className = usageClass((data.memory_usage_mb / 8192) * 100); // Example: scale to 8GB
    });
    fetch("/network").then(r => r.json()).then(data => {
        document.getElementById("network_up").textContent = (data.upload_rate/1024).toFixed(1) + " KB/s";
        document.getElementById("network_down").textContent = (data.download_rate/1024).toFixed(1) + " KB/s";
    });
}
setInterval(updateStatus, 2000);
updateStatus();


function updateDrives() {
    fetch("/drives").then(r => r.json()).then(data => {
        let html = "<tr><th>Device</th><th>Mount</th><th>Total</th><th>Used</th><th>Free</th><th>Usage</th></tr>";
        for (const d of data) {
            let usageClassName = usageClass(d.percent);
            let rowBg = bgClass(d.percent);
            let mountLink = d.mountpoint.replace(/\\\\/g, "/");
            if (!mountLink.endsWith("/")) mountLink += "/";
		html += `<tr class="${rowBg}">
    		<td>${d.device}</td>
    	<td>
        	<button onclick="copyMount('${d.mountpoint.replace(/\\\\/g, "/")}')">Copy Path</button>
        	<span style="margin-left:8px;">${d.mountpoint}</span>
    	</td>
    <td>${(d.total/1e9).toFixed(1)} GB</td>
    <td>${(d.used/1e9).toFixed(1)} GB</td>
    <td>${(d.free/1e9).toFixed(1)} GB</td>
    <td><span class="${usageClassName}">${d.percent}%</span></td>
</tr>`;

        }
        document.getElementById("drives_table").innerHTML = html;
    });
}
setInterval(updateDrives, 5000);
updateDrives();

function copyMount(mountPath) {
    navigator.clipboard.writeText(mountPath);
    alert("Mount path copied to clipboard!");
}

function updateTasks() {
    fetch("/tasks").then(r => r.json()).then(data => {
        let html = "<tr><th>PID</th><th>Name</th><th>User</th><th>CPU %</th><th>Memory (MB)</th></tr>";
        for (const p of data) {
            let cpuClass = usageClass(p.cpu);
            let memClass = usageClass(p.mem); // Optionally scale memory usage
            html += `<tr>
                <td>${p.pid}</td>
                <td>${p.name}</td>
                <td>${p.user || ""}</td>
                <td><span class="${cpuClass}">${p.cpu.toFixed(1)}</span></td>
                <td><span class="${memClass}">${p.mem.toFixed(1)}</span></td>
            </tr>`;
        }
        document.getElementById("tasks_table").innerHTML = html;
    });
}
setInterval(updateTasks, 3000);
updateTasks();

function startLogStream(which) {
    let logElem = document.getElementById(which + "_log");
    let es = new EventSource(`/stream/${which}`);
    es.onmessage = function(event) {
        logElem.textContent += event.data + "\\n";
        if (!scrollPaused[which]) {
            logElem.scrollTop = logElem.scrollHeight;
        }
    };
    es.onerror = function() {
        es.close();
        setTimeout(() => startLogStream(which), 2000);
    };
}
startLogStream('stdout');
startLogStream('stderr');
</script>
</body>
</html>
"""

# ---------- Helpers ----------
def service_running() -> bool:
    try:
        out = subprocess.check_output(["sc", "query", SERVICE_NAME], text=True)
        return "RUNNING" in out
    except subprocess.CalledProcessError:
        return False

def find_organizer_proc():
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline'] or []
                if any('organizer.py' in str(a) for a in cmdline):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def last_n_lines(path, n=200):
    if not os.path.exists(path):
        return "(log file not found)"
    with open(path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        block = 1024
        data = b''
        pos = size
        while pos > 0 and len(data.splitlines()) <= n:
            pos = max(0, pos - block)
            f.seek(pos)
            data = f.read(size - pos) + data
        lines = data.splitlines()[-n:]
        return b'\n'.join(lines).decode('utf-8', errors='replace')

def sse_stream(path):
    if not os.path.exists(path):
        while not os.path.exists(path):
            time.sleep(1)
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        f.seek(0, os.SEEK_END)
        while True:
            where = f.tell()
            line = f.readline()
            if not line:
                try:
                    cur_size = os.path.getsize(path)
                    if cur_size < where:
                        f.close()
                        time.sleep(0.5)
                        f = open(path, 'r', encoding='utf-8', errors='replace')
                        f.seek(0, os.SEEK_END)
                    else:
                        time.sleep(0.5)
                except Exception:
                    time.sleep(0.5)
                continue
            yield f"data: {line.rstrip()}\n\n"

# ---------- Routes ----------

@app.route("/")
def dashboard():
    return render_template_string(
        HTML,
        routes=config['routes'],
        memory_threshold=config['memory_threshold_mb'],
        cpu_threshold=config['cpu_threshold_percent'],
        logs_dir=config['logs_dir']
    )


@app.route("/update", methods=["POST"])
def update_config():
    new_routes = {}
    i = 1
    while True:
        folder_key = f"folder_{i}"
        exts_key = f"exts_{i}"
        delete_key = f"delete_{i}"
        if folder_key in request.form and exts_key in request.form:
            folder = request.form[folder_key].strip()
            exts = [e.strip() for e in request.form[exts_key].split(",") if e.strip()]
            if folder and delete_key not in request.form:
                new_routes[folder] = exts
            i += 1
        else:
            break
    new_folder = request.form.get("folder_new", "").strip()
    new_exts = request.form.get("exts_new", "").strip()
    if new_folder:
        new_routes[new_folder] = [e.strip() for e in new_exts.split(",") if e.strip()]
    mem = request.form.get("memory_threshold", str(config['memory_threshold_mb'])).strip()
    cpu = request.form.get("cpu_threshold", str(config['cpu_threshold_percent'])).strip()
    logs = request.form.get("logs_dir", config['logs_dir']).strip()
    try:
        config['memory_threshold_mb'] = int(mem)
    except ValueError:
        pass
    try:
        config['cpu_threshold_percent'] = int(cpu)
    except ValueError:
        pass
    if logs:
        config['logs_dir'] = logs
    config['routes'] = new_routes
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    global LOGS_DIR, STDOUT_LOG, STDERR_LOG
    LOGS_DIR = config['logs_dir']
    STDOUT_LOG = os.path.join(LOGS_DIR, "organizer_stdout.log")
    STDERR_LOG = os.path.join(LOGS_DIR, "organizer_stderr.log")
    return redirect("/")

@app.route("/metrics")
def metrics():
    running = service_running()
    mem_mb = 0.0
    cpu_pct = 0.0
    ram_pct = psutil.virtual_memory().percent
    proc = find_organizer_proc()
    global proc_cpu_cache
    if proc:
        try:
            # Use PID as key to cache last cpu_percent call
            pid = proc.pid
            if pid not in proc_cpu_cache:
                proc.cpu_percent(interval=None)  # Prime the measurement
                proc_cpu_cache[pid] = time.time()
                cpu_pct = 0.0
            else:
                cpu_pct = proc.cpu_percent(interval=0.2)
                proc_cpu_cache[pid] = time.time()
            mem_mb = proc.memory_info().rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return jsonify({
        "service_status": "Running" if running else "Stopped",
        "memory_usage_mb": mem_mb,
        "cpu_percent": cpu_pct,
        "ram_percent": ram_pct
    })


@app.route("/restart", methods=["POST"])
def restart_service():
    try:
        subprocess.run(["sc", "stop", SERVICE_NAME], capture_output=True, text=True)
        subprocess.run(["sc", "start", SERVICE_NAME], capture_output=True, text=True)
        return redirect("/")
    except Exception as e:
        return f"Restart failed: {e}", 500

@app.route("/tail/<which>")
def tail(which):
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    lines = int(request.args.get("lines", "200"))
    return last_n_lines(path, lines)

@app.route("/stream/<which>")
def stream(which):
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    return Response(sse_stream(path), mimetype="text/event-stream")

@app.route("/clear_log/<which>", methods=["POST"])
def clear_log(which):
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    try:
        with open(path, "w", encoding="utf-8"):
            pass  # Truncate file
        return "OK", 200
    except Exception as e:
        return f"Failed to clear log: {e}", 500

# --- Drive Space ---
@app.route("/drives")
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

# --- Network Usage ---

last_net = psutil.net_io_counters()
last_time = time.time()

@app.route("/network")
def network():
    global last_net, last_time
    now_net = psutil.net_io_counters()
    now_time = time.time()
    interval = now_time - last_time
    upload_rate = (now_net.bytes_sent - last_net.bytes_sent) / interval if interval > 0 else 0
    download_rate = (now_net.bytes_recv - last_net.bytes_recv) / interval if interval > 0 else 0
    last_net = now_net
    last_time = now_time
    return jsonify({
        "upload_rate": upload_rate,
        "download_rate": download_rate,
        "total_sent": now_net.bytes_sent,
        "total_recv": now_net.bytes_recv
    })


# --- Task Manager ---

@app.route("/tasks")
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
    return jsonify(procs[:5])  # Only top 5 by CPU usage

# --- OS ---

def get_windows_version():
    if sys.platform == "win32":
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            product_name, _ = winreg.QueryValueEx(key, "ProductName")
            display_version, _ = winreg.QueryValueEx(key, "DisplayVersion")
            return f"{product_name} {display_version}"
        except Exception:
            return platform.platform()
    else:
        return platform.platform()


# --- Hardware ---

import sys
import platform
import socket
import psutil

if sys.platform == "win32":
    import winreg

def get_cpu_name():
    if sys.platform == "win32":
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            return cpu_name.strip()
        except Exception:
            return platform.processor() or platform.machine()
    else:
        # For Linux/macOS, try /proc/cpuinfo or fallback
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return platform.processor() or platform.machine()

def get_windows_version():
    if sys.platform == "win32":
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            product_name, _ = winreg.QueryValueEx(key, "ProductName")
            display_version, _ = winreg.QueryValueEx(key, "DisplayVersion")
            return f"{product_name} {display_version}"
        except Exception:
            return platform.platform()
    else:
        return platform.platform()

def get_gpus():
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if not gpus:
            return ["No GPU detected"]
        return [f"{gpu.name} ({gpu.memoryTotal}MB)" for gpu in gpus]
    except Exception as e:
        return [f"GPUtil error: {e}"]

def get_ipv4():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return "Unavailable"

@app.route("/hardware")
def hardware():
    info = {
        "hostname": socket.gethostname(),
        "os": get_windows_version(),
        "cpu": get_cpu_name(),
        "cpu_count": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "ipv4": get_ipv4(),
        "gpus": get_gpus()
    }
    return jsonify(info)

# ---------- Main ----------

if __name__ == "__main__":
    print("✅ Dashboard running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)

