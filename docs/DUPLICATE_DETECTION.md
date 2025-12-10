# Duplicate File Detection - Quick Reference

## Overview

The Duplicate File Detection feature automatically identifies files with identical content using SHA256 hash comparison. This helps users find and remove duplicate files to free up storage space.

## How It Works

### 1. Automatic Hash Calculation

- When a file is downloaded and organized, DownloadsOrganizeR calculates its SHA256 hash
- The hash is stored in `file_hashes.json` along with the file's path
- This happens transparently during normal file organization

### 2. Duplicate Detection
- Before moving a file, the system checks if its hash already exists
- If found, a warning is logged and a notification is sent
- The file is still organized normally - detection doesn't prevent organization

### 3. Dashboard Display
- Navigate to the main dashboard to see the "Duplicate Files" module
- Shows all detected duplicate groups with:
  - Number of duplicate files per group
  - Total size of duplicates
  - Wasted space calculation
  - Individual file metadata (name, size, modified time, path)

## Using the Dashboard

### Viewing Duplicates
1. Open dashboard at `http://localhost:5000`
2. Look for the "Duplicate Files" card (full-width module)
3. Badges show total duplicate groups and wasted space
4. Click "Refresh" button to reload duplicate data

### Managing Duplicates

#### Keep Newest
- Keeps the most recently modified file
- Deletes all older duplicates
- Useful for keeping the latest version

#### Keep Largest
- Keeps the file with the largest size
- Deletes all smaller duplicates
- Useful when file quality matters

#### Delete All
- Deletes ALL files in the duplicate group
- **WARNING**: Use with caution - cannot be undone
- Useful for removing unwanted files entirely

#### Individual Actions
- Each file has a trash icon for single deletion
- Use checkboxes to select specific files
- Combine selections across groups for batch operations

### API Endpoints

#### GET `/api/duplicates`
Returns all duplicate file groups:

```json
{
  "duplicates": [
    {
      "hash": "abc123...",
      "count": 3,
      "total_size": 1048576,
      "total_size_human": "1.0 MB",
      "files": [
        {
          "path": "C:/Users/.../file.jpg",
          "name": "file.jpg",
          "size": 349525,
          "size_human": "341.3 KB",
          "modified": "2025-12-02T10:30:00",
          "modified_human": "2025-12-02 10:30:00"
        }
      ]
    }
  ],
  "total_duplicates": 1,
  "total_duplicate_files": 3,
  "wasted_space": 699050,
  "wasted_space_human": "682.7 KB"
}
```

#### POST `/api/duplicates/resolve`

Delete specified files:

```json
{
  "action": "delete",
  "files": [
    "C:/path/to/file1.jpg",
    "C:/path/to/file2.jpg"
  ]
}
```

Response:

```json
{
  "success": true,
  "deleted": ["C:/path/to/file1.jpg"],
  "failed": [],
  "message": "Deleted 1 file(s)"
}
```

## Configuration

### Hash Database Location

Default: `./config/json/file_hashes.json`

Override in `organizer_config.json`:

```json
{
  "file_hashes_json": "C:/custom/path/file_hashes.json"
}
```

### Notification Settings

Notifications are sent when duplicates are detected. Default location: `notification_history.json`

Override in `organizer_config.json`:

```json
{
  "notification_history_json": "C:/custom/path/notification_history.json"
}
```

## File Structure

### file_hashes.json

```json
{
  "0123eb2da45b...": [
    "C:/Users/username/Downloads/Images/photo1.jpg",
    "C:/Users/username/Downloads/Images/photo1 (1).jpg"
  ],
  "eb976165ceb7...": [
    "C:/Users/username/Downloads/Documents/report.pdf",
    "C:/Users/username/Downloads/Backup/report.pdf"
  ]
}
```

## Implementation Details

### Modified Files

- **Organizer.py**: Added hash calculation, duplicate detection, notification sending
  - `calculate_file_hash()`: SHA256 hash calculation
  - `load_file_hashes()`: Load hash database
  - `save_file_hashes()`: Save hash database
  - `check_duplicate()`: Check if file is duplicate
  - `register_file_hash()`: Register file hash after organization
  - `send_notification()`: Send notification to dashboard
  - `format_file_size()`: Human-readable size formatting

- **OrganizerDashboard/routes/duplicates.py**: NEW - API endpoints
  - GET `/api/duplicates`: List all duplicates
  - POST `/api/duplicates/resolve`: Delete specified files

- **dash/dashboard.html**: Added duplicate files module
  - Full-width card with badges and action buttons
  - Table display with metadata and checkboxes
  - Grouped by hash with per-group actions

- **dash/dashboard_scripts.html**: JavaScript functions
  - `loadDuplicates()`: Fetch and render duplicates
  - `keepNewest()`: Keep most recent file
  - `keepLargest()`: Keep largest file
  - `deleteAllDuplicates()`: Delete all in group
  - `deleteSingleFile()`: Delete one file
  - `resolveDuplicates()`: API call to delete files

## Testing

Run the test suite:

```bash
python test_duplicate_detection.py
```

Tests verify:

- Hash calculation accuracy
- Database structure
- API endpoint responses
- Different content detection

## Troubleshooting

### Duplicates Not Showing

1. Check if `file_hashes.json` exists and has data
2. Verify dashboard is running: `ps aux | grep OrganizerDashboard`
3. Check browser console for JavaScript errors
4. Try manual refresh with the Refresh button

### API Errors

1. Verify authentication credentials
2. Check dashboard logs: `tail -f /tmp/dashboard_duplicates.log`
3. Test API directly: `curl -u admin:password http://localhost:5000/api/duplicates`

### Hash Database Issues

1. File is JSON format - verify with `type .\config\json\file_hashes.json | more` (Windows) or `cat ./config/json/file_hashes.json | head` (Linux/macOS)
2. Permissions - ensure writable by service user
3. Manual reset: Delete file and restart service (will rebuild on next file)

## Performance

### Hash Calculation

- Uses SHA256 algorithm (cryptographically secure)
- Reads files in 4KB chunks (memory efficient)
- Average speed: ~100MB/s on modern hardware
- Large files (>1GB) may take a few seconds

### Database Size

- Typical hash entry: ~100 bytes (hash + path)
- 10,000 files ≈ 1MB database size
- Automatic cleanup removes non-existent files

### Dashboard Loading

- Duplicate detection runs on-demand (not real-time)
- Click Refresh to update data
- Large duplicate sets (1000+ groups) may take 1-2 seconds to render

## Best Practices

1. **Regular Review**: Check duplicates weekly to catch recent downloads
2. **Sort by Wasted Space**: Focus on large duplicates first
3. **Preview Before Delete**: Verify file paths before bulk deletion
4. **Keep Backups**: Hash database is not a backup - maintain separate backups
5. **Monitor Notifications**: Act on duplicate alerts promptly

## Credits

Developed by **Richard Dennett** as part of DownloadsOrganizeR v1.1.0

Feature requested on: December 2, 2025
Implemented: December 2, 2025

## Related Documentation

- [CHANGELOG.md](CHANGELOG.md) - Version history
- [ROADMAP.md](ROADMAP.md) - Future enhancements
- [README.md](readme.md) - Project overview
