# SortNStore (formerly DownloadsOrganizeR) - AI Coding Agent Instructions

## Project Overview

**SortNStore** is a production-ready Windows file organization service with advanced multi-folder watching, flexible routing rules, and enterprise-grade web dashboard. The project underwent significant architecture evolution (6 phases) integrating battle-tested awesome-python libraries.

### Core Components

1. **SortNStoreService.py** (main service, 713 lines) - Multi-folder file watcher with advanced routing
   - Wrapper shim: `Organizer.py` (legacy compatibility)
2. **SortNStoreDashboard.py** (main app, 885 lines) - Flask web dashboard with real-time monitoring
   - Package directory: `SortNStoreDashboard/` (modular architecture)
3. **SortNStoreTrayApp.py** - Windows system tray GUI
4. **Installers** - PowerShell-based installation (`installers/install.ps1`, 525+ lines)

### Project Status
- **6 phases complete** (structured logging, API docs, auth, admin, async tasks, WebSocket)
- **40/40 tests passing** (100%)
- **9,430+ lines total** (5,340 implementation + 1,690 tests + 2,400 docs)

## Architecture & Data Flow

### Multi-Folder File Organization (SortNStoreService.py)

```
Watch Folders (multiple) → [Watchdog Observer] → SortNStoreHandler
                                ↓
                    Configuration-Driven Routing:
                    1. Pattern Routes (regex)
                    2. Tag Routes (filename tags)
                    3. Custom Routes (extension → absolute path)
                    4. Size Rules (file size ranges)
                    5. Standard Extension Map (fallback)
                                ↓
                    Destination: subfolder OR absolute custom path
                                ↓
                    Duplicate Handling (hash-based)
```

**Advanced Routing Priority** (in order):
1. **Pattern Routes** - Regex-based filename matching → custom destination
2. **Tag Routes** - Tag in filename (e.g., `[work]`) → custom destination  
3. **Custom Routes** - Extension override → absolute path (e.g., `.pdf` → `D:\Documents\PDFs\`)
4. **Size Rules** - File size ranges → category override (e.g., files >100MB → `Large Files`)
5. **Standard Extension Map** - Default category by extension (9+ categories)

**Destination Modes:**
- `subfolder`: Files go to `{watch_folder}/{Category}/` (relative)
- `custom`: Files go to `{base_destination}/{Category}/` (absolute paths, supports network/cloud)

### Dashboard Architecture (Flask + Modular Package)

```
SortNStoreDashboard.py (entry point)
├─ Imports → SortNStoreDashboard/ package
│  ├─ __init__.py (package initialization)
│  ├─ config_runtime.py (decoupled config accessor)
│  ├─ structured_logging.py (@structlog integration)
│  ├─ restx_api.py (@flask-restx Swagger/OpenAPI docs at /api/docs)
│  ├─ tasks.py (@celery async task queue)
│  ├─ websocket.py (@flask-socketio real-time updates)
│  ├─ admin_panel.py (@flask-admin auto-generated admin UI at /admin)
│  ├─ auth/ (authentication: basic, LDAP, Windows Auth)
│  ├─ routes/ (API endpoints & views)
│  └─ helpers/ (utility functions)
├─ Templates → dash/ (HTML templates, Bootstrap 5)
└─ Static Assets → static/ (CSS, JS, images)
```

**Package Name Collision Shim** (lines 1-23 of SortNStoreDashboard.py):
- When running script directly, Python prefers file over package directory
- Shim forces package resolution by manually setting up `sys.modules[_pkg_name]`
- Critical pattern for maintaining modular architecture while keeping top-level script runnable

### Configuration System

**Two Config Files:**
1. **sortnstore_config.json** (service config) - File routing, thresholds, auth settings
2. **dashboard_config.json** (dashboard config) - Users, roles, layout, setup state

**Config Paths Priority** (SortNStoreService.py lines 38-46):
```python
CONFIG_PATHS = [
    SCRIPT_DIR / "organizer_config.json",  # Local (dev)
    Path("C:/Scripts/organizer_config.json"),  # Legacy service install
    Path("C:/ProgramData/SortNStore/organizer_config.json")  # Enterprise install
]
```

**Writable Path Fallback** (config_runtime.py `_ensure_writable_path`):
- Tries original path first
- Falls back to `%LOCALAPPDATA%\DownloadsOrganizeR`
- Last resort: temp directory
- Ensures configs work in permission-restricted environments

## Critical Developer Workflows

### Development (Cross-Platform via Dev Container)
```bash
# Running in dev container (Ubuntu 24.04 LTS)
cd /workspaces/DownloadsOrganizeR

# Install dependencies
pip install -r requirements.txt

# Run service (development mode)
python SortNStoreService.py

# Run dashboard (in another terminal)
python SortNStoreDashboard.py
# Access: http://localhost:5000
# Defaults: admin / (check env: DASHBOARD_USER, DASHBOARD_PASS)

# Run tests
pytest tests/ -v
```

### Production Deployment (Windows)

**One-Liner Installation** (PowerShell as Administrator):
```powershell
irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex
```

**Manual Installation:**
```powershell
# Clone/download repository
git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
cd DownloadsOrganizeR

# Run installer (auto-elevates)
.\installers\install.ps1
```

**Installer Features** (installers/install.ps1):
- Role-based deployment (Personal vs Enterprise)
- TLS 1.2+ enforcement
- Security hardening & audit logging
- Health checks & system validation
- Automatic recovery & rollback
- Silent & interactive modes

### Testing & Validation
```bash
# Run all tests
pytest tests/ -v

# Specific test suites
pytest tests/test_phase2_api_integration.py  # API docs
pytest tests/test_setup_validation.py  # Setup wizard
pytest tests/test_routes_smoke.py  # Dashboard routes

# Environment check
python scripts/check_environment.py
```

### Accessing Production Features

**Swagger API Documentation:**
- URL: `http://localhost:5000/api/docs`
- Auto-generated from flask-restx decorators
- Interactive API testing interface

**Admin Interface:**
- URL: `http://localhost:5000/admin`
- Auto-generated CRUD for users/roles/config
- Role-based access control

**Real-Time Dashboard:**
- WebSocket updates at `/` (main dashboard)
- Live task monitoring, worker status, system metrics

## Project-Specific Patterns

### Naming Convention Evolution
- **Current:** `SortNStoreService.py`, `SortNStoreDashboard.py`, `SortNStoreTrayApp.py`
- **Legacy (still works):** `Organizer.py`, `OrganizerDashboard.py`, `OrganizerTrayApp.py`
- **Wrapper pattern:** `*_wrapper.py` files ensure backward compatibility
- **When referencing:** Use "SortNStore" for new code; legacy names work via shims

### Configuration-Driven Everything
**Service behavior entirely driven by config:**
- Watch folders (multiple)
- Routing rules (patterns, tags, custom, size)
- Destination mode (subfolder vs custom)
- Authentication method (basic, LDAP, Windows)
- Thresholds (memory, CPU)

**No hardcoded defaults in service** - all rules come from config or fallback map.

### Awesome-Python Integration Pattern
**Optional, Non-Breaking Enhancements** (see AWESOME_PYTHON_SUMMARY.md):
- All libraries have graceful fallback if not installed
- Check pattern: `try: import X; AVAILABLE=True except: AVAILABLE=False`
- Example: `restx_api.py` lines 27-31, `tasks.py` lines 34-40
- Enables progressive adoption without breaking existing deployments

### Structured Logging (@structlog)
```python
from SortNStoreDashboard.structured_logging import get_logger
log = get_logger(__name__)

# JSON logging with context
log.info("file_organized", 
         file=filename, 
         category=category, 
         destination=dest_path)
```

**Key Benefits:**
- Machine-parseable JSON logs
- Context binding (request IDs, user, etc.)
- Colored console output for humans
- Used throughout dashboard & service

### Async Task Pattern (@celery)
```python
from SortNStoreDashboard.tasks import organize_files_task

# Queue async task
task = organize_files_task.delay(path='/path/to/folder')

# Check status
status = task.status  # PENDING, STARTED, SUCCESS, FAILURE
result = task.result
```

**Infrastructure:**
- Broker: Redis (localhost:6379)
- Workers: Separate process pool (`celery -A SortNStoreDashboard.tasks worker`)
- Monitoring: Flower UI (optional)

### Real-Time Updates (@flask-socketio)
**Server-side event emission:**
```python
from SortNStoreDashboard.websocket import get_socketio
socketio = get_socketio()

socketio.emit('task_started', {'task_id': task_id})
socketio.emit('system_metrics', {'cpu': cpu_pct, 'memory': mem_pct})
```

**Client-side (templates):**
- Bootstrap 5 responsive UI
- Socket.IO JavaScript client
- Real-time dashboard updates without polling

## Integration Points & Dependencies

### Battle-Tested Libraries (awesome-python)
- **@structlog 23.0+** - Structured JSON logging
- **@flask-restx 1.0+** - API documentation (Swagger/OpenAPI)
- **@flask-security-too 5.0+** - Enhanced auth (RBAC, password reset)
- **@flask-admin 1.6+** - Auto-generated admin UI
- **@celery 5.3+** - Distributed task queue
- **@redis 5.0+** - Message broker & result backend
- **@flask-socketio** - WebSocket real-time updates

### Core Dependencies
- **Flask 3.0+** - Web framework
- **watchdog 3.0+** - File system monitoring
- **psutil 5.9+** - System metrics
- **bcrypt 4.0+** - Password hashing
- **ldap3 2.9+** - LDAP authentication
- **pywin32 306+** - Windows integration (Windows only)

### Windows-Specific (Production)
- **Service Manager:** NSSM or native Windows service (see installers)
- **Auth Integration:** Windows Authentication, LDAP, Basic
- **Paths:** `C:\Scripts\`, `C:\ProgramData\SortNStore\`, `%LOCALAPPDATA%\DownloadsOrganizeR\`

### Development Environment
- **Dev Container:** Ubuntu 24.04.3 LTS
- **Package Manager:** pip
- **Testing:** pytest
- **Tools:** apt, docker, git, gh, kubectl, curl

## Common Modifications & Tips

### Adding New File Category
1. Update `DEFAULT_CONFIG["routes"]` in `SortNStoreDashboard.py` (line ~49)
2. If using legacy `EXTENSION_MAP` in `SortNStoreService.py`, update `_default_extension_map()` (line ~71)
3. Update `sortnstore_config.json` routes section
4. Restart service

### Adding Advanced Routing Rule
**Pattern Route** (regex-based):
```json
{
  "pattern_routes": {
    "^invoice_.*\\.pdf$": "D:\\Accounting\\Invoices",
    "\\[urgent\\]": "D:\\Priority"
  }
}
```

**Tag Route** (filename tags):
```json
{
  "tag_routes": {
    "[work]": "D:\\Work",
    "[personal]": "D:\\Personal"
  }
}
```

**Size Rule** (override category by size):
```json
{
  "size_rules": [
    {"min_mb": 100, "category": "Large Files"},
    {"max_mb": 1, "category": "Small Files"}
  ]
}
```

### Debugging Tips

**Service Issues:**
- Check logs: `C:\Scripts\service-logs\organizer_stdout.log`
- Verify watch folders exist and are readable
- Confirm routing priority (pattern > tag > custom > size > extension)

**Dashboard Issues:**
- Check structured logs (JSON format) in console or file
- Access `/api/docs` for API testing
- Verify config paths via `config_runtime.py` fallback logic

**Package Import Issues:**
- Ensure `SortNStoreDashboard/` directory treated as package
- Check shim at top of `SortNStoreDashboard.py` (lines 1-23)
- Verify `sys.path` includes script directory

### Environment Variables (Dashboard)
- `DASHBOARD_USER` - Basic auth username (default: "admin")
- `DASHBOARD_PASS` - Basic auth password (default: from config file)
- Also: config file takes precedence (`dashboard_user`, `dashboard_pass_hash`)

## Documentation Structure

### Essential Docs (see docs/INDEX.md)
- **Getting Started:** `docs/getting-started/QUICKSTART.md`
- **Architecture:** `docs/architecture/DASHBOARD_ORGANIZER_INTEGRATION.md`
- **Deployment:** `docs/deployment/ENTERPRISE_SETUP.md`
- **Awesome-Python Enhancements:** `AWESOME_PYTHON_SUMMARY.md`, `AWESOME_PYTHON_INTEGRATION_PLAN.md`

### Key Reference Files

| File | Purpose |
|------|---------|
| `SortNStoreService.py` | Core multi-folder file organization (713 lines) |
| `SortNStoreDashboard.py` | Main Flask app entry point (885 lines) |
| `SortNStoreDashboard/` | Modular dashboard package (restx, tasks, websocket, auth) |
| `sortnstore_config.json` | Service configuration (routing, auth, thresholds) |
| `dashboard_config.json` | Dashboard configuration (users, roles, layout) |
| `requirements.txt` | Python dependencies (27 packages) |
| `pyproject.toml` | Package metadata, linting config |
| `PROJECT_STATUS_OVERVIEW.md` | Current project state & metrics |
| `installers/install.ps1` | Enterprise-grade PowerShell installer |

### Example Configurations
- `config_examples/organizer_simple_local.json` - Basic local setup
- `config_examples/organizer_network_nas_example.json` - NAS integration
- `config_examples/organizer_onedrive_example.json` - Cloud storage
- `config_examples/organizer_mixed_cloud_network.json` - Hybrid deployment
