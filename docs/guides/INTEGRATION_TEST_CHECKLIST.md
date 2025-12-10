# Dashboard-Organizer Integration Test Checklist

## Quick Test Procedures

### Test 1: Enable Organizer Service
**Duration:** 2 minutes

```
Steps:
1. Open dashboard at http://localhost:5000
2. Navigate to Configuration page
3. Locate "Organizer Status & Control" module
4. Verify initial status shows "DISABLED" (yellow badge)
5. Click "Enable Organizer" button
6. Click "OK" in confirmation dialog
7. Verify success notification appears
8. Verify badge changes to "ENABLED" (green)
9. Note warning about service restart

Expected Results:
✅ Badge changes from yellow to green
✅ Enable button disappears, Disable button appears
✅ Success notification displayed
✅ organizer_config.json updated with "organizer_enabled": true
```

### Test 2: Disable Organizer Service
**Duration:** 2 minutes

```
Steps:
1. With organizer enabled from Test 1
2. Click "Disable Organizer" button
3. Click "OK" in confirmation dialog
4. Verify success notification appears
5. Verify badge changes to "DISABLED" (yellow)

Expected Results:
✅ Badge changes from green to yellow
✅ Disable button disappears, Enable button appears
✅ Success notification displayed
✅ organizer_config.json updated with "organizer_enabled": false
```

### Test 3: Change to Custom Destination Mode
**Duration:** 3 minutes

```
Steps:
1. In Organizer Status & Control module
2. Locate destination mode dropdown
3. Select "Custom Base Destination"
4. Verify custom path input field appears
5. Enter a test path: C:\CustomOrganized
6. Click "Save Configuration"
7. Verify success notification appears
8. Click "Refresh" button
9. Verify dropdown shows "Custom Base Destination"
10. Verify custom path shows C:\CustomOrganized

Expected Results:
✅ Custom path input appears when mode changed
✅ Configuration saves successfully
✅ organizer_config.json updated with:
   - "destination_mode": "custom"
   - "base_destination": "C:\\CustomOrganized"
✅ UI persists values after refresh
```

### Test 4: Switch Back to Subfolder Mode
**Duration:** 2 minutes

```
Steps:
1. With custom mode active from Test 3
2. Change dropdown to "Subfolder Mode (Default)"
3. Verify custom path input disappears
4. Click "Save Configuration"
5. Verify success notification appears
6. Click "Refresh" button
7. Verify dropdown shows "Subfolder Mode (Default)"

Expected Results:
✅ Custom path input hidden
✅ Configuration saves successfully
✅ organizer_config.json updated with "destination_mode": "subfolder"
✅ UI persists value after refresh
```

### Test 5: Status Refresh
**Duration:** 1 minute

```
Steps:
1. Open dashboard config page
2. Note current organizer status
3. Click "Refresh" button
4. Verify status updates immediately
5. Verify watch folders list displays
6. Verify no errors in browser console

Expected Results:
✅ Status loads without errors
✅ Badge displays correct state
✅ Watch folders list shows configured paths
✅ No JavaScript errors in console
```

### Test 6: Page Load Status Display
**Duration:** 1 minute

```
Steps:
1. Close dashboard
2. Reopen dashboard at http://localhost:5000
3. Navigate to Configuration page
4. Observe "Organizer Status & Control" module
5. Wait 2 seconds for initial load

Expected Results:
✅ Status loads automatically on page load
✅ Badge shows correct initial state
✅ Watch folders populate automatically
✅ Destination mode shows current setting
```

### Test 7: Validation - Custom Mode Without Path
**Duration:** 1 minute

```
Steps:
1. Select "Custom Base Destination" mode
2. Leave custom path input empty
3. Click "Save Configuration"
4. Observe validation message

Expected Results:
✅ Warning notification displayed
✅ Message: "Please specify a base destination path for custom mode"
✅ Configuration not saved
✅ UI remains in current state
```

### Test 8: API Direct Test
**Duration:** 2 minutes

```
Prerequisites: Have curl or Postman installed

Test GET Status:
curl -X GET http://localhost:5000/api/organizer/status \
  -H "Authorization: Basic <base64_credentials>" \
  -H "Content-Type: application/json"

Expected Response:
{
  "success": true,
  "organizer_enabled": false,
  "destination_mode": "subfolder",
  "base_destination": "",
  "watch_folders": ["/path/to/downloads"],
  "setup_completed": true
}

Test POST Enable:
curl -X POST http://localhost:5000/api/organizer/enable \
  -H "Authorization: Basic <base64_credentials>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

Expected Response:
{
  "success": true,
  "message": "Organizer enabled successfully",
  "organizer_enabled": true
}
```

### Test 9: End-to-End File Organization
**Duration:** 5 minutes

```
Prerequisites: Service must be restarted after enabling

Steps:
1. Enable organizer via dashboard
2. Set destination mode to "subfolder"
3. Save configuration
4. Restart Windows service:
   Restart-Service DownloadsOrganizer
5. Copy test file to Downloads:
   Copy-Item test_image.jpg C:\Users\{username}\Downloads\
6. Wait 2-3 seconds
7. Verify file moved to:
   C:\Users\{username}\Downloads\Images\test_image.jpg

Expected Results:
✅ File detected by organizer
✅ File moved to correct subfolder
✅ Original file removed from Downloads root
✅ Check organizer.log for "Moved" entry
```

### Test 10: Custom Destination Organization
**Duration:** 5 minutes

```
Prerequisites: Service must be restarted after config change

Steps:
1. Enable organizer via dashboard
2. Set destination mode to "custom"
3. Set base destination to: C:\CustomOrganized
4. Save configuration
5. Create C:\CustomOrganized folder manually
6. Restart Windows service:
   Restart-Service DownloadsOrganizer
7. Copy test file to Downloads:
   Copy-Item test_video.mp4 C:\Users\{username}\Downloads\
8. Wait 2-3 seconds
9. Verify file moved to:
   C:\CustomOrganized\Videos\test_video.mp4

Expected Results:
✅ File detected by organizer
✅ File moved to custom base path + category subfolder
✅ Original file removed from Downloads root
✅ Check organizer.log for "Moved" entry
```

## Error Handling Tests

### Test 11: Network Disconnected
**Duration:** 2 minutes

```
Steps:
1. Open browser developer tools (F12)
2. Go to Network tab
3. Set throttling to "Offline"
4. Click "Refresh" button in organizer module
5. Observe error notification
6. Re-enable network
7. Click "Refresh" again

Expected Results:
✅ Error notification displayed when offline
✅ Message: "Error refreshing organizer status: ..."
✅ UI gracefully handles failure
✅ Success when network restored
```

### Test 12: Invalid Custom Path
**Duration:** 2 minutes

```
Steps:
1. Select "Custom Base Destination" mode
2. Enter invalid path: "<invalid>path"
3. Click "Save Configuration"
4. Observe validation/error response

Expected Results:
✅ Backend validation catches invalid path
✅ Error notification displayed
✅ Configuration not saved
✅ organizer_config.json unchanged
```

### Test 13: Authentication Failure
**Duration:** 2 minutes

```
Steps:
1. Open browser developer tools (F12)
2. Go to Application > Cookies
3. Clear authentication cookies
4. Click "Refresh" button in organizer module
5. Observe behavior

Expected Results:
✅ Redirected to login page OR
✅ 401 Unauthorized error handled gracefully
✅ User prompted to re-authenticate
```

## Configuration File Verification

### Test 14: Manual Config Check
**Duration:** 2 minutes

```
Steps:
1. Open organizer_config.json in text editor
2. Note current values
3. Change settings via dashboard
4. Save configuration
5. Reload organizer_config.json in editor
6. Verify changes persisted

Expected Fields:
{
  "organizer_enabled": <should match dashboard>,
  "destination_mode": <should match dropdown>,
  "base_destination": <should match input if custom>,
  "watch_folders": [...],
  "routes": {...}
}
```

## Browser Console Tests

### Test 15: JavaScript Errors
**Duration:** Continuous during all tests

```
Monitor:
1. Open browser developer tools (F12)
2. Go to Console tab
3. Perform all UI actions
4. Watch for JavaScript errors

Expected Results:
✅ No uncaught exceptions
✅ No undefined variable errors
✅ No 404 errors for assets
✅ API calls return 200 or expected error codes
```

## Performance Tests

### Test 16: Status Refresh Speed
**Duration:** 1 minute

```
Steps:
1. Open browser developer tools (F12)
2. Go to Network tab
3. Click "Refresh" button
4. Measure time to complete

Expected Results:
✅ API call completes in <500ms
✅ UI updates within 1 second
✅ No blocking operations
```

## Summary Report Template

```
Test Date: ____________
Tester: ____________
Dashboard Version: ____________

[ ] Test 1: Enable Organizer Service - PASS / FAIL
[ ] Test 2: Disable Organizer Service - PASS / FAIL
[ ] Test 3: Change to Custom Destination - PASS / FAIL
[ ] Test 4: Switch to Subfolder Mode - PASS / FAIL
[ ] Test 5: Status Refresh - PASS / FAIL
[ ] Test 6: Page Load Status Display - PASS / FAIL
[ ] Test 7: Validation - Custom Mode - PASS / FAIL
[ ] Test 8: API Direct Test - PASS / FAIL
[ ] Test 9: End-to-End Subfolder Organization - PASS / FAIL
[ ] Test 10: Custom Destination Organization - PASS / FAIL
[ ] Test 11: Network Disconnected - PASS / FAIL
[ ] Test 12: Invalid Custom Path - PASS / FAIL
[ ] Test 13: Authentication Failure - PASS / FAIL
[ ] Test 14: Manual Config Check - PASS / FAIL
[ ] Test 15: JavaScript Errors - PASS / FAIL
[ ] Test 16: Status Refresh Speed - PASS / FAIL

Overall Status: ____________
Issues Found: ____________
Notes: ____________
```

## Quick Smoke Test (5 minutes)

For rapid verification, run these minimal tests:

```
1. Load config page → Status displays correctly
2. Click Enable → Badge turns green
3. Click Disable → Badge turns yellow
4. Select Custom mode → Input appears
5. Save config → Success notification
6. Click Refresh → Status reloads correctly

If all pass: Integration likely working ✅
If any fail: Run full test suite
```

## Debugging Tips

**If status doesn't load:**
- Check browser console for JavaScript errors
- Verify `/api/organizer/status` endpoint returns 200
- Confirm `getAuthHeaders()` function exists in dashboard_scripts.html

**If enable/disable doesn't work:**
- Verify organizer_config.json is writable
- Check Flask logs for API errors
- Confirm authentication headers are valid

**If file organization fails:**
- Verify service is actually restarted after config changes
- Check Organizer.py logs at `C:\Users\{username}\Downloads\organizer.log`
- Confirm watch folder path is correct
- Test with simple file first (test.txt)

**If custom path doesn't work:**
- Verify destination folder exists and is writable
- Check path format (Windows: C:\Path\, Linux: /path/)
- Confirm no special characters in path
- Test with absolute path, not relative

---

**Document Version:** 1.0  
**Integration Status:** Ready for Testing  
**Estimated Test Time:** 30-45 minutes (full suite)
