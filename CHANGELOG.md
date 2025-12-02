# DownloadsOrganizeR Changelog

All notable changes to this project will be documented in this file.

## [v1.1.0] - December 2, 2025

### 🎉 Major Features Added

#### Duplicate File Detection

- **SHA256 hash calculation** for all organized files
- **Hash database** stored in `file_hashes.json` with automatic cleanup
- **Duplicate detection** checks new files against existing hashes before organizing
- **Duplicate logging** warns when duplicates are found with full path details
- **Dashboard module** displays all duplicate file groups with metadata
- **Grouped display** shows files by hash with count and total size
- **Action buttons**: Keep Newest, Keep Largest, Delete All per group
- **Individual file actions** with single-file delete button
- **Batch selection** with checkboxes to delete multiple files at once
- **File metadata** includes name, size (human-readable), modified time, full path
- **Wasted space calculation** shows total storage used by duplicates
- **Notification alerts** sent when duplicates are detected during organization
- **API endpoints**: `/api/duplicates` (GET) and `/api/duplicates/resolve` (POST)
- **Auto-refresh** after deletion with updated duplicate count
- **Database cleanup** removes entries for deleted or non-existent files

#### Export/Import Configuration System

- **Export endpoint** (`/api/config/export`) downloads complete configuration backup
- **Import endpoint** (`/api/config/import`) restores configuration from JSON file
- **Validation endpoint** (`/api/config/validate`) pre-validates import files
- **Timestamped filenames** (e.g., `organizer_backup_20251202_184106.json`)
- **Version metadata** included in export (export_version, export_timestamp, application)
- **Selective import** options for organizer and/or dashboard configs
- **Admin user preservation** during import to prevent lockout
- **UI controls** in config page with Export/Import buttons
- **File picker** with `.json` filter and hidden input element
- **Validation feedback** shows errors and warnings before import
- **Confirmation dialog** displays export timestamp and version
- **Auto-reload** after successful import to apply changes
- **Error handling** with user-friendly notifications
- **Complete backup** includes routes, roles, users, network targets, credentials, SMTP, all settings

#### Config Page Search & Filter

- **Real-time search** across all config module tables
- **Users table filter** by username or role (case-insensitive)
- **Roles table filter** by role name or rights
- **Network Targets filter** by name, path, or credential
- **Log search** with line highlighting and dimming
- **Visual feedback** for no results ("No users found" messages)
- **Clear buttons** with instant reset functionality
- **Smooth performance** with optimized DOM manipulation
- **Preserved during updates** - search state maintained during log streaming

#### Notification Center with History

- **Bell icon** with unread badge counter in top-right corner
- **Dropdown panel** showing last 50 notifications with slide-down animation
- **Mark as read/unread** functionality for individual notifications
- **Mark all as read** and **clear all** batch operations
- **Delete individual notifications** with hover X button
- **Persistent storage** in `notification_history.json`
- **Auto-cleanup** of notifications older than 7 days
- **Auto-save** all toast notifications to history automatically
- **Auto-refresh** every 30 seconds
- **Smart time formatting** ("2m ago", "5h ago", "3d ago")
- **Type-based icons** for success, warning, danger, and info alerts

#### File Organization Statistics Dashboard

- **Overview cards** showing total files, today, week, month, categories, and avg/day
- **Doughnut chart** for files by category breakdown
- **Bar chart** for top 10 file extensions
- **Line chart** for 30-day activity timeline with trend visualization
- **Bar chart** for hourly activity heatmap
- **Full API** with 6 endpoints for statistics data retrieval
- **Real-time updates** with Chart.js visualizations
- **Dark mode support** for all charts and stat cards

#### Keyboard Shortcuts & Command Palette

- **Ctrl+K** - Open command palette with fuzzy search
- **Ctrl+D** - Toggle dark mode instantly
- **Ctrl+R** - Refresh dashboard data
- **Ctrl+N** - Open notification center
- **Esc** - Close modals, dropdowns, and command palette
- **?** - Show keyboard shortcuts help overlay
- **First-time user tutorial** with feature highlights
- **Searchable command palette** for all dashboard actions

#### About & Documentation

- **About modal** with project overview and credits
- **Version information** (v1.1.0)
- **Licensing details** (MIT License)
- **Creator credits**: Richard Dennett
- **GitHub repository** links
- **Commission information** for custom development
- **Feature capability overview**
- **Setup documentation** and initial configuration guide
- **Accessible via Ctrl+H** or Help menu

### 🎨 UI/UX Enhancements

#### Mobile/Tablet Responsive Design

- **44px minimum touch targets** for all interactive elements
- **Responsive breakpoints** at 320px, 480px, 768px, and 1024px viewports
- **Collapsible card headers** on mobile with chevron indicators
- **Horizontal table scrolling** with smooth momentum on touch devices
- **Vertical button stacking** for improved mobile navigation
- **Larger form controls** (1rem font-size, increased padding)
- **Full-width modals** on small screens for better usability
- **Optimized spacing** with reduced gaps and margins on mobile
- **JavaScript touch handlers** for tap-to-collapse functionality
- **Automatic layout adjustment** on window resize
- **Enhanced notification bell** (54px on mobile)
- **Better table readability** with adjusted font sizes

#### Dark Mode Implementation

- **Sun/moon toggle** with smooth transitions
- **Persistent theme** saved to localStorage
- **Complete coverage** across all components, cards, forms, and charts
- **CSS variables** for easy theme customization
- **Beautiful animations** on theme switch

#### Layout Improvements

- **Fixed notification container** in top-right (no more page jumping)
- **Slide-in animations** for toast notifications
- **Centered content** with max-width 1600px for intentional design
- **Drag-and-drop** for all dashboard and config modules
- **Hide/show modules** with visual indicators

### 🔧 Configuration & Customization

#### Custom Branding System

- **Custom title** for dashboard
- **Logo upload** capability
- **Primary color** customization
- **Custom CSS** injection for advanced styling
- **Branding API** endpoints (GET/POST)

#### Config Page Restructure

- **Removed layout editor** in favor of drag-and-drop
- **Moved logs** from main dashboard to config page
- **Unified UX** with same drag-drop as main dashboard
- **Flexbox modules** for fluid, responsive layout

### 🐛 Bug Fixes

- Fixed GPU detection and reporting
- Fixed public IP detection with IPChicken iframe embed
- Improved drag-and-drop visual feedback
- Enhanced mobile responsiveness

### 📚 Documentation

- Created comprehensive **ROADMAP.md** with development priorities
- Added **CHANGELOG.md** (this file)
- Enhanced inline code comments
- Improved API documentation

---

## [v1.0-beta] - November 2025

### Initial Release

#### Core Features

- **File organization service** watching Downloads folder
- **Automatic categorization** by file type (9 categories + Other)
- **Windows service** installation with NSSM
- **Web dashboard** with Flask
- **Basic authentication** with username/password
- **Service controls** (start, stop, restart)
- **System monitoring** (CPU, RAM, processes)
- **File movement tracking** with JSON logging
- **Recent files** display

#### Dashboard Modules

- System information display
- Service status and resource usage
- Task manager (top 5 processes)
- Recent file movements
- Hardware metrics
- Network information
- Disk drives overview

#### Authentication System

- Basic HTTP authentication
- Role-based access control (admin, editor, viewer)
- LDAP integration support
- Windows authentication option
- Password change functionality
- Session management

#### Configuration

- User and role management
- File route configuration by extension
- Custom destination folders
- Tag-based routing
- SMTP credentials for email alerts
- Network targets configuration

---

## Roadmap

### Coming Soon (High Priority)

- 🔍 **Search/Filter in Config Modules** - Quick search across users, routes, settings
- 📱 **Mobile/Tablet Optimization** - Enhanced touch support and responsive design
- 📊 **Export/Import Configuration** - Backup and restore dashboard settings

### Future Enhancements

- Duplicate file detection
- Watch multiple folders
- File preview functionality
- Smart categorization with ML
- Cloud storage integration (Google Drive, Dropbox, OneDrive)
- Scheduled organization rules
- Email notifications
- Webhook support
- Progressive Web App (PWA)
- Docker container support

---

## Credits

**DownloadsOrganizeR** is designed, developed, and maintained by **Richard Dennett**.

For custom development, feature requests, or commissioning work, please visit:

- GitHub: [https://github.com/Atomsk865](https://github.com/Atomsk865)
- Repository: [https://github.com/Atomsk865/DownloadsOrganizeR](https://github.com/Atomsk865/DownloadsOrganizeR)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
