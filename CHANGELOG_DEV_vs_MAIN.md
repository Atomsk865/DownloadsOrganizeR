# Changelog: dev-branch vs main

This document summarizes all functional and structural changes introduced on `dev-branch` relative to `main`.

## Added
- Dashboard configuration page (`/config`) with:
  - Drag-and-drop layout ordering
  - Hide/show sections via checkboxes
  - User & role management UI
- `dashboard_config.json` new persistent file storing users, roles, layout.
- Role-based rights system with predefined roles:
  - `admin`, `operator`, `viewer`
  - Rights: `manage_service`, `manage_config`, `view_metrics`, `view_recent_files`, `modify_layout`
- `requires_right` decorator enforcing granular access.
- Multi-user Basic authentication support (additional bcrypt-hashed users beyond primary admin).
- New blueprint: `routes_dashboard_config` (file: `OrganizerDashboard/routes/dashboard_config.py`).
- Template `dash/dashboard_config.html` for configuration page.
- Extended README with sections for roles, layout, and new features.
- `CONFIGURATION.md` expanded with API endpoints and role details.

## Changed
- Service control routes (`/start`, `/stop`, `/restart`) now require `manage_service` instead of simple auth.
- Organizer configuration update route (`/update`) now requires `manage_config`.
- BasicAuthProvider authentication logic updated to search `dashboard_config.json` for additional users.
- `OrganizerDashboard.py` loads and persists `dashboard_config.json` alongside existing `organizer_config.json`.
- File structure in README updated to include new files and generated artifacts.
- Dashboard features list expanded (layout editor, role management, rights enforcement).

## Security / Access Control
- Introduced rights gating rather than single boolean authentication for sensitive operations.
- Passwords for additional users stored only as bcrypt hashes (`password_hash`).
- Fallback authentication remains configurable (`auth_fallback_enabled`).

## New Files
- `dashboard_config.json`
- `OrganizerDashboard/routes/dashboard_config.py`
- `dash/dashboard_config.html`
- `CHANGELOG_DEV_vs_MAIN.md` (this file)

## Removed / Deprecated
- Implicit assumption of single admin user for all operations (now role-based).
- Direct modification of service/config routes without rights checks.

## Pending / Future (Not yet enforced on dev)
- Rights enforcement for view-only endpoints (`view_metrics`, `view_recent_files`).
- UI state disabling actions based on user rights.
- Password rotation & recovery flows.

## Migration Notes
1. Pull latest `dev-branch`.
2. On first dashboard start, `dashboard_config.json` is created with default roles and the primary admin user.
3. Visit `/config` to add additional users and tailor layout.
4. Ensure any automation scripts using service endpoints authenticate with a user having `manage_service` right.

## Verification Checklist
- Access `/config` after login -> page renders roles table, users list, layout list.
- Add a user; confirm entry appears in `dashboard_config.json` with `password_hash`.
- Reorder sections and hide one; refresh main dashboard to verify ordering/visibility changes.
- Attempt service restart with a viewer role user -> receive 403 Forbidden.

---
Generated: 2025-12-01

