# DownloadsOrganizeR 📦

Automatically organize your Downloads folder by file type. DownloadsOrganizeR monitors your Downloads folder in real-time and sorts files into categories (Images, Videos, Documents, etc.) — no manual work required.

---

## Quick Start (5 minutes)

### Option 1: Automated Service Installation (Recommended)

1. **Install Python** if you haven't already ([python.org](https://www.python.org/downloads/))
2. **Download this repository** or clone it:
   ```bash
   git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
   cd DownloadsOrganizeR
   ```
3. **Run the installer** (Right-click PowerShell → Run as Administrator):
   ```powershell
   .\Install-And-Monitor-OrganizerService.ps1
   ```
4. **Done!** The service will start automatically on boot and organize your Downloads in real-time.

### Option 2: Manual Run (No Service)

```powershell
cd DownloadsOrganizeR
pip install -r requirements.txt
python Organizer.py
```

---

## Dashboard 📊

Monitor and configure the organizer from a web dashboard:

```bash
pip install -r requirements.txt
python OrganizerDashboard.py
```

Then open: **http://localhost:5000**

**Default credentials (Dashboard)**

- **Username:** `admin`
- **Password:** `change_this_password`

You can override these by setting environment variables before launching the dashboard:

```bash
export DASHBOARD_USER=myusername
export DASHBOARD_PASS=mypassword
python OrganizerDashboard.py
```

### Dashboard Features
- 🔍 Real-time service monitoring
- 📈 CPU, RAM, and network usage
- ⚙️ Customize file organization rules
- 📋 Live log viewer
- 💾 Drive space overview
- 📱 Responsive web UI

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

### Editing Organization Rules

1. Open the Dashboard: http://localhost:5000
2. Go to "Configuration" section
3. Add/remove file extensions for each category
4. Changes apply immediately

### Environment Variables (Dashboard Security)

Set custom login credentials:

```bash
set DASHBOARD_USER=myusername
set DASHBOARD_PASS=mypassword
python OrganizerDashboard.py
```

---

## Troubleshooting

### Service won't start?
- Check logs: `C:\Scripts\service-logs\organizer_stdout.log`
- Ensure Python is in PATH: `python --version`
- Try running manually: `cd C:\Scripts && python Organizer.py`

### Dashboard won't connect?
- Verify service is running: Check Windows Services
- Ensure port 5000 is available: `netstat -ano | findstr :5000`
- Check firewall settings

### Files not organizing?
- Check the organizer log: `C:\Users\{username}\Downloads\organizer.log`
- Verify file extensions are in the config
- Ensure destination folders are writable

---

## Uninstall

Remove the Windows service:

```powershell
nssm remove DownloadsOrganizer confirm
```

Then delete the `C:\Scripts\Organizer.py` file if desired.

---

## Requirements

- **Windows** (Service installation only)
- **Python 3.7+**
- **Dependencies:**
  ```
  watchdog==6.0.0     # File monitoring
  Flask==3.1.2        # Dashboard web framework
  psutil==7.1.3       # System metrics
  gputil==1.4.0       # GPU info (optional)
  ```

---

## File Structure

```
DownloadsOrganizeR/
├── Organizer.py                          # Core file organizer
├── OrganizerDashboard.py                 # Web dashboard
├── Install-And-Monitor-OrganizerService.ps1  # Service installer
├── organizer_config.json                 # Configuration file
├── requirements.txt                      # Python dependencies
└── README.md                             # This file
```

---

## License

[LICENSE](LICENSE)

---

## Support

Found a bug? Have a feature request? Open an issue on [GitHub](https://github.com/Atomsk865/DownloadsOrganizeR/issues).
