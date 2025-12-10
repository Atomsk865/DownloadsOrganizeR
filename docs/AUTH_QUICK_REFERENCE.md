# Authentication Quick Reference

## Switching Authentication Methods

### Via Configuration File (`organizer_config.json`)

```json
{
  "auth_method": "basic"     // or "ldap" or "windows"
}
```

### Via API

```bash
curl -X POST http://localhost:5000/api/auth/settings \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{"auth_method": "ldap"}'
```

## Quick Setup Examples

### LDAP (Active Directory)

```json
{
  "auth_method": "ldap",
  "ldap_config": {
    "server": "ldaps://ad.company.com:636",
    "base_dn": "dc=company,dc=com",
    "search_filter": "(sAMAccountName={username})",
    "allowed_groups": ["cn=IT Staff,ou=Groups,dc=company,dc=com"]
  }
}
```

### Windows Domain

```json
{
  "auth_method": "windows",
  "windows_auth_config": {
    "domain": "COMPANY",
    "allowed_groups": ["COMPANY\\Admins"]
  }
}
```

### Basic (Default)

```json
{
  "auth_method": "basic",
  "dashboard_user": "admin"
}
```

## Testing Authentication

```bash
# Test LDAP
curl -X POST http://localhost:5000/api/auth/test \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass", "method": "ldap"}'

# Test Windows
curl -X POST http://localhost:5000/api/auth/test \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{"username": "DOMAIN\\testuser", "password": "testpass", "method": "windows"}'
```

## Common Issues & Quick Fixes

| Issue | Fix |
|-------|-----|
| LDAP timeout | Check `server` address and port, verify firewall |
| Windows auth unavailable | Install on Windows: `pip install pywin32` |
| Locked out | Set `"auth_method": "basic"` in config file |
| Groups not working | Verify group DN format and user membership |
| No fallback | Set `"auth_fallback_enabled": true` |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/settings` | GET | Get current auth config |
| `/api/auth/settings` | POST | Update auth config |
| `/api/auth/test` | POST | Test authentication |

## Config File Location

- **Windows:** `C:\Scripts\organizer_config.json`
- **Development:** `./organizer_config.json`

## Emergency Access

If locked out:
1. Edit `organizer_config.json` manually
2. Set `"auth_method": "basic"`
3. Set `"auth_fallback_enabled": true`
4. Restart dashboard service

## Environment Variables

```bash
# Set default basic auth credentials (used if config missing)
export DASHBOARD_USER=admin
export DASHBOARD_PASS=change_this_password
```

## Available Auth Methods Query

```bash
curl http://localhost:5000/api/auth/settings -u admin:password | jq '.available_methods'
# Returns: ["basic", "ldap", "windows"]  (depending on system)
```
