# Phase 2 Module Reference Documentation

Complete API contracts, usage examples, error codes, and troubleshooting for all 4 Phase 2 configuration modules.

---

## Table of Contents

1. [Users & Roles Config API](#users--roles-config-api)
2. [Network Targets Config API](#network-targets-config-api)
3. [SMTP & Credentials Manager API](#smtp--credentials-manager-api)
4. [Watched Folders Config API](#watched-folders-config-api)
5. [Error Codes & Status](#error-codes--status)
6. [Performance Benchmarks](#performance-benchmarks)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## Users & Roles Config API

Manage user accounts, roles, permissions, and authentication sources.

### Endpoints

#### GET /api/organizer/config/users
Retrieve all configured users with their roles and metadata.

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": "user-123",
      "username": "john.doe",
      "email": "john@example.com",
      "roles": ["editor", "viewer"],
      "source": "local",
      "created_at": "2025-01-15T10:30:00Z",
      "last_login": "2025-01-20T14:22:00Z",
      "enabled": true,
      "mfa_enabled": false
    }
  ],
  "total": 5,
  "active": 4
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized (auth required)
- `500` - Server error

#### POST /api/organizer/config/users
Create a new user account.

**Request Body:**
```json
{
  "username": "jane.smith",
  "email": "jane@example.com",
  "password": "SecurePassword123!",
  "roles": ["viewer"],
  "source": "local",
  "description": "Optional user description"
}
```

**Response (201 Created):**
```json
{
  "id": "user-456",
  "username": "jane.smith",
  "email": "jane@example.com",
  "roles": ["viewer"],
  "source": "local",
  "created_at": "2025-01-21T09:15:00Z",
  "message": "User created successfully"
}
```

**Validation Rules:**
- `username`: 3-32 characters, alphanumeric + underscore/dash
- `email`: Valid email format (RFC 5322)
- `password`: Min 8 chars, requires uppercase, lowercase, number, special char
- `roles`: Must be valid role names from the system

**Status Codes:**
- `201` - User created
- `400` - Invalid input (see error details)
- `409` - User already exists
- `401` - Unauthorized
- `500` - Server error

#### PUT /api/organizer/config/users/{user_id}
Update an existing user's settings.

**Request Body:**
```json
{
  "email": "jane.updated@example.com",
  "roles": ["editor", "viewer"],
  "enabled": true,
  "password": "NewPassword456!"
}
```

**Response (200 OK):**
```json
{
  "id": "user-456",
  "username": "jane.smith",
  "email": "jane.updated@example.com",
  "roles": ["editor", "viewer"],
  "updated_at": "2025-01-21T10:45:00Z",
  "message": "User updated successfully"
}
```

**Status Codes:**
- `200` - Updated
- `400` - Invalid input
- `404` - User not found
- `409` - Email already in use
- `401` - Unauthorized
- `500` - Server error

#### DELETE /api/organizer/config/users/{user_id}
Remove a user account.

**Response (204 No Content):**
No body returned.

**Status Codes:**
- `204` - Deleted
- `404` - User not found
- `401` - Unauthorized (admin only)
- `500` - Server error

#### GET /api/organizer/config/roles
Retrieve all available roles and their permissions.

**Response (200 OK):**
```json
{
  "roles": [
    {
      "id": "admin",
      "name": "Administrator",
      "description": "Full system access",
      "permissions": [
        "config:read",
        "config:write",
        "users:manage",
        "audit:read",
        "system:manage"
      ]
    },
    {
      "id": "editor",
      "name": "Editor",
      "description": "Can modify configurations",
      "permissions": [
        "config:read",
        "config:write",
        "audit:read"
      ]
    },
    {
      "id": "viewer",
      "name": "Viewer",
      "description": "Read-only access",
      "permissions": [
        "config:read",
        "audit:read"
      ]
    }
  ]
}
```

#### GET /api/organizer/config/roles/{role_id}
Get detailed information about a specific role.

**Response (200 OK):**
```json
{
  "id": "editor",
  "name": "Editor",
  "description": "Can modify configurations",
  "permissions": [
    "config:read",
    "config:write",
    "audit:read"
  ],
  "user_count": 3
}
```

### JavaScript Usage Example

```javascript
const usersConfig = new UsersRolesConfig('#users-container', {
  apiEndpoint: '/api/organizer/config/users',
  rolesEndpoint: '/api/organizer/config/roles',
  onUserAdded: (user) => console.log('User added:', user),
  onUserUpdated: (user) => console.log('User updated:', user),
  onUserRemoved: (userId) => console.log('User removed:', userId)
});

// Add user programmatically
usersConfig.addUser({
  username: 'newuser',
  email: 'new@example.com',
  roles: ['viewer']
}).then(user => console.log('Created:', user))
  .catch(error => console.error('Error:', error));

// Update user roles
usersConfig.updateUser('user-456', {
  roles: ['editor']
}).then(user => console.log('Updated:', user));

// Delete user
usersConfig.deleteUser('user-456')
  .then(() => console.log('Deleted'))
  .catch(error => console.error('Error:', error));
```

---

## Network Targets Config API

Manage network shares, UNC paths, and remote storage connections.

### Endpoints

#### GET /api/organizer/config/network-targets
Retrieve all configured network targets.

**Query Parameters:**
- `include_status=true` - Include live connectivity status
- `filter=active` - Filter by status (active, inactive, error)

**Response (200 OK):**
```json
{
  "targets": [
    {
      "id": "nas-001",
      "name": "Company NAS",
      "path": "\\\\192.168.1.50\\shared",
      "description": "Main backup location",
      "enabled": true,
      "credentials_id": "cred-nas-001",
      "protocol": "smb3",
      "status": {
        "connected": true,
        "last_check": "2025-01-21T10:55:00Z",
        "response_time_ms": 145,
        "free_space_gb": 2048,
        "used_space_gb": 512
      },
      "cache_enabled": true,
      "cache_ttl_seconds": 300
    }
  ],
  "total": 3,
  "healthy": 3
}
```

#### POST /api/organizer/config/network-targets
Add a new network target.

**Request Body:**
```json
{
  "name": "Cloud Backup",
  "path": "\\\\cloud-storage.example.com\\backup",
  "description": "Cloud-based backup storage",
  "protocol": "smb3",
  "credentials_id": "cred-cloud-123",
  "enabled": true,
  "cache_enabled": true,
  "cache_ttl_seconds": 300
}
```

**Response (201 Created):**
```json
{
  "id": "nas-002",
  "name": "Cloud Backup",
  "path": "\\\\cloud-storage.example.com\\backup",
  "enabled": true,
  "created_at": "2025-01-21T11:00:00Z",
  "message": "Network target added"
}
```

**Validation Rules:**
- `name`: 1-64 characters
- `path`: Must match UNC format (\\\\server\\share) or Windows path
- `credentials_id`: Must reference existing credential
- `cache_ttl_seconds`: 60-3600

**Status Codes:**
- `201` - Created
- `400` - Invalid input
- `409` - Target already exists
- `401` - Unauthorized
- `500` - Server error

#### POST /api/organizer/config/network-targets/test
Test connectivity to a network target.

**Request Body:**
```json
{
  "path": "\\\\192.168.1.50\\shared",
  "username": "domain\\user",
  "password": "password",
  "timeout_seconds": 10
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "path": "\\\\192.168.1.50\\shared",
  "accessible": true,
  "readable": true,
  "writable": true,
  "response_time_ms": 234,
  "free_space_gb": 2048,
  "used_space_gb": 512,
  "file_count": 1250,
  "message": "Connection successful"
}
```

**Error Response (200 OK with error details):**
```json
{
  "success": false,
  "path": "\\\\invalid.server\\share",
  "accessible": false,
  "error": "host_not_found",
  "details": "Cannot resolve hostname: invalid.server",
  "response_time_ms": 5000
}
```

**Status Codes:**
- `200` - Test completed (check `success` field for result)
- `400` - Invalid path format
- `401` - Unauthorized
- `504` - Timeout

#### PUT /api/organizer/config/network-targets/{target_id}
Update a network target configuration.

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "enabled": false,
  "cache_ttl_seconds": 600
}
```

**Response (200 OK):**
```json
{
  "id": "nas-001",
  "name": "Updated Name",
  "updated_at": "2025-01-21T11:15:00Z",
  "message": "Network target updated"
}
```

#### PUT /api/organizer/config/network-targets/{target_id}/credentials
Update credentials for a network target.

**Request Body:**
```json
{
  "username": "domain\\newuser",
  "password": "newpassword"
}
```

**Response (200 OK):**
```json
{
  "id": "nas-001",
  "credentials_updated": true,
  "message": "Credentials updated securely"
}
```

#### DELETE /api/organizer/config/network-targets/{target_id}
Remove a network target.

**Response (204 No Content):**
No body returned.

**Status Codes:**
- `204` - Deleted
- `404` - Target not found
- `401` - Unauthorized
- `500` - Server error

### JavaScript Usage Example

```javascript
const networkConfig = new NetworkTargetsConfig('#network-container', {
  apiEndpoint: '/api/organizer/config/network-targets',
  testEndpoint: '/api/organizer/config/network-targets/test',
  onTargetAdded: (target) => console.log('Target added:', target),
  onConnectionTest: (result) => console.log('Test result:', result)
});

// Test connection
networkConfig.testConnection({
  path: '\\\\192.168.1.50\\shared',
  username: 'domain\\user',
  password: 'password'
}).then(result => {
  console.log('Connected:', result.accessible);
  console.log('Free space:', result.free_space_gb, 'GB');
});

// Update credentials
networkConfig.updateCredentials('nas-001', {
  username: 'domain\\newuser',
  password: 'newpassword'
}).then(() => console.log('Credentials updated'));
```

---

## SMTP & Credentials Manager API

Manage email server configuration and encrypted credentials storage.

### Endpoints

#### GET /api/organizer/config/smtp
Retrieve SMTP server configuration.

**Response (200 OK):**
```json
{
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "use_tls": true,
    "use_ssl": false,
    "username": "notifications@company.com",
    "from_email": "notifications@company.com",
    "from_name": "DownloadsOrganizeR",
    "configured": true,
    "last_test": "2025-01-21T09:30:00Z",
    "last_test_success": true
  }
}
```

#### PUT /api/organizer/config/smtp
Update SMTP configuration.

**Request Body:**
```json
{
  "host": "smtp.gmail.com",
  "port": 587,
  "use_tls": true,
  "use_ssl": false,
  "username": "notifications@company.com",
  "password": "app-specific-password",
  "from_email": "notifications@company.com",
  "from_name": "DownloadsOrganizeR"
}
```

**Response (200 OK):**
```json
{
  "message": "SMTP configuration updated",
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "from_email": "notifications@company.com",
    "configured": true
  }
}
```

**Validation Rules:**
- `host`: Non-empty string, valid hostname/IP
- `port`: 1-65535
- `username`: 1-255 characters
- `password`: Min 6 characters
- `from_email`: Valid email format

**Status Codes:**
- `200` - Updated
- `400` - Invalid input
- `401` - Unauthorized
- `500` - Server error

#### POST /api/organizer/config/smtp/test
Test SMTP connection and authentication.

**Request Body:**
```json
{
  "host": "smtp.gmail.com",
  "port": 587,
  "use_tls": true,
  "username": "test@gmail.com",
  "password": "app-password",
  "timeout_seconds": 30
}
```

**Response (200 OK - Success):**
```json
{
  "success": true,
  "message": "SMTP connection successful",
  "response_time_ms": 450,
  "server_info": "Gmail SMTP server ready",
  "auth_success": true
}
```

**Response (200 OK - Failure):**
```json
{
  "success": false,
  "message": "Authentication failed",
  "error": "invalid_credentials",
  "details": "Login credentials rejected by SMTP server",
  "response_time_ms": 1200
}
```

**Status Codes:**
- `200` - Test completed (check `success` field)
- `400` - Invalid parameters
- `401` - Unauthorized
- `504` - Connection timeout

#### GET /api/organizer/config/credentials
List all stored credentials (passwords/tokens not returned).

**Response (200 OK):**
```json
{
  "credentials": [
    {
      "id": "cred-nas-001",
      "name": "NAS Credentials",
      "type": "basic",
      "username": "domain\\user",
      "created_at": "2025-01-15T10:00:00Z",
      "last_used": "2025-01-21T09:45:00Z",
      "encrypted": true
    },
    {
      "id": "cred-oauth-gmail",
      "name": "Gmail OAuth",
      "type": "oauth2",
      "provider": "google",
      "created_at": "2025-01-18T14:30:00Z",
      "last_used": "2025-01-21T10:00:00Z",
      "scopes": ["mail.send"]
    }
  ],
  "total": 2
}
```

#### POST /api/organizer/config/credentials
Add a new credential.

**Request Body (Basic Auth):**
```json
{
  "name": "Remote Server",
  "type": "basic",
  "username": "admin",
  "password": "SecurePassword123!"
}
```

**Request Body (OAuth2):**
```json
{
  "name": "Azure OAuth",
  "type": "oauth2",
  "provider": "microsoft",
  "client_id": "client-id-here",
  "client_secret": "secret-here",
  "scopes": ["Directory.Read.All"]
}
```

**Response (201 Created):**
```json
{
  "id": "cred-new-001",
  "name": "Remote Server",
  "type": "basic",
  "username": "admin",
  "created_at": "2025-01-21T11:30:00Z",
  "message": "Credential stored securely"
}
```

**Validation Rules:**
- `name`: 1-64 characters, unique
- `type`: `basic`, `oauth2`, `ldap`, or `certificate`
- For `basic`: username (1-255), password (min 6)
- For `oauth2`: client_id, client_secret, provider

**Status Codes:**
- `201` - Created
- `400` - Invalid input
- `409` - Credential name already exists
- `401` - Unauthorized
- `500` - Server error

#### POST /api/organizer/config/credentials/validate
Validate credentials without storing.

**Request Body:**
```json
{
  "type": "basic",
  "username": "testuser",
  "password": "testpass",
  "target_type": "ldap",
  "ldap_server": "ldap.company.com"
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "message": "Credentials validated successfully",
  "details": {
    "user_dn": "cn=testuser,ou=users,dc=company,dc=com",
    "groups": ["Users", "Staff"]
  }
}
```

#### DELETE /api/organizer/config/credentials/{credential_id}
Remove a credential.

**Response (204 No Content):**
No body returned.

**Status Codes:**
- `204` - Deleted
- `404` - Credential not found
- `401` - Unauthorized
- `500` - Server error

### JavaScript Usage Example

```javascript
const smtpConfig = new SmtpCredentialsManager('#smtp-container', {
  apiEndpoint: '/api/organizer/config/smtp',
  credentialsEndpoint: '/api/organizer/config/credentials',
  testEndpoint: '/api/organizer/config/smtp/test'
});

// Update SMTP config
smtpConfig.updateSmtp({
  host: 'smtp.gmail.com',
  port: 587,
  use_tls: true,
  username: 'test@gmail.com',
  password: 'app-password'
}).then(() => console.log('SMTP configured'));

// Test connection
smtpConfig.testSmtp({
  host: 'smtp.gmail.com',
  port: 587,
  use_tls: true,
  username: 'test@gmail.com',
  password: 'app-password'
}).then(result => {
  console.log('Test successful:', result.success);
  console.log('Response time:', result.response_time_ms, 'ms');
});

// Store credentials
smtpConfig.addCredential({
  name: 'NAS Admin',
  type: 'basic',
  username: 'domain\\admin',
  password: 'password'
}).then(cred => console.log('Credential stored:', cred.id));
```

---

## Watched Folders Config API

Monitor and organize files from multiple source folders.

### Endpoints

#### GET /api/organizer/config/folders
Retrieve all watched folders.

**Response (200 OK):**
```json
{
  "folders": [
    {
      "id": "folder-downloads",
      "path": "C:\\Users\\username\\Downloads",
      "enabled": true,
      "recursive": true,
      "description": "Main downloads folder",
      "created_at": "2025-01-10T08:00:00Z",
      "status": {
        "accessible": true,
        "readable": true,
        "writable": true,
        "file_count": 245,
        "size_mb": 1250,
        "last_scanned": "2025-01-21T10:55:00Z"
      }
    },
    {
      "id": "folder-desktop",
      "path": "/home/user/Desktop",
      "enabled": true,
      "recursive": false,
      "description": "Desktop folder",
      "status": {
        "accessible": true,
        "readable": true,
        "writable": true,
        "file_count": 12,
        "size_mb": 245
      }
    }
  ],
  "total": 2,
  "healthy": 2
}
```

#### POST /api/organizer/config/folders
Add a new watched folder.

**Request Body:**
```json
{
  "path": "/home/user/Downloads",
  "enabled": true,
  "recursive": true,
  "description": "Main downloads directory",
  "create_if_missing": true
}
```

**Response (201 Created):**
```json
{
  "id": "folder-new-001",
  "path": "/home/user/Downloads",
  "enabled": true,
  "created_at": "2025-01-21T11:45:00Z",
  "message": "Folder added to watch list"
}
```

**Validation Rules:**
- `path`: Must be valid filesystem path (Windows/UNC/Unix formats)
- Supports placeholders: `%USERNAME%`, `%USER%`, `%USERPROFILE%`
- Max path length: 260 characters (Windows) or 4096 (Unix)

**Status Codes:**
- `201` - Created
- `400` - Invalid path format
- `409` - Folder already in watch list
- `401` - Unauthorized
- `500` - Server error

#### POST /api/organizer/config/folders/test
Test a folder path for accessibility.

**Request Body:**
```json
{
  "path": "/home/user/Downloads",
  "check_write": true,
  "resolve_placeholders": true
}
```

**Response (200 OK):**
```json
{
  "path": "/home/user/Downloads",
  "resolved_path": "/home/user/Downloads",
  "accessible": true,
  "readable": true,
  "writable": true,
  "exists": true,
  "is_directory": true,
  "file_count": 245,
  "size_mb": 1250,
  "last_modified": "2025-01-21T10:55:00Z",
  "permissions": "rwx",
  "message": "Folder is accessible and ready"
}
```

**Error Response (200 OK):**
```json
{
  "path": "%USERPROFILE%\\Downloads",
  "resolved_path": "C:\\Users\\john.doe\\Downloads",
  "accessible": false,
  "readable": false,
  "writable": false,
  "error": "permission_denied",
  "details": "Insufficient permissions to access folder"
}
```

**Status Codes:**
- `200` - Test completed
- `400` - Invalid path format
- `401` - Unauthorized
- `504` - Timeout (path too slow to access)

#### POST /api/organizer/config/folders/test-all
Test all configured folders for accessibility.

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "folder-downloads",
      "path": "C:\\Users\\username\\Downloads",
      "accessible": true,
      "readable": true,
      "writable": true,
      "file_count": 245
    },
    {
      "id": "folder-desktop",
      "path": "/home/user/Desktop",
      "accessible": true,
      "readable": true,
      "writable": true,
      "file_count": 12
    }
  ],
  "total": 2,
  "healthy": 2,
  "completed_at": "2025-01-21T11:50:00Z"
}
```

#### PUT /api/organizer/config/folders/{folder_id}
Update folder configuration.

**Request Body:**
```json
{
  "enabled": false,
  "recursive": true,
  "description": "Updated description"
}
```

**Response (200 OK):**
```json
{
  "id": "folder-downloads",
  "path": "C:\\Users\\username\\Downloads",
  "updated_at": "2025-01-21T12:00:00Z",
  "message": "Folder configuration updated"
}
```

#### DELETE /api/organizer/config/folders/{folder_id}
Stop watching a folder.

**Response (204 No Content):**
No body returned.

**Status Codes:**
- `204` - Deleted
- `404` - Folder not found
- `401` - Unauthorized
- `500` - Server error

#### GET /api/organizer/config/audit/folders
Get audit log for folder configuration changes.

**Response (200 OK):**
```json
{
  "audit_log": [
    {
      "timestamp": "2025-01-21T11:45:00Z",
      "action": "folder_added",
      "folder_id": "folder-new-001",
      "path": "/home/user/Downloads",
      "user": "admin",
      "details": "New folder added to watch list"
    },
    {
      "timestamp": "2025-01-21T12:00:00Z",
      "action": "folder_updated",
      "folder_id": "folder-downloads",
      "changes": {
        "enabled": false
      },
      "user": "admin"
    }
  ],
  "total": 15,
  "oldest": "2025-01-10T08:00:00Z"
}
```

### JavaScript Usage Example

```javascript
const foldersConfig = new WatchedFoldersConfig('#folders-container', {
  apiEndpoint: '/api/organizer/config/folders',
  testEndpoint: '/api/organizer/config/folders/test',
  auditEndpoint: '/api/organizer/config/audit/folders'
});

// Add folder to watch list
foldersConfig.addFolder({
  path: '/home/user/Downloads',
  enabled: true,
  recursive: true,
  description: 'Main downloads'
}).then(folder => console.log('Folder added:', folder.id));

// Test folder access
foldersConfig.testFolder({
  path: '%USERPROFILE%\\Documents',
  check_write: true,
  resolve_placeholders: true
}).then(result => {
  console.log('Accessible:', result.accessible);
  console.log('Files:', result.file_count);
  console.log('Size:', result.size_mb, 'MB');
});

// Batch test all folders
foldersConfig.testAllFolders()
  .then(results => {
    console.log('Total folders:', results.total);
    console.log('Healthy:', results.healthy);
  });

// View audit log
foldersConfig.getAuditLog()
  .then(log => console.log('Recent changes:', log.audit_log.slice(0, 5)));
```

---

## Error Codes & Status

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| `200` | OK | Success - operation completed |
| `201` | Created | Resource created successfully |
| `204` | No Content | Success - no response body (e.g., DELETE) |
| `400` | Bad Request | Invalid input - check request format |
| `401` | Unauthorized | Authentication required - login first |
| `403` | Forbidden | Authenticated but permission denied |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Resource already exists / conflict detected |
| `413` | Payload Too Large | Request body exceeds size limit |
| `500` | Server Error | Internal server error - contact support |
| `504` | Timeout | Operation timed out (network/disk access) |

### API Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "field_name",
    "reason": "Detailed explanation"
  },
  "timestamp": "2025-01-21T12:00:00Z",
  "request_id": "req-12345"
}
```

### Error Codes Reference

#### User Management Errors
- `invalid_username` - Username format invalid
- `password_too_weak` - Password doesn't meet requirements
- `user_exists` - Username/email already in system
- `user_not_found` - User ID doesn't exist
- `role_invalid` - Role name not recognized
- `role_not_found` - Role doesn't exist

#### Network Target Errors
- `invalid_path_format` - UNC/network path format incorrect
- `host_not_found` - Network host cannot be resolved
- `connection_refused` - Server rejected connection
- `auth_failed` - Credentials rejected by server
- `timeout` - Connection/operation timed out
- `permission_denied` - Access denied by server
- `target_exists` - Network target already configured

#### SMTP Errors
- `invalid_host` - SMTP host format invalid
- `invalid_port` - SMTP port out of valid range
- `connection_failed` - Cannot connect to SMTP server
- `auth_failed` - SMTP authentication failed
- `tls_required` - Server requires TLS/SSL
- `invalid_email` - Email address format invalid
- `smtp_error` - Generic SMTP server error

#### Folder Errors
- `invalid_path_format` - Path format not recognized
- `path_not_found` - Folder doesn't exist
- `permission_denied` - Cannot access folder
- `path_too_long` - Path exceeds maximum length
- `folder_exists` - Folder already in watch list
- `invalid_placeholder` - Placeholder token not recognized
- `recursive_error` - Issue with recursive watching

---

## Performance Benchmarks

### Response Times (Target)

| Operation | Target Time | Notes |
|-----------|------------|-------|
| List all users | < 100ms | Up to 1000 users |
| List all network targets | < 200ms | With status checks |
| Get SMTP config | < 50ms | Simple read |
| List watched folders | < 150ms | With file counts |
| Test single folder | < 2s | Depends on folder size |
| Test network path | < 10s | Network latency included |
| Test SMTP | < 5s | Network timeout |

### Concurrent Users

- Dashboard: Supports up to 10 concurrent users
- API: Supports 50+ concurrent requests
- Config file: Thread-safe read/write operations

### Data Limits

| Parameter | Limit | Notes |
|-----------|-------|-------|
| Max users | 10,000 | Practical limit depends on storage |
| Max network targets | 1,000 | Per organization |
| Max watched folders | 500 | Per system |
| Max credentials | 10,000 | Encrypted storage |
| Config file size | 100MB | Auto-backup at 50MB |
| Audit log size | 1GB | Auto-rotate when full |

---

## Troubleshooting Guide

### Users & Roles Issues

#### Problem: "User already exists" error
**Cause:** Username or email already in system
**Solution:** 
- Check existing users: `GET /api/organizer/config/users`
- Use unique username/email or update existing user: `PUT /api/organizer/config/users/{id}`
- Check case sensitivity (usernames are case-insensitive)

#### Problem: "Password too weak" error
**Cause:** Password doesn't meet security requirements
**Solution:**
- Password must be at least 8 characters
- Must include: uppercase (A-Z), lowercase (a-z), number (0-9), special character (!@#$%^&*)
- Example: `SecurePass123!`

#### Problem: Permission denied when updating roles
**Cause:** Insufficient permissions
**Solution:**
- Verify your user has `users:manage` permission
- Check your role: `GET /api/organizer/config/roles`
- Contact administrator to elevate permissions

### Network Target Issues

#### Problem: "Host not found" when testing UNC path
**Cause:** Server name cannot be resolved
**Solution:**
- Verify server name spelling: `\\server\share`
- Check DNS resolution: `ping server`
- Verify network connectivity
- Check firewall rules (SMB port 445)
- Try IP address instead: `\\192.168.1.50\share`

#### Problem: "Connection refused" on network test
**Cause:** Server rejected connection
**Solution:**
- Verify server is online: `ping server`
- Check SMB service is running on server
- Verify port 445 is open (Windows Firewall)
- Check network interface is enabled

#### Problem: "Permission denied" after adding target
**Cause:** Credentials incorrect or insufficient permissions
**Solution:**
- Verify username format: `DOMAIN\username` (not just `username`)
- Confirm password is correct
- Check folder permissions on server
- Try with different credentials: `PUT /api/organizer/config/network-targets/{id}/credentials`
- Verify network share isn't restricted to specific IPs

### SMTP Configuration Issues

#### Problem: "SMTP test failed" - "Connection refused"
**Cause:** Cannot reach SMTP server
**Solution:**
- Verify SMTP server address: common ones are:
  - Gmail: `smtp.gmail.com:587` (TLS)
  - Office 365: `smtp.office365.com:587` (TLS)
  - Outlook: `smtp-mail.outlook.com:587` (TLS)
- Check firewall allows outbound port 587 or 465
- Disable VPN/proxy temporarily to test
- Verify server is not rate-limiting connections

#### Problem: "SMTP authentication failed"
**Cause:** Invalid credentials
**Solution:**
- Double-check username and password
- For Gmail: Use app-specific password, not regular password
- For Office 365: Verify username is full email address
- Check if account has MFA enabled (may need app password)
- Verify account isn't locked due to too many failed attempts

#### Problem: "TLS required but not enabled"
**Cause:** Server requires encryption
**Solution:**
- Enable TLS: Set `use_tls: true` in configuration
- For Gmail/Office 365: Use port 587 with TLS
- For secure connections: Use port 465 with SSL
- Don't use port 25 (deprecated, requires TLS)

### Watched Folders Issues

#### Problem: "Invalid path format" error
**Cause:** Path doesn't match expected format
**Solution:**
- Windows paths: `C:\Users\username\Downloads` or `C:/Users/username/Downloads`
- UNC paths: `\\server\share\folder`
- Unix paths: `/home/user/Downloads`
- Check for invalid characters: `< > : " | ? *`
- Verify path length (max 260 Windows, 4096 Unix)

#### Problem: "Permission denied" when testing folder
**Cause:** Insufficient folder permissions
**Solution:**
- Check folder ownership: `ls -l folder` (Unix) or Properties (Windows)
- Verify read/execute permissions for current user
- Try with `sudo` on Unix systems
- Check if folder is mounted and accessible
- Verify external drive is connected and mounted

#### Problem: Placeholder not resolving
**Cause:** Unsupported placeholder token
**Solution:**
- Supported placeholders: `%USERNAME%`, `%USER%`, `%USERPROFILE%`
- These are case-insensitive
- Verify token is spelled correctly
- Custom placeholders not supported - use full paths instead

#### Problem: "Folder already in watch list"
**Cause:** Folder is already being monitored
**Solution:**
- Check existing folders: `GET /api/organizer/config/folders`
- Delete existing entry if needed: `DELETE /api/organizer/config/folders/{id}`
- Watch lists are per-system, not per-user

### General Troubleshooting

#### Check Audit Logs
```javascript
// View recent changes
GET /api/organizer/config/audit/users
GET /api/organizer/config/audit/network
GET /api/organizer/config/audit/smtp
GET /api/organizer/config/audit/folders
```

#### Export Configuration
```javascript
// Backup config for analysis
const config = await fetch('/api/organizer/config/export').then(r => r.json());
console.log(JSON.stringify(config, null, 2));
```

#### Health Check
```javascript
// Check overall system health
const health = await fetch('/api/organizer/health').then(r => r.json());
console.log('System status:', health.status);
```

#### Enable Debug Logging
Set environment variable: `DEBUG=sortnstore:*`
Then check logs: `cat organizer.log | grep ERROR`

---

## Additional Resources

- [Configuration Guide](./CONFIGURATION.md)
- [API Quick Reference](./API_QUICK_REFERENCE.md)
- [Security Best Practices](./SECURITY.md)
- [Deployment Guide](./DEPLOYMENT_CHECKLIST.md)
- [GitHub Issues](https://github.com/Atomsk865/DownloadsOrganizeR/issues)
