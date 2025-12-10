# Architecture

**System design and architecture documentation**

## Document Overview

### 📊 Dashboard Architecture Analysis
- **Focus:** Dashboard component design and internals
- **Details:** Flask structure, routes, security, state management
- **Use When:** You need to understand how dashboard is built

### 🔗 Dashboard-Organizer Integration
- **Focus:** How dashboard and organizer service communicate
- **Details:** APIs, message passing, file organization flow
- **Use When:** You're working on integration or adding features

### 🎨 Cross-Platform Architecture Diagrams
- **Focus:** Visual system architecture and data flow
- **Details:** Component relationships, network diagrams, flow charts
- **Use When:** You want visual understanding of the system

---

## Architecture Highlights

### Current Architecture (Windows)
```
User Downloads Folder
         ↓
  Organizer.py (File Watcher)
         ↓
  Categorizes by Extension
         ↓
  Creates Organized Folders
         ↓
  Dashboard Web UI (Flask)
```

### Components
- **Organizer.py** - File system monitoring and organization
- **OrganizerDashboard.py** - Flask web interface
- **organizer_config.json** - Configuration rules
- **Windows Service** - NSSM-based service management

---

## Design Principles

✓ **Modular** - Independent dashboard and organizer  
✓ **Configurable** - JSON-based rule configuration  
✓ **Secure** - Basic auth, CORS, input validation  
✓ **Observable** - Detailed logging and health monitoring  
✓ **Expandable** - Ready for cross-platform adaptation  

---

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| Flask for Dashboard | Lightweight, Python, easy to extend |
| JSON Configuration | Human-readable, easily parseable |
| File Extension-Based Routing | Simple, fast, reliable |
| Web-Based UI | Cross-browser, remote access capable |
| Windows Service via NSSM | Works with Windows service manager |

---

## Planning Cross-Platform?

See [Cross-Platform Architecture Diagrams](./CROSS_PLATFORM_ARCHITECTURE_DIAGRAMS.md) for how to expand system architecture to Linux/Mac.

---

## Related Documentation

- **Implementation Details** → See [Features](../features/)
- **Deployment Options** → See [Deployment](../deployment/)
- **Future Design** → See [Roadmaps](../roadmaps/)
- **Code Examples** → See [Guides](../guides/)

---

[← Back to Main Documentation](../INDEX.md)
