# Dashboard Configuration Page

The dashboard now includes a configuration interface at `/config` ("Dashboard Configuration") providing:

## Features
- User Management: Add, update, or delete non-primary users with assigned roles.
- Role Rights Display: Shows built-in roles (`admin`, `operator`, `viewer`) and their rights.
- Layout Editor: Drag to reorder dashboard sections; hide sections via checkbox.

## Roles & Rights
| Right | Purpose |
|-------|---------|
| manage_service | Start/stop/restart the organizer Windows service |
| manage_config  | Modify organizer routing and thresholds |
| view_metrics    | Access metrics endpoints (future enforcement) |
| view_recent_files | View recent file movement list |
| modify_layout   | Change dashboard layout ordering/visibility |

### Default Role Mapping
- admin: All rights
- operator: manage_service + view_* rights
- viewer: view_* rights only

## Persisted Configuration File
Stored in `dashboard_config.json` automatically created with defaults:
```
{
  "users": [
    {"username": "admin", "role": "admin"}
  ],
  "roles": { ... },
  "layout": {
    "sections_order": ["System Information", ...],
    "hidden_sections": []
  }
}
```
User password hashes are stored per user entry under `password_hash` when a password is set.

## API Endpoints
- GET `/api/dashboard/config` – Returns users (without hashes), roles, layout.
- POST `/api/dashboard/users` – Body: `{username, role, password?}`
- DELETE `/api/dashboard/users/<username>` – Removes user (cannot delete primary admin).
- POST `/api/dashboard/layout` – Body: `{sections_order: [...], hidden_sections: [...]}`

All modification endpoints require proper rights:
- manage_config for user CRUD
- modify_layout for layout changes
- manage_service for service control actions (already enforced)

## Authentication & Roles
The `BasicAuthProvider` now supports additional users via `dashboard_config.json`. If a user other than the primary admin authenticates, the system looks up their `password_hash` and role. The primary admin must retain role `admin`.

## Future Enhancements
- Enforce view-specific rights (`view_metrics`, `view_recent_files`) on related endpoints.
- UI feedback for disabled actions based on role.
- Password rotation / force reset workflows.

## Notes
- Plain passwords are never stored—only bcrypt hashes.
- Sending `password: "***"` or omitting `password` in update leaves existing hash unchanged.
- Layout changes affect rendering order & visibility dynamically (client-side application on load).
