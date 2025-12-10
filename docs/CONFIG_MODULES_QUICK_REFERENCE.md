# Config Modules Quick Reference

**Quick navigation guide for developers implementing the config modules modernization.**

---

## Module Overview

| # | Module | Priority | Size | Status | Dependencies |
|---|--------|----------|------|--------|--------------|
| 1 | Features & Integrations | ✅ | 200 lines | COMPLETE | - |
| 2 | Users & Roles | 🔴 HIGH | 350 lines | TO DO | FormValidator, TableManager |
| 3 | Role Rights (read-only) | 🟡 MED | 200 lines | TO DO | TableManager |
| 4 | Service Installation | 🟡 MED | 250 lines | TO DO | - |
| 5 | Network Targets | 🔴 HIGH | 400 lines | TO DO | FormValidator, TableManager |
| 6 | SMTP & Credentials | 🔴 HIGH | 450 lines | TO DO | FormValidator, TableManager |
| 7 | Watched Folders | 🔴 HIGH | 350 lines | TO DO | FormValidator |
| 8 | Branding & Themes | 🔴 HIGH | 600 lines | TO DO | TemplateEngine |
| 9 | Logs Viewer | 🟡 MED | 300 lines | TO DO | - |

**Total:** ~3,100 lines across 9 modules

---

## Module Template

**Copy-paste starter for new modules:**

```javascript
/**
 * ModuleNameConfig - Description
 * 
 * @module static/js/modules/module-name-config
 * @requires BaseModule, Store, EventBus, API, UI
 */

import BaseModule from '../base-module.js';
import Store from '../store.js';
import EventBus from '../event-bus.js';
import API from '../api.js';
import UI from '../ui.js';

class ModuleNameConfig extends BaseModule {
    constructor() {
        super('module-name-config');
        
        // Initialize state
        this.setState({
            // Your state properties
            data: [],
            loading: false,
            error: null
        });
        
        // Bind methods
        this.load = this.load.bind(this);
        this.save = this.save.bind(this);
    }
    
    /**
     * Module initialization
     */
    async init() {
        console.log(`[${this.name}] Initializing...`);
        
        try {
            await this.load();
            this.bindEvents();
            this.render();
        } catch (error) {
            console.error(`[${this.name}] Init failed:`, error);
            this.setState({ error: error.message });
        }
    }
    
    /**
     * Load data from API
     */
    async load() {
        this.setState({ loading: true });
        
        try {
            const response = await API.get('/api/endpoint');
            this.setState({ 
                data: response.data,
                loading: false 
            });
            
            EventBus.emit('module-name:loaded', response.data);
        } catch (error) {
            this.setState({ 
                error: error.message,
                loading: false 
            });
            UI.error('Failed to load data');
        }
    }
    
    /**
     * Save data to API
     */
    async save() {
        const data = this.getState('data');
        
        try {
            await API.post('/api/endpoint', { data });
            UI.success('Saved successfully');
            EventBus.emit('module-name:saved', data);
        } catch (error) {
            UI.error('Failed to save');
            console.error(`[${this.name}] Save failed:`, error);
        }
    }
    
    /**
     * Bind DOM events
     */
    bindEvents() {
        const container = this.container;
        if (!container) return;
        
        // Save button
        container.querySelector('[data-action="save"]')
            ?.addEventListener('click', this.save);
        
        // Other events...
    }
    
    /**
     * Render UI
     */
    render() {
        const container = this.container;
        if (!container) return;
        
        const data = this.getState('data');
        const loading = this.getState('loading');
        
        // Update UI based on state
        container.classList.toggle('loading', loading);
        
        // Render data...
    }
    
    /**
     * Cleanup
     */
    destroy() {
        console.log(`[${this.name}] Destroying...`);
        // Cleanup event listeners, timers, etc.
        super.destroy();
    }
}

export default ModuleNameConfig;
```

---

## Common Patterns

### 1. Form Validation

```javascript
// Using FormValidator utility
import FormValidator from '../utilities/form-validator.js';

const validator = new FormValidator({
    username: {
        required: true,
        minLength: 3,
        maxLength: 32,
        pattern: /^[a-zA-Z0-9_]+$/,
        message: 'Username: 3-32 chars, alphanumeric + underscore'
    },
    email: {
        required: true,
        type: 'email',
        message: 'Enter a valid email address'
    }
});

// Validate form
const errors = validator.validate({
    username: 'john_doe',
    email: 'john@example.com'
});

if (errors.length === 0) {
    // Form is valid
    await this.save();
} else {
    // Show errors
    errors.forEach(error => {
        UI.error(error.message);
    });
}
```

### 2. Table Management

```javascript
// Using TableManager utility
import TableManager from '../utilities/table-manager.js';

const table = new TableManager('#users-table', {
    columns: [
        { key: 'username', label: 'Username', sortable: true },
        { key: 'role', label: 'Role', sortable: true },
        { key: 'actions', label: 'Actions', render: this.renderActions }
    ],
    searchable: true,
    selectable: true,
    onRowClick: this.onRowClick.bind(this),
    onRowDelete: this.onRowDelete.bind(this)
});

// Update table data
table.setData(users);

// Get selected rows
const selected = table.getSelected();
```

### 3. Real-time Updates

```javascript
// EventBus pattern for cross-module updates
EventBus.on('users:updated', (users) => {
    this.setState({ users });
    this.renderTable();
});

// Emit events when data changes
EventBus.emit('users:updated', newUsers);
```

### 4. Loading States

```javascript
async performAction() {
    // Set loading state
    this.setState({ loading: true });
    this.container?.classList.add('loading');
    
    try {
        const result = await API.post('/api/action');
        
        // Success
        this.setState({ loading: false });
        this.container?.classList.remove('loading');
        UI.success('Action completed');
        
        return result;
    } catch (error) {
        // Error
        this.setState({ 
            loading: false,
            error: error.message 
        });
        this.container?.classList.remove('loading');
        UI.error('Action failed');
        
        throw error;
    }
}
```

### 5. Debounced Search

```javascript
import { debounce } from '../utilities/helpers.js';

constructor() {
    super('module-name');
    
    // Debounced search (300ms delay)
    this.search = debounce(this.performSearch.bind(this), 300);
}

performSearch(query) {
    const data = this.getState('data');
    const filtered = data.filter(item => 
        item.name.toLowerCase().includes(query.toLowerCase())
    );
    
    this.setState({ filtered });
    this.render();
}

bindEvents() {
    // Search input
    this.container.querySelector('#search')
        ?.addEventListener('input', (e) => {
            this.search(e.target.value);
        });
}
```

---

## API Endpoint Reference

### Existing Endpoints

```javascript
// Features
GET  /api/organizer/config        // Load organizer config
POST /api/update                  // Save organizer config

// Users & Roles
GET    /api/dashboard/config      // Load users, roles, layout
POST   /api/dashboard/users       // Create/update user
DELETE /api/dashboard/users/:id   // Delete user
POST   /api/dashboard/layout      // Save layout

// Service
GET  /api/service/installation-config  // Get service config
POST /api/service/install              // Install service
POST /api/service/reinstall            // Reinstall service
POST /api/service/uninstall            // Uninstall service

// Branding
GET  /api/dashboard/branding      // Load branding
POST /api/dashboard/branding      // Save branding

// Logs
GET  /stream/stdout               // SSE stdout stream
GET  /stream/stderr               // SSE stderr stream
POST /clear-log                   // Clear logs
```

### New Endpoints (To Be Created)

```javascript
// Network Targets
POST /api/test-nas                // Test NAS connection
// Body: { name, path, credential_key }
// Response: { success, message, latency_ms, readable, writable }

// SMTP
POST /api/test-smtp               // Send test email
// Body: { host, port, from, to, user, pass, tls }
// Response: { success, message, smtp_response }

// Watched Folders
POST /api/test-folder             // Test folder access
// Body: { path }
// Response: { success, exists, readable, writable, resolved_path }

GET /api/config/actions           // Get audit log
// Response: { actions: [{ timestamp, user, action, details }] }

// Logs
GET /api/logs/download            // Download logs as file
// Response: file attachment
```

---

## State Management

### Store Pattern

```javascript
// Get state
const users = this.getState('users');
const loading = this.getState('loading');

// Set state (triggers reactivity)
this.setState({ 
    users: newUsers,
    loading: false 
});

// Watch state changes
Store.watch('users', (newUsers, oldUsers) => {
    console.log('Users changed:', newUsers);
    this.renderTable();
});
```

### EventBus Pattern

```javascript
// Subscribe to events
EventBus.on('users:updated', this.onUsersUpdated.bind(this));
EventBus.on('config:saved', this.onConfigSaved.bind(this));

// Emit events
EventBus.emit('users:updated', users);
EventBus.emit('config:saved', config);

// One-time listener
EventBus.once('module:init', () => {
    console.log('Module initialized');
});

// Unsubscribe
EventBus.off('users:updated', handler);
```

---

## UI Components

### Notification System

```javascript
// Success notification
UI.success('Configuration saved');

// Error notification
UI.error('Failed to save configuration');

// Warning notification
UI.warning('Some fields are missing');

// Info notification
UI.info('Loading data...');

// Custom notification
UI.notify({
    message: 'Custom message',
    type: 'success',
    duration: 5000,
    dismissible: true
});
```

### Confirmation Dialogs

```javascript
// Simple confirm
const confirmed = await UI.confirm('Delete this user?');
if (confirmed) {
    await this.deleteUser(userId);
}

// Custom confirm
const confirmed = await UI.confirm({
    title: 'Delete User',
    message: 'Are you sure you want to delete this user? This cannot be undone.',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
});
```

### Loading Indicators

```javascript
// Show loading
UI.showLoading('Saving configuration...');

// Hide loading
UI.hideLoading();

// Async wrapper
await UI.withLoading('Saving...', async () => {
    await this.save();
});
```

---

## Testing

### Unit Test Template

```javascript
// tests/modules/module-name-config.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest';
import ModuleNameConfig from '@/modules/module-name-config';
import API from '@/api';

// Mock API
vi.mock('@/api', () => ({
    default: {
        get: vi.fn(),
        post: vi.fn()
    }
}));

describe('ModuleNameConfig', () => {
    let module;
    
    beforeEach(() => {
        module = new ModuleNameConfig();
    });
    
    it('should initialize with default state', () => {
        expect(module.getState('data')).toEqual([]);
        expect(module.getState('loading')).toBe(false);
    });
    
    it('should load data from API', async () => {
        const mockData = [{ id: 1, name: 'Test' }];
        API.get.mockResolvedValue({ data: mockData });
        
        await module.load();
        
        expect(module.getState('data')).toEqual(mockData);
        expect(API.get).toHaveBeenCalledWith('/api/endpoint');
    });
    
    it('should handle API errors', async () => {
        API.get.mockRejectedValue(new Error('Network error'));
        
        await module.load();
        
        expect(module.getState('error')).toBe('Network error');
        expect(module.getState('loading')).toBe(false);
    });
});
```

### E2E Test Template

```javascript
// tests/e2e/module-name.spec.js
import { test, expect } from '@playwright/test';

test.describe('Module Name Config', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/config');
    });
    
    test('should display module', async ({ page }) => {
        const module = page.locator('[data-module="module-name"]');
        await expect(module).toBeVisible();
    });
    
    test('should save configuration', async ({ page }) => {
        // Fill form
        await page.fill('#input-field', 'test value');
        
        // Click save
        await page.click('button:has-text("Save")');
        
        // Assert success
        await expect(page.locator('text=Saved successfully')).toBeVisible();
    });
});
```

---

## Troubleshooting

### Common Issues

**1. Module Not Loading**
```javascript
// Check module registration
console.log(ModuleSystem.getModule('module-name'));

// Check container exists
const container = document.querySelector('[data-module="module-name"]');
console.log('Container:', container);

// Check for JavaScript errors
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});
```

**2. State Not Updating**
```javascript
// Verify setState is called
this.setState({ data: newData });
console.log('New state:', this.getState('data'));

// Check Store watchers
Store.watch('data', (newVal) => {
    console.log('State changed:', newVal);
});
```

**3. Events Not Firing**
```javascript
// Verify event emission
EventBus.emit('test:event', { data: 'test' });

// Check listeners
EventBus.on('test:event', (data) => {
    console.log('Event received:', data);
});

// List all listeners
console.log('EventBus listeners:', EventBus._listeners);
```

**4. API Calls Failing**
```javascript
// Check auth headers
console.log('Auth headers:', API.getHeaders());

// Verify endpoint
console.log('API base URL:', API.baseURL);

// Check response
try {
    const response = await API.get('/api/endpoint');
    console.log('Response:', response);
} catch (error) {
    console.error('API error:', error);
    console.error('Status:', error.status);
    console.error('Response:', error.response);
}
```

---

## Performance Tips

### 1. Debounce Search
```javascript
// Use debounce for search inputs
this.search = debounce(this.performSearch, 300);
```

### 2. Virtual Scrolling
```javascript
// For large tables (1000+ rows)
import VirtualScroll from '../utilities/virtual-scroll.js';

const virtualScroll = new VirtualScroll({
    container: '#table-container',
    rowHeight: 40,
    data: largeDataset,
    renderRow: this.renderRow.bind(this)
});
```

### 3. Lazy Loading
```javascript
// Load data only when module is visible
async init() {
    if (this.isVisible()) {
        await this.load();
    } else {
        // Load when scrolled into view
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                this.load();
                observer.disconnect();
            }
        });
        observer.observe(this.container);
    }
}
```

### 4. Memoization
```javascript
// Cache expensive computations
import { memoize } from '../utilities/helpers.js';

this.filterUsers = memoize((users, query) => {
    return users.filter(u => 
        u.username.toLowerCase().includes(query.toLowerCase())
    );
});
```

---

## Quick Commands

**Start Dashboard:**
```bash
cd /workspaces/DownloadsOrganizeR
source venv/bin/activate
python SortNStoreDashboard.py
```

**Run Tests:**
```bash
npm test                    # All tests
npm test -- users-roles     # Specific module
npm run test:e2e           # E2E tests only
npm run test:coverage      # With coverage
```

**Lint Code:**
```bash
npm run lint               # Check all files
npm run lint:fix           # Auto-fix issues
```

**Build for Production:**
```bash
npm run build              # Minify/bundle
```

---

## Related Documentation

- **[CONFIG_MODULES_ARCHITECTURE.md](./CONFIG_MODULES_ARCHITECTURE.md)** - Complete architecture
- **[JAVASCRIPT_MODULARIZATION.md](./JAVASCRIPT_MODULARIZATION.md)** - Core patterns
- **[DEBUGGING_SUITE_MODERNIZATION.md](./DEBUGGING_SUITE_MODERNIZATION.md)** - Debug tools
- **[AUTHENTICATION.md](./AUTHENTICATION.md)** - Auth system

---

**Last Updated:** December 5, 2025  
**Maintainer:** Development Team  
**Status:** Living Document
