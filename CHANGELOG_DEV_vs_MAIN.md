# Changelog: Prod-Beta vs main

This document summarizes all functional and structural changes introduced on `Prod-Beta` branch relative to `main`.

## Added (December 2025)

### User Links Feature
- **User Links Manager** (`/user-links`) - Create and manage custom quick-access links
  - Categorized link organization (Work, Personal, Tools, Reference, Other)
  - Link descriptions and metadata
  - Quick copy-to-clipboard functionality
  - Full CRUD operations via API
- New blueprint: `routes_user_links` (file: `OrganizerDashboard/routes/user_links.py`)
- API endpoints: `/api/user-links` (GET, POST, PUT, DELETE)

### Reports & Analytics Feature
- **Comprehensive Reports Dashboard** (`/reports`) with advanced analytics:
  - File organization statistics with date range filtering
  - Category-based analysis (Images, Videos, Documents, etc.)
  - File size distribution and storage usage metrics
  - Organization pattern insights
  - Time-based filtering (today, yesterday, last 7/30 days, custom range)
  - Category filtering with multi-select support
  - Export capabilities for data analysis
- New blueprint: `reports_bp` (file: `OrganizerDashboard/routes/reports.py`)
- API endpoints: `/api/reports/summary`, `/api/reports/category-stats`, `/api/reports/file-sizes`

### Recent Files Enhancement
- Enhanced Recent File Movements viewer with quick actions:
  - Open file directly from dashboard
  - Reveal file in folder/explorer
  - Remove entries from recent list
  - Real-time refresh capability
- New API endpoints for file operations
- New blueprints: `routes_api_open_file`, `routes_api_recent_files`

### Configuration & Setup Features
- Dashboard configuration page (`/config`) with:
  - Drag-and-drop layout ordering
  - Hide/show sections via checkboxes
  - User & role management UI
  - Service installation controls
  - Network targets (NAS/SMB) configuration
  - SMTP and credentials management
  - Factory reset and setup wizard controls
- `dashboard_config.json` new persistent file storing users, roles, layout
- Role-based rights system with predefined roles:
  - `admin`, `operator`, `viewer`
  - Rights: `manage_service`, `manage_config`, `view_metrics`, `view_recent_files`, `modify_layout`, `test_smtp`, `test_nas`, `manage_network_targets`, `manage_credentials`, `send_reports`
- `requires_right` decorator enforcing granular access
- Multi-user Basic authentication support (additional bcrypt-hashed users beyond primary admin)
- New blueprint: `routes_dashboard_config` (file: `OrganizerDashboard/routes/dashboard_config.py`)
- Template `dash/dashboard_config.html` for configuration page
- Extended README with sections for roles, layout, and new features
- `CONFIGURATION.md` expanded with API endpoints and role details

## Bug Fixes (December 2025)

### Template Fixes
- **Fixed Jinja2 template syntax errors** in `dashboard.html`
  - Removed duplicate collapsible section structures causing `{% endfor %}` / `{% endblock %}` mismatch
  - Cleaned up card body structures for all dashboard sections
  - Simplified HTML hierarchy for better maintainability

### Config Page Fixes
- **Fixed non-functional buttons** in dashboard configuration page
  - Moved scoped functions to global scope: `resetSetup()`, `installService()`, `uninstallService()`, `reinstallService()`, `factoryReset()`, `repairAuth()`, `viewAuthState()`
  - Functions were trapped inside `applyConfigRights()` making them inaccessible to onclick handlers
  - Separated rights enforcement logic from function definitions

### Security Enhancements
- **Added CSRF protection** with flask-wtf integration
  - Implemented CSRF token management across all forms
  - Added CSRF token endpoint for AJAX requests
  - Exempted login and setup routes from CSRF validation

## Changed

- Service control routes (`/start`, `/stop`, `/restart`) now require `manage_service` instead of simple auth
- Organizer configuration update route (`/update`) now requires `manage_config`
- BasicAuthProvider authentication logic updated to search `dashboard_config.json` for additional users
- `OrganizerDashboard.py` loads and persists `dashboard_config.json` alongside existing `organizer_config.json`
- File structure in README updated to include new files and generated artifacts
- Dashboard features list expanded (layout editor, role management, rights enforcement, reports, user links)

## Security / Access Control
- Introduced rights gating rather than single boolean authentication for sensitive operations.
- Passwords for additional users stored only as bcrypt hashes (`password_hash`).
- Fallback authentication remains configurable (`auth_fallback_enabled`).

## New Files

- `dashboard_config.json`
- `OrganizerDashboard/routes/dashboard_config.py`
- `OrganizerDashboard/routes/user_links.py`
- `OrganizerDashboard/routes/reports.py`
- `OrganizerDashboard/routes/api_recent_files.py`
- `OrganizerDashboard/routes/api_open_file.py`
- `OrganizerDashboard/routes/admin_tools.py`
- `OrganizerDashboard/routes/csrf_token.py`
- `dash/dashboard_config.html`
- `CHANGELOG_DEV_vs_MAIN.md` (this file)
- `RECENT_FILES_FEATURE.md`
- `RECENT_FILES_QUICKSTART.md`

## Removed / Deprecated
- Implicit assumption of single admin user for all operations (now role-based).
- Direct modification of service/config routes without rights checks.

## Pending / Future (Not yet enforced on dev)
- Rights enforcement for view-only endpoints (`view_metrics`, `view_recent_files`).
- UI state disabling actions based on user rights.
- Password rotation & recovery flows.

## Migration Notes

1. Pull latest `Prod-Beta` branch
2. Install/update dependencies: `pip install -r requirements.txt`
3. On first dashboard start, `dashboard_config.json` is created with default roles and the primary admin user
4. Visit `/config` to add additional users and tailor layout
5. Ensure any automation scripts using service endpoints authenticate with a user having `manage_service` right
6. Explore new features:
   - `/user-links` - Manage custom quick-access links
   - `/reports` - View file organization analytics

## Verification Checklist

- Access `/config` after login -> page renders roles table, users list, layout list
- Test all config page buttons (Factory Reset, Service Install, etc.) -> verify they work
- Add a user; confirm entry appears in `dashboard_config.json` with `password_hash`
- Reorder sections and hide one; refresh main dashboard to verify ordering/visibility changes
- Attempt service restart with a viewer role user -> receive 403 Forbidden
- Create a user link at `/user-links` -> verify it persists and displays correctly
- Generate a report at `/reports` with custom date range -> verify accurate statistics
- Open a recent file from dashboard -> file opens in default application
- Reveal a recent file in folder -> explorer/finder opens to file location

---
Generated: 2025-12-02

