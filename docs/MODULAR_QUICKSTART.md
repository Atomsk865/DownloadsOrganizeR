# Modular Architecture - Quick Start Guide

## Overview

The new modular architecture provides a clean, scalable way to build dashboard features with:
- ES6 modules
- Reactive state management
- Built-in theming
- Event-driven communication
- Consistent patterns

## Creating Your First Module (5 minutes)

### Step 1: Create Module File

Create `static/js/modules/my-feature-module.js`:

```javascript
import { BaseModule, ModuleSystem } from './module-system.js';
import { API, UI } from './core-library.js';

export class MyFeatureModule extends BaseModule {
    constructor() {
        super('MyFeature');
    }

    async onInit() {
        // Mount to DOM container
        if (!this.mount('#my-feature-container')) {
            return;
        }

        // Show loading state
        this.container.innerHTML = '<p>Loading...</p>';

        // Load data from API
        try {
            const data = await API.get('/api/my-feature');
            this.setState('data', data);
            this.render(data);
            this.success('Data loaded successfully');
        } catch (error) {
            this.error('Failed to load data');
            console.error(error);
        }
    }

    render(data) {
        this.container.innerHTML = `
            <div class="card">
                <div class="card-header">My Feature</div>
                <div class="card-body">
                    <p>${JSON.stringify(data)}</p>
                </div>
            </div>
        `;
    }

    async onDestroy() {
        // Cleanup resources if needed
    }
}

// Register module
ModuleSystem.register('MyFeature', {
    init: () => new MyFeatureModule().init()
});
```

### Step 2: Add Module to HTML

In your template (e.g., `dash/my-page.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/core.css') }}">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
    <style>
        body { font-family: inherit; }
    </style>
</head>
<body>
    <!-- Your module container -->
    <div id="my-feature-container"></div>

    <!-- Core scripts -->
    <script src="{{ url_for('static', filename='js/theme-system.js') }}" defer></script>
    
    <!-- Load modules -->
    <script type="module">
        import { ModuleSystem, autoInitModules } from '{{ url_for("static", filename="js/modules/module-system.js") }}';
        import './{{ url_for("static", filename="js/modules/my-feature-module.js") }}';
        
        // Auto-initialize all registered modules
        autoInitModules();
    </script>

    <!-- Notifications container -->
    <div id="notification-container"></div>
</body>
</html>
```

### Step 3: Test It

1. Restart the dashboard
2. Navigate to your page
3. Module automatically initializes and loads data
4. Notifications appear for success/error

## Common Tasks

### Show Notification

```javascript
// Quick methods
this.success('Operation successful');
this.error('Something went wrong');
this.warning('Be careful');
this.notify('Custom message', 'info', 3000);
```

### Manage State

```javascript
// Set and get state
this.setState('myKey', 'myValue');
const value = this.getState('myKey');

// Subscribe to changes
const unsubscribe = this.onState('myKey', (newVal, oldVal) => {
    console.log('State changed:', newVal);
});
```

### Emit Events

```javascript
// Emit event from this module
this.emit('my-event', { data: 'value' });

// Listen to events from other modules
this.on('other-module:event', (data) => {
    console.log('Event received:', data);
});
```

### Make API Calls

```javascript
import { API } from './core-library.js';

// Simple GET
const data = await API.get('/api/endpoint');

// POST with data
const result = await API.post('/api/endpoint', {
    name: 'John',
    email: 'john@example.com'
});

// PUT/DELETE
await API.put('/api/endpoint/1', { field: 'updated' });
await API.delete('/api/endpoint/1');
```

### DOM Manipulation

```javascript
import { DOM } from './core-library.js';

// Query
const element = DOM.query('.my-class');
const all = DOM.queryAll('.my-class');

// Create
const div = DOM.create('div', {
    className: 'my-class',
    text: 'Hello World',
    parent: document.body
});

// Modify
DOM.addClass(element, 'active');
DOM.toggleClass(element, 'highlight');
```

### Format Data

```javascript
import { Utils } from './core-library.js';

// File size
Utils.formatFileSize(1048576); // "1 MB"

// Date
Utils.formatDate(new Date(), 'YYYY-MM-DD HH:mm:ss');

// Debounce search input
const search = Utils.debounce(async (query) => {
    const results = await API.get(`/api/search?q=${query}`);
    this.render(results);
}, 300);
```

## Module Lifecycle

```
register() → init() → onInit() → [running] → destroy() → onDestroy() → cleanup
```

Key points:
- `onInit()` - Initialize your module, load data, render
- `onDestroy()` - Clean up resources (timers, listeners, etc.)
- `onState()` - React to state changes
- `on()` - Listen to events from other modules
- `emit()` - Send events to other modules

## CSS Classes & Variables

Use CSS variables for theming:

```css
/* Light mode (default) */
:root {
    --bg-primary: #f8f9fa;
    --text-primary: #212529;
    --color-primary: #0d6efd;
}

/* Dark mode (automatic) */
[data-theme="dark"] {
    --bg-primary: #1a1d23;
    --text-primary: #e9ecef;
    --color-primary: #0d6efd;
}
```

Use in your styles:

```css
.my-component {
    background: var(--bg-primary);
    color: var(--text-primary);
    border-color: var(--border-color);
}
```

Utility classes:

```html
<!-- Grid -->
<div class="grid grid-cols-3 gap-md"></div>

<!-- Flex -->
<div class="flex flex-between gap-sm"></div>

<!-- Spacing -->
<div class="mt-2 mb-3 p-2"></div>

<!-- Text -->
<p class="text-center text-muted"></p>

<!-- Buttons -->
<button class="btn btn-primary">Click me</button>
<button class="btn btn-secondary btn-sm">Small</button>

<!-- Cards -->
<div class="card shadow-md">
    <div class="card-header">Header</div>
    <div class="card-body">Content</div>
</div>
```

## Debugging

### Check if Module Initialized

Open browser console:

```javascript
ModuleSystem.isInitialized('MyFeature')
```

### View Module State

```javascript
Store.getAll()
```

### Listen to All Events

```javascript
const originalEmit = EventBus.emit;
EventBus.emit = function(event, data) {
    console.log('Event:', event, data);
    return originalEmit.call(this, event, data);
};
```

## Best Practices

1. ✅ Always handle errors in `try/catch`
2. ✅ Clean up resources in `onDestroy()`
3. ✅ Use `this.notify()` for user feedback
4. ✅ Subscribe to state for reactive updates
5. ✅ Use CSS variables for consistent theming
6. ✅ Document your module with JSDoc comments
7. ✅ Use TypeScript annotations if available
8. ✅ Keep modules focused and single-purpose

## Examples

See these files for complete working examples:
- `static/js/modules/statistics-module.js`
- `static/js/modules/health-module.js`
- `static/js/modules/config-app.js`

## Need Help?

See full documentation in:
- `MODULAR_ARCHITECTURE.md` - Complete reference
- `MODULAR_MIGRATION_COMPLETE.md` - Migration summary
