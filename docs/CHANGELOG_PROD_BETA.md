# Changelog - Prod-Beta Release

## Version 2.1.0 - Feature Enhancement & Bug Fixes (2025-12-02)

### 🎉 New Features

#### User Links Manager
- **Custom Quick-Access Links** - Create and organize personalized links for quick access
  - Categorized organization (Work, Personal, Tools, Reference, Other)
  - Add titles, URLs, and descriptions
  - Quick copy-to-clipboard functionality
  - Search and filter capabilities
  - Full CRUD operations via REST API
- **API Endpoints:**
  - `GET /api/user-links` - Retrieve all user links
  - `POST /api/user-links` - Create new link
  - `PUT /api/user-links/<id>` - Update existing link
  - `DELETE /api/user-links/<id>` - Delete link

#### Reports & Analytics Dashboard
- **Comprehensive File Organization Analytics** at `/reports`
  - File organization statistics with interactive filtering
  - Category-based analysis (Images, Videos, Documents, etc.)
  - File size distribution charts
  - Storage usage metrics
  - Organization pattern insights
- **Advanced Filtering:**
  - Date range selection (Today, Yesterday, Last 7/30 Days, Custom Range)
  - Category filtering with multi-select support
  - Real-time data updates
  - Export capabilities for external analysis
- **API Endpoints:**
  - `GET /api/reports/summary` - Overall statistics
  - `GET /api/reports/category-stats` - Per-category analysis
  - `GET /api/reports/file-sizes` - Size distribution data

#### Recent Files Enhancement
- **Enhanced File Operations** directly from dashboard:
  - Open file in default application
  - Reveal file in Windows Explorer/Finder
  - Remove entries from recent list
  - Real-time list refresh
- **Quick Actions:** One-click access to recent files
- **API Endpoints:**
  - `GET /api/recent_files` - Retrieve recent file movements
  - `DELETE /api/recent_files/<index>` - Remove from recent list
  - `POST /api/open_file` - Open or reveal file

### 🐛 Bug Fixes

#### Template Syntax Errors
- **Fixed Jinja2 template errors** in `dashboard.html`
  - Resolved `{% endfor %}` / `{% endblock %}` mismatch errors
  - Removed duplicate collapsible section structures
  - Cleaned up nested card body structures across all sections:
    - Service Status & Resource Usage
    - Task Manager
    - Drive Space
    - Settings
    - Recent File Movements
    - File Categories
    - Custom Routes
    - Logs
  - Simplified HTML hierarchy for better maintainability
- **Impact:** Dashboard now loads without template compilation errors

#### Config Page Button Functionality
- **Fixed non-functional buttons** in dashboard configuration page (`/config`)
  - Moved JavaScript functions from nested scope to global scope
  - Fixed functions:
    - `resetSetup()` - Re-run setup wizard
    - `installService()` - Install Windows service
    - `uninstallService()` - Remove Windows service
    - `reinstallService()` - Reinstall service with new settings
    - `factoryReset()` - Reset all configurations
    - `repairAuth()` - Align admin credentials
    - `viewAuthState()` - Display current auth state
  - Separated rights enforcement from function definitions
- **Root Cause:** Functions were defined inside `applyConfigRights()` making them inaccessible to onclick handlers
- **Impact:** All config page buttons now function correctly

### 🔒 Security Enhancements

#### CSRF Protection
- **Implemented CSRF token management** using flask-wtf
  - CSRF tokens for all POST/PUT/DELETE requests
  - Token refresh mechanism for AJAX calls
  - Automatic token injection for forms
  - Exempted routes: `/setup`, `/login` (pre-session)
- **New API Endpoint:**
  - `GET /api/csrf-token` - Retrieve current CSRF token

#### Session Security
- Enhanced cookie security settings:
  - `SESSION_COOKIE_HTTPONLY = True`
  - `SESSION_COOKIE_SAMESITE = 'Lax'`
- Secure session management with flask-login integration

### 📦 Dependencies

#### Updated
- `flask-wtf==1.2.1` - Added for CSRF protection

#### Existing
- `Flask>=3.0,<4` - Web framework
- `psutil>=5.9,<6.1` - System metrics
- `bcrypt>=4.0.1,<5` - Password hashing
- `watchdog>=3.0,<5` - File monitoring
- `ldap3>=2.9,<3` - LDAP authentication (optional)
- `pywin32>=306` - Windows integration (Windows only)
- `flask-login>=0.6,<0.7` - Session management
- `gputil>=1.4,<2` - GPU info (optional)

### 🔧 Technical Improvements

#### Code Organization
- Better separation of concerns in template structure
- Improved JavaScript function scoping
- Enhanced error handling in file operations
- Cleaner API endpoint organization

#### Blueprint Architecture
- Added new blueprints for modular functionality:
  - `routes_user_links` - User links management
  - `reports_bp` - Reports and analytics
  - `routes_api_recent_files` - Recent files API
  - `routes_api_open_file` - File operations API
  - `routes_csrf` - CSRF token management
  - `routes_admin_tools` - Admin utilities

#### Rights Management
- Expanded rights system to include:
  - `send_reports` - Access to reports dashboard
  - Enhanced `view_recent_files` enforcement
  - Granular control over file operations

### 📝 Documentation

#### Updated Files
- `readme.md` - Updated with new features and latest capabilities
- `CHANGELOG_DEV_vs_MAIN.md` - Comprehensive changelog vs main branch
- `CHANGELOG_PROD_BETA.md` - This file

#### New Documentation
- Enhanced inline code documentation
- Improved API endpoint documentation
- Better error message clarity

### 🚀 Performance

- Optimized recent files queries
- Improved dashboard loading times
- Enhanced template rendering efficiency
- Reduced redundant API calls

### 🔄 Breaking Changes

None. This release is fully backward compatible with existing configurations.

### 📋 Migration Guide

1. **Backup existing configurations:**
   ```bash
   cp organizer_config.json organizer_config.json.backup
   cp dashboard_config.json dashboard_config.json.backup
   ```

2. **Pull latest changes:**
   ```bash
   git checkout Prod-Beta
   git pull origin Prod-Beta
   ```

3. **Update dependencies:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **Restart dashboard:**
   ```bash
   python OrganizerDashboard.py
   ```

5. **Verify functionality:**
   - Visit `/config` and test all buttons
   - Create a user link at `/user-links`
   - Generate a report at `/reports`
   - Test recent file operations

### ✅ Verification Checklist

- [ ] Dashboard loads without template errors
- [ ] All config page buttons respond correctly
- [ ] Factory Reset button prompts for confirmation
- [ ] Service Install/Uninstall buttons function
- [ ] User Links page displays and allows CRUD operations
- [ ] Reports page shows accurate statistics
- [ ] Recent files can be opened and revealed
- [ ] CSRF tokens are properly managed
- [ ] Rights enforcement works as expected
- [ ] No console errors in browser developer tools

### 🐛 Known Issues

None at this time.

### 🔮 Upcoming Features

- Email notifications for file organization events
- Scheduled reporting
- Advanced file search capabilities
- Integration with cloud storage providers
- Mobile-responsive dashboard improvements

---

**Release Date:** December 2, 2025  
**Branch:** Prod-Beta  
**Contributors:** Atomsk865  
**Tested On:** Windows 10/11, Python 3.9+
