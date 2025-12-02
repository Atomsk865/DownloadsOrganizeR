# DownloadsOrganizeR 📦

Automated, real-time organization of your Downloads folder plus a role-aware web dashboard for monitoring, configuration, and service control.

---

## Quick Start (5 minutes)

### Option 1: Automated Service Installation (Recommended)

1. **Install Python** if you haven't already ([python.org](https://www.python.org/downloads/))

1. **Download this repository** or clone it:

```bash
git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
cd DownloadsOrganizeR
```

1. **Run the installer** (Right-click PowerShell → Run as Administrator):

  ```powershell
  .\Install-And-Monitor-OrganizerService.ps1
  ```

1. **Done!** The service will start automatically on boot and organize your Downloads in real-time.

### Option 2: Manual Run (No Service)


```powershell
cd DownloadsOrganizeR
pip install -r requirements.txt
python Organizer.py
```

---

## Dashboard 📊

Monitor, configure, and customize layout & access control from the web dashboard:


```bash
pip install -r requirements.txt
python OrganizerDashboard.py
```

Then open: <http://localhost:5000>

### Default credentials (Dashboard)

- **Username:** `admin`
- **Password:** `change_this_password`

You can override these by setting environment variables before launching the dashboard:


```bash
export DASHBOARD_USER=myusername
export DASHBOARD_PASS=mypassword
python OrganizerDashboard.py
```

### Dashboard Features

- 🔍 Real-time service monitoring & control (rights gated)
- 📈 CPU, RAM, network usage & top processes
- 🧩 Drag-and-drop dashboard layout editor (`/config`)
- 👥 User & role management (admin/operator/viewer)
- ⚙️ File organization rule editor
- 📋 Live stdout/stderr log streaming & clearing
- 💾 Drive space overview & hardware info
- 🪪 Multiple authentication methods (Basic, LDAP, Windows) with fallback
- 🛡️ Rights-based route protection (`manage_service`, `manage_config`, `modify_layout`, `view_metrics`, `view_recent_files`, `send_reports`)
- 📂 Recent File Movements - View and manage recently organized files with quick actions (open, reveal, remove)
- 🔗 User Links - Create custom quick-access links with categories and descriptions
- 📊 Reports & Analytics - Comprehensive file organization reports with advanced filtering:
  - Date range filtering (today, yesterday, last 7/30 days, custom range)
  - Category filtering (Images, Videos, Documents, etc.)
  - File size analysis and storage usage
  - Organization pattern insights
  - Export capabilities

### Authentication & Authorization Options

Supported auth methods:

1. **Basic** (Default) – Bcrypt hashed password (admin + additional configured users)
2. **LDAP/Active Directory** – Bind + optional group filtering
3. **Windows Local/Domain** – Native logon (Windows only)

If the primary method fails and fallback is enabled, Basic authentication is attempted.

Configure via `organizer_config.json` or `/api/auth/settings`:

```json
{
  "auth_method": "basic",  // or "ldap" or "windows"
  "auth_fallback_enabled": true
}
```

📖 **See [AUTHENTICATION.md](AUTHENTICATION.md) for complete setup guide**  
⚡ **See [AUTH_QUICK_REFERENCE.md](AUTH_QUICK_REFERENCE.md) for quick commands**

---

## What Gets Organized?

Files are automatically sorted into folders by type:

| Category | File Types |
|----------|-----------|
| **Images** | jpg, png, gif, svg, webp, heic, psd, ai, ... |
| **Videos** | mp4, mkv, avi, mov, wmv, webm, flv, ... |
| **Music** | mp3, wav, flac, aac, ogg, wma, m4a, ... |
| **Documents** | pdf, doc, docx, txt, excel, ppt, csv, ... |
| **Archives** | zip, rar, 7z, tar, gz, iso, ... |
| **Executables** | exe, msi, bat, cmd, ps1, app, ... |
| **Scripts** | py, js, html, css, json, xml, ts, php, ... |
| **Fonts** | ttf, otf, woff, eot, ... |
| **Shortcuts** | lnk, url, webloc, ... |
| **Logs** | log, out, err |
| **Other** | Everything else |

---

## Configuration

### File Organization Rules

Dashboard main page: modify categories in the "File Categories" section and click Save. Persisted to `organizer_config.json`.

### Dashboard User / Role / Layout Configuration

Navigate to `/config` after login:

- Add/update/delete non-primary users (bcrypt-hashed passwords)
- Assign roles (admin/operator/viewer) with predefined rights
- Drag to reorder sections; hide with checkboxes; save persists to `dashboard_config.json`

### Watch Folders & VirusTotal

- `watch_folders`: Absolute paths the Organizer monitors. Configure during Setup (Recommended Watch Folders) or later under Configuration → Watched Folders. Used by `Organizer.py` to start filesystem observers and for initial scans.
- `vt_api_key`: VirusTotal v3 API key for hash lookups. Configure during Setup or under Configuration → Features & Integrations. When present and enabled, Recent Files shows a “Scan with VirusTotal” button and a detailed modal; responses are cached to `./config/json/vt_cache.json`.

Feature toggles: When a feature is disabled in `features` (e.g., `virustotal_enabled`, `duplicates_enabled`, `reports_enabled`), related UI controls are hidden or show a small disabled notice, and API endpoints return empty data or a 400 error where appropriate.

Example `organizer_config.json` snippet:

```json
{
  "watch_folders": [
    "C:/Users/YourName/Downloads",
    "/home/youruser/Downloads"
  ],
  "vt_api_key": "YOUR_VIRUSTOTAL_API_KEY",
  "features": {
    "virustotal_enabled": true,
    "duplicates_enabled": true,
    "reports_enabled": true
  },
  "file_moves_json": "./config/json/file_moves.json",
  "file_hashes_json": "./config/json/file_hashes.json",
  "vt_cache_json": "./config/json/vt_cache.json",
  "logs_dir": "./logs"
}
```

See Configuration → Features & Integrations in the dashboard to adjust these at any time.


### Environment Variables (Primary Admin Credentials)

Set before starting `OrganizerDashboard.py` to override defaults:

```bash
set DASHBOARD_USER=myusername
set DASHBOARD_PASS=mypassword
python OrganizerDashboard.py
```

---

## Troubleshooting

### Service won't start?

- Check service logs (NSSM): `C:\<InstallDir>\service-logs\organizer_stdout.log`
- Ensure Python is in PATH: `python --version`
- Try running manually from install directory: `cd C:\<InstallDir> && python Organizer.py`

### Dashboard won't connect?

- Verify service is running: Check Windows Services
- Ensure port 5000 is available: `netstat -ano | findstr :5000`
- Check firewall settings

### Files not organizing?

- Check the organizer log: `./logs/organizer.log`
- Verify routes/categories in `organizer_config.json`
- Ensure destination folders are writable
- Confirm JSON state paths exist: `./config/json/` (created automatically)

---

## Uninstall

Remove the Windows service:

```powershell
nssm remove DownloadsOrganizer confirm
```

Then delete the installed organizer directory (e.g., `C:\<InstallDir>`) if desired.

---

## Requirements

- **Windows** (Service installation only, dashboard works cross-platform)
- **Python 3.7+**
- **Dependencies:**

```text
watchdog==6.0.0     # File monitoring
Flask==3.1.2        # Dashboard web framework
psutil==7.1.3       # System metrics
bcrypt==4.0.1       # Password hashing
gputil==1.4.0       # GPU info (optional)
ldap3==2.9.1        # LDAP authentication (optional)
pywin32==306        # Windows authentication (Windows only, optional)
flask-login==0.6.3  # Session management
```

---

## File Structure

```text
DownloadsOrganizeR/
├── Organizer.py                          # Core file system watcher & mover
├── OrganizerDashboard.py                 # Flask dashboard entry point
├── dashboard_config.json                 # Dashboard users/roles/layout (generated)
├── organizer_config.json                 # Organizer routing & thresholds
├── Install-And-Monitor-OrganizerService.ps1  # Windows service installer
├── Monitor-OrganizerService.ps1          # Generated health monitor script
├── OrganizerDashboard/                   # Dashboard blueprints & auth helpers
├── dash/                                 # Jinja2 templates (dashboard & config)
├── requirements.txt                      # Python dependencies
└── readme.md                             # Project overview (this file)
```

## Latest Features (Prod-Beta Branch)

### December 2025 Update

- ✅ **User Links Manager** - Create and organize custom quick-access links with categories
- ✅ **Reports & Analytics** - Comprehensive file organization analytics with advanced filtering
- ✅ **Recent Files Enhancement** - Quick actions to open files and reveal in folder
- ✅ **Template Fixes** - Resolved Jinja2 template syntax errors for improved stability
- ✅ **Config Page Repairs** - Fixed non-functional buttons (Factory Reset, Service Management, Auth tools)
- ✅ **CSRF Protection** - Enhanced security with flask-wtf integration

See `CHANGELOG_DEV_vs_MAIN.md` for full differences from `main` (roles, layout editor, rights enforcement, multi-user support).

---

## License

[LICENSE](LICENSE)

---

## Support

Found a bug? Have a feature request? Open an issue on [GitHub](https://github.com/Atomsk865/DownloadsOrganizeR/issues).
