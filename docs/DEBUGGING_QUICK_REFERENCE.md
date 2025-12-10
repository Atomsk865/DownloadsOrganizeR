# Debugging Suite Quick Reference

## Quick Access

**Debug Page URL**: `/env-test` (requires authentication)

**Developer Mode Toggle**: `/config` → Features → Developer Mode

## Console Quick Commands

### Access Modules
```javascript
// Get debug suite
const debugSuite = ModuleSystem.get('debug-suite');

// Get developer mode
const devMode = ModuleSystem.get('developer-mode');

// Get debug utilities
const debugUtils = ModuleSystem.get('debug-utils');
```

### Run Tests
```javascript
// Run all API endpoint tests
await debugSuite.runAllTests();

// Run pytest suite
await debugSuite.runPytests();

// Run smart self-test
await debugSuite.runSmartSelfTest();

// Clear test log
debugSuite.clearLog();
```

### Developer Mode
```javascript
// Toggle developer mode
await devMode.toggle();

// Enable developer mode
await devMode.enable();

// Disable developer mode
await devMode.disable();

// Check if enabled
devMode.isEnabled(); // true/false
```

### Logging
```javascript
// Enable logging with level
debugUtils.enableLogging('debug'); // levels: debug, info, warn, error

// Log messages
debugUtils.debug('Debug message', { data: 'optional' });
debugUtils.info('Info message');
debugUtils.warn('Warning message');
debugUtils.error('Error message');

// Get log buffer
debugUtils.getLogBuffer();

// Clear logs
debugUtils.clearLogBuffer();
```

### Network Monitoring
```javascript
// Enable network monitoring
debugUtils.enableNetworkMonitoring();

// Get network requests
const requests = debugUtils.getNetworkRequests();
console.table(requests);

// Disable monitoring
debugUtils.disableNetworkMonitoring();

// Clear requests
debugUtils.clearNetworkRequests();
```

### Performance Profiling
```javascript
// Mark performance points
debugUtils.mark('operation-start');
// ... do work ...
debugUtils.mark('operation-end');

// Measure between marks
debugUtils.measure('operation-time', 'operation-start', 'operation-end');

// Get all performance metrics
debugUtils.getPerformanceMetrics();
```

### State Inspection
```javascript
// Inspect Store state
debugUtils.inspectStore(); // Shows table in console

// Watch Store key
debugUtils.watchStore('userAuth', (value) => {
    console.log('Auth changed:', value);
});

// Inspect all modules
debugUtils.inspectModules();

// Inspect specific module
debugUtils.inspectModule('debug-suite');
```

### Error Tracking
```javascript
// Get tracked errors
const errors = debugUtils.getErrors();
console.table(errors);

// Clear error records
debugUtils.clearErrors();
```

### Export Debug Data
```javascript
// Download all debug data as JSON
debugUtils.downloadData();

// Or export to variable
const data = debugUtils.exportData();
console.log(data);
```

### Enable All Debug Tools
```javascript
// Enable everything at once
debugUtils.enable(); // Enables logging + network monitoring

// Disable everything
debugUtils.disable();
```

## Common Use Cases

### Debugging API Issues
```javascript
// Enable network monitoring
debugUtils.enableNetworkMonitoring();

// Make API calls (automatic tracking)
// ... use dashboard normally ...

// View all requests
const requests = debugUtils.getNetworkRequests();
console.table(requests);

// Filter failed requests
const failed = requests.filter(r => !r.success);
console.log('Failed requests:', failed);
```

### Tracking Performance
```javascript
// Mark page load start
debugUtils.mark('page-load-start');

// ... page loads ...

// Mark page load end
debugUtils.mark('page-load-end');

// Measure
const duration = debugUtils.measure('page-load', 'page-load-start', 'page-load-end');
console.log(`Page load took ${duration}ms`);

// Get all metrics
debugUtils.getPerformanceMetrics();
```

### Finding Errors
```javascript
// Get all errors
const errors = debugUtils.getErrors();

// Group by type
const byType = errors.reduce((acc, err) => {
    acc[err.type] = acc[err.type] || [];
    acc[err.type].push(err);
    return acc;
}, {});

console.log('Errors by type:', byType);
```

### Testing Dashboard Features
```javascript
// Run comprehensive test
await debugSuite.runSmartSelfTest();

// Check results
const results = debugSuite.getState('results');
console.log(`Passed: ${results.passed}/${results.total}`);

// Run specific API test
await debugSuite.runAllTests();
```

### Monitoring State Changes
```javascript
// Watch developer mode
debugUtils.watchStore('developerMode', (enabled) => {
    console.log('Developer mode:', enabled ? 'ON' : 'OFF');
});

// Watch any Store key
debugUtils.watchStore('authToken', (token) => {
    console.log('Auth token changed:', token ? 'logged in' : 'logged out');
});
```

## Keyboard Shortcuts (Future)

*Coming soon: Command palette integration*

- `Ctrl+Shift+D` - Toggle developer mode
- `Ctrl+Shift+T` - Run tests
- `Ctrl+Shift+L` - Toggle logging
- `Ctrl+Shift+N` - Toggle network monitoring
- `Ctrl+Shift+E` - Export debug data

## Tips & Tricks

### 1. Auto-enable on Load
Add to browser console snippets:
```javascript
// Enable all debug tools automatically
if (ModuleSystem.get('debug-utils')) {
    ModuleSystem.get('debug-utils').enable();
}
```

### 2. Custom Log Filters
```javascript
// Get only error logs
const errors = debugUtils.getLogBuffer().filter(log => log.level === 'error');
console.table(errors);
```

### 3. Network Performance Analysis
```javascript
// Get average request duration
const requests = debugUtils.getNetworkRequests();
const avg = requests.reduce((sum, r) => sum + r.duration, 0) / requests.length;
console.log(`Average request time: ${Math.round(avg)}ms`);

// Find slow requests
const slow = requests.filter(r => r.duration > 1000);
console.log('Slow requests (>1s):', slow);
```

### 4. Memory Leak Detection
```javascript
// Check memory periodically
setInterval(() => {
    const metrics = debugUtils.getPerformanceMetrics();
    if (metrics.memory) {
        console.log(`Memory usage: ${metrics.memory.usedJSHeapSize}MB / ${metrics.memory.limit}MB`);
    }
}, 5000);
```

### 5. Export Before Refresh
```javascript
// Save debug data before page refresh
window.addEventListener('beforeunload', () => {
    const debugUtils = ModuleSystem.get('debug-utils');
    if (debugUtils) {
        localStorage.setItem('debug-backup', JSON.stringify(debugUtils.exportData()));
    }
});
```

## Troubleshooting

### Module Not Found
```javascript
// Check if module is registered
console.log(ModuleSystem.getAll());

// Re-initialize if needed
await ModuleSystem.initAll();
```

### Tests Not Running
```javascript
// Check if debug suite is initialized
const debugSuite = ModuleSystem.get('debug-suite');
console.log('Initialized:', debugSuite.initialized);

// Re-init if needed
await debugSuite.init();
```

### Developer Mode Not Working
```javascript
// Check state
const devMode = ModuleSystem.get('developer-mode');
console.log('Enabled:', devMode.getState('enabled'));

// Check body class
console.log('Body class:', document.body.classList.contains('developer-mode'));

// Force enable
await devMode.enable();
```

## Links

- **Full Documentation**: `DEBUGGING_SUITE_MODERNIZATION.md`
- **Architecture Guide**: `MODULAR_ARCHITECTURE.md`
- **Quick Start**: `MODULAR_QUICKSTART.md`

