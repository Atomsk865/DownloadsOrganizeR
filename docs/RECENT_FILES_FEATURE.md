# Recent Files Feature Documentation

## Overview

The Recent Files feature allows users to view, track, and interact with files that have been automatically organized by the DownloadsOrganizer service. Users can click on files from the web dashboard to open them or reveal them in their file explorer.

## How It Works

### 1. File Movement Tracking

When a file is moved by `Organizer.py`, the following information is logged to `file_moves.json`:

```json
{
  "timestamp": "2025-12-01T10:30:45.123456",
  "original_path": "C:\\Users\\Username\\Downloads\\document.pdf",
  "destination_path": "C:\\Users\\Username\\Downloads\\Documents\\document.pdf",
  "category": "Documents",
  "filename": "document.pdf"
}
```

**Key Details:**
- Maintains up to **100 most recent file movements**
- Stored in `C:\Scripts\file_moves.json` (configurable via `organizer_config.json`)
- Ordered chronologically with newest files first
- Automatically created/updated on every file move

### 2. Dashboard Display

The dashboard displays the 20 most recent file movements in a dedicated "Recent File Movements" card with:

- **Timestamp**: When the file was moved
- **Filename**: Name and full destination path
- **Category**: Color-coded badge (Images, Documents, Videos, etc.)
- **Action buttons**:
  - **Open**: Launches file in default application
  - **Show**: Opens file explorer and selects the file

### 3. File Interaction

#### Open File
- **Windows**: Uses `os.startfile()` to open with default application
- **macOS**: Uses `open` command
- **Linux**: Uses `xdg-open` command

#### Show in Folder
- **Windows**: Uses `explorer /select,` to highlight file
- **macOS**: Uses `open -R` to reveal in Finder
- **Linux**: Opens parent directory in file manager

## Configuration

### organizer_config.json

Add or modify these settings:

```json
{
  "file_moves_json": "C:\\Scripts\\file_moves.json",
  "routes": {
    // ... your file category mappings
  }
}
```

**Configuration Options:**
- `file_moves_json`: Path where file movement history is stored (default: `C:\Scripts\file_moves.json`)

## API Endpoints

### GET /api/recent_files

Returns the most recent file movements (up to 20).

**Authentication**: Requires HTTP Basic Auth

**Response Example:**
```json
[
  {
    "timestamp": "2025-12-01T10:30:45.123456",
    "original_path": "C:\\Users\\Username\\Downloads\\photo.jpg",
    "destination_path": "C:\\Users\\Username\\Downloads\\Images\\photo.jpg",
    "category": "Images",
    "filename": "photo.jpg"
  }
]
```

### POST /api/open_file

Opens or reveals a file in the file system.

**Authentication**: Requires HTTP Basic Auth

**Request Body:**
```json
{
  "file_path": "C:\\Users\\Username\\Downloads\\Images\\photo.jpg",
  "action": "open"  // "open" or "reveal"
}
```

**Response:**
```json
{
  "success": true,
  "message": "File opened"
}
```

**Error Responses:**
- `400`: Missing file path
- `404`: File not found
- `500`: Error opening file

## User Interface

### Recent File Movements Card

Located between the Settings and File Categories sections, it includes:

1. **Header with Refresh Button**: Manually refresh the file list
2. **Table Display**:
   - Time column showing local timestamp
   - Filename with full path in muted text
   - Category badge with color coding
   - Action buttons for file interaction

3. **Auto-Refresh**: List automatically updates every 30 seconds

### Category Badge Colors

- **Images**: Green (success)
- **Videos**: Blue (primary)
- **Music**: Light blue (info)
- **Documents**: Yellow (warning)
- **Archives**: Gray (secondary)
- **Executables**: Red (danger)
- **Scripts**: Dark gray (dark)
- **Fonts**: Light gray (light)
- **Shortcuts**: Light blue (info)
- **Logs**: Gray (secondary)
- **Other**: Gray (secondary)

## Security Considerations

1. **Authentication Required**: All API endpoints require HTTP Basic Auth
2. **Path Validation**: Checks file existence before attempting to open
3. **Error Handling**: Graceful fallbacks for missing files or permissions issues
4. **File Limit**: Only stores 100 most recent files to prevent unbounded growth

## Troubleshooting

### Files Don't Appear in Dashboard

1. **Check file_moves.json exists**: Should be at `C:\Scripts\file_moves.json`
2. **Verify service is running**: Files only logged when service processes them
3. **Check permissions**: Ensure service can write to `C:\Scripts\`
4. **Review logs**: Check `organizer.log` for errors

### Can't Open Files

1. **File not found**: File may have been moved/deleted after being logged
2. **Permission issues**: Ensure user has permissions to access the file
3. **No default application**: File type may not have a default program associated
4. **Cross-platform issues**: Ensure appropriate file manager commands are available

### API Returns 401 Unauthorized

1. **Check credentials**: Verify `DASHBOARD_USER` and `DASHBOARD_PASS` environment variables
2. **Clear browser cache**: Old auth tokens may be cached
3. **Check config**: Verify `dashboard_user` and `dashboard_pass_hash` in `organizer_config.json`

## Development Notes

### Modified Files

1. **Organizer.py**:
   - Added `FILE_MOVES_JSON` configuration
   - Added `log_file_move()` function
   - Modified `organize_file()` to call `log_file_move()`

2. **OrganizerDashboard.py**:
   - Added `/api/recent_files` endpoint
   - Added `/api/open_file` endpoint
   - Added Recent Files UI card
   - Added JavaScript functions: `refreshRecentFiles()`, `displayRecentFiles()`, `openFile()`
   - Added Bootstrap Icons CDN link

3. **organizer_config.json**:
   - Added `file_moves_json` configuration option

### Testing

To test the feature locally:

1. Start the organizer service:
   ```bash
   python Organizer.py
   ```

2. Start the dashboard:
   ```bash
   python OrganizerDashboard.py
   ```

3. Copy a test file to your Downloads folder

4. Open `http://localhost:5000` and view Recent File Movements

5. Click "Open" or "Show" buttons to test file interaction

## Future Enhancements

Potential improvements for this feature:

1. **Search/Filter**: Add ability to search/filter recent files
2. **Date Range**: Filter files by date range
3. **Category Filter**: Show only files from specific categories
4. **Bulk Actions**: Select multiple files for batch operations
5. **File Preview**: Show thumbnails for images/documents
6. **Export History**: Download file movement history as CSV
7. **Undo Move**: Option to move file back to original location
8. **Statistics**: Show charts of file movements by category over time
