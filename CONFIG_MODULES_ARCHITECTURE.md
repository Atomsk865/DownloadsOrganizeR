# Config Modules Modernization Architecture

**Version:** 1.0  
**Date:** December 5, 2025  
**Status:** Architecture Planning Phase

## Executive Summary

Complete redesign of all 9 configuration modules to use modern ES6 architecture, improved UX/UI patterns, and consistent BaseModule integration. This document serves as the master blueprint for systematic implementation.

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Target Architecture](#target-architecture)
3. [Module Specifications](#module-specifications)
4. [UI/UX Modernization Strategy](#uiux-modernization-strategy)
5. [API Integration Mapping](#api-integration-mapping)
6. [Implementation Phases](#implementation-phases)
7. [Migration Guide](#migration-guide)
8. [Testing Strategy](#testing-strategy)

---

## Current State Analysis

### Existing Implementation

**File:** `dash/config_modules.html` (547 lines)

**Problems Identified:**
- ❌ Inline `onclick` handlers throughout
- ❌ Global function namespace pollution (60+ functions)
- ❌ No state management or reactivity
- ❌ Mixed concerns (UI + business logic + API calls)
- ❌ Limited error handling and validation
- ❌ No cross-module communication
- ❌ Inconsistent loading states and feedback
- ❌ Manual DOM manipulation scattered across code

### Legacy Functions Inventory

**Dashboard Scripts** (`dashboard_scripts.html` - 4770 lines):

```javascript
// Features & Integrations (1 function)
saveFeaturesConfig()

// Users & Roles (5 functions)
filterUsers(), clearUserSearch(), saveUser(), deleteUser(), loadUsers()

// Role Rights (2 functions)
filterRoles(), clearRoleSearch()

// Service Installation (3 functions)
installService(), reinstallService(), uninstallService()

// Network Targets (6 functions)
filterNetworkTargets(), clearNetworkTargetSearch(), applyNASTemplate(),
addNetworkTarget(), testNAS(), saveNetworkConfig()

// SMTP & Credentials (6 functions)
applySMTPTemplate(), addCredential(), deleteCredential(),
testSMTP(), saveSmtpAndCredentials(), loadCredentials()

// Watched Folders (7 functions)
addWatchFolder(), saveWatchFolders(), testSelectedWatchFolder(),
loadWatchedFolders(), deleteWatchFolder(), openConfigActions(),
selectWatchFolder()

// Branding & Themes (14 functions)
applyPresetTheme(), saveBranding(), exportTheme(), resetBranding(),
toggleThemePreview(), extractColorsFromLogo(), previewTheme(),
updateColorSwatchBackground(), loadThemeFromServer(),
updateDashboardLogo(), updateThemeFormFields(),
clearPersistedTheme(), exportPersistedTheme(), applyThemeStyles()

// Logs (3 functions)
clearLog(), filterLogs(), clearLogSearch()

// TOTAL: ~50 global functions to be modularized
```

---

## Target Architecture

### Core Technology Stack

```javascript
// Foundation
- ES6 Modules (import/export)
- BaseModule extension pattern
- Store (reactive state management)
- EventBus (cross-module events)
- API utility (HTTP client)
- UI utility (notifications)
- DOM utility (element manipulation)

// New Utilities (to be created)
- FormValidator (centralized validation)
- TableManager (CRUD operations)
- TemplateEngine (dynamic UI generation)
```

### Architectural Principles

1. **Single Responsibility**: Each module manages one config domain
2. **Reactive State**: All data changes flow through Store
3. **Event-Driven**: Modules communicate via EventBus
4. **API-First**: All server interactions through API utility
5. **Progressive Enhancement**: Graceful degradation on errors
6. **Accessibility**: ARIA labels, keyboard navigation, screen reader support
7. **Performance**: Debounced searches, lazy loading, virtual scrolling

### File Structure

```
static/js/modules/
├── config/
│   ├── features-config.js          ✅ COMPLETE
│   ├── users-roles-config.js       📝 TO DO
│   ├── service-install-config.js   📝 TO DO
│   ├── network-targets-config.js   📝 TO DO
│   ├── smtp-credentials-config.js  📝 TO DO
│   ├── watched-folders-config.js   📝 TO DO
│   ├── branding-config.js          📝 TO DO
│   ├── logs-viewer-config.js       📝 TO DO
│   └── role-rights-config.js       📝 TO DO (read-only viewer)
├── utilities/
│   ├── form-validator.js           📝 TO DO
│   ├── table-manager.js            📝 TO DO
│   └── template-engine.js          📝 TO DO
└── config-coordinator.js           📝 TO DO (orchestrator)

dash/
├── config_page.html                📝 UPDATE (remove inline scripts)
└── config_modules.html             📝 UPDATE (modernize markup)
```

---

## Module Specifications

### 1. Features & Integrations Config ✅

**Status:** COMPLETE  
**File:** `static/js/modules/features-config.js` (200 lines)

**Functionality:**
- VirusTotal API key management
- Feature toggles (duplicates, reports, developer mode)
- Real-time validation
- Auto-save on toggle

**API Endpoints:**
- `GET /api/organizer/config` - Load config
- `POST /api/update` - Save config

**State:**
```javascript
{
  virustotal_enabled: Boolean,
  vt_api_key: String,
  duplicates_enabled: Boolean,
  reports_enabled: Boolean,
  developer_mode: Boolean
}
```

**Events Emitted:**
- `config:updated` - Full config saved
- `features:updated` - Feature flags changed
- `developer-mode:changed` - Developer mode toggled

---

### 2. Users & Roles Config 📝

**Priority:** HIGH (Most used admin feature)  
**File:** `static/js/modules/users-roles-config.js`  
**Estimated Size:** 350 lines

**Functionality:**
- User table with search/filter
- Add/edit/delete users (CRUD)
- Role assignment dropdown
- Password management (hashed server-side)
- Real-time table updates
- Inline editing mode
- Bulk operations (export, delete selected)

**API Endpoints:**
- `GET /api/dashboard/config` - Load users (sanitized, no password hashes)
- `POST /api/dashboard/users` - Create/update user
  ```json
  { "username": "john", "role": "viewer", "password": "optional" }
  ```
- `DELETE /api/dashboard/users/<username>` - Delete user

**State:**
```javascript
{
  users: Array<{ username: String, role: String }>,
  roles: Object,  // Available roles with rights
  searchQuery: String,
  selectedUser: Object|null,
  editMode: Boolean,
  sortField: String,
  sortDirection: 'asc'|'desc'
}
```

**UI Components:**
- Search bar with debounced filter (300ms)
- Sortable table headers
- Action buttons (edit, delete) with confirmation
- Add/Edit form with validation
- Password strength indicator
- Role selector with rights preview

**Events Emitted:**
- `users:updated` - User list changed
- `user:created` - New user added
- `user:deleted` - User removed
- `user:selected` - User clicked for editing

**Validation Rules:**
- Username: 3-32 chars, alphanumeric + underscore
- Password: 8+ chars, 1 upper, 1 lower, 1 number (optional on update)
- Role: Must exist in roles dictionary
- Cannot delete currently logged-in user

**UX Enhancements:**
- Inline edit mode (double-click row)
- Keyboard shortcuts (Ctrl+N = new user, Delete = delete selected)
- Undo/redo for recent changes (3 actions)
- Export users to CSV
- Import users from CSV

---

### 3. Role Rights Config 📝

**Priority:** MEDIUM (Read-only display)  
**File:** `static/js/modules/role-rights-config.js`  
**Estimated Size:** 200 lines

**Functionality:**
- Display role permissions matrix
- Search/filter roles
- Expandable rights details
- Visual permission indicators (badges)
- Future: Role editing (requires backend changes)

**API Endpoints:**
- `GET /api/dashboard/config` - Load roles dict

**State:**
```javascript
{
  roles: Object,  // { role_name: { right: boolean } }
  searchQuery: String,
  expandedRoles: Set<String>
}
```

**UI Components:**
- Search bar
- Permission matrix table
- Badge indicators (green=allowed, gray=denied)
- Expand/collapse rows
- Legend/help text

**Events Emitted:**
- `roles:loaded` - Roles data fetched

**UX Enhancements:**
- Click badge to see right description
- Export role matrix to PDF/CSV
- Visual diff between roles (compare mode)

---

### 4. Service Installation Config 📝

**Priority:** MEDIUM (Windows-only, admin feature)  
**File:** `static/js/modules/service-install-config.js`  
**Estimated Size:** 250 lines

**Functionality:**
- Install/reinstall/uninstall Windows service
- Service configuration (name, paths, thresholds)
- Platform detection (disable on non-Windows)
- Real-time service status
- Installation progress tracking

**API Endpoints:**
- `GET /api/service/installation-config` - Get config
- `POST /api/service/install` - Install service
  ```json
  {
    "service_name": "DownloadsOrganizer",
    "scripts_root": "C:\\Scripts",
    "memory_threshold_mb": 200,
    "cpu_threshold_percent": 60
  }
  ```
- `POST /api/service/reinstall` - Reinstall
- `POST /api/service/uninstall` - Uninstall

**State:**
```javascript
{
  isWindows: Boolean,
  serviceName: String,
  scriptsRoot: String,
  memoryThresholdMb: Number,
  cpuThresholdPercent: Number,
  isInstalled: Boolean,
  installationStatus: 'idle'|'installing'|'success'|'error',
  installationLog: Array<String>
}
```

**UI Components:**
- Platform check banner (hide module on non-Windows)
- Configuration form
- Install/reinstall/uninstall buttons (disabled during operation)
- Progress indicator with logs
- Service status badge (running/stopped/not installed)

**Events Emitted:**
- `service:installing` - Installation started
- `service:installed` - Installation complete
- `service:uninstalled` - Service removed
- `service:error` - Installation failed

**Validation Rules:**
- Service name: Alphanumeric, no spaces
- Scripts root: Valid Windows path
- Memory threshold: 50-2000 MB
- CPU threshold: 10-100%

**UX Enhancements:**
- Real-time installation log streaming
- Auto-refresh service status every 5s
- Rollback on failed installation
- Service health diagnostics

---

### 5. Network Targets Config 📝

**Priority:** HIGH (NAS/SMB critical feature)  
**File:** `static/js/modules/network-targets-config.js`  
**Estimated Size:** 400 lines

**Functionality:**
- NAS/SMB target management (CRUD)
- Template system (Synology, QNAP, Windows, Generic)
- UNC path validation
- Credential key linking
- Test connection functionality
- Ping/connectivity check

**API Endpoints:**
- `GET /api/dashboard/config` - Load network_targets array
- `POST /api/update` - Save targets
  ```json
  {
    "network_targets": [
      {
        "name": "Synology NAS",
        "path": "\\\\192.168.1.100\\downloads",
        "credential_key": "nas_default"
      }
    ]
  }
  ```
- `POST /api/test-nas` - Test connection (to be created)

**State:**
```javascript
{
  targets: Array<{ name, path, credential_key }>,
  selectedTemplate: String|null,
  searchQuery: String,
  editingTarget: Object|null,
  testResults: Map<String, Object>  // target_name -> { success, message, latency }
}
```

**Templates:**
```javascript
const NAS_TEMPLATES = {
  synology: {
    name: "Synology NAS",
    defaultPath: "\\\\<IP>\\<share>",
    defaultPort: 5000,
    protocol: "SMB2/3"
  },
  qnap: {
    name: "QNAP NAS",
    defaultPath: "\\\\<IP>\\<share>",
    defaultPort: 445,
    protocol: "SMB3"
  },
  windows: {
    name: "Windows Share",
    defaultPath: "\\\\<hostname>\\<share>",
    defaultPort: 445,
    protocol: "SMB2/3"
  },
  generic: {
    name: "Generic SMB/CIFS",
    defaultPath: "\\\\<server>\\<share>\\<path>",
    protocol: "Auto-detect"
  }
}
```

**UI Components:**
- Template selector dropdown
- Targets table with status indicators
- Add/Edit form with live validation
- Test connection button (per target)
- Credential key autocomplete (from credentials list)
- Connectivity status badges (online/offline/untested)

**Events Emitted:**
- `network-targets:updated` - Targets list changed
- `network-target:tested` - Connection test complete
- `network-target:selected` - Target selected for editing

**Validation Rules:**
- Name: 3-64 chars, alphanumeric + spaces
- Path: Valid UNC format `\\server\share[\path]`
- Credential key: Must exist in credentials vault

**UX Enhancements:**
- Auto-detect path format (convert forward slashes)
- Quick test all targets (batch operation)
- Path placeholder resolution preview
- Latency indicator (green <100ms, yellow <500ms, red >500ms)
- Auto-fill from discovered network shares (SMB discovery)

---

### 6. SMTP & Credentials Config 📝

**Priority:** HIGH (Email + credential vault)  
**File:** `static/js/modules/smtp-credentials-config.js`  
**Estimated Size:** 450 lines

**Functionality:**
- SMTP configuration with templates
- Email test functionality
- Credentials vault (username/password base64)
- Credential key management (CRUD)
- SMTP provider presets
- TLS/SSL configuration

**API Endpoints:**
- `GET /api/dashboard/config` - Load smtp and credentials
- `POST /api/update` - Save smtp and credentials
  ```json
  {
    "smtp": {
      "host": "smtp.gmail.com",
      "port": 587,
      "from": "noreply@example.com",
      "to": "admin@example.com",
      "user": "user@gmail.com",
      "pass": "app_password",
      "tls": true
    },
    "credentials": {
      "nas_default": {
        "username": "admin",
        "password": "cGFzc3dvcmQ="  // base64
      }
    }
  }
  ```
- `POST /api/test-smtp` - Send test email (to be created)

**State:**
```javascript
{
  smtp: {
    host: String,
    port: Number,
    from: String,
    to: String,
    user: String,
    pass: String,
    tls: Boolean
  },
  credentials: Object,  // { key: { username, password_base64 } }
  selectedSmtpTemplate: String|null,
  editingCredential: String|null,
  testStatus: 'idle'|'testing'|'success'|'error'
}
```

**SMTP Templates:**
```javascript
const SMTP_TEMPLATES = {
  gmail: {
    host: "smtp.gmail.com",
    port: 587,
    tls: true,
    instructions: "Use App Password, not regular password"
  },
  outlook: {
    host: "smtp-mail.outlook.com",
    port: 587,
    tls: true
  },
  office365: {
    host: "smtp.office365.com",
    port: 587,
    tls: true
  },
  yahoo: {
    host: "smtp.mail.yahoo.com",
    port: 587,
    tls: true
  },
  generic: {
    host: "",
    port: 587,
    tls: true
  }
}
```

**UI Components:**
- SMTP template selector
- SMTP config form (host, port, from, to, auth, TLS)
- Test email button with status
- Credentials vault table
- Add/Edit credential form
- Base64 encode/decode helper
- Password visibility toggle

**Events Emitted:**
- `smtp:updated` - SMTP config changed
- `smtp:tested` - Test email sent
- `credentials:updated` - Credential added/deleted
- `credential:selected` - Credential selected for editing

**Validation Rules:**
- SMTP host: Valid hostname/IP
- Port: 1-65535 (common: 25, 465, 587)
- From/To: Valid email format
- Credential key: 3-64 chars, alphanumeric + underscore
- Password: Base64 encoded string

**Security Considerations:**
- ⚠️ Passwords stored as base64 (encoding, NOT encryption)
- Recommend OS credential vault for production
- Never log passwords to console/errors
- Clear password fields after save
- Mask passwords in UI (reveal on hover/click)

**UX Enhancements:**
- Test email with custom message
- Provider-specific setup instructions (tooltips)
- Auto-detect SMTP settings from email domain
- Import credentials from CSV (encrypted)
- Password strength indicator
- Connection troubleshooting wizard

---

### 7. Watched Folders Config 📝

**Priority:** HIGH (Core organizer feature)  
**File:** `static/js/modules/watched-folders-config.js`  
**Estimated Size:** 350 lines

**Functionality:**
- Watched folders list (CRUD)
- Path validation (UNC, Windows, Unix)
- Placeholder resolution (%USERNAME%, %USER%)
- Create missing folder option
- Test selected folder
- Config actions audit log viewer

**API Endpoints:**
- `GET /api/organizer/config` - Load watched_folders array
- `POST /api/update` - Save watched_folders
  ```json
  {
    "watched_folders": [
      "C:/Users/%USERNAME%/Downloads",
      "\\\\NAS\\downloads"
    ]
  }
  ```
- `POST /api/test-folder` - Test folder access (to be created)
- `GET /api/config/actions` - Get audit log (to be created)

**State:**
```javascript
{
  folders: Array<String>,
  selectedFolder: String|null,
  createIfMissing: Boolean,
  searchQuery: String,
  testResults: Map<String, Object>,  // path -> { exists, writable, readable }
  auditLog: Array<Object>  // Recent config changes
}
```

**UI Components:**
- Folder path input with validation
- Watched folders list (sortable, selectable)
- Add/Save/Test buttons
- Create missing checkbox
- Test result badges (✓ writable, ⚠ read-only, ✗ no access)
- Audit log modal (recent changes)

**Path Formats Supported:**
- UNC: `\\server\share\path`
- Windows absolute: `C:\path` or `C:/path`
- Unix absolute: `/path/to/folder`
- Placeholders: `%USERNAME%`, `%USER%` (resolved at runtime)

**Events Emitted:**
- `watched-folders:updated` - Folder list changed
- `watched-folder:tested` - Test complete
- `watched-folder:selected` - Folder selected

**Validation Rules:**
- Path: Non-empty, valid format for platform
- No duplicate paths (case-insensitive on Windows)
- Placeholders: Only %USERNAME% and %USER%

**UX Enhancements:**
- Drag-and-drop to add folders
- File browser dialog (if accessible)
- Path autocomplete from common locations
- Batch test all folders
- Folder size/file count preview
- Visual indicator of actively monitored folders (from service)

---

### 8. Branding & Themes Config 📝

**Priority:** HIGH (Most complex UI module)  
**File:** `static/js/modules/branding-config.js`  
**Estimated Size:** 600 lines

**Functionality:**
- 7 preset themes
- Custom theme creator (colors, fonts, spacing)
- Auto-extract colors from logo
- Custom CSS editor
- Theme preview mode
- Import/export themes
- Integration with existing ThemeSystem

**API Endpoints:**
- `GET /api/dashboard/branding` - Load branding config
- `POST /api/dashboard/branding` - Save branding
  ```json
  {
    "title": "DownloadsOrganizeR",
    "logo": "https://example.com/logo.png",
    "theme_name": "Custom Blue",
    "colors": {
      "primary": "#0d6efd",
      "secondary": "#6c757d",
      "success": "#198754",
      "danger": "#dc3545",
      "warning": "#ffc107",
      "info": "#0dcaf0"
    },
    "advanced": {
      "border_radius": "8px",
      "font_size": "100%",
      "shadow": "normal"
    },
    "custom_css": "/* Custom styles */"
  }
  ```

**State:**
```javascript
{
  title: String,
  logo: String,
  themeName: String,
  colors: {
    primary, secondary, success, danger, warning, info: String  // hex
  },
  advanced: {
    borderRadius: String,
    fontSize: String,
    shadow: String
  },
  customCss: String,
  previewMode: Boolean,
  autoGenerateColors: Boolean,
  activePreset: String|null
}
```

**Preset Themes:**
```javascript
const PRESET_THEMES = {
  default: {
    name: "Default Blue",
    colors: { primary: "#0d6efd", secondary: "#6c757d", ... }
  },
  dark: {
    name: "Dark Mode",
    colors: { primary: "#375a7f", secondary: "#444", ... }
  },
  forest: {
    name: "Forest Green",
    colors: { primary: "#2d5016", secondary: "#5c8a3c", ... }
  },
  sunset: {
    name: "Sunset Orange",
    colors: { primary: "#ff6f00", secondary: "#ff8f00", ... }
  },
  ocean: {
    name: "Ocean Blue",
    colors: { primary: "#006994", secondary: "#0096c7", ... }
  },
  mint: {
    name: "Mint Fresh",
    colors: { primary: "#40916c", secondary: "#52b788", ... }
  },
  cyberpunk: {
    name: "Cyberpunk Neon",
    colors: { primary: "#ff006e", secondary: "#8338ec", ... }
  }
}
```

**UI Components:**
- Preset theme buttons (7)
- Title/logo inputs
- 6 color pickers (primary, secondary, success, danger, warning, info)
- Advanced options dropdowns (border radius, font size, shadow)
- Custom CSS editor (syntax highlighted)
- Auto-generate from logo button
- Preview/Save/Export/Reset buttons
- Live preview panel (optional)

**Color Extraction Algorithm:**
```javascript
// Extract dominant colors from logo image
async extractColorsFromLogo(logoUrl) {
  const img = await loadImage(logoUrl);
  const canvas = createCanvas(img.width, img.height);
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);
  
  // Use color-thief or similar library
  const colorThief = new ColorThief();
  const palette = colorThief.getPalette(img, 6);
  
  // Map to theme colors
  return {
    primary: rgbToHex(palette[0]),
    secondary: rgbToHex(palette[1]),
    success: adjustHue(palette[0], 120),  // Green-shifted
    danger: adjustHue(palette[0], -30),   // Red-shifted
    warning: adjustHue(palette[0], 60),   // Yellow-shifted
    info: adjustHue(palette[0], 180)      // Cyan-shifted
  };
}
```

**Events Emitted:**
- `branding:updated` - Branding saved
- `theme:applied` - Theme applied
- `theme:previewed` - Preview toggled
- `colors:extracted` - Colors extracted from logo

**Validation Rules:**
- Logo URL: Valid HTTP(S) URL or data URI
- Colors: Valid hex format (#RRGGBB)
- Border radius: 0-50px
- Font size: 80-150%
- Custom CSS: No `<script>` tags (XSS prevention)

**UX Enhancements:**
- Live preview mode (toggle on/off)
- Color harmony suggestions (complementary, analogous)
- Accessibility contrast checker (WCAG AA/AAA)
- Theme versioning (undo/redo)
- Share theme as JSON file
- Import theme from file
- Color palette history (recent colors)
- Dark mode auto-detection

---

### 9. Logs Viewer Config 📝

**Priority:** MEDIUM (Real-time monitoring)  
**File:** `static/js/modules/logs-viewer-config.js`  
**Estimated Size:** 300 lines

**Functionality:**
- Real-time log streaming (stdout, stderr)
- Search/filter logs with highlighting
- Clear log functionality
- Auto-scroll to bottom
- Log level filtering
- Export logs to file

**API Endpoints:**
- `GET /stream/stdout` - SSE stream for stdout (existing)
- `GET /stream/stderr` - SSE stream for stderr (existing)
- `POST /clear-log` - Clear logs (existing)
- `GET /api/logs/download` - Download logs (to be created)

**State:**
```javascript
{
  stdoutLogs: Array<String>,
  stderrLogs: Array<String>,
  searchQuery: String,
  autoScroll: Boolean,
  logLevel: 'all'|'info'|'warning'|'error',
  streaming: Boolean,
  maxLines: Number  // Performance limit
}
```

**UI Components:**
- Search bar with highlighting
- Log level filter (all, info, warning, error)
- Stdout/Stderr split view
- Clear log buttons
- Auto-scroll toggle
- Download logs button
- Line numbers
- Timestamp column

**Log Parsing:**
```javascript
// Parse log lines for metadata
parseLogLine(line) {
  // Example: [2025-12-05 10:23:45] INFO: File organized
  const regex = /^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+): (.+)$/;
  const match = line.match(regex);
  
  if (match) {
    return {
      timestamp: match[1],
      level: match[2],
      message: match[3]
    };
  }
  
  return { timestamp: null, level: 'INFO', message: line };
}
```

**Events Emitted:**
- `logs:updated` - New logs received
- `logs:cleared` - Logs cleared
- `logs:filtered` - Search query changed

**Performance Optimizations:**
- Virtual scrolling for 10K+ lines
- Debounced search (300ms)
- Log rotation (max 5000 lines in memory)
- Lazy rendering (only visible lines)

**UX Enhancements:**
- Syntax highlighting for known formats (JSON, XML)
- Click to copy line
- Multi-line selection
- Regex search mode
- Tail mode (always show last N lines)
- Log level color coding (info=blue, warning=yellow, error=red)
- Collapse similar consecutive lines

---

## UI/UX Modernization Strategy

### Design System

**Colors:**
```css
--config-primary: #0d6efd;
--config-success: #198754;
--config-warning: #ffc107;
--config-danger: #dc3545;
--config-info: #0dcaf0;
--config-secondary: #6c757d;

--config-bg-module: #ffffff;
--config-bg-hover: #f8f9fa;
--config-border: #dee2e6;
--config-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
```

**Typography:**
```css
--config-font-family: 'Segoe UI', system-ui, sans-serif;
--config-font-size-base: 0.9rem;
--config-font-size-small: 0.8rem;
--config-line-height: 1.5;
```

**Spacing:**
```css
--config-spacing-xs: 0.25rem;
--config-spacing-sm: 0.5rem;
--config-spacing-md: 1rem;
--config-spacing-lg: 1.5rem;
--config-spacing-xl: 2rem;
```

### Component Library

**1. Config Card**
```html
<div class="config-card" data-module="module-name">
  <div class="config-card-header">
    <h5 class="config-card-title">
      <i class="bi bi-icon"></i> Module Title
    </h5>
    <div class="config-card-actions">
      <button class="btn-icon" title="Help">
        <i class="bi bi-question-circle"></i>
      </button>
      <span class="drag-handle">
        <i class="bi bi-grip-vertical"></i>
      </span>
    </div>
  </div>
  <div class="config-card-body">
    <!-- Module content -->
  </div>
  <div class="config-card-footer">
    <!-- Actions -->
  </div>
</div>
```

**2. Form Field**
```html
<div class="form-field">
  <label class="form-label">
    Field Label
    <span class="form-label-required">*</span>
    <i class="bi bi-info-circle" title="Help text"></i>
  </label>
  <input type="text" class="form-control" data-validate="required">
  <div class="form-feedback invalid">Error message</div>
  <div class="form-feedback valid">Success message</div>
  <small class="form-text">Helper text</small>
</div>
```

**3. Data Table**
```html
<div class="data-table-wrapper">
  <div class="data-table-toolbar">
    <div class="search-box">
      <i class="bi bi-search"></i>
      <input type="text" placeholder="Search...">
    </div>
    <button class="btn-primary">Add</button>
  </div>
  <table class="data-table">
    <thead>
      <tr>
        <th class="sortable" data-sort="name">
          Name <i class="bi bi-sort"></i>
        </th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <!-- Rows generated by module -->
    </tbody>
  </table>
  <div class="data-table-footer">
    <span class="row-count">Showing 1-10 of 25</span>
  </div>
</div>
```

**4. Status Badge**
```html
<span class="status-badge status-success">
  <i class="bi bi-check-circle"></i> Online
</span>
<span class="status-badge status-warning">
  <i class="bi bi-exclamation-triangle"></i> Testing
</span>
<span class="status-badge status-danger">
  <i class="bi bi-x-circle"></i> Error
</span>
```

### Animation & Transitions

```css
/* Smooth transitions */
.config-card, .form-control, .btn {
  transition: all 0.2s ease-in-out;
}

/* Loading states */
.config-card.loading {
  opacity: 0.6;
  pointer-events: none;
}

.config-card.loading::after {
  content: '';
  position: absolute;
  inset: 0;
  background: url('/static/img/spinner.svg') center/48px no-repeat;
}

/* Success flash */
@keyframes success-flash {
  0%, 100% { background-color: transparent; }
  50% { background-color: var(--config-success-light); }
}

.config-card.saved {
  animation: success-flash 0.5s ease-in-out;
}
```

### Accessibility (WCAG 2.1 AA)

**Keyboard Navigation:**
- Tab order follows visual flow
- Focus indicators visible (3px outline)
- Escape closes modals/dialogs
- Enter submits forms
- Arrow keys navigate lists/tables

**ARIA Labels:**
```html
<button aria-label="Delete user John" title="Delete">
  <i class="bi bi-trash"></i>
</button>

<input 
  type="text" 
  aria-describedby="username-help"
  aria-invalid="false"
>
<small id="username-help">3-32 characters</small>
```

**Screen Reader Support:**
- Live regions for dynamic updates
- Hidden labels for icon buttons
- Role attributes for custom components
- Error announcements

---

## API Integration Mapping

### Existing Endpoints

| Module | Method | Endpoint | Purpose |
|--------|--------|----------|---------|
| Features | GET | `/api/organizer/config` | Load config |
| Features | POST | `/api/update` | Save config |
| Users | GET | `/api/dashboard/config` | Load users/roles |
| Users | POST | `/api/dashboard/users` | Create/update user |
| Users | DELETE | `/api/dashboard/users/<username>` | Delete user |
| Layout | POST | `/api/dashboard/layout` | Save dashboard layout |
| Service | GET | `/api/service/installation-config` | Get service config |
| Service | POST | `/api/service/install` | Install service |
| Service | POST | `/api/service/reinstall` | Reinstall service |
| Service | POST | `/api/service/uninstall` | Uninstall service |
| Branding | GET | `/api/dashboard/branding` | Load branding |
| Branding | POST | `/api/dashboard/branding` | Save branding |
| Logs | GET | `/stream/stdout` | SSE stdout stream |
| Logs | GET | `/stream/stderr` | SSE stderr stream |
| Logs | POST | `/clear-log` | Clear logs |

### New Endpoints Needed

| Module | Method | Endpoint | Purpose | Priority |
|--------|--------|----------|---------|----------|
| Network | POST | `/api/test-nas` | Test NAS connection | HIGH |
| SMTP | POST | `/api/test-smtp` | Send test email | HIGH |
| Watched | POST | `/api/test-folder` | Test folder access | MEDIUM |
| Watched | GET | `/api/config/actions` | Audit log | LOW |
| Logs | GET | `/api/logs/download` | Download logs | LOW |

### Request/Response Schemas

**Test NAS Connection:**
```json
// POST /api/test-nas
{
  "name": "Synology NAS",
  "path": "\\\\192.168.1.100\\downloads",
  "credential_key": "nas_default"
}

// Response
{
  "success": true,
  "message": "Connection successful",
  "latency_ms": 45,
  "readable": true,
  "writable": true,
  "file_count": 128
}
```

**Test SMTP:**
```json
// POST /api/test-smtp
{
  "host": "smtp.gmail.com",
  "port": 587,
  "from": "noreply@example.com",
  "to": "admin@example.com",
  "user": "user@gmail.com",
  "pass": "app_password",
  "tls": true,
  "subject": "Test Email",
  "body": "This is a test email from DownloadsOrganizeR"
}

// Response
{
  "success": true,
  "message": "Email sent successfully",
  "smtp_response": "250 2.0.0 OK"
}
```

**Test Folder:**
```json
// POST /api/test-folder
{
  "path": "C:\\Users\\admin\\Downloads"
}

// Response
{
  "success": true,
  "exists": true,
  "readable": true,
  "writable": true,
  "size_bytes": 1073741824,
  "file_count": 42,
  "resolved_path": "C:\\Users\\admin\\Downloads"  // After placeholder resolution
}
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Deliverables:**
- ✅ Features config module (COMPLETE)
- 📝 Form validator utility
- 📝 Table manager utility
- 📝 Template engine utility

**Tasks:**
1. Create `utilities/form-validator.js` (150 lines)
   - Validation rules engine
   - Real-time validation
   - Error message templating

2. Create `utilities/table-manager.js` (200 lines)
   - CRUD operations
   - Sorting/filtering
   - Row selection
   - Inline editing

3. Create `utilities/template-engine.js` (100 lines)
   - HTML template rendering
   - Data binding
   - Conditional rendering

**Testing:**
- Unit tests for each utility
- Integration test with features-config

---

### Phase 2: High-Priority Modules (Week 2)

**Deliverables:**
- 📝 Users & roles config module
- 📝 Network targets config module
- 📝 SMTP & credentials config module
- 📝 Watched folders config module

**Tasks:**
1. `users-roles-config.js` (350 lines)
   - User CRUD
   - Role assignment
   - Password management

2. `network-targets-config.js` (400 lines)
   - Target CRUD
   - Template system
   - Connection testing

3. `smtp-credentials-config.js` (450 lines)
   - SMTP config
   - Credential vault
   - Email testing

4. `watched-folders-config.js` (350 lines)
   - Folder management
   - Path validation
   - Test functionality

**Backend Work:**
- Implement `/api/test-nas` endpoint
- Implement `/api/test-smtp` endpoint
- Implement `/api/test-folder` endpoint

**Testing:**
- Smoke tests for all modules
- E2E test for complete config workflow

---

### Phase 3: Medium-Priority Modules (Week 3)

**Deliverables:**
- 📝 Branding config module
- 📝 Service install config module
- 📝 Role rights config module (read-only)

**Tasks:**
1. `branding-config.js` (600 lines)
   - Preset themes
   - Custom theme creator
   - Color extraction
   - CSS editor

2. `service-install-config.js` (250 lines)
   - Service control
   - Platform detection
   - Progress tracking

3. `role-rights-config.js` (200 lines)
   - Permission matrix
   - Search/filter
   - Visual indicators

**Testing:**
- Theme compatibility tests
- Service installation tests (Windows VM)
- Permission matrix validation

---

### Phase 4: Logs & Polish (Week 4)

**Deliverables:**
- 📝 Logs viewer config module
- 📝 Config coordinator (orchestrator)
- 📝 Updated config_page.html
- 📝 Updated config_modules.html
- 📝 Documentation

**Tasks:**
1. `logs-viewer-config.js` (300 lines)
   - Real-time streaming
   - Search/filter
   - Log parsing
   - Export functionality

2. `config-coordinator.js` (200 lines)
   - Module lifecycle management
   - Cross-module communication
   - State persistence
   - Error handling

3. Update HTML templates
   - Remove inline scripts
   - Add module data attributes
   - Modernize markup

4. Documentation
   - CONFIG_MODULES_QUICK_REFERENCE.md
   - API_ENDPOINTS.md
   - MIGRATION_GUIDE.md

**Testing:**
- Full integration tests
- Performance testing (10K log lines, 100 network targets)
- Accessibility audit (WAVE, axe)
- Cross-browser testing (Chrome, Firefox, Edge)

---

## Migration Guide

### For Developers

**Before Migration:**
```html
<!-- Old: Inline onclick handler -->
<button onclick="saveUser()">Save</button>

<script>
function saveUser() {
  const username = document.getElementById('username').value;
  // ... API call
}
</script>
```

**After Migration:**
```html
<!-- New: Module-managed -->
<button data-action="save">Save</button>

<script type="module">
import UsersRolesConfig from './modules/users-roles-config.js';

const usersConfig = new UsersRolesConfig();
usersConfig.mount('#users-roles-module');
</script>
```

### Backward Compatibility

**Legacy Function Wrappers:**
```javascript
// In config_page.html (temporary compatibility layer)
window.saveUser = () => {
  console.warn('Using legacy saveUser(). Update to UsersRolesConfig module.');
  const module = ModuleSystem.getModule('users-roles-config');
  module?.saveUser();
};
```

### Breaking Changes

1. ❌ Global functions removed (60+ functions)
2. ❌ Direct DOM manipulation replaced with modules
3. ❌ Inline onclick handlers removed
4. ✅ New API endpoints may change response format
5. ✅ State management now centralized in Store

### Migration Checklist

- [ ] Update all HTML templates
- [ ] Remove inline script blocks
- [ ] Add module imports to config_page.html
- [ ] Update any custom scripts that call old functions
- [ ] Test all config workflows
- [ ] Update documentation
- [ ] Train admin users on new UI

---

## Testing Strategy

### Unit Tests

**Each Module:**
```javascript
// tests/modules/users-roles-config.test.js
import { describe, it, expect, beforeEach } from 'vitest';
import UsersRolesConfig from '@/modules/users-roles-config';

describe('UsersRolesConfig', () => {
  let module;
  
  beforeEach(() => {
    module = new UsersRolesConfig();
  });
  
  it('should load users from API', async () => {
    const users = await module.loadUsers();
    expect(users).toBeInstanceOf(Array);
  });
  
  it('should validate username format', () => {
    expect(module.validateUsername('john123')).toBe(true);
    expect(module.validateUsername('a')).toBe(false);  // Too short
    expect(module.validateUsername('john@123')).toBe(false);  // Invalid char
  });
  
  it('should emit user:created event', async () => {
    const spy = vi.fn();
    EventBus.on('user:created', spy);
    
    await module.createUser({ username: 'test', role: 'viewer' });
    expect(spy).toHaveBeenCalled();
  });
});
```

### Integration Tests

**Full Config Workflow:**
```javascript
// tests/integration/config-workflow.test.js
describe('Config Workflow', () => {
  it('should complete full configuration', async () => {
    // 1. Set features
    await featuresConfig.toggleFeature('virustotal', true);
    
    // 2. Add user
    await usersConfig.createUser({ 
      username: 'testuser', 
      role: 'editor' 
    });
    
    // 3. Add network target
    await networkConfig.addTarget({
      name: 'Test NAS',
      path: '\\\\nas\\share',
      credential_key: 'test_cred'
    });
    
    // 4. Test connection
    const result = await networkConfig.testTarget('Test NAS');
    expect(result.success).toBe(true);
    
    // 5. Save all
    await coordinator.saveAll();
  });
});
```

### E2E Tests (Playwright)

**Config Page Navigation:**
```javascript
// tests/e2e/config-page.spec.js
import { test, expect } from '@playwright/test';

test('should navigate all config modules', async ({ page }) => {
  await page.goto('/config');
  
  // Features module
  await page.click('[data-module="features-integrations"]');
  await expect(page.locator('#cfg-vt-api-key')).toBeVisible();
  
  // Users module
  await page.click('[data-module="users-roles"]');
  await expect(page.locator('#users-table')).toBeVisible();
  
  // Test search
  await page.fill('#search-users', 'admin');
  await expect(page.locator('#users-tbody tr')).toHaveCount(1);
});

test('should add and delete user', async ({ page }) => {
  await page.goto('/config');
  
  // Add user
  await page.fill('#new-username', 'e2etest');
  await page.selectOption('#new-role', 'viewer');
  await page.fill('#user-new-password', 'testpass123');
  await page.click('button:has-text("Save User")');
  
  await expect(page.locator('text=User saved')).toBeVisible();
  
  // Delete user
  await page.click('[data-username="e2etest"] .btn-delete');
  await page.click('button:has-text("Confirm")');
  
  await expect(page.locator('text=User deleted')).toBeVisible();
});
```

### Performance Tests

**Load Testing:**
```javascript
// tests/performance/table-performance.test.js
describe('Table Performance', () => {
  it('should handle 1000 users without lag', async () => {
    const users = generateMockUsers(1000);
    
    const startTime = performance.now();
    await usersConfig.setState({ users });
    await usersConfig.renderTable();
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(100);  // 100ms max
  });
  
  it('should search 1000 users in <50ms', async () => {
    const users = generateMockUsers(1000);
    await usersConfig.setState({ users });
    
    const startTime = performance.now();
    usersConfig.searchUsers('john');
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(50);
  });
});
```

### Accessibility Tests

**WCAG 2.1 AA Compliance:**
```javascript
// tests/accessibility/config-a11y.test.js
import { axe } from 'jest-axe';

describe('Accessibility', () => {
  it('should have no violations on config page', async () => {
    const html = await renderConfigPage();
    const results = await axe(html);
    
    expect(results.violations).toHaveLength(0);
  });
  
  it('should support keyboard navigation', async () => {
    await page.goto('/config');
    
    // Tab through all interactive elements
    await page.keyboard.press('Tab');
    expect(await page.evaluate(() => document.activeElement.tagName))
      .toBe('BUTTON');
    
    // Enter should activate buttons
    await page.keyboard.press('Enter');
    // Assert action triggered
  });
});
```

---

## Appendix

### Glossary

- **BaseModule**: Base class that all modules extend
- **Store**: Reactive state management system
- **EventBus**: Pub/sub event system for cross-module communication
- **CRUD**: Create, Read, Update, Delete operations
- **UNC Path**: Universal Naming Convention (\\server\share\path)
- **SSE**: Server-Sent Events (real-time streaming)
- **WCAG**: Web Content Accessibility Guidelines

### Dependencies

**Existing:**
- ES6 Modules
- BaseModule (static/js/base-module.js)
- Store (static/js/store.js)
- EventBus (static/js/event-bus.js)
- API utility (static/js/api.js)
- UI utility (static/js/ui.js)
- DOM utility (static/js/dom.js)

**New:**
- FormValidator utility
- TableManager utility
- TemplateEngine utility
- ConfigCoordinator (orchestrator)

### Related Documentation

- [JAVASCRIPT_MODULARIZATION.md](./JAVASCRIPT_MODULARIZATION.md) - Core architecture
- [DEBUGGING_SUITE_MODERNIZATION.md](./DEBUGGING_SUITE_MODERNIZATION.md) - Debug tools
- [CONFIGURATION.md](./CONFIGURATION.md) - Backend config guide
- [AUTHENTICATION.md](./AUTHENTICATION.md) - Auth/rights system

### Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-05 | Initial architecture document |

---

## Next Steps

1. **Review & Approval**: Stakeholders review architecture
2. **Prototype**: Build form-validator utility + one module (users-roles)
3. **Iterate**: Refine based on prototype learnings
4. **Implement**: Systematic rollout per phases
5. **Test**: Comprehensive testing at each phase
6. **Deploy**: Staged rollout with feature flags
7. **Document**: User-facing documentation + developer guides

---

**Document Status:** 📋 Planning Phase  
**Estimated Effort:** 4 weeks (1 developer)  
**Lines of Code:** ~4500 lines across 12 files  
**Complexity:** High (UI + State + API + Utilities)  
**Priority:** HIGH (Core dashboard feature)
