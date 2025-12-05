# Release Notes - v2.0-beta

**Release Date:** December 5, 2025  
**Branch/Tag:** Prod-Beta / `v2.0.0-beta`

## Highlights

- Phase 2 configuration platform completed (four production-ready modules with blueprints wired for Phase 4 backend routes)
- Multi-method authentication (Basic, LDAP/AD, Windows) with configurable fallback and provider pattern
- Config export/import/validate with timestamped backups and selective restore paths
- Dashboard UX hardening: global search/filter across tables, notification center with history, stats dashboards, command palette, mobile responsiveness
- Documentation set refreshed: architecture review findings, module reference, auth quickstart/implementation guides

## Feature Detail

### Phase 2 Modules
- **Users & Roles Config**: lifecycle management, role-based rights, LDAP/AD hooks, bcrypt hashes, audit-friendly responses
- **Network Targets Config**: UNC validation, SMB3-aware connection pooling, credential storage, reliability monitoring, batch path tests
- **SMTP & Credentials Manager**: TLS/OAuth email settings, encrypted credential handling, notification templates, send/test flows
- **Watched Folders Config**: multi-path monitoring with placeholder resolution (`%USERNAME%`, `%USER%`), read/write checks, batch folder tests, audit logging

### Authentication & Security
- Multi-provider auth chain with fallback
- LDAP/AD and Windows auth options; basic auth remains default
- Rights-based gating for service/config actions; CSRF protection via flask-wtf

### Configuration & Backup
- Export/import/validate endpoints with timestamped filenames and version metadata
- Selective restore (organizer-only, dashboard-only, or both)
- Admin user preservation during import to prevent lockout

### UI/UX Enhancements
- Search/filter across config tables and logs; state preserved during updates
- Notification center with unread badges, history, and batch operations
- Charts for organization statistics (category breakdown, extension top 10, timeline, heatmap)
- Keyboard shortcuts and command palette; responsive layouts with mobile-friendly controls

## Testing & Quality

- **API Integration**: `tests/test_phase2_api_integration.py` (30+ routes, 200/201/204/400/401/404/409/500/504 paths)
- **Dashboard Smoke**: `tests/test_phase2_dashboard_smoke.py` (rendering, forms, tables, JS modules, accessibility)
- **Coverage Target**: 85%+ (`pytest tests/test_phase2_*.py --cov`)
- **Performance Target**: <200ms list operations; concurrency/state persistence scenarios covered

## Upgrade / Migration Steps

1. **Back up configs**:
   ```bash
   cp organizer_config.json organizer_config.json.bak
   cp dashboard_config.json dashboard_config.json.bak
   ```
2. **Pull release** (tag `v2.0.0-beta` on Prod-Beta):
   ```bash
   git pull
   ```
3. **Dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
4. **Run tests (recommended)**:
   ```bash
   pytest tests/test_phase2_*.py -v
   ```
5. **Restart services**: restart Organizer service and `OrganizerDashboard.py`
6. **Verify**: login, visit `/config`, run network target tests, SMTP test, and sample API calls

## Installation (same as v1.0-beta with updated bits)

### Online Installer (Recommended)
```powershell
PowerShell -ExecutionPolicy Bypass -File .\dist\Setup-DownloadsOrganizeR-Online.ps1
```

### Offline Installer (if provided for this tag)
```powershell
PowerShell -ExecutionPolicy Bypass -File .\Setup-Offline.ps1
```

### Options
- `-Branch <branch>` (default: Prod-Beta)
- `-InstallService`
- `-NoStartDashboard`

## Known Issues / Notes

- LDAP SSL certs must be trusted by the host
- Windows auth requires domain-joined host for domain users
- Service logs directory must be writable by service account
- Use HTTPS reverse proxy for production deployments

## Verification Checklist

- [ ] Dashboard loads without template errors; keyboard shortcuts and command palette respond
- [ ] `/config` renders users/roles/network targets/SMTP/folder sections; buttons execute (install/uninstall/restart/factory reset)
- [ ] Network target test succeeds for at least one UNC path; credentials save and persist
- [ ] SMTP test email sends successfully; credentials stored encrypted
- [ ] Watched folder tests pass with placeholder resolution (e.g., `%USERNAME%`)
- [ ] Export/import/validate flows succeed; admin account preserved after import
- [ ] API integration spot-check: create user, add network target, test SMTP, add watched folder
- [ ] Tests (optional but recommended): `pytest tests/test_phase2_*.py -v`

## Files Included (core)

- `Organizer.py`, `OrganizerDashboard.py`, `OrganizerDashboard/` modules
- `dash/` templates and static assets
- `organizer_config.json`, `dashboard_config.json`
- `Install-And-Monitor-OrganizerService.ps1`, `Windows-Dashboard-SmokeTest.ps1`
- Documentation: `docs/PHASE2_MODULE_REFERENCE.md`, authentication guides, architecture review findings

## Support

- GitHub Issues: https://github.com/Atomsk865/DownloadsOrganizeR/issues
- Docs: `readme.md`, `docs/` directory

