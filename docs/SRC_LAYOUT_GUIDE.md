# SortNStore - Project Structure Guide

## 📁 Professional `src/` Layout

The project now follows Python packaging best practices using a `src/` directory layout.

### Directory Structure

```
SortNStore/
├── src/                                 ← All Python source code
│   ├── sortnstore/                     ← Main package
│   │   ├── __init__.py                 ← Package initialization
│   │   ├── organizer.py                ← Core file organization service
│   │   ├── dashboard.py                ← Flask dashboard entry point
│   │   ├── tray_app.py                 ← Windows system tray application
│   │   └── dashboard_app/              ← Flask application package
│   │       ├── __init__.py
│   │       ├── auth/
│   │       ├── routes/
│   │       ├── helpers/
│   │       └── config_runtime.py
│   └── __init__.py
│
├── tests/                              ← Unit and integration tests
├── docs/                               ← Documentation
├── installers/                         ← Build and installer scripts
├── scripts/                            ← Utility scripts
├── examples/                           ← Example configurations
│
├── pyproject.toml                      ← Modern Python packaging config
├── setup.cfg                           ← setuptools configuration
├── MANIFEST.in                         ← Package data manifest
├── README.md                           ← Main README
├── LICENSE                             ← MIT License
│
├── Organizer_wrapper.py                ← Root-level compatibility wrapper
├── SortNStoreDashboard_wrapper.py       ← Root-level compatibility wrapper
└── OrganizerTrayApp_wrapper.py          ← Root-level compatibility wrapper
```

## ✅ Benefits of `src/` Layout

| Benefit | Explanation |
|---------|------------|
| **Namespace Protection** | Prevents accidental imports of non-installed package |
| **Installation Testing** | Forces proper installation through setuptools |
| **IDE Support** | Better support in PyCharm, VS Code, etc. |
| **Type Checking** | Improved mypy and pylance type checking |
| **Distribution** | Industry standard for PyPI packages |
| **Testing** | Tests always use installed package, not local code |

## 🚀 Installation

### Development Installation

```bash
# Install in editable mode (development)
pip install -e .

# Install with optional dependencies
pip install -e ".[dev]"    # Development tools
pip install -e ".[gpu]"    # GPU support
pip install -e ".[dev,gpu]" # Everything
```

### Production Installation

```bash
pip install sortnstore
```

## 📦 Package Contents

### Core Modules in `src/sortnstore/`

| Module | Purpose |
|--------|---------|
| `organizer.py` | File organization service (watches Downloads folder) |
| `dashboard.py` | Flask web application server entry point |
| `tray_app.py` | Windows system tray GUI application |
| `dashboard_app/` | Flask application package with routes and configuration |

### Entry Points

The `pyproject.toml` defines CLI entry points:

```bash
sortnstore-dashboard     # Start web dashboard
sortnstore-organizer    # Start file organization service
sortnstore-tray         # Start system tray application
```

## 🔄 Backward Compatibility

Root-level wrapper scripts (`*_wrapper.py`) maintain compatibility with existing installation scripts:

- `Organizer.py` → `Organizer_wrapper.py` → `src/sortnstore/organizer.py`
- `SortNStoreDashboard.py` → `SortNStoreDashboard_wrapper.py` → `src/sortnstore/dashboard.py`
- `OrganizerTrayApp.py` → `OrganizerTrayApp_wrapper.py` → `src/sortnstore/tray_app.py`

These wrappers ensure:
- Existing Windows service configurations continue to work
- PowerShell installation scripts don't need immediate updates
- Gradual migration path to new structure

## 🔧 Development Workflow

### Running Locally

```bash
# Install in development mode
pip install -e ".[dev]"

# Run components directly
python -m sortnstore.organizer
python -m sortnstore.dashboard
python -m sortnstore.tray_app

# Or use entry points
sortnstore-organizer
sortnstore-dashboard
sortnstore-tray
```

### Building Distribution

```bash
# Build wheel and source distribution
python -m build

# Outputs to dist/
# - dist/sortnstore-1.0.0-py3-none-any.whl
# - dist/sortnstore-1.0.0.tar.gz
```

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# With coverage
pytest --cov=sortnstore tests/
```

## 📝 Import Examples

### Internal Imports (within package)

```python
# In src/sortnstore/module.py
from .organizer import Organizer
from .dashboard_app.config_runtime import load_config
from . import __version__
```

### External Imports (installed package)

```python
# After: pip install sortnstore
from sortnstore import __version__
from sortnstore.organizer import Organizer
from sortnstore.dashboard_app import create_app
```

## 🔍 Migration Path

### Phase 1 (Current): Setup ✅
- ✅ Create `src/sortnstore/` structure
- ✅ Move core modules to package
- ✅ Create wrapper scripts for backward compatibility
- ✅ Update `pyproject.toml` with modern config

### Phase 2: Updates (Gradual)
- Update Windows service scripts to use wrapper scripts
- Update PowerShell installers (still use root wrappers)
- Migrate internal projects to use `pip install -e .`

### Phase 3: Full Migration (Future)
- Update service to use entry points
- Remove root-level original files (keep wrappers as aliases)
- Require package installation for all deployments

## 📖 Resources

- **Python Packaging Guide**: https://packaging.python.org/
- **setuptools Documentation**: https://setuptools.pypa.io/
- **PEP 517**: https://peps.python.org/pep-0517/
- **PEP 518**: https://peps.python.org/pep-0518/
- **SRC Layout**: https://hynek.me/articles/testing-packaging/

## ❓ FAQ

**Q: Why move to `src/` layout?**  
A: It's the Python packaging standard recommended by all major tools and follows best practices used by professional projects.

**Q: Will existing installations break?**  
A: No! Wrapper scripts maintain backward compatibility. Existing Windows services will continue to work.

**Q: Can I still run scripts from the root?**  
A: Yes, through the wrapper scripts. For development, use `pip install -e .` to install in editable mode.

**Q: How do I import sortnstore in my code?**  
A: After installation: `from sortnstore.organizer import Organizer` or `from sortnstore.dashboard import create_app`

**Q: Do I need to update my PowerShell scripts?**  
A: Not immediately. The wrapper scripts provide compatibility. Update when convenient.
