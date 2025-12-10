# Configuration Panel Guide

## Overview

The SortNStore Dashboard now features a comprehensive tabbed configuration interface that allows administrators to manage all aspects of the system without editing configuration files directly.

## Accessing Configuration

1. Navigate to the main dashboard
2. Click the **Configuration** link in the navigation menu
3. You'll be presented with a tabbed interface organized by category

## Configuration Tabs

### 1. General Tab

**Features & Integrations**
- **VirusTotal API Key**: Optional API key for hash lookups in Recent Files
  - Leave blank to disable VirusTotal integration
  - Obtain key from: https://www.virustotal.com/gui/my-apikey
  
- **Feature Toggles**:
  - ☑ VirusTotal Integration
  - ☑ Duplicate Detection
  - ☑ Reports & Analytics
  - ☐ Developer Mode (shows debugging tools)

**Branding**
- **Dashboard Title**: Customize the page title
- **Favicon URL**: Path to custom favicon icon

### 2. Security Tab

#### Rate Limiting & Failed Login Protection

Configure protection against brute-force login attempts:

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Rate Limit | 10 | 1-100 | Max login attempts per IP per minute |
| Rate Window | 60s | 10-300s | Time window for rate calculation |
| Failed Attempts | 5 | 3-20 | Attempts before lockout |
| Lockout Duration | 5 min | 1-60 min | How long lockout lasts |

**Features**:
- Per-IP rate limiting (prevents automated attacks)
- Per-username lockout (prevents credential stuffing)
- Per-IP lockout (blocks malicious sources)
- Persistent state (survives service restarts)

**Actions**:
- **Save Rate Limit Settings**: Apply changes
- **View Lockout Status**: See currently locked IPs/users

#### Session Timeout

Automatic session expiration for idle or long-running sessions:

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Absolute Lifetime | 60 min | 10-480 min | Max session duration |
| Idle Timeout | 30 min | 5-120 min | Inactivity before logout |
| Warning Threshold | 25 min | 1-60 min | Show warning at this idle time |

**Features**:
- Absolute timeout (sessions expire after N minutes regardless of activity)
- Idle timeout (sessions expire after N minutes of inactivity)
- Warning popup before idle expiration
- Keep-alive mechanism via API calls

**Actions**:
- **Save Session Settings**: Apply changes
- **Current Session Info**: View your session age and idle time

#### IP Allowlist (CIDR-Based Access Control)

Restrict dashboard access to specific IP addresses or CIDR ranges:

**Configuration**:
- Enter one IP address or CIDR range per line
- Supports IPv4 and IPv6
- **Empty list = All IPs allowed** (feature disabled)
- Non-empty list = Only listed IPs/ranges allowed

**CIDR Examples**:
```
192.168.1.0/24      # Local network (192.168.1.0 to 192.168.1.255)
10.0.0.0/8          # Private class A (10.0.0.0 to 10.255.255.255)
172.16.0.0/12       # Private class B
203.0.113.42/32     # Single IP address
2001:db8::/32       # IPv6 range
```

**Quick Insert Buttons**:
- Local Network (192.168.1.0/24)
- Private Class A (10.0.0.0/8)
- Private Class B (172.16.0.0/12)

**Features**:
- CIDR notation validation before saving
- X-Forwarded-For header support (proxy-aware)
- Fail-open on configuration errors (prevents admin lockout)
- Status indicator (ENABLED/DISABLED badge)

**Actions**:
- **Save IP Allowlist**: Apply CIDR list
- **Validate CIDR Syntax**: Check for errors without applying
- **Clear (Allow All)**: Remove all restrictions

**⚠️ Warning**: Test carefully! Invalid configuration could lock you out. Always validate CIDR syntax first.

#### Security Headers

Automatically applied HTTP security headers (requires service restart to modify):

| Header | Status | Value |
|--------|--------|-------|
| Content-Security-Policy | ✅ Active | Restricts resource loading |
| X-Frame-Options | ✅ Active | DENY (prevents clickjacking) |
| X-Content-Type-Options | ✅ Active | nosniff (prevents MIME confusion) |
| Referrer-Policy | ✅ Active | strict-origin-when-cross-origin |
| Strict-Transport-Security | ⚠️ Production Only | max-age=31536000 (HTTPS required) |

These headers are configured in the application code and provide defense-in-depth against common web attacks.

#### Audit Log

Configure audit log retention and size limits:

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Retention Days | 90 | 7-365 | Auto-delete entries older than N days |
| Max Entries | 10,000 | 1k-100k | Maximum audit log size |

**Audit Events Logged**:
- Successful logins
- Failed login attempts
- Rate limit violations
- Lockout triggers
- IP allowlist denials
- Admin actions (unlock, config changes)

**Actions**:
- **Save Audit Settings**: Apply retention policy
- **View Audit Log**: Open last 50 events in new window

### 3. Users & Auth Tab

#### User Management

Manage dashboard users and their roles:

**User Table**:
- Username
- Assigned Role
- Actions (Edit, Delete)

**Add/Update User**:
1. Enter username
2. Enter password (leave blank to keep existing when updating)
3. Select role (Admin, Operator, Viewer)
4. Click **Add** or **Update**

**Search**: Filter users by username using search box

#### Role Permissions

Configure granular permissions for each role:

| Permission | Admin | Operator | Viewer | Description |
|------------|-------|----------|--------|-------------|
| Manage Service | ✅ | ✅ | ❌ | Start/stop service |
| Manage Config | ✅ | ❌ | ❌ | Edit configuration |
| View Metrics | ✅ | ✅ | ✅ | See system stats |
| View Recent Files | ✅ | ✅ | ✅ | Access file history |
| Modify Layout | ✅ | ❌ | ❌ | Customize dashboard |
| Test SMTP | ✅ | ❌ | ❌ | Send test emails |
| Test NAS | ✅ | ❌ | ❌ | Test network shares |
| Manage Network Targets | ✅ | ❌ | ❌ | Add/edit UNC paths |
| Manage Credentials | ✅ | ❌ | ❌ | Edit stored passwords |
| Send Reports | ✅ | ❌ | ❌ | Generate reports |

### 4. Service Tab

#### Service Installation

Install SortNStore as a Windows service for automatic startup:

- Click **Launch Service Installer** to open the installation wizard
- Configure service to run at system boot
- Manage service via Windows Services panel

#### Watched Folders

Configure which folders SortNStore monitors for new files:

- Add new watched folders with **Add Watched Folder** button
- Each folder can have custom organization rules
- Enable/disable monitoring per folder

#### Network Targets (UNC Paths)

Configure credentials for network shares:

- Store credentials for UNC paths (\\server\share)
- Credentials encrypted in configuration
- Test connectivity before saving

### 5. Advanced Tab

#### API Settings

Configure API behavior:

- **Rate Limit**: Requests per minute for API endpoints
- **Timeout**: Maximum request duration in seconds

#### Logs

View and manage service logs:

- Real-time log viewer with refresh
- Clear logs button (removes old entries)
- Logs displayed in monospace font for readability

#### Danger Zone

⚠️ **Warning**: These actions cannot be undone!

- **Factory Reset**: Restore all settings to defaults (preserves admin user)
- **Re-run Setup Wizard**: Restart initial configuration process
- **Repair Auth Config**: Align admin credentials across config files

## Global Actions

Available at the top of all tabs:

- **Export**: Download complete configuration backup (JSON)
- **Import**: Restore configuration from backup file
  - Validates backup before importing
  - Shows export timestamp and version
  - Confirms before overwriting
- **Reset**: Factory reset (available in Advanced tab too)
- **Back**: Return to main dashboard

## Best Practices

### Security Configuration

1. **Start with defaults**: Test before tightening security
2. **Document changes**: Note why specific thresholds were chosen
3. **Test lockout recovery**: Ensure you can unlock accounts
4. **Monitor audit log**: Review regularly for suspicious activity
5. **IP allowlist**: Test with single IP before adding ranges

### Session Management

1. **Balance security and usability**: 30min idle is reasonable for most use cases
2. **Warn before timeout**: 25min warning gives 5min to save work
3. **Consider user workflows**: Longer sessions for batch operations

### Rate Limiting

1. **10 req/min is safe for humans**: Blocks automated attacks without impacting users
2. **5 failed attempts**: Catches brute force without false positives from typos
3. **5min lockout**: Long enough to deter attacks, short enough to unlock quickly

### IP Allowlist

1. **Start permissive**: Add restrictions after confirming connectivity
2. **Use CIDR ranges**: Easier than individual IPs for networks
3. **Consider remote access**: VPN, dynamic IPs, proxies
4. **Test before production**: Validate access from all expected sources
5. **Have a backup**: SSH access, console login, or physical access

## Troubleshooting

### "Failed to save security settings"

**Cause**: Invalid configuration values or missing permissions

**Solutions**:
1. Check browser console for specific error
2. Verify values are within allowed ranges
3. Ensure admin role has `manage_config` permission
4. Check dashboard service logs for errors

### "IP allowlist locked me out"

**Causes**: 
- Your IP not in allowlist
- Proxy/NAT changed your IP
- CIDR syntax error

**Recovery**:
1. Edit `dashboard_config.json` directly
2. Set `ip_allowlist: []` to disable feature
3. Restart dashboard service
4. Re-configure with correct IPs

**Prevention**:
- Always validate CIDR before saving
- Test with single known-good IP first
- Add your current IP via "Current IP" button (if implemented)

### "Session expired" immediately after login

**Cause**: System clock mismatch or negative timeout values

**Solutions**:
1. Verify server time is correct: `date`
2. Check session timeout values are positive
3. Review `session_lifetime` > `idle_timeout`
4. Check browser cookies enabled

### "Rate limit exceeded" for legitimate user

**Cause**: Shared IP (NAT/proxy) hitting rate limit

**Solutions**:
1. Increase rate limit threshold temporarily
2. Unlock IP via `/api/security/unlock`
3. Add IP to allowlist to bypass rate limiting (if trusted)
4. Configure X-Forwarded-For if behind proxy

## Configuration Files

Settings are persisted in:

| File | Contents |
|------|----------|
| `dashboard_config.json` | Users, roles, layout, security_config, ip_allowlist |
| `sortnstore_config.json` | Service settings, routes, features |
| `config/json/auth_state.json` | Lockout state, failed attempts |
| `config/json/auth_audit.json` | Audit log entries |

**Backup Strategy**:
1. Export config regularly via UI (includes all settings)
2. Store backups securely (contains sensitive data)
3. Version backups by date: `config_backup_2025-12-10.json`

## API Endpoints

For programmatic access (requires admin authentication):

### Security Configuration

```bash
# Get all security settings
curl -u admin:password http://localhost:5000/api/security/config

# Update security settings
curl -u admin:password -X POST \
  -H "Content-Type: application/json" \
  -d '{"rate_limit": 20, "lockout_attempts": 10}' \
  http://localhost:5000/api/security/config

# Validate CIDR list
curl -u admin:password -X POST \
  -H "Content-Type: application/json" \
  -d '{"cidrs": ["192.168.1.0/24", "10.0.0.0/8"]}' \
  http://localhost:5000/api/security/validate-cidr

# View lockout status
curl -u admin:password http://localhost:5000/api/security/lockout-status

# Unlock IP or user
curl -u admin:password -X POST \
  -H "Content-Type: application/json" \
  -d '{"identifier": "192.168.1.100", "type": "ip"}' \
  http://localhost:5000/api/security/unlock
```

---

**Last Updated**: December 10, 2025  
**Version**: 2.0 (Tabbed UI)  
**Related Docs**: 
- [Security Hardening Guide](security/SECURITY_HARDENING.md)
- [HTTPS/TLS Configuration](security/HTTPS_TLS_GUIDE.md)
- [Authentication Guide](AUTHENTICATION.md)
