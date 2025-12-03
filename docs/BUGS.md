# Known Bugs & Limitations

A concise list of current issues and practical workarounds.

## Windows Service Target
- The organizer service targets Windows. The dashboard runs cross-platform, but file organization service is Windows-first.

## Configuration Sync Pattern
- Organizer.py has a hardcoded `EXTENSION_MAP` while the dashboard updates `organizer_config.json`.
- Workaround: When adding categories via dashboard, also update `EXTENSION_MAP` in Organizer.py.

## Incomplete Downloads Ignored
- Files with `.crdownload`, `.part`, `.tmp` are ignored until complete.
- Behavior: Files will organize once the download finishes.

## Authentication Caveats
- Basic auth defaults to `admin` / `change_this_password` unless overridden via env vars.
- LDAP/Windows auth require correct environment and optional dependencies (`ldap3`, `pywin32`).

## GPU Info Optional
- `gputil` is optional; missing library degrades gracefully in dashboard.

## Service Permissions
- Destination folder must be writable by the service account.
- If moves fail, check logs and permissions.

## File Path Assumptions
- Defaults assume `C:\Scripts` for service and config.
- If customized, ensure dashboard and service point to the same config paths.

