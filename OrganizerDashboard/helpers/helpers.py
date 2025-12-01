import os
import sys
import time
import psutil
import platform
import subprocess
import socket
import json

def update_log_paths():
    """Update global log paths based on config."""
    import sys
    main = sys.modules['__main__']
    main.LOGS_DIR = main.config.get("logs_dir", main.DEFAULT_CONFIG["logs_dir"])  # type: ignore
    main.STDOUT_LOG = os.path.join(main.LOGS_DIR, "organizer_stdout.log")  # type: ignore
    main.STDERR_LOG = os.path.join(main.LOGS_DIR, "organizer_stderr.log")  # type: ignore

def service_running() -> bool:
    """Check if the DownloadsOrganizer service is running."""
    import sys
    main = sys.modules['__main__']
    if sys.platform != "win32":
        proc = find_organizer_proc()
        return proc is not None
    try:
        out = subprocess.check_output(["sc", "query", main.SERVICE_NAME], text=True)
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
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return platform.processor() or platform.machine()

def get_gpus():
    try:
        output = subprocess.check_output(
            ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
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
        import requests  # type: ignore
        return requests.get("https://api.ipify.org").text
    except Exception:
        return "Unavailable"

def find_organizer_proc():
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline'] or []
                if any('organizer.py' in str(a).lower() for a in cmdline):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def last_n_lines_normalized(path, n=200):
    if not os.path.exists(path):
        return "(log file not found)"
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()[-n:]
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

def load_dashboard_json():
    DASHBOARD_JSON = "C:\\Scripts\\downloads_dashboard.json"
    try:
        with open(DASHBOARD_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return {}
