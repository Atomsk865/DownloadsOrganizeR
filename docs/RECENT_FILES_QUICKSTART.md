# Recent Files Feature - Quick Start Guide

## What's New?

The DownloadsOrganizer dashboard now includes a **Recent File Movements** section that lets you:
- ✅ View the last 20 files that were automatically organized
- ✅ Click to **open files** directly from the browser
- ✅ Click to **show files in Explorer** (reveal/locate)
- ✅ See timestamps, categories, and file paths
- ✅ Auto-refreshes every 30 seconds

## Screenshot Preview

```
┌─────────────────────────────────────────────────────────────┐
│ Recent File Movements                        [Refresh]      │
├──────────────┬────────────────┬───────────┬─────────────────┤
│ Time         │ Filename       │ Category  │ Actions         │
├──────────────┼────────────────┼───────────┼─────────────────┤
│ 10:30:45 AM  │ photo.jpg      │ [Images]  │ [Open] [Show]  │
│              │ C:\...\photo   │           │                 │
├──────────────┼────────────────┼───────────┼─────────────────┤
│ 10:25:12 AM  │ document.pdf   │[Documents]│ [Open] [Show]  │
│              │ C:\...\doc.pdf │           │                 │
└──────────────┴────────────────┴───────────┴─────────────────┘
```

## How to Use

### Step 1: Files are Tracked Automatically
Every time `Organizer.py` moves a file, it logs:
- Original location
- New location
- Category (Images, Documents, etc.)
- Timestamp
- Filename

### Step 2: View in Dashboard
1. Open the dashboard: `http://localhost:5000`
2. Login with your credentials
3. Scroll to "Recent File Movements" card
4. See your last 20 organized files

### Step 3: Interact with Files
Click buttons next to any file:

**[Open]** - Opens the file in its default application
- PDFs → Adobe Reader
- Images → Photo Viewer
- Videos → Media Player
- etc.

**[Show]** - Opens Explorer and highlights the file
- Windows: `explorer /select,<file>`
- Useful for finding where the file went

### Step 4: Manual Refresh
Click the **[Refresh]** button in the card header to update the list immediately (otherwise it auto-updates every 30 seconds).

## Technical Details

### Files Modified
1. **Organizer.py** - Added file tracking to `log_file_move()`
2. **OrganizerDashboard.py** - Added UI card and API endpoints
3. **organizer_config.json** - Added `file_moves_json` path

### New Files Created
- **C:\Scripts\file_moves.json** - Stores movement history (max 100 entries)

### API Endpoints
- `GET /api/recent_files` - Returns recent file movements
- `POST /api/open_file` - Opens or reveals a file

## Configuration

In `organizer_config.json`:

```json
{
  "file_moves_json": "C:\\Scripts\\file_moves.json"
}
```

Change this path if you want to store the history elsewhere.

## Testing

### Quick Test
1. Start organizer: `python Organizer.py`
2. Start dashboard: `python OrganizerDashboard.py`
3. Drop a file in Downloads folder
4. Check dashboard at `http://localhost:5000`
5. Click [Open] or [Show] to test

### Run Test Script
```bash
python test_recent_files.py
```

This will:
- Check if `file_moves.json` exists
- Show the most recent file movement
- Optionally create a test file
- Provide API testing instructions

## Troubleshooting

**Q: No files showing up?**
- Ensure `Organizer.py` is running
- Check that `C:\Scripts\file_moves.json` exists
- Move a test file to Downloads to trigger logging

**Q: Can't open files?**
- File may have been deleted after being moved
- Check file permissions
- Ensure default application is configured for that file type

**Q: Getting 401 errors?**
- Verify you're logged into the dashboard
- Check your username/password credentials

## Future Ideas

Want more features? Consider:
- Search/filter by filename or category
- Date range filtering
- Undo move functionality
- File statistics/charts
- Export history to CSV

## Support

See `RECENT_FILES_FEATURE.md` for detailed technical documentation.
