# SortNStore

**Intelligent file organization service for Windows that automatically categorizes downloaded files into organized folders.**

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)

---

## 📚 Documentation Quick Links

**Find what you need:**

| Need | Link |
|------|------|
| **New to this?** | [Getting Started Guide](docs/getting-started/) |
| **Want full docs?** | [Documentation Index](docs/INDEX.md) |
| **Plan mobile expansion?** | [Cross-Platform Roadmap](docs/roadmaps/CROSS_PLATFORM_MOBILE_ROADMAP.md) |
| **Deploy to production?** | [Deployment Guide](docs/deployment/) |
| **Understand architecture?** | [Architecture Guide](docs/architecture/) |
| **Need specific features?** | [Features Guide](docs/features/) |
| **What changed?** | [Changelogs](docs/changelogs/) |

**All documentation organized into 8 categories** - See [docs/INDEX.md](docs/INDEX.md) for complete navigation.

---

## Features

✨ **Automatic File Organization**
- Real-time monitoring of Downloads folder
- Automatic categorization by file type
- Customizable rules and destinations
- Duplicate detection and handling

🎛️ **Web Dashboard**
- Real-time service monitoring
- Configuration management
- Log viewing and analysis
- Recent file movements tracking
- System metrics and statistics

🔐 **Authentication & Security**
- Multiple auth methods: Basic, LDAP, Windows Auth
- Session management
- Access control

🖥️ **System Tray Application**
- Quick service control
- One-click dashboard launch
- Auto-start on login
- GitHub integration for updates

⚡ **Battle-Tested Libraries** (awesome-python recommendations)
- **@structlog**: Structured JSON logging for better observability
- **@flask-restx**: Automatic API documentation with Swagger UI at `/api/docs`
- Enhanced authentication & admin interface (coming soon)

---

## Quick Start

> **Naming update:** The core service script is now `SortNStoreService.py`. `Organizer.py` remains as a compatibility shim for legacy tooling.

### One-Liner Installation (Recommended)

Download and install the latest version in one command (run in PowerShell as Administrator):

```powershell
irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex
```

This will:
- ✅ Download latest release from GitHub
- ✅ Extract files to `C:\DownloadsOrganizeR`
- ✅ Install Python dependencies
- ✅ Set up configuration directories
- ✅ Optionally install as Windows service

### Manual Installation

1. **Clone or download the repository**
   ```powershell
   git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
   cd DownloadsOrganizeR
   ```

2. **Run the installer** (as Administrator)
   ```powershell
   .\installers\install.ps1
   ```

3. **Configure settings**
   - Edit `organizer_config.json` to customize file categories
   - Adjust thresholds and monitor settings

4. **Start the service**
   - Use the system tray application or PowerShell
   - Dashboard will be available at `http://localhost:5000`

### Running from Source

**Prerequisites:**
- Python 3.8+
- pip (Python package manager)

**Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Start the organizer service
python Organizer.py

# In another terminal, start the dashboard
python SortNStoreDashboard.py
```

---

## File Structure

```
DownloadsOrganizeR/
├── README.md                          ← You are here
├── LICENSE                            ← MIT License
├── Organizer.py                       ← Core file organization service
├── OrganizerTrayApp.py                ← Windows system tray GUI
├── SortNStoreDashboard.py             ← Flask web dashboard
├── requirements.txt                   ← Python dependencies
├── organizer_config.json              ← Service configuration
├── dashboard_config.json              ← Dashboard configuration
│
├── docs/                              ← Documentation
│   ├── INSTALLATION.md                ← Setup & installation guide
│   ├── CONFIGURATION.md               ← Configuration options
│   ├── TROUBLESHOOTING.md             ← Common issues & solutions
│   ├── ARCHITECTURE.md                ← System design & components
│   └── ...
│
├── installers/                        ← Installation & build scripts
│   ├── install.ps1                     ← One-liner installer (GitHub releases)
│   ├── Setup-Installer.ps1             ← Manual local installation
│   ├── Install-And-Monitor-OrganizerService.ps1 ← Service setup
│   ├── build.py                        ← Build script
│   └── ...
│
├── scripts/                           ← Utility & development scripts
│   ├── check_environment.py           ← Environment verification
│   ├── check_routes.py                ← Route checking
│   ├── Monitor-OrganizerService.ps1   ← Service monitoring
│   └── ...
│
├── SortNStoreDashboard/               ← Dashboard Python package
│   ├── __init__.py                    ← Package initialization
│   ├── config_runtime.py              ← Configuration management
│   ├── auth/                          ← Authentication module
│   ├── routes/                        ← API endpoints & views
│   ├── helpers/                       ← Utility functions
│   └── ...
│
├── dash/                              ← HTML templates
│   ├── dashboard.html                 ← Main dashboard UI
│   ├── login.html                     ← Login page
│   └── ...
│
├── static/                            ← CSS, JavaScript, images
│   ├── css/                           ← Stylesheets
│   ├── js/                            ← JavaScript files
│   └── img/                           ← Images & icons
│
├── config/                            ← Configuration data files
├── examples/                          ← Example configurations
└── tests/                             ← Unit & integration tests
```

---

## Configuration

### organizer_config.json
Controls how files are organized:

```json
{
  "routes": {
    "Images": ["jpg", "png", "gif", "svg"],
    "Videos": ["mp4", "mkv", "avi", "mov"],
    "Documents": ["pdf", "doc", "docx", "txt"],
    "Archives": ["zip", "rar", "7z"]
  },
  "memory_threshold_mb": 200,
  "cpu_threshold_percent": 60,
  "auth_method": "basic"
}
```

See [Configuration Guide](docs/CONFIGURATION.md) for all options.

### dashboard_config.json
Controls dashboard UI and features:

```json
{
  "dashboard_user": "admin",
  "setup_completed": true,
  "theme": "dark",
  "features": {
    "recent_files": true,
    "duplicates": true,
    "statistics": true
  }
}
```

---

## Usage

### Via System Tray (Windows)
1. Click the tray icon to open menu
2. Start/Stop service
3. Launch Dashboard
4. View service status

### Via Command Line
```bash
# Start service
python Organizer.py

# Start dashboard (separate terminal)
python SortNStoreDashboard.py
```

### Via Web Dashboard
- **URL**: http://localhost:5000
- **Default Username**: admin
- **Password**: Check `organizer_config.json` or set in dashboard

---

## Documentation

- 📖 [Installation Guide](docs/INSTALLATION.md) - Setup & requirements
- ⚙️ [Configuration Guide](docs/CONFIGURATION.md) - All config options
- 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues & solutions
- 🏗️ [Architecture](docs/ARCHITECTURE.md) - System design & components
- 📝 [Changelog](docs/CHANGELOG.md) - Version history

**For developers:** See [docs/](docs/) folder for technical documentation.

---

## System Requirements

| Requirement | Details |
|---|---|
| **OS** | Windows 7 SP1 or later |
| **Python** | 3.8+ (for running from source) |
| **RAM** | 256 MB minimum |
| **Disk** | 100 MB for installation |
| **Admin Rights** | Required for Windows service installation |

---

## Features by Component

### Organizer.py (Service)
- Real-time Downloads folder monitoring
- Automatic file categorization
- Extensible configuration system
- Service logging & health monitoring

### SortNStoreDashboard.py (Dashboard)
- Live service status
- Configuration management UI
- Log viewing & analysis
- Statistics & analytics
- API endpoints for automation
- Multiple authentication methods

### OrganizerTrayApp.py (System Tray)
- Quick service control
- Dashboard launcher
- Auto-start capability
- GitHub update integration
- Status monitoring

---

## API Endpoints

The dashboard provides REST API endpoints for automation:

| Endpoint | Method | Description |
|---|---|---|
| `/api/config` | GET/POST | Get/update configuration |
| `/api/service/start` | POST | Start service |
| `/api/service/stop` | POST | Stop service |
| `/api/service/restart` | POST | Restart service |
| `/api/metrics` | GET | System metrics |
| `/api/logs` | GET | Get log entries |
| `/api/recent-files` | GET | Recent file movements |

See [API Documentation](docs/API.md) for complete details.

---

## Troubleshooting

### Common Issues

**Dashboard won't start**
- Check `requirements.txt` is installed: `pip install -r requirements.txt`
- Verify port 5000 is not in use: `netstat -an | find ":5000"`
- See [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

**Service won't start**
- Verify Python is in PATH
- Run terminal as Administrator
- Check logs: `C:\ProgramData\DownloadsOrganizeR\logs\`

**Files not organizing**
- Verify `organizer_config.json` routes are correct
- Check file extensions match your configuration
- Review logs for errors

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more solutions.

---

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## Support

- 📧 **Issues**: Open an issue on GitHub
- 📚 **Documentation**: See [docs/](docs/) folder
- 💬 **Discussions**: Use GitHub Discussions

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Changelog

See [CHANGELOG.md](docs/CHANGELOG.md) for version history and release notes.

---

## Authors

- **Created by**: Atomsk865
- **Contributors**: See [CONTRIBUTORS.md](docs/CONTRIBUTORS.md)

---

## Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Watchdog](https://github.com/gorakhargosh/watchdog) - File monitoring
- [psutil](https://github.com/giampaolo/psutil) - System monitoring
- [Bootstrap 5](https://getbootstrap.com/) - UI framework

### Optional Enhancements

SortNStore can be enhanced with battle-tested libraries from [awesome-python](https://github.com/vinta/awesome-python):

- [Flask-RESTX](https://flask-restx.readthedocs.io/) - Automatic API documentation with Swagger UI
- [Flask-Security-Too](https://flask-security-too.readthedocs.io/) - Enhanced authentication & authorization
- [Flask-Admin](https://flask-admin.readthedocs.io/) - Auto-generated admin interface
- [structlog](https://www.structlog.org/) - Structured JSON logging

See [AWESOME_PYTHON_ENHANCEMENTS.md](docs/AWESOME_PYTHON_ENHANCEMENTS.md) for detailed integration guide and examples in `examples/awesome-python-integrations/`.

---

**Last Updated**: December 19, 2025  
**Version**: See [version.json](version.json)

