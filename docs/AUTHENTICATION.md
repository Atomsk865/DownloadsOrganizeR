# Authentication Configuration Guide

## Overview

DownloadsOrganizeR Dashboard now supports three authentication methods:
- **Basic Authentication** - Username/password with bcrypt hashing (default)
- **LDAP/Active Directory** - Enterprise directory authentication
- **Windows Local/Domain** - Native Windows authentication

## Authentication Methods

### 1. Basic Authentication (Default)

Uses bcrypt-hashed passwords stored in `organizer_config.json`.

**Configuration:**
```json
{
  "auth_method": "basic",
  "dashboard_user": "admin",
  "dashboard_pass_hash": "$2b$12$..."
}
```

**Setup:**
1. Default credentials: `admin` / `change_this_password`
2. Change password via Dashboard UI or set `DASHBOARD_USER` and `DASHBOARD_PASS` environment variables
3. Password is automatically hashed and stored in config file

### 2. LDAP/Active Directory Authentication

Authenticate users against an LDAP or Active Directory server.

**Configuration:**
```json
{
  "auth_method": "ldap",
  "auth_fallback_enabled": true,
  "ldap_config": {
    "server": "ldap://ldap.example.com:389",
    "base_dn": "dc=example,dc=com",
    "user_dn_template": "uid={username},{base_dn}",
    "use_ssl": true,
    "bind_dn": "cn=service,dc=example,dc=com",
    "bind_password": "service_password",
    "search_filter": "(uid={username})",
    "allowed_groups": ["cn=admins,ou=groups,dc=example,dc=com"]
  }
}
```

**Fields:**
- `server` - LDAP server URI (required)
  - Examples: `ldap://server.com:389`, `ldaps://server.com:636`
- `base_dn` - Base distinguished name for searches (required)
  - Example: `dc=company,dc=com`
- `user_dn_template` - Template for user DN (optional)
  - Default: `uid={username},{base_dn}`
  - Active Directory: `cn={username},{base_dn}` or use UPN format
- `use_ssl` - Use SSL/TLS connection (default: true)
- `bind_dn` - Service account DN for binding (optional)
  - Leave empty for anonymous bind or user bind
- `bind_password` - Service account password (optional)
- `search_filter` - LDAP search filter (default: `(uid={username})`)
  - Active Directory: `(sAMAccountName={username})`
- `allowed_groups` - List of group DNs that users must belong to (optional)
  - Leave empty to allow all authenticated users

**Active Directory Example:**
```json
{
  "auth_method": "ldap",
  "ldap_config": {
    "server": "ldaps://ad.company.com:636",
    "base_dn": "dc=company,dc=com",
    "user_dn_template": "cn={username},cn=users,dc=company,dc=com",
    "use_ssl": true,
    "search_filter": "(sAMAccountName={username})",
    "allowed_groups": [
      "cn=Dashboard Admins,ou=Security Groups,dc=company,dc=com"
    ]
  }
}
```

**OpenLDAP Example:**
```json
{
  "auth_method": "ldap",
  "ldap_config": {
    "server": "ldap://ldap.company.com:389",
    "base_dn": "dc=company,dc=com",
    "user_dn_template": "uid={username},ou=people,dc=company,dc=com",
    "use_ssl": false,
    "search_filter": "(uid={username})"
  }
}
```

### 3. Windows Local/Domain Authentication

Authenticate using Windows credentials (local accounts or domain accounts).

**Configuration:**
```json
{
  "auth_method": "windows",
  "auth_fallback_enabled": true,
  "windows_auth_config": {
    "domain": "COMPANY",
    "allowed_groups": ["COMPANY\\Dashboard Admins", "BUILTIN\\Administrators"]
  }
}
```

**Fields:**
- `domain` - Windows domain name (optional)
  - If empty, accepts local accounts
  - Users can specify domain in username: `DOMAIN\username` or `username@domain.com`
- `allowed_groups` - List of Windows groups users must belong to (optional)
  - Format: `DOMAIN\GroupName` or `GroupName` for local groups
  - Example: `["COMPANY\\IT Staff", "BUILTIN\\Administrators"]`

**Requirements:**
- Only available on Windows systems
- Requires `pywin32` package (automatically installed on Windows)
- Dashboard service must run with appropriate permissions

## Authentication Fallback

When `auth_fallback_enabled` is set to `true` (default), the system will fall back to Basic authentication if the primary method fails. This is useful for:
- Maintaining admin access if LDAP/Windows auth is misconfigured
- Allowing local admin access alongside directory authentication
- Service continuity during network issues

**Disable fallback for strict authentication:**
```json
{
  "auth_method": "ldap",
  "auth_fallback_enabled": false
}
```

## Configuration via API

### Get Current Settings
```bash
GET /api/auth/settings
Authorization: Basic <credentials>
```

**Response:**
```json
{
  "auth_method": "ldap",
  "auth_fallback_enabled": true,
  "available_methods": ["basic", "ldap"],
  "ldap_config": { ... },
  "windows_auth_config": { ... },
  "dashboard_user": "admin"
}
```

### Update Settings
```bash
POST /api/auth/settings
Authorization: Basic <credentials>
Content-Type: application/json

{
  "auth_method": "ldap",
  "ldap_config": {
    "server": "ldap://ldap.company.com:389",
    "base_dn": "dc=company,dc=com"
  }
}
```

### Test Authentication
```bash
POST /api/auth/test
Authorization: Basic <credentials>
Content-Type: application/json

{
  "username": "testuser",
  "password": "testpass",
  "method": "ldap"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful"
}
```

## Security Best Practices

1. **Use SSL/TLS for LDAP**
   - Set `use_ssl: true` in LDAP config
   - Use `ldaps://` protocol (port 636)

2. **Restrict Access with Groups**
   - Configure `allowed_groups` to limit dashboard access
   - Use dedicated security groups for better access control

3. **Secure Configuration File**
   - Set appropriate file permissions on `organizer_config.json`
   - Windows: Only SYSTEM and Administrators should have access
   - Linux: `chmod 600 organizer_config.json`

4. **Regular Password Rotation**
   - Rotate service account passwords regularly
   - Update `bind_password` in config when changed

5. **Monitor Authentication Logs**
   - Check dashboard logs for failed authentication attempts
   - Investigate repeated failures from same IP/user

## Troubleshooting

### LDAP Authentication Issues

**Problem:** "LDAP module not available"
```bash
# Solution: Install ldap3 package
pip install ldap3
```

**Problem:** Connection timeout or refused
- Verify LDAP server address and port
- Check firewall rules allow connections to LDAP port (389/636)
- Test connectivity: `telnet ldap.company.com 389`

**Problem:** Authentication fails for valid users
- Verify `base_dn` and `user_dn_template` are correct
- Check user DN format: `ldapsearch -x -H ldap://server -b "dc=company,dc=com" "(uid=username)"`
- Review LDAP server logs for binding errors

**Problem:** Group membership check fails
- Verify `search_filter` returns user object
- Check `memberOf` attribute exists on user objects
- Some LDAP servers require separate group query

### Windows Authentication Issues

**Problem:** "Windows authentication not available"
- Only works on Windows systems
- Install pywin32: `pip install pywin32`

**Problem:** "Access denied" errors
- Dashboard service needs appropriate permissions
- Run as domain user if authenticating domain accounts
- Local admin rights may be required for group checks

**Problem:** Domain users can't authenticate
- Specify domain in config: `"domain": "COMPANY"`
- Users can specify domain: `COMPANY\username` or `username@company.com`
- Verify trust relationship between machine and domain

### General Issues

**Problem:** Locked out of dashboard
- Enable fallback authentication: `"auth_fallback_enabled": true`
- Manually edit `organizer_config.json` and set `"auth_method": "basic"`
- Reset basic auth password using environment variables

**Problem:** Config changes not taking effect
- Restart dashboard service
- Auth manager is reinitialized on config update
- Check logs for configuration errors

## Migration Guide

### Migrating from Basic to LDAP

1. Ensure `auth_fallback_enabled` is `true` (default)
2. Add LDAP configuration to `organizer_config.json`
3. Set `auth_method` to `"ldap"`
4. Test LDAP authentication with test user
5. If working correctly, optionally disable fallback

### Migrating from LDAP to Windows Auth

1. Add Windows auth configuration
2. Change `auth_method` to `"windows"`
3. Keep `auth_fallback_enabled: true` for transition period
4. Test Windows authentication
5. Remove LDAP config if no longer needed

## Environment Variables

Override configuration using environment variables:

- `DASHBOARD_USER` - Basic auth username (default: "admin")
- `DASHBOARD_PASS` - Basic auth password (default: "change_this_password")

These are used only for initial setup if no config exists.

## Example Configurations

### Development (Basic Auth)
```json
{
  "auth_method": "basic",
  "dashboard_user": "dev",
  "auth_fallback_enabled": true
}
```

### Enterprise (LDAP with Fallback)
```json
{
  "auth_method": "ldap",
  "auth_fallback_enabled": true,
  "ldap_config": {
    "server": "ldaps://ldap.company.com:636",
    "base_dn": "dc=company,dc=com",
    "user_dn_template": "uid={username},ou=people,dc=company,dc=com",
    "use_ssl": true,
    "allowed_groups": ["cn=it-team,ou=groups,dc=company,dc=com"]
  }
}
```

### Windows Domain (Strict)
```json
{
  "auth_method": "windows",
  "auth_fallback_enabled": false,
  "windows_auth_config": {
    "domain": "COMPANY",
    "allowed_groups": ["COMPANY\\IT Admins"]
  }
}
```

## Support

For additional help:
1. Check dashboard logs: `C:\Scripts\service-logs\organizer_stdout.log`
2. Enable debug logging in Flask app
3. Review LDAP/AD server logs
4. Test authentication using API endpoints
