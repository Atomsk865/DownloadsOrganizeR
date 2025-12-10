# UNC Path Credentials Management Feature

## Overview

The UNC (Universal Naming Convention) Credentials Management feature enables users to configure authentication for network file shares (UNC paths) directly from the Dashboard Settings module. This feature provides a secure, user-friendly way to:

- Validate UNC path syntax
- Test network connectivity with authentication credentials
- Store and manage Windows Auth and LDAP credentials
- Organize files from network shares with automatic categorization

## Architecture

### Backend Components

#### 1. **UNC Credentials Route Module** (`OrganizerDashboard/routes/unc_credentials.py`)
Blueprint-based Flask routes for credential management with 4 endpoints:

**POST `/api/unc/validate-syntax`**
- Input: `{ "unc_path": "\\\\server\\share" }`
- Output: `{ "valid": true/false, "message": "..." }`
- Validates UNC path format (must start with `\\`) and tests basic path reachability

**POST `/api/unc/test-credentials`**
- Input: `{ "unc_path", "username", "password", "domain", "hostname", "auth_type" }`
- Output: `{ "success": true/false, "message": "..." }`
- Tests connection with provided credentials
- Windows Auth: Uses `net use` command with domain\username
- LDAP: Validates LDAP connectivity
- Only executed if syntax validation passes

**POST `/api/unc/save-credentials`**
- Input: Credential object with all fields
- Output: `{ "success": true, "message": "Credentials saved" }`
- Persists credentials to `organizer_config.json` under `unc_credentials` key
- Only stores non-empty fields (sparse config pattern)
- Password is encrypted before storage

**GET `/api/unc/get-credentials/<path>`**
- Input: UNC path (URL-encoded)
- Output: `{ "credentials": { "username", "domain", "hostname", "auth_type" } }`
- Retrieves saved credentials (password field is excluded for security)
- Allows users to edit existing credentials without re-entering password

### Frontend Components

#### 1. **Settings Module** (`dash/modules/settings.html`)

**Watch Folder Input**
- Added UNC credentials button (appears only for UNC paths)
- Blue info alert displays when UNC path is detected
- Placeholder text updated to include UNC example: `\\server\share`

**UNC Credentials Modal**
- Form sections:
  - **UNC Path Display**: Read-only field showing current path
  - **Authentication Type**: Dropdown selector (Windows Auth / LDAP)
  - **Windows Auth Fields**: Domain and Hostname (optional)
  - **Credentials**: Username and Password (required)
  - **Status Messages**: Info/error alerts for validation and test results

**Modal Buttons**
- Cancel: Closes modal without saving
- Test Connection: Validates credentials before saving
- Save Credentials: Persists credentials to backend

#### 2. **Dashboard Scripts** (`dash/dashboard_scripts.html`)

**UNC Credential Functions:**

```javascript
showUNCCredentialsModal()          // Opens credential form
validateUNCSyntax(path)            // Validates UNC path format
loadUNCCredentials(path)           // Retrieves saved credentials
updateUNCAuthFields()              // Shows/hides auth type specific fields
testUNCCredentials()               // Tests connection with credentials
saveUNCCredentials()               // Persists credentials to backend
clearUNCFields()                   // Resets form fields
showUNCMessage(msg, type)          // Displays success messages
showUNCError(msg)                  // Displays error messages
```

**Auto-Detection Logic**
- Watches `watch_folder` input blur event
- Detects paths starting with `\\` (UNC paths)
- Shows warning message and credentials button when UNC path detected
- Hides both when local path is entered

## User Workflow

### Step 1: Enter UNC Path
User enters UNC path in Watch Folder field: `\\server\share`

### Step 2: Trigger Credentials Dialog
- Option A: Click "UNC Creds" button that appears
- Option B: Blur the input field (auto-detection)
Modal opens with syntax validation result

### Step 3: Choose Authentication Type
- **Windows Auth (Default)**
  - Autofill: Username field empty, Domain/Hostname optional
  - Recommended for Active Directory environments
- **LDAP**
  - Autofill: Hostname field (LDAP server)
  - Recommended for LDAP directory services

### Step 4: Enter Credentials
- Username: Required
- Password: Required, never pre-filled for security
- Domain: Optional (Windows Auth only)
- Hostname: Optional (Windows Auth) or LDAP server address

### Step 5: Test Connection (Optional)
Click "Test Connection" button to verify credentials before saving
- Displays "Testing..." spinner while validating
- Shows success message if connection succeeds
- Shows error message if connection fails

### Step 6: Save Credentials
Click "Save Credentials" button
- Only non-empty fields are stored (sparse config)
- Modal closes on success
- Success notification displays in dashboard

## Configuration Storage

### Config Location
`organizer_config.json` → `unc_credentials` section

### Example Configuration
```json
{
  "unc_credentials": {
    "\\\\server\\share": {
      "username": "domain\\user",
      "domain": "DOMAIN",
      "hostname": "server",
      "auth_type": "windows"
    },
    "\\\\ldap-server\\data": {
      "username": "user@ldap.example.com",
      "hostname": "ldap-server",
      "auth_type": "ldap"
    }
  }
}
```

### Security Considerations
- Passwords are encrypted before storage (uses Flask session security)
- Password field is never returned by `get-credentials` endpoint
- All credential transmissions use HTTPS (recommended)
- Authentication header required for all UNC credential endpoints

## Integration with Organizer.py

### Watch Folders Configuration
When user sets UNC path in watch_folder setting:

1. **Backend stores UNC path** in `watch_folders` configuration
2. **Backend stores credentials** in `unc_credentials` section
3. **Service restart required** (prompted after save)
4. **Organizer.py loads credentials** from config on startup
5. **Credentials used for network access** when organizing files from UNC path

### Network Retry Logic
Organizer.py includes network retry queue for handling:
- Temporary network unavailability
- Credential failures (retries with stored credentials)
- File access timeouts

## Error Handling

### Frontend Error Messages
- **Invalid UNC Syntax**: "Invalid UNC path format" (must start with \\)
- **Connection Failed**: Error from backend (e.g., "Access denied")
- **Missing Required Fields**: "Username and password are required"
- **Save Failed**: Generic error message with details

### Backend Error Responses
All endpoints return JSON with error details:
```json
{
  "error": "Detailed error message",
  "status": "error"
}
```

## Testing the Feature

### Manual Testing Steps

1. **Test Syntax Validation**
   - Enter invalid UNC path: `\invalid\path` → Should show error
   - Enter valid UNC path: `\\server\share` → Should validate

2. **Test Credential Testing**
   - Enter valid credentials and click "Test Connection"
   - Verify success/failure message displays correctly

3. **Test Credential Storage**
   - Click "Save Credentials"
   - Verify credentials saved in config
   - Edit same UNC path → Verify credentials pre-populate (except password)

4. **Test Auto-Detection**
   - Enter UNC path in watch folder → Warning should appear
   - Switch to local path → Warning should disappear

5. **Test Service Integration**
   - Set UNC path with credentials
   - Restart service
   - Verify Organizer.py uses stored credentials for file organization

## Troubleshooting

### Issue: "UNC Creds" button doesn't appear
**Solution**: Ensure path starts with `\\` (e.g., `\\server\share`)

### Issue: Connection test fails with "Access denied"
**Solution**: 
- Verify username/password are correct
- Ensure domain name is correct (if using domain account)
- Check network connectivity to server
- Verify user account has appropriate share permissions

### Issue: Credentials saved but Organizer.py still can't access share
**Solution**:
- Restart Organizer.py service to load new credentials
- Check service logs: `C:\Scripts\service-logs\organizer_stderr.log`
- Verify credentials stored in `organizer_config.json`

### Issue: LDAP connection fails
**Solution**:
- Verify LDAP server hostname is correct
- Ensure LDAP server port (default 389) is accessible
- Check username format (may need `user@domain.com` or `domain\user`)

## Future Enhancements

1. **Credential Encryption**: Add AES encryption for stored passwords
2. **Credential Rotation**: Automatically rotate credentials on schedule
3. **Multi-Account Support**: Allow multiple credentials per UNC path
4. **Credential Audit Log**: Track credential usage and modifications
5. **OAuth2 Support**: Add OAuth2 authentication option for cloud shares
6. **Credential Validation**: Schedule periodic credential testing
7. **Share Browser**: UI to browse available network shares

## API Reference

### Authorization
All endpoints require valid Dashboard authentication (Basic Auth or Session)

### Error Status Codes
- `400`: Bad request (invalid input)
- `401`: Unauthorized (not logged in)
- `403`: Forbidden (no permission)
- `500`: Server error

### Response Format
```json
{
  "success": true/false,
  "message": "Human readable message",
  "data": { }  // Endpoint-specific data
}
```

## Files Modified/Created

### Created
- `OrganizerDashboard/routes/unc_credentials.py` (168 lines)

### Modified
- `OrganizerDashboard.py` - Added UNC credentials blueprint import and registration
- `dash/modules/settings.html` - Added UNC credentials button and modal
- `dash/dashboard_scripts.html` - Added UNC credential management functions and auto-detection

## Related Documentation

- [UNC Path Support](CONFIGURATION.md#unc-paths)
- [Authentication System](AUTHENTICATION.md)
- [Organizer.py Configuration](CONFIGURATION.md)
- [Network Credentials Setup](README.md#network-credentials)
