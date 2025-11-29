
from flask import Flask, render_template_string, request, redirect, Response, jsonify
import os
import json
import time
import psutil
import platform
import subprocess
import socket
import sys
from functools import wraps

"""OrganizerDashboard

Flask-based dashboard to monitor and control the DownloadsOrganizer service.
This module exposes JSON endpoints used by the UI (AJAX) and renders a
single-page dashboard with controls, logs, and configuration.
"""

# --- Authentication ---

import os
ADMIN_USER = os.environ.get("DASHBOARD_USER", "admin")
ADMIN_PASS = os.environ.get("DASHBOARD_PASS", "change_this_password")
def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS


def authenticate():
    return Response(
        'Authentication required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- Service and Config ---
SERVICE_NAME = "DownloadsOrganizer"
CONFIG_FILE = "organizer_config.json"

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

# If credentials are stored in the config file, prefer them (persisted change-password support)
if isinstance(config, dict):
    dashboard_user = config.get("dashboard_user")
    dashboard_pass = config.get("dashboard_pass")
    if dashboard_user:
        ADMIN_USER = dashboard_user
    if dashboard_pass:
        ADMIN_PASS = dashboard_pass

def update_log_paths():
    global LOGS_DIR, STDOUT_LOG, STDERR_LOG
    LOGS_DIR = config.get("logs_dir", DEFAULT_CONFIG["logs_dir"])
    STDOUT_LOG = os.path.join(LOGS_DIR, "organizer_stdout.log")
    STDERR_LOG = os.path.join(LOGS_DIR, "organizer_stderr.log")

update_log_paths()

app = Flask(__name__)


# --- HTML Template ---

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organizer Service Dashboard</title>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <style>
        body { background: #f8f9fa; }
        .dashboard-title { margin: 30px 0; }
        .card { margin-bottom: 20px; }
        .table th, .table td { vertical-align: middle; }
        .config-label { font-weight: bold; }
        .config-input { width: 120px; }
        .progress { height: 20px; border-radius: 10px; }
        .progress-bar {
            font-size: 12px;
            line-height: 20px;
            transition: width 0.8s ease-in-out; /* Smooth animation */
        }
    </style>
</head>
<body>
<div class="container">
    <h1 class="dashboard-title text-center">Organizer Service Dashboard</h1>
    <div class="text-end mb-2">
        <button id="login-btn" class="btn btn-outline-primary btn-sm" onclick="promptLogin()">Login</button>
        <button id="logout-btn" class="btn btn-outline-secondary btn-sm d-none" onclick="logout()">Logout</button>
    </div>

    <!-- System Info / Service Status / Network -->
    <div class="row">
        <!-- System Info -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">System Info</div>
                <div class="card-body">
                    <ul class="list-unstyled mb-0">
                        <li><b>Hostname:</b> {{ hostname }}</li>
                        <li><b>OS:</b> {{ os }}</li>
                        <li><b>CPU:</b> {{ cpu }}</li>
                        <li><b>RAM:</b> {{ ram_gb }} GB</li>
                        <li><b>GPU:</b> {{ gpu }}</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Service Status -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">Service Status</div>
                <div class="card-body text-center">
                    <span id="service-badge" class="badge bg-{{ 'success' if service_status == 'Running' else 'danger' }}">
                        {{ service_status }}
                    </span>
                    <div class="d-flex justify-content-center gap-2 mt-3">
                        <button class="btn btn-success btn-sm" onclick="serviceAction('start')">Start</button>
                        <button class="btn btn-warning btn-sm" onclick="serviceAction('stop')">Stop</button>
                        <button class="btn btn-primary btn-sm" onclick="serviceAction('restart')">Restart</button>
                    </div>
                    <div class="mt-3">
                        <a href="https://www.speedtest.net/" target="_blank" class="btn btn-outline-secondary btn-sm">Speed Test</a>
                        <a href="https://github.com/Atomsk865/DownloadsOrganizeR" target="_blank" class="btn btn-outline-dark btn-sm">GitHub Repo</a>
                    </div>
                </div>
            </div>
        </div>

        <!-- Network -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">Network</div>
                <div class="card-body">
                    <ul class="list-unstyled mb-0">
                        <li><b>Private IP:</b> {{ private_ip }}</li>
                        <li><b>Public IP:</b> {{ public_ip }}</li>
                        <li><b>Up:</b> {{ upload_rate_kb }} KB/s ({{ upload_rate_mb }} MB/s)</li>
                        <li><b>Down:</b> {{ download_rate_kb }} KB/s ({{ download_rate_mb }} MB/s)</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Resource Usage with Animated Bars -->
    <div class="row">
        <!-- Memory Usage -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">Memory Usage</div>
                <div class="card-body">
                    <p><b>Service:</b> {{ service_memory_mb }} MB</p>
                    <p><b>System:</b> {{ total_memory_mb }} MB / {{ total_memory_gb }} GB</p>
                    <div class="progress">
                        <div class="progress-bar bg-{{ 'success' if ram_percent < 50 else 'warning' if ram_percent < 80 else 'danger' }}"
                             role="progressbar"
                             style="width: {{ ram_percent }}%;">
                            {{ ram_percent }}%
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- CPU Usage -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">CPU Usage</div>
                <div class="card-body">
                    <p><b>Service:</b> {{ service_cpu_percent }}%</p>
                    <p><b>System:</b> {{ total_cpu_percent }}%</p>
                    <div class="progress">
                        <div class="progress-bar bg-{{ 'success' if total_cpu_percent < 50 else 'warning' if total_cpu_percent < 80 else 'danger' }}"
                             role="progressbar"
                             style="width: {{ total_cpu_percent }}%;">
                            {{ total_cpu_percent }}%
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- RAM Usage -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">RAM Usage</div>
                <div class="card-body">
                    <div class="progress">
                        <div class="progress-bar bg-{{ 'success' if ram_percent < 50 else 'warning' if ram_percent < 80 else 'danger' }}"
                             role="progressbar"
                             style="width: {{ ram_percent }}%;">
                            {{ ram_percent }}%
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Drive Space -->
    <div class="card">
        <div class="card-header">Drive Space</div>
        <div class="card-body">
            <table class="table table-bordered table-sm">
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Total</th>
                        <th>Used</th>
                        <th>Free</th>
                        <th>Usage</th>
                    </tr>
                </thead>
                <tbody>
                    {% for drive in drives %}
                    <tr>
                        <td>{{ drive.device }}</td>
                        <td>{{ drive.total }}</td>
                        <td>{{ drive.used }}</td>
                        <td>{{ drive.free }}</td>
                        <td>
                            <div class="progress">
                                <div class="progress-bar bg-{{ 'success' if drive.percent < 50 else 'warning' if drive.percent < 80 else 'danger' }}"
                                     role="progressbar"
                                     style="width: {{ drive.percent }}%;">
                                    {{ drive.percent }}%
                                </div>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Task Manager -->
    <div class="card">
        <div class="card-header">Task Manager (Top 5 by CPU)</div>
        <div class="card-body">
            <table class="table table-bordered table-sm">
                <thead>
                    <tr>
                        <th>PID</th>
                        <th>Name</th>
                        <th>User</th>
                        <th>CPU (%)</th>
                        <th>Memory (MB)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for proc in tasks %}
                    <tr>
                        <td>{{ proc.pid }}</td>
                        <td>{{ proc.name }}</td>
                        <td>{{ proc.user }}</td>
                        <td>{{ proc.cpu }}</td>
                        <td>{{ proc.mem }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Configuration -->

<div class="card">
    <div class="card-header">Configuration</div>
    <div class="card-body">
<form id="config-form">
    <table class="table table-bordered table-sm">
        <thead>
            <tr>
                <th>Folder</th>
                <th>Extensions (comma-separated)</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            <!-- Images -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_1" value="Images"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_1"
                        value="jpg, jpeg, png, gif, bmp, tiff, svg, webp, heic, ico, raw, psd, ai, eps">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Music -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_2" value="Music"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_2"
                        value="mp3, wav, flac, aac, ogg, wma, m4a, alac, aiff, opus, amr, mid, midi">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Videos -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_3" value="Videos"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_3"
                        value="mp4, mkv, avi, mov, wmv, flv, webm, mpeg, mpg, m4v, 3gp, vob, ogv, ts, mts, m2ts">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Documents -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_4" value="Documents"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_4"
                        value="pdf, doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx, csv, md, tex, epub, mobi, pages, numbers, key">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Archives -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_5" value="Archives"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_5"
                        value="zip, rar, 7z, tar, gz, bz2, xz, iso, cab, arj, lzh, ace, uue, jar, tar.gz, tar.bz2">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Executables -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_6" value="Executables"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_6"
                        value="exe, msi, bat, cmd, ps1, sh, app, deb, rpm, apk, com, bin, run">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Shortcuts -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_7" value="Shortcuts"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_7"
                        value="lnk, url, desktop, webloc">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Scripts -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_8" value="Scripts"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_8"
                        value="py, js, html, css, json, xml, sh, ts, php, rb, pl, swift, go, c, cpp, cs, java, scala, lua, r, ipynb, jsx, tsx">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Fonts -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_9" value="Fonts"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_9"
                        value="ttf, otf, woff, woff2, fon, fnt, eot, svg">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Logs -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_10" value="Logs"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_10"
                        value="log, out, err">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Other -->
            <tr>
                <td><input class="form-control form-control-sm" type="text" name="folder_11" value="Other"></td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_11" value="">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" type="button" onclick="deleteRow(this)">Delete</button>
                </td>
            </tr>
            <!-- Add new -->
            <tr>
                <td>
                    <input class="form-control form-control-sm" type="text" name="folder_new" placeholder="New folder">
                </td>
                <td>
                    <input class="form-control form-control-sm" type="text" name="exts_new" placeholder="Extensions">
                </td>
                <td></td>
            </tr>
        </tbody>
    </table>
    <div class="mb-2">
        <label class="config-label">Memory Threshold (MB):</label>
        <input class="config-input form-control form-control-sm d-inline-block" type="number" name="memory_threshold" value="{{ memory_threshold }}">
    </div>
    <div class="mb-2">
        <label class="config-label">CPU Threshold (%):</label>
        <input class="config-input form-control form-control-sm d-inline-block" type="number" name="cpu_threshold" value="{{ cpu_threshold }}">
    </div>
    <div class="mb-2">
        <label class="config-label">Logs Directory:</label>
        <input class="config-input form-control form-control-sm d-inline-block" type="text" name="logs_dir" value="{{ logs_dir }}">
    </div>
    <button class="btn btn-primary btn-sm" type="button" onclick="saveConfiguration()">Save Configuration</button>
    </button>
    </form>
    </div>
</div>


    <!-- Logs -->
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">Stdout (real-time)</div>
                <div class="card-body">
                    <button class="btn btn-secondary btn-sm" onclick="clearLog('stdout')">Clear</button>
                    <pre id="stdout-log">{{ stdout_log }}</pre>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">Stderr (real-time)</div>
                <div class="card-body">
                    <button class="btn btn-secondary btn-sm" onclick="clearLog('stderr')">Clear</button>
                    <pre id="stderr-log">{{ stderr_log }}</pre>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
// Simple client-side Basic Auth support for AJAX calls.
// The server still enforces authentication, but fetch() won't trigger
// the browser login dialog. We capture credentials once and attach a
// Basic Authorization header to all protected requests.
let __authHeader = null;
function promptLogin() {
    const user = prompt('Username:', 'admin');
    if (!user) return;
    const pass = prompt('Password:');
    if (pass === null) return;
    __authHeader = 'Basic ' + btoa(`${user}:${pass}`);
    // Verify credentials by calling a lightweight protected endpoint
    fetch('/metrics', { headers: getAuthHeaders() })
        .then(r => {
            if (!r.ok) throw new Error('Invalid credentials');
            // If user logged in with the default password, prompt to change it
            const DEFAULT_PASS = 'change_this_password';
            if (pass === DEFAULT_PASS) {
                // Force change
                let np = prompt('Please choose a new dashboard password:');
                if (!np) {
                    showNotification('Password change required to proceed', 'warning');
                    // Still mark logged in visually, but require change for sensitive actions
                    document.getElementById('login-btn').classList.add('d-none');
                    document.getElementById('logout-btn').classList.remove('d-none');
                    return;
                }
                let np2 = prompt('Confirm new password:');
                if (np !== np2) {
                    showNotification('Passwords did not match; try logging in again', 'danger');
                    return;
                }
                // Call server to update the password (requires current auth)
                fetch('/change_password', {
                    method: 'POST',
                    headers: Object.assign({'Content-Type': 'application/json'}, getAuthHeaders()),
                    body: JSON.stringify({ new_password: np })
                }).then(r2 => {
                    if (r2.ok) {
                        // Update auth header with new password
                        __authHeader = 'Basic ' + btoa(`${user}:${np}`);
                        document.getElementById('login-btn').classList.add('d-none');
                        document.getElementById('logout-btn').classList.remove('d-none');
                        showNotification('Password changed and logged in', 'success');
                    } else {
                        showNotification('Failed to change password', 'danger');
                    }
                }).catch(err => {
                    showNotification('Error changing password: ' + err.message, 'danger');
                });
            } else {
                document.getElementById('login-btn').classList.add('d-none');
                document.getElementById('logout-btn').classList.remove('d-none');
                showNotification('Logged in (credentials stored in session)', 'success');
            }
        })
        .catch(err => {
            showNotification('Login failed: ' + err.message, 'danger');
            __authHeader = null;
        });
}
function logout() {
    __authHeader = null;
    document.getElementById('login-btn').classList.remove('d-none');
    document.getElementById('logout-btn').classList.add('d-none');
    showNotification('Logged out', 'info');
}
function getAuthHeaders() {
    return __authHeader ? { 'Authorization': __authHeader } : {};
}
// Service Control Functions
async function serviceAction(action) {
    const button = event.target;
    button.disabled = true;
    try {
        if (!__authHeader) {
            showNotification('Please login before performing service actions', 'warning');
            return;
        }
        const response = await fetch(`/${action}`, {
            method: 'POST',
            credentials: 'include',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            showNotification(`Service ${action}ed successfully`, 'success');
            // Update service status badge
            setTimeout(updateServiceStatus, 1000);
        } else {
            showNotification(`Failed to ${action} service`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    } finally {
        button.disabled = false;
    }
}

// Update service status
async function updateServiceStatus() {
    try {
        const response = await fetch('/metrics');
        const data = await response.json();
        const badge = document.getElementById('service-badge');
        const statusClass = data.service_status === 'Running' ? 'bg-success' : 'bg-danger';
        badge.textContent = data.service_status;
        badge.className = `badge ${statusClass}`;
    } catch (error) {
        console.error('Error updating service status:', error);
    }
}

// Configuration Save
async function saveConfiguration() {
    const form = document.getElementById('config-form');
    const formData = new FormData(form);
    
    try {
        if (!__authHeader) {
            showNotification('Please login before saving configuration', 'warning');
            return;
        }
        const response = await fetch('/update', {
            method: 'POST',
            body: formData,
            credentials: 'include',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            showNotification('Configuration saved successfully', 'success');
        } else {
            showNotification('Failed to save configuration', 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

// Delete row
function deleteRow(button) {
    const row = button.closest('tr');
    const folder = row.querySelector('input[name^="folder_"]');
    if (folder && folder.value) {
        row.remove();
    }
}

// Clear logs
async function clearLog(which) {
    try {
        if (!__authHeader) {
            showNotification('Please login before clearing logs', 'warning');
            return;
        }
        const response = await fetch(`/clear_log/${which}`, {
            method: 'POST',
            credentials: 'include',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            const logElement = document.getElementById(`${which}-log`);
            logElement.textContent = '';
            showNotification(`${which.toUpperCase()} log cleared`, 'success');
        } else {
            showNotification(`Failed to clear ${which} log`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

// Show notification
function showNotification(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
</script>
</body>
</html>
"""


# --- Helper Functions ---
def service_running() -> bool:
    # On non-Windows platforms the `sc` tool is not available. Fall back to
    # detecting the organizer process by name so the dashboard can run in
    # containers for preview/testing.
    if sys.platform != "win32":
        proc = find_organizer_proc()
        return proc is not None
    try:
        out = subprocess.check_output(["sc", "query", SERVICE_NAME], text=True)
        return "RUNNING" in out
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def get_windows_version():
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
            product_name, _ = winreg.QueryValueEx(key, "ProductName")
            display_version, _ = winreg.QueryValueEx(key, "DisplayVersion")
            build_number, _ = winreg.QueryValueEx(key, "CurrentBuildNumber")
            if int(build_number) >= 22000:
                product_name = product_name.replace("Windows 10", "Windows 11")
            return f"{product_name} {display_version}"
        except Exception:
            return platform.platform()
    else:
        return platform.platform()

def get_cpu_name():
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0")
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
        except Exception as e:
            print(f"Exception: {e}")
        return platform.processor() or platform.machine()
        

import subprocess

def get_gpus():
    try:
        output = subprocess.check_output(
            ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        # Skip the header and empty lines
        gpus = [line.strip() for line in output.split('\n') if line.strip() and 'Name' not in line]
        return gpus
    except Exception:
        return []


def get_private_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return "Unavailable"

def get_public_ip():
    try:
        import requests
        return requests.get("https://api.ipify.org").text
    except Exception:
        return "Unavailable"

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

def last_n_lines_normalized(path, n=200):
    if not os.path.exists(path):
        return "(log file not found)"
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()[-n:]
    # Normalize: strip whitespace, replace any internal newlines in each line
    normalized = [line.replace('\n', ' ').replace('\r', '').strip() for line in lines]
    return '\n'.join(normalized)

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

def format_bytes(num):
    """Convert bytes to GB or TB as a string with 2 decimals."""
    num = float(num)
    gb = num / (1024 ** 3)
    if gb < 1024:
        return f"{gb:.2f} GB"
    tb = gb / 1024
    return f"{tb:.2f} TB"
    
    
import json

DASHBOARD_JSON = "C:\\Scripts\\downloads_dashboard.json"

def load_dashboard_json():
    try:
        with open(DASHBOARD_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return {}



# --- Flask Routes ---

@app.route("/")
def dashboard():
    dashboard_data = load_dashboard_json()
    try:
        # System Info
        hostname = socket.gethostname()
        os_version = get_windows_version()
        cpu_name = get_cpu_name()
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        
        try:
            gpu_list = get_gpus()
            gpu = " / ".join(gpu_list) if gpu_list else "N/A"
        except Exception:
            gpu = "N/A"

        # Service Status
        service_status = "Running" if service_running() else "Stopped"

        # Service process info
        service_memory_mb = 0
        service_cpu_percent = 0
        proc = find_organizer_proc()
        if proc:
            try:
                service_cpu_percent = proc.cpu_percent(interval=0.2)
                service_memory_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
            except Exception:
                pass

        # System memory/cpu
        total_memory_mb = round(psutil.virtual_memory().used / (1024 * 1024), 2)
        total_memory_gb = round(psutil.virtual_memory().total / (1024 * 1024 * 1024), 2)
        total_cpu_percent = psutil.cpu_percent(interval=0.2)
        ram_percent = psutil.virtual_memory().percent

        # Network info (dummy values, replace with real if you track deltas)
        upload_rate_kb = 0
        upload_rate_mb = 0
        download_rate_kb = 0
        download_rate_mb = 0

        private_ip = get_private_ip()
        public_ip = get_public_ip()

        # Drives info (now formatted in GB/TB)
        drives = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                drives.append({
                    "device": part.device,
                #    "mountpoint": part.mountpoint,
                    "total": format_bytes(usage.total),
                    "used": format_bytes(usage.used),
                    "free": format_bytes(usage.free),
                    "percent": usage.percent
                })
            except Exception:
                continue

        # Tasks info (top 5 by CPU)
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
                    "mem": round(proc.info['memory_info'].rss / (1024*1024), 2)
                })
            except Exception:
                continue
        procs.sort(key=lambda x: x['cpu'], reverse=True)
        tasks = procs[:5]

        # Logs (last 50 lines)
        stdout_log = last_n_lines_normalized(STDOUT_LOG, 50)
        stderr_log = last_n_lines_normalized(STDERR_LOG, 50)

        # Render the dashboard
        return render_template_string(
            HTML,
            hostname=hostname,
            os=os_version,
            cpu=cpu_name,
            ram_gb=ram_gb,
            gpu=gpu,
            service_status=service_status,
            service_memory_mb=service_memory_mb,
            total_memory_mb=total_memory_mb,
            total_memory_gb=total_memory_gb,
            service_cpu_percent=service_cpu_percent,
            total_cpu_percent=total_cpu_percent,
            ram_percent=ram_percent,
            private_ip=private_ip,
            public_ip=public_ip,
            upload_rate_kb=upload_rate_kb,
            upload_rate_mb=upload_rate_mb,
            download_rate_kb=download_rate_kb,
            download_rate_mb=download_rate_mb,
            drives=drives,
            tasks=tasks,
            routes=config['routes'],
            memory_threshold=config['memory_threshold_mb'],
            cpu_threshold=config['cpu_threshold_percent'],
            logs_dir=config['logs_dir'],
            stdout_log=stdout_log,
            stderr_log=stderr_log
        )
    except Exception as e:
        # Show error in browser for debugging
        return f"<pre>Dashboard error: {e}</pre>", 500


@app.route("/update", methods=["POST"])
@requires_auth
def update_config():
    """Update configuration routes and thresholds.

    Expects form-encoded data from the UI. Returns JSON with status and
    message so the frontend can give immediate feedback without a full
    page reload.
    """
    new_routes = {}
    i = 1
    while True:
        folder_key = f"folder_{i}"
        exts_key = f"exts_{i}"
        if folder_key in request.form and exts_key in request.form:
            folder = request.form[folder_key].strip()
            exts = [e.strip() for e in request.form[exts_key].split(",") if e.strip()]
            if folder:
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
        return jsonify({"status": "error", "message": "Invalid memory threshold value"}), 400
    try:
        config['cpu_threshold_percent'] = int(cpu)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid CPU threshold value"}), 400
    if logs:
        config['logs_dir'] = logs
    config['routes'] = new_routes
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    update_log_paths()
    return jsonify({"status": "success", "message": "Configuration saved"}), 200

@app.route("/metrics")
def metrics():
    running = service_running()
    mem_mb = 0.0
    cpu_pct = 0.0
    ram_pct = psutil.virtual_memory().percent
    proc = find_organizer_proc()
    if proc:
        try:
            cpu_pct = proc.cpu_percent(interval=0.2)
            mem_mb = proc.memory_info().rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return jsonify({
        "service_status": "Running" if running else "Stopped",
        "service_memory_mb": mem_mb,
        "total_memory_mb": psutil.virtual_memory().used / (1024 * 1024),
        "total_memory_gb": psutil.virtual_memory().total / (1024 * 1024 * 1024),
        "service_cpu_percent": cpu_pct,
        "total_cpu_percent": psutil.cpu_percent(interval=0.2),
        "ram_percent": ram_pct
    })

@app.route("/restart", methods=["POST"])
@requires_auth
def restart_service():
    """Restart the Windows service using `sc`.

    On non-Windows platforms this returns an error JSON since `sc` is not
    available. Returns JSON status/messages for AJAX consumption.
    """
    if sys.platform != "win32":
        return jsonify({"status": "error", "message": "Service control unsupported on this platform"}), 400
    try:
        subprocess.run(["sc", "stop", SERVICE_NAME], capture_output=True, text=True)
        subprocess.run(["sc", "start", SERVICE_NAME], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "Service restarted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Restart failed: {e}"}), 500

@app.route("/stop", methods=["POST"])
@requires_auth
def stop_service():
    """Stop the Windows service and return JSON result.

    Returns an error JSON on non-Windows platforms.
    """
    if sys.platform != "win32":
        return jsonify({"status": "error", "message": "Service control unsupported on this platform"}), 400
    try:
        subprocess.run(["sc", "stop", SERVICE_NAME], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "Service stopped"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Stop failed: {e}"}), 500

@app.route("/start", methods=["POST"])
@requires_auth
def start_service():
    """Start the Windows service and return JSON result.

    Returns an error JSON on non-Windows platforms.
    """
    if sys.platform != "win32":
        return jsonify({"status": "error", "message": "Service control unsupported on this platform"}), 400
    try:
        subprocess.run(["sc", "start", SERVICE_NAME], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "Service started"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Start failed: {e}"}), 500

@app.route("/tail/<which>")
def tail(which):
    if which not in ("stdout", "stderr"):
        return "Invalid log type", 400
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    lines = int(request.args.get("lines", "200"))
    return last_n_lines_normalized(path, lines)

@app.route("/stream/<which>")
def stream(which):
    if which not in ("stdout", "stderr"):
        return "Invalid log type", 400
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    return Response(sse_stream(path), mimetype="text/event-stream")

@app.route("/clear_log/<which>", methods=["POST"])
@requires_auth
def clear_log(which):
    """Clear the specified log file (stdout or stderr).

    Returns JSON success/error so the frontend can update the UI.
    """
    if which not in ("stdout", "stderr"):
        return jsonify({"status": "error", "message": "Invalid log type"}), 400
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    try:
        # Truncate the logfile
        with open(path, "w", encoding="utf-8"):
            pass
        return jsonify({"status": "success", "message": f"{which} log cleared"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to clear log: {e}"}), 500


@app.route("/change_password", methods=["POST"])
@requires_auth
def change_password():
    """Change the dashboard password and persist it to the config file.

    Expects JSON: { "new_password": "..." }
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    new = data.get("new_password") if isinstance(data, dict) else None
    if not new:
        return jsonify({"status": "error", "message": "Missing new_password"}), 400
    # Persist to config and update runtime ADMIN_PASS
    try:
        config['dashboard_user'] = ADMIN_USER
        config['dashboard_pass'] = new
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        global ADMIN_PASS
        ADMIN_PASS = new
        return jsonify({"status": "success", "message": "Password changed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save password: {e}"}), 500

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
    upload_rate_b = (now_net.bytes_sent - last_net.bytes_sent) / interval if interval > 0 else 0
    download_rate_b = (now_net.bytes_recv - last_net.bytes_recv) / interval if interval > 0 else 0
    last_net = now_net
    last_time = now_time
    # Convert to KB/s and MB/s
    upload_rate_kb = upload_rate_b / 1024
    download_rate_kb = download_rate_b / 1024
    upload_rate_mb = upload_rate_b / (1024 * 1024)
    download_rate_mb = download_rate_b / (1024 * 1024)
    return jsonify({
        "upload_rate_b": upload_rate_b,
        "download_rate_b": download_rate_b,
        "upload_rate_kb": upload_rate_kb,
        "download_rate_kb": download_rate_kb,
        "upload_rate_mb": upload_rate_mb,
        "download_rate_mb": download_rate_mb,
        "total_sent": now_net.bytes_sent,
        "total_recv": now_net.bytes_recv
    })

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

@app.route("/hardware")
def hardware():
    info = {
        "hostname": socket.gethostname(),
        "os": get_windows_version(),
        "cpu": get_cpu_name(),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "private_ip": get_private_ip(),
        "public_ip": get_public_ip()
    }
    return jsonify(info)

# --- Main Entry Point ---
if __name__ == "__main__":
    print("✅ Dashboard running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)
