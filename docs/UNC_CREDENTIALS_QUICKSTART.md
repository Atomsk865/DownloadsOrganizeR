# UNC Credentials Feature - Quick Start Guide

## What's New

The Dashboard Settings module now includes built-in UNC (network share) credential management! This allows you to:

- Configure and test network share authentication
- Automatically organize files from network drives
- Store credentials securely in the config

## How It Works

### Step 1: Enable Network Share Monitoring

1. Open **Settings** module in the Dashboard
2. Enter a UNC path in the "Watch Folder" field:
   ```
   \\server\share
   ```
3. A blue info message appears: "This is a UNC path. Click UNC Creds to configure authentication."

### Step 2: Configure Credentials

1. Click the **UNC Creds** button
2. Modal dialog opens with credential form
3. Choose authentication type:
   - **Windows Auth** (Default) - For Active Directory / Windows domains
   - **LDAP** - For LDAP directories

### Step 3: Enter Credentials

**For Windows Auth:**
- Username: `domain\username` or just `username`
- Password: Your Windows password
- Domain: (Optional) `DOMAIN` or `DOMAIN.COM`
- Hostname: (Optional) Server name for Windows auth

**For LDAP:**
- Username: `username@ldap.domain.com` or `uid=username,...`
- Password: Your LDAP password
- Hostname: LDAP server address

### Step 4: Test Connection

Click **Test Connection** button to verify credentials work:
- ✅ "Connection successful!" - Credentials are valid
- ❌ "Connection failed" - Check username/password/permissions

### Step 5: Save & Apply

1. Click **Save Credentials** button
2. Return to Settings and click **Save Settings**
3. When prompted, click **Yes** to restart the Organizer service
4. Service will now organize files from the network share

## Example Scenarios

### Scenario 1: Windows Domain Network Share

```
Settings:
  Watch Folder: \\fileserver01\Downloads
  
Credentials Modal:
  Auth Type: Windows Auth
  Username: john.doe
  Password: MyPassword123
  Domain: MYCOMPANY
  Hostname: fileserver01
  
Result: Files from \\fileserver01\Downloads are organized automatically
```

### Scenario 2: LDAP-Based File Server

```
Settings:
  Watch Folder: \\ldap-fs01\shared-downloads
  
Credentials Modal:
  Auth Type: LDAP
  Username: john.doe@company.ldap
  Password: LdapPassword456
  Hostname: ldap-fs01.company.com
  
Result: Files from \\ldap-fs01\shared-downloads are organized automatically
```

### Scenario 3: Network NAS Device

```
Settings:
  Watch Folder: \\nas.local\media\downloads
  
Credentials Modal:
  Auth Type: Windows Auth
  Username: nas_user
  Password: NasPassword789
  Hostname: nas.local
  
Result: Files from \\nas.local\media\downloads are organized automatically
```

## Auto-Detection Features

### UNC Path Recognition
- Automatically detects UNC paths (those starting with `\\`)
- Shows "UNC Creds" button when UNC path is entered
- Hides button when local path is used

### Credential Pre-Loading
- When editing existing UNC path, credentials auto-load (except password for security)
- Allows quick credential updates without re-entering everything

## Error Messages & Solutions

| Error | Solution |
|-------|----------|
| "Invalid UNC path format" | Ensure path starts with `\\` and format is `\\server\share` |
| "Connection failed: Access denied" | Check username/password, verify user has share permissions |
| "Connection failed: The network path was not found" | Verify server name/IP is correct, check network connectivity |
| "Connection failed: No such host" | LDAP hostname is incorrect or server is unreachable |
| "Username and password are required" | Both fields must be filled before testing/saving |

## Security Notes

⚠️ **Important Security Information:**

- Passwords are stored encrypted in the config file
- Never share your `organizer_config.json` file if it contains credentials
- The Dashboard password field is never pre-filled when editing
- All credential transmission uses HTTPS (when using SSL)
- Consider using service accounts with minimal permissions

## Backend Storage

Credentials are stored in `organizer_config.json`:

```json
{
  "unc_credentials": {
    "\\\\fileserver01\\Downloads": {
      "username": "john.doe",
      "domain": "MYCOMPANY",
      "hostname": "fileserver01",
      "auth_type": "windows"
    }
  }
}
```

**Note:** Passwords are encrypted before storage and never exposed in the config file.

## Troubleshooting

### Q: The UNC Creds button doesn't appear
**A:** Ensure your path starts with `\\` (e.g., `\\server\share`, not `\server\share`)

### Q: Connection test succeeds but files aren't being organized
**A:** 
1. Restart the Organizer service
2. Check the service logs for errors
3. Verify the service account has access to the network share

### Q: How do I change credentials later?
**A:** 
1. Click "UNC Creds" button again
2. Credentials will auto-load (password field empty for security)
3. Update fields as needed
4. Click "Test Connection" to verify
5. Click "Save Credentials" to update

### Q: Can I use multiple network shares?
**A:** Yes! Each UNC path can have its own credentials. Simply add another watch folder with different UNC path when needed (requires service configuration to monitor multiple paths).

## Integration with Organizer Service

### Service Startup
1. Organizer.py reads watch folders from config
2. For each UNC path, it loads stored credentials
3. Uses credentials to access network share
4. Begins organizing files found in the share

### File Organization
- Files are sorted by type (Images, Videos, Documents, etc.)
- Same organization logic as local Downloads folder
- Files moved to `\\server\share\{Category}\` folders

### Error Handling
- If network unavailable, service queues files for later
- If credentials invalid, service logs error and retries
- Service continues monitoring local folders if network fails

## API Endpoints (For Developers)

### Validate UNC Syntax
```
POST /api/unc/validate-syntax
{
  "unc_path": "\\\\server\\share"
}
```

### Test Credentials
```
POST /api/unc/test-credentials
{
  "unc_path": "\\\\server\\share",
  "username": "user",
  "password": "pass",
  "domain": "DOMAIN",
  "hostname": "server",
  "auth_type": "windows"
}
```

### Save Credentials
```
POST /api/unc/save-credentials
{
  "unc_path": "\\\\server\\share",
  "username": "user",
  "password": "pass",
  "auth_type": "windows"
}
```

### Get Saved Credentials
```
GET /api/unc/get-credentials/\\server\share
```

## Next Steps

1. Configure your first UNC path in Settings
2. Click UNC Creds and enter your network credentials
3. Test the connection
4. Save and restart the service
5. Files from your network share will now be automatically organized!

## Support & Feedback

For issues or feature requests related to UNC credentials:
1. Check the troubleshooting section above
2. Review service logs in Dashboard > Logs
3. Verify configuration in Dashboard > File Categories

---

**Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production Ready
