# Cross-Platform Architecture Overview

**Visual guide to the multi-platform and mobile expansion**

---

## Current Architecture (Windows-Only)

```
┌─────────────────────────────────────────┐
│         Windows PC User                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Web Browser                    │   │
│  │  http://localhost:5000          │   │
│  │  Dashboard (Flask + Bootstrap)  │   │
│  └──────────────┬──────────────────┘   │
│                 │                      │
│                 │ (localhost)          │
│                 ▼                      │
│  ┌─────────────────────────────────┐   │
│  │  Flask App                      │   │
│  │  (SortNStoreDashboard.py)       │   │
│  │  - Config management           │   │
│  │  - Service control             │   │
│  │  - Statistics display          │   │
│  └──────────────┬──────────────────┘   │
│                 │                      │
│                 │ (local IPC)          │
│                 ▼                      │
│  ┌─────────────────────────────────┐   │
│  │  Windows Service (NSSM)         │   │
│  │  (Organizer.py)                 │   │
│  │  - File watching               │   │
│  │  - File organization           │   │
│  │  - Logging                     │   │
│  └──────────────┬──────────────────┘   │
│                 │                      │
│                 │ (file system)        │
│                 ▼                      │
│  ┌─────────────────────────────────┐   │
│  │  C:\Users\{user}\Downloads\    │   │
│  │  ├─ Images/                     │   │
│  │  ├─ Videos/                     │   │
│  │  ├─ Documents/                  │   │
│  │  └─ ...                         │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

---

## Target Architecture (Phase 1: Cross-Platform)

```
┌──────────────────────────────────────────────────────────────────┐
│                     ANY OPERATING SYSTEM                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Web Browser (any OS)                                    │   │
│  │  Dashboard (responsive, platform-agnostic)              │   │
│  │  ✅ Windows, ✅ macOS, ✅ Linux                         │   │
│  └──────────────┬─────────────────────────────────────────┘   │
│                 │                                              │
│                 │ HTTP/HTTPS                                  │
│                 ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Flask App (Cross-Platform)                              │   │
│  │  (SortNStoreDashboard.py)                                │   │
│  │  ├─ Platform detection (platform.system())             │   │
│  │  ├─ Config management (Paths module)                   │   │
│  │  ├─ Service control (ServiceManager abstraction)       │   │
│  │  └─ Auth backends (platform-specific)                 │   │
│  │                                                          │   │
│  │  Uses: SortNStoreDashboard/                             │   │
│  │  ├─ helpers/platform_paths.py      ← Path resolution    │   │
│  │  ├─ services/service_manager.py    ← Service control    │   │
│  │  └─ auth/auth_backends.py          ← Authentication     │   │
│  └──────────────┬─────────────────────────────────────────┘   │
│                 │                                              │
│        ┌────────┴────────┬────────────┐                        │
│        │                 │            │                        │
│   Windows        macOS           Linux                        │
│   (NSSM)       (launchctl)      (systemd)                    │
│        │                 │            │                        │
│        ▼                 ▼            ▼                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Organizer.py (Platform-Agnostic Core)            │   │
│  │                                                          │   │
│  │  ├─ File watching (watchdog - all platforms)          │   │
│  │  ├─ Config loading (JSON - all platforms)             │   │
│  │  ├─ File organization (pathlib - all platforms)       │   │
│  │  ├─ Logging (Python logging - all platforms)          │   │
│  │  └─ Path handling (platform_paths module)             │   │
│  │                                                          │   │
│  │  No Windows-specific code!                             │   │
│  └──────────────┬─────────────────────────────────────────┘   │
│                 │                                              │
│                 │ (file system)                                │
│                 ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Downloads Folder (Platform-Specific Location)    │   │
│  │                                                          │   │
│  │  Windows:  C:\Users\{user}\Downloads\                   │   │
│  │  macOS:    /Users/{user}/Downloads/                     │   │
│  │  Linux:    /home/{user}/Downloads/                      │   │
│  │                                                          │   │
│  │  Content (all platforms):                               │   │
│  │  ├─ Images/                                            │   │
│  │  ├─ Videos/                                            │   │
│  │  ├─ Documents/                                         │   │
│  │  └─ ...                                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Target Architecture (Phase 3: With Mobile)

```
┌──────────────────────────────────────────────────────────────────────┐
│                      MULTI-PLATFORM ECOSYSTEM                        │
└──────────────────────────────────────────────────────────────────────┘

                          Phase 3 Components
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
           Months 5-6         Months 6-8       Month 8+
               │                │                │
        ┌──────▼──────┐    ┌──────▼──────┐  ┌───▼────────┐
        │   Web MVP   │    │   Native    │  │ Production │
        │   (React)   │    │   Apps      │  │  Support   │
        └──────┬──────┘    └──────┬──────┘  └────────────┘
               │                  │
               └──────────┬───────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼─────┐    ┌──────▼──────┐    ┌───▼─────┐
   │ Web App  │    │ Mobile Apps │    │ Backend │
   │ (React)  │    │(React Native)    │(Python) │
   └────┬─────┘    └──────┬──────┘    └───┬─────┘
        │                 │                │
        ▼                 ▼                ▼

   DESKTOP       PHONE & TABLET      SERVER(S)
   BROWSERS       DEVICES           (Any OS)
        │                 │                │
        │        ┌────────┼────────┐      │
        │        │        │        │      │
   ┌────┼────┐ ┌─┴──┐ ┌──┴──┐ ┌──┴──┐  │
   │ Windows │ │iOS │ │Andr │ │macOS│  │
   │ macOS   │ │ app│ │oid  │ │Linu │  │
   │ Linux   │ │    │ │ app │ │ x   │  │
   │ Browser │ └────┘ └─────┘ └─────┘  │
   └────┬────┘        │        │        │
        │             │        │        │
        └─────────────┼────────┼────────┘
                      │        │
                      └────┬───┘
                           │
            ┌──────────────▼───────────────┐
            │  HTTPS REST API              │
            │  (SortNStoreDashboard.py)    │
            │                              │
            │  /api/v1/* (Web UI)         │
            │  /api/v2/* (Mobile)         │
            │  /api/organizer/* (Control) │
            │  /api/status/* (Status)     │
            │  /api/stats/* (Analytics)   │
            └──────────────┬───────────────┘
                           │
                           │
            ┌──────────────▼───────────────┐
            │  Organizer Service           │
            │  (Any OS: Win/Mac/Linux)     │
            │                              │
            │  Single codebase:           │
            │  ├─ File watching          │
            │  ├─ Organization           │
            │  ├─ Logging                │
            │  └─ Config management      │
            └──────────────┬───────────────┘
                           │
                           │
            ┌──────────────▼───────────────┐
            │  User Downloads Folder       │
            │  (Platform-Specific Path)    │
            │                              │
            │  All files organized by:     │
            │  ├─ Images                  │
            │  ├─ Videos                  │
            │  ├─ Documents               │
            │  └─ ...                     │
            └──────────────────────────────┘
```

---

## Data Flow: Dashboard Control → File Organization

```
USER ACTION
    │
    │ (Click "Pause Organizer")
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Device (Windows/macOS/Linux/iOS/Android/Browser)           │
│                                                             │
│  User Interface (Web Browser, Mobile App, or PWA)         │
└──────────────────────────────────────────────────────────┘
    │
    │ HTTPS REST API Call
    │ POST /api/v2/quick-actions
    │ {"action": "pause"}
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend Server (Any OS)                                    │
│                                                             │
│  Flask App (SortNStoreDashboard.py)                       │
│  @app.route('/api/v2/quick-actions')                      │
│  def handle_quick_action()                                │
│      if action == 'pause':                                │
│          send_signal_to_organizer('pause')               │
│      return jsonify({'success': True})                    │
└──────────────────────────────────────────────────────────┘
    │
    │ Inter-process Communication
    │ (File event, signal, queue, etc.)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Organizer Service (Windows/macOS/Linux)                    │
│                                                             │
│  Organizer.py                                             │
│  if pause_requested():                                    │
│      stop_watching()                                      │
│      log("Organizer paused")                              │
│      notify_dashboard("paused")                           │
└──────────────────────────────────────────────────────────┘
    │
    │ (Updates status in config)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ User Interface Updates                                      │
│                                                             │
│  Dashboard refreshes status                               │
│  Display: "Organizer Status: PAUSED"                      │
│  Button: "Resume Organizer"                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Code Organization After Phase 1

```
DownloadsOrganizeR/
│
├─ Organizer.py (core service - UNCHANGED in functionality)
│  ├─ Uses: platform_paths.Paths
│  ├─ Uses: service_manager.get_service_manager()
│  ├─ Uses: auth_backends.get_auth_backend()
│  └─ Platform-agnostic implementation
│
├─ SortNStoreDashboard.py (main app - enhanced)
│  ├─ Imports platform detection
│  ├─ Uses: platform_paths.Paths
│  ├─ Uses: service_manager.get_service_manager()
│  ├─ Routes for all platforms
│  └─ Added /api/config/paths endpoint
│
├─ SortNStoreDashboard/
│  │
│  ├─ helpers/
│  │  └─ platform_paths.py ✨ NEW
│  │     ├─ class PlatformPaths
│  │     ├─ get_downloads_folder()
│  │     ├─ get_config_paths()
│  │     ├─ get_logs_directory()
│  │     ├─ get_cache_directory()
│  │     └─ get_data_directory()
│  │
│  ├─ services/
│  │  └─ service_manager.py ✨ NEW
│  │     ├─ class ServiceManager (abstract)
│  │     ├─ class WindowsServiceManager (NSSM)
│  │     ├─ class LinuxSystemdManager (systemd)
│  │     ├─ class MacOSLaunchctlManager (launchctl)
│  │     └─ get_service_manager()
│  │
│  ├─ auth/
│  │  ├─ auth.py (existing - enhanced)
│  │  └─ auth_backends.py ✨ NEW
│  │     ├─ class AuthBackend (abstract)
│  │     ├─ class LocalFileAuth
│  │     ├─ class LDAPAuth
│  │     ├─ class WindowsActiveDirectoryAuth
│  │     ├─ class UnixPAMAuth
│  │     └─ get_auth_backend()
│  │
│  ├─ routes/
│  │  ├─ (existing routes - enhanced)
│  │  └─ mobile_api.py ✨ NEW (Phase 3)
│  │     ├─ /api/v2/status
│  │     ├─ /api/v2/quick-actions
│  │     ├─ /api/v2/notifications
│  │     ├─ /api/v2/statistics
│  │     └─ /api/v2/settings
│  │
│  └─ (other modules unchanged)
│
├─ dash/ (templates)
│  ├─ dashboard.html (enhanced with platform detection)
│  └─ (other templates)
│
├─ tests/
│  ├─ test_platform_paths.py ✨ NEW
│  ├─ test_service_manager.py ✨ NEW
│  ├─ test_auth_backends.py ✨ NEW
│  └─ (existing tests)
│
├─ requirements.txt (updated)
│  ├─ watchdog (already present) ✅
│  ├─ psutil (already present) ✅
│  ├─ flask (already present) ✅
│  ├─ pywin32>=306; sys_platform=='win32' (conditional) ✅
│  ├─ python-pam (new, Linux/macOS) ✨
│  ├─ python-daemon (new, Unix) ✨
│  └─ ldap3 (new, optional)
│
└─ (configuration files)
   ├─ organizer_config.json
   └─ (platform-agnostic)
```

---

## Phase 3 Web App Architecture

```
Frontend                            Backend
┌──────────────────────┐            ┌──────────────────────┐
│  React Web App       │            │  Existing Flask API  │
│  (3000-5000 loc)     │            │  (extended)          │
│                      │            │                      │
│  Pages:              │ HTTP/JSON  │  Routes:             │
│  ├─ Dashboard        ├───────────▶│  ├─ /api/v1/* (UI)  │
│  ├─ Statistics       │◀───────────┤  ├─ /api/v2/* (web) │
│  ├─ Notifications    │            │  └─ /api/status/*   │
│  ├─ Settings         │            │                      │
│  └─ Login            │            │  New endpoints:      │
│                      │            │  ├─ /api/v2/status  │
│  Components:         │            │  ├─ /api/v2/actions │
│  ├─ StatusCard       │            │  ├─ /api/v2/notif   │
│  ├─ Chart            │            │  └─ /api/v2/stats   │
│  ├─ QuickActions     │            │                      │
│  └─ NotificationList │            │  Services:           │
│                      │            │  ├─ service_manager │
│  Storage:            │            │  ├─ auth_backends   │
│  ├─ AsyncStorage     │            │  └─ platform_paths  │
│  ├─ IndexedDB        │            │                      │
│  └─ ServiceWorker    │            │  Config:             │
│                      │            │  └─ organizer_config │
│  PWA:                │            │                      │
│  ├─ Manifest         │            │  Organizer:          │
│  ├─ ServiceWorker    │            │  └─ Organizer.py    │
│  └─ Offline cache    │            │                      │
└──────────────────────┘            └──────────────────────┘
```

---

## Phase 3 Mobile App Architecture

```
iOS App                 Shared Code             Android App
(Swift/RN)             (JavaScript/TS)         (Kotlin/RN)
   │                         │                      │
   ├─ Swift Bridge           │                      │
   │  (native modules)       │                      │
   │                         │                      │
   └──────────────┬──────────┼──────────────┬──────┘
                  │          │              │
              React Native   │          React Native
                  │          │              │
              Screens ◀──────┴─────▶ API Client
              ├─ Dashboard       Axios / React Query
              ├─ Statistics      ├─ POST /api/v2/status
              ├─ Actions         ├─ GET /api/v2/actions
              ├─ Notifications   ├─ GET /api/v2/notif
              ├─ Settings        ├─ GET /api/v2/stats
              └─ Login           └─ POST /api/v2/control
                  │                      │
              Components          Redux Store
              ├─ StatusCard       ├─ authSlice
              ├─ Chart            ├─ statusSlice
              ├─ ActionButton     └─ settingsSlice
              └─ NotificationItem     │
                  │                   │
              Navigation         Local Storage
              └─ React Navigation ├─ AsyncStorage
                                 ├─ JWT tokens
                                 └─ Config cache
```

---

## Deployment Architecture (Post-Phase 3)

```
                        Cloud/On-Premise
                        ┌──────────────────┐
                        │  Backend Server  │
                        │  (Any OS)        │
                        │                  │
                        │  Flask + Python  │
                        │  ├─ Dashboard UI │
                        │  ├─ Web API      │
                        │  ├─ Mobile API   │
                        │  └─ Auth         │
                        │                  │
                        │  Organizer       │
                        │  ├─ File watch   │
                        │  ├─ Organization│
                        │  └─ Logging     │
                        └────────┬─────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
         Device 1          Device 2          Device 3
         ┌──────────┐   ┌──────────┐   ┌──────────┐
         │ Windows  │   │  macOS   │   │  Linux   │
         │  Desktop │   │  Desktop │   │  Server  │
         │          │   │          │   │          │
         │ Browser: │   │ Browser: │   │ Browser: │
         │ Dashboard│   │Dashboard │   │Dashboard │
         └──────────┘   └──────────┘   └──────────┘
                │                │                │
                │ HTTPS          │ HTTPS          │ HTTPS
                │                │                │
                └────────────────┼────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ Web App at       │
                        │ web.sortnstore   │
                        │                  │
                        │ React PWA        │
                        │ Responsive       │
                        │ All browsers     │
                        └──────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              ┌─────▼──────┐           ┌─────▼──────┐
              │ iOS App    │           │ Android App│
              │            │           │            │
              │ React Native           │ React Native
              │ AppStore   │           │ PlayStore  │
              └────────────┘           └────────────┘
```

---

This architecture ensures:
- ✅ Single codebase for desktop (Phase 1)
- ✅ Easy platform-specific deployment (Phase 2)
- ✅ Multiple device types for remote administration (Phase 3)
- ✅ Consistent experience across platforms
- ✅ Scalable and maintainable

---

**Status:** Architecture Complete, Ready to Build
