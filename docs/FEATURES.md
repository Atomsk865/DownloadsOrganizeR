# Features

DownloadsOrganizeR organizes your Downloads and provides a dashboard for visibility and control. Below are the core features with intended purposes and useful scenarios.

## Real-time Organization
- **Purpose:** Automatically keeps Downloads tidy without manual effort.
- **How:** Uses Watchdog to observe file system events.
- **Scenarios:** Frequent downloads from browsers, messaging apps, or email attachments.

## Category Routing by Extension
- **Purpose:** Maps file extensions to categories (Images, Videos, Documents, Archives, Audio, Installers, Code, Data, Apps, Other).
- **How:** Matches extension to target folder inside Downloads.
- **Scenarios:** Teams receiving mixed file types; users wanting predictable storage.

## Unique Path Handling
- **Purpose:** Avoid overwriting existing files.
- **How:** Appends `(1)`, `(2)`, etc., to duplicates: `name (1).ext`.
- **Scenarios:** Re-downloading the same file or batch downloads.

## Incomplete Download Ignoring
- **Purpose:** Prevents moving partial/incomplete files.
- **How:** Skips `.crdownload`, `.part`, `.tmp`.
- **Scenarios:** Browser downloads still in progress.

## Dashboard Modules
- **Recent Files:** View and manage recently organized files; quick actions to open/reveal.
- **Duplicates:** Identify duplicate files by hash; manage cleanup.
- **File Categories:** Edit extension routes and categories.
- **Resource Monitor:** CPU, memory, top processes.
- **System Info:** OS, hardware overview.
- **Statistics:** Organization metrics and summaries.
- **Settings:** General configuration and thresholds.
- **Admin Tools:** Log management, service-related actions.
- **Reports & Analytics:** Filter by date/category; storage usage; export insights.
- **User Links:** Create categorized quick-access links.

## Health Monitoring
- **Purpose:** Detect when organizer exceeds CPU/memory thresholds.
- **How:** Configurable `memory_threshold_mb` and `cpu_threshold_percent`.
- **Scenarios:** Keeping the service efficient on older machines.

## Logging
- **Purpose:** Trace file movements and service behavior.
- **How:** Organizer logs to Downloads; service logs in `C:\Scripts\service-logs`.
- **Scenarios:** Troubleshooting missed moves or permission issues.

