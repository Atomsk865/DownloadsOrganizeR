# Modular Architecture Documentation

## Overview

The new modular architecture provides a clean, scalable foundation for building dashboard features. It uses ES6 modules, event-driven architecture, and a core library of utilities.

## Core Components

### 1. Core Library (`core-library.js`)

Provides essential utilities for all modules:

- **Store** - State management with reactive updates
- **EventBus** - Event system for inter-module communication
- **API** - HTTP utilities with auth header support
- **UI** - Notification system
- **Theme** - Theme system integration
- **DOM** - DOM manipulation utilities
- **Utils** - Common utilities (debounce, throttle, formatting, etc.)

### 2. Module System (`module-system.js`)

- **ModuleSystem** - Module registry and lifecycle management
- **BaseModule** - Base class for all modules with common features
- **autoInitModules()** - Auto-initialization function

### 3. Core Styles (`core.css`)

Provides:
- CSS variables for theming
- Base styles for common components
- Utility classes
- Responsive design foundations

## Creating a Module

### Basic Module Structure

```javascript
import { BaseModule, ModuleSystem } from './module-system.js';
import { API, UI, Store } from './core-library.js';

export class MyModule extends BaseModule {
    constructor() {
        super('MyModule', {
            // Module options
            refreshInterval: 5000
        });
    }

    /**
     * Initialize module
     */
    async onInit() {
        // Mount to DOM
        if (!this.mount('#my-container')) return;

        // Load data
        await this.loadData();

        // Render UI
        this.render();
    }

    /**
     * Load data
     */
    async loadData() {
        try {
            const data = await API.get('/api/my-endpoint');
            this.setState('data', data);
        } catch (error) {
            this.error('Failed to load data');
        }
    }

    /**
     * Render UI
     */
    render() {
        if (!this.container) return;
        this.container.innerHTML = '<div>My Module Content</div>';
    }

    /**
     * Cleanup
     */
    async onDestroy() {
        // Cleanup resources
    }
}

// Register module
ModuleSystem.register('MyModule', {
    init: () => new MyModule().init(),
    dependencies: [] // List dependencies if needed
});
```

## Using the Core Library

### Store (State Management)

```javascript
import { Store } from './core-library.js';

// Set state
Store.set('key', value);

// Get state
const value = Store.get('key', defaultValue);

// Subscribe to changes
const unsubscribe = Store.subscribe('key', (newValue, oldValue) => {
    console.log('State changed:', newValue);
});
```

### EventBus (Inter-Module Communication)

```javascript
import { EventBus } from './core-library.js';

// Emit event
EventBus.emit('my-event', { data: 'value' });

// Listen to event
const unsubscribe = EventBus.on('my-event', (data) => {
    console.log('Event received:', data);
});

// Listen once
EventBus.once('my-event', (data) => {
    console.log('First occurrence:', data);
});
```

### API (HTTP Requests)

```javascript
import { API } from './core-library.js';

// GET request
const data = await API.get('/api/endpoint');

// POST request
const result = await API.post('/api/endpoint', { body: 'data' });

// PUT request
const updated = await API.put('/api/endpoint/1', { field: 'value' });

// DELETE request
await API.delete('/api/endpoint/1');

// Custom request
const response = await API.request('/api/endpoint', {
    method: 'GET',
    headers: { 'Custom-Header': 'value' }
});
```

### UI (Notifications)

```javascript
import { UI } from './core-library.js';

// Show notification
UI.notify('Message', 'info', 5000);

// Shorthand methods
UI.success('Operation successful');
UI.error('Operation failed');
UI.warning('Warning message');
UI.info('Information message');

// Show loading state on button
UI.setLoading(button, true);
UI.setLoading(button, false);

// Confirm dialog
if (await UI.confirm('Are you sure?')) {
    // User confirmed
}
```

### Theme (Theme System)

```javascript
import { Theme } from './core-library.js';

// Initialize theme system
await Theme.init();

// Toggle theme
Theme.toggle();

// Apply theme
Theme.apply('dark');

// Get current theme
const current = Theme.getCurrent();

// Get saved theme
const saved = Theme.getSaved();

// Apply custom theme
Theme.applyCustom({
    colors: { primary: '#0d6efd' }
});

// Reset theme
Theme.reset();
```

### DOM (DOM Utilities)

```javascript
import { DOM } from './core-library.js';

// Query
const element = DOM.query('.my-class');
const elements = DOM.queryAll('.my-class');

// Create element
const div = DOM.create('div', {
    className: 'my-class',
    id: 'my-id',
    html: '<p>Content</p>',
    text: 'Text content',
    attributes: { 'data-value': '123' },
    styles: { color: 'red' },
    parent: document.body
});

// Class manipulation
DOM.addClass(element, 'active');
DOM.removeClass(element, 'active');
DOM.toggleClass(element, 'active');
DOM.hasClass(element, 'active');

// Remove element
DOM.remove(element);
```

### Utils (Utilities)

```javascript
import { Utils } from './core-library.js';

// Debounce
const debouncedFunc = Utils.debounce(myFunc, 300);

// Throttle
const throttledFunc = Utils.throttle(myFunc, 300);

// Clone object
const copy = Utils.clone(originalObject);

// Merge objects
const merged = Utils.merge(obj1, obj2);

// Format file size
Utils.formatFileSize(1024); // "1 KB"

// Format date
Utils.formatDate(new Date(), 'YYYY-MM-DD HH:mm:ss');

// Wait for condition
await Utils.waitFor(() => someCondition, 5000);
```

### BaseModule (Module Base Class)

```javascript
export class MyModule extends BaseModule {
    constructor() {
        super('MyModule', { /* options */ });
    }

    async onInit() {
        // Initialize
    }

    // State management
    this.setState('key', value);
    const value = this.getState('key');
    const unsubscribe = this.onState('key', callback);

    // Events
    this.emit('event-name', data);
    this.on('event-name', callback);

    // Notifications
    this.success('Message');
    this.error('Error');
    this.warning('Warning');
    this.notify('Message', 'type', duration);
}
```

## Module Registration

```javascript
ModuleSystem.register('MyModule', {
    init: () => new MyModule().init(),
    destroy: () => myModuleInstance.destroy(),
    dependencies: ['DependencyModule'] // Optional
});
```

## Module Lifecycle

1. **Register** - `ModuleSystem.register()`
2. **Initialize** - `module.onInit()` called
3. **Ready** - Module emits `module:name:initialized` event
4. **Running** - Module functions
5. **Destroy** - `module.onDestroy()` called
6. **Cleanup** - Module emits `module:name:destroyed` event

## CSS Variables

Available theme CSS variables for styling:

```css
/* Colors */
--color-primary
--color-secondary
--color-success
--color-danger
--color-warning
--color-info

/* Backgrounds */
--bg-primary
--bg-secondary
--bg-tertiary

/* Text */
--text-primary
--text-secondary
--text-muted

/* Borders */
--border-color
--border-light
--border-radius

/* Shadows */
--shadow-sm
--shadow-md
--shadow-lg

/* Transitions */
--transition-fast
--transition-normal
--transition-slow

/* Spacing */
--spacing-xs
--spacing-sm
--spacing-md
--spacing-lg
--spacing-xl
--spacing-2xl
```

## Utility Classes

Common utility classes available:

```html
<!-- Layout -->
<div class="grid grid-cols-2"></div>
<div class="flex flex-center"></div>
<div class="gap-md"></div>

<!-- Text -->
<p class="text-center text-muted"></p>
<p class="text-primary text-secondary"></p>

<!-- Spacing -->
<div class="mt-2 mb-3 p-2"></div>

<!-- Styling -->
<div class="rounded shadow-md"></div>

<!-- Visibility -->
<div class="hidden"></div>
<div class="visible"></div>
```

## Best Practices

1. **Use BaseModule** - Extend BaseModule for consistent behavior
2. **Handle Errors** - Always use try/catch with API calls
3. **Clean Up** - Implement onDestroy for resource cleanup
4. **Notify Users** - Use UI notifications for feedback
5. **State Management** - Use Store for shared state
6. **Events** - Use EventBus for inter-module communication
7. **Lazy Load** - Only initialize modules when needed
8. **Responsive** - Use CSS variables for theme support

## Migration Guide

### From Old System to New

**Old:**
```javascript
function myFunction() {
    fetch('/api/endpoint').then(r => r.json()).then(data => {
        // handle data
    });
}
```

**New:**
```javascript
class MyModule extends BaseModule {
    async onInit() {
        const data = await API.get('/api/endpoint');
        // handle data
    }
}
```

## Example: Complete Dashboard Module

See `statistics-module.js` and `health-module.js` for complete examples.

## Troubleshooting

### Module not initializing
- Check if module is registered
- Verify dependencies are initialized first
- Check browser console for errors

### State not updating
- Use `Store.set()` instead of direct assignment
- Subscribe to changes with `Store.subscribe()`

### Events not firing
- Verify event name is correct
- Check module name prefix in event
- Use `EventBus.emit()` to dispatch

### Theme not applied
- Ensure `Theme.init()` is called first
- Check `data-theme` attribute on HTML element
- Verify CSS variables are defined
