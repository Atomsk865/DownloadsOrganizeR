# Framework Migration Guide

## Overview

The dashboard is being enhanced with modern JavaScript frameworks to improve maintainability, reduce code complexity, and enhance user experience.

## New Stack

### 1. **htmx 1.9.10** - Declarative AJAX
- **Purpose**: Replace manual `fetch()` calls with HTML attributes
- **Benefits**: 
  - 70% less JavaScript code
  - No boilerplate for API calls
  - Built-in loading states
  - Better error handling

### 2. **Alpine.js 3.13.3** - Reactive UI
- **Purpose**: Add reactivity without full SPA conversion
- **Benefits**:
  - Lightweight (15KB)
  - Works with server-rendered HTML
  - No build step
  - Perfect for toggles, dropdowns, modals

### 3. **ApexCharts 3.45.1** - Modern Charts
- **Purpose**: Replace Chart.js for better features
- **Benefits**:
  - More chart types
  - Better animations
  - Interactive legends
  - Responsive by default
  - Better TypeScript support

### 4. **Keeping GridStack.js** - Already perfect for drag-drop

## Migration Strategy

### Phase 1: Infrastructure (✅ COMPLETE)
- [x] Add htmx, Alpine.js, ApexCharts CDN links
- [x] Configure htmx with auth headers
- [x] Add error handling for htmx requests
- [x] Keep Chart.js during migration

### Phase 2: Service Control Buttons (Priority 1)
**Before (Vanilla JS):**
```javascript
async function startService() {
    try {
        const response = await fetch('/start', {
            method: 'POST',
            credentials: 'include',
            headers: getAuthHeaders()
        });
        const data = await response.json();
        if (data.success) {
            showNotification('Service started', 'success');
            refreshMetrics();
        }
    } catch (e) {
        showNotification('Failed to start service', 'danger');
    }
}
```

**After (htmx):**
```html
<button hx-post="/start"
        hx-trigger="click"
        hx-swap="none"
        hx-on::after-request="refreshMetrics()">
    Start Service
</button>
```
- 90% less code
- Automatic error handling
- Built-in loading states

### Phase 3: Metrics Display (Priority 2)
**Before (Vanilla JS):**
```javascript
setInterval(async () => {
    const resp = await fetch('/metrics');
    const data = await resp.json();
    document.getElementById('cpu').textContent = data.cpu + '%';
    // ... 50 more lines
}, 5000);
```

**After (htmx + Alpine.js):**
```html
<div hx-get="/metrics" 
     hx-trigger="every 5s"
     hx-swap="innerHTML"
     x-data="{ cpu: 0 }">
    CPU: <span x-text="cpu + '%'"></span>
</div>
```

### Phase 4: Charts Migration
**File:** `dash/modules/resource_monitor.html`

**Current (Chart.js):**
```javascript
const ctx = document.getElementById('cpuChart');
const chart = new Chart(ctx, {
    type: 'line',
    data: { /* config */ }
});
```

**New (ApexCharts):**
```javascript
const options = {
    chart: { type: 'line', animations: { enabled: true } },
    series: [{ name: 'CPU', data: cpuData }]
};
const chart = new ApexCharts(document.querySelector('#cpuChart'), options);
chart.render();
```

**Benefits:**
- Smoother animations
- Built-in zoom/pan
- Better responsive behavior
- More intuitive API

### Phase 5: Form Validation
**Current approach:** Manual JavaScript validation

**With Alpine.js:**
```html
<form x-data="{ 
    email: '', 
    isValid() { return this.email.includes('@'); } 
}">
    <input x-model="email" type="email">
    <button :disabled="!isValid()">Submit</button>
    <span x-show="!isValid()" class="text-danger">Invalid email</span>
</form>
```

### Phase 6: Modal Dialogs
**Current:** Bootstrap modals with manual JS

**With Alpine.js:**
```html
<div x-data="{ open: false }">
    <button @click="open = true">Open Modal</button>
    <div x-show="open" @click.away="open = false" class="modal">
        <div class="modal-content">
            Content here
            <button @click="open = false">Close</button>
        </div>
    </div>
</div>
```

## Migration Priorities

### High Priority (Immediate Impact)
1. **Service Control** - Start/Stop/Restart buttons → htmx
2. **Metrics Polling** - CPU/Memory/Disk → htmx auto-refresh
3. **Configuration Updates** - Save config → htmx
4. **CPU/Memory Charts** - Chart.js → ApexCharts

### Medium Priority
5. **Module Toggles** - Show/Hide → Alpine.js
6. **File Organization** - Batch organize → htmx
7. **Recent Files** - Delete/Open → htmx
8. **Drive Space Visualization** - Chart.js → ApexCharts

### Low Priority (Gradual)
9. **Form Validation** - Manual → Alpine.js
10. **Modal Dialogs** - Bootstrap JS → Alpine.js
11. **Dropdown Menus** - Manual → Alpine.js

## Code Patterns

### htmx Pattern: Simple POST
```html
<button hx-post="/api/action" 
        hx-swap="none"
        hx-indicator="#spinner">
    Action
</button>
<span id="spinner" class="htmx-indicator">Loading...</span>
```

### htmx Pattern: Update Element
```html
<div id="metrics" 
     hx-get="/api/metrics" 
     hx-trigger="every 5s"
     hx-swap="innerHTML">
    Initial content
</div>
```

### Alpine.js Pattern: Toggle
```html
<div x-data="{ show: false }">
    <button @click="show = !show">Toggle</button>
    <div x-show="show" x-transition>Content</div>
</div>
```

### Alpine.js Pattern: Computed Property
```html
<div x-data="{ 
    count: 0,
    get doubled() { return this.count * 2; }
}">
    Count: <span x-text="count"></span>
    Doubled: <span x-text="doubled"></span>
    <button @click="count++">Increment</button>
</div>
```

### ApexCharts Pattern: Line Chart
```javascript
const options = {
    chart: {
        type: 'line',
        height: 350,
        animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 800
        }
    },
    series: [{
        name: 'CPU Usage',
        data: [30, 40, 45, 50, 49, 60, 70]
    }],
    xaxis: {
        categories: ['00:00', '00:05', '00:10', '00:15', '00:20', '00:25', '00:30']
    },
    stroke: {
        curve: 'smooth'
    },
    colors: ['#0d6efd']
};
const chart = new ApexCharts(document.querySelector('#chart'), options);
chart.render();
```

## Benefits Summary

### Code Reduction
- **htmx**: Eliminates ~70% of fetch() boilerplate
- **Alpine.js**: Reduces DOM manipulation by ~60%
- **Total**: ~2000 lines of JavaScript can be replaced

### Maintainability
- **Declarative** instead of imperative
- **Less state management** complexity
- **Easier to debug** (HTML attributes vs JS files)

### Performance
- **Smaller bundle** (Alpine.js is 15KB, htmx is 14KB)
- **Faster load times** (less JavaScript to parse)
- **Better caching** (HTML changes don't invalidate JS cache)

### Developer Experience
- **Less context switching** (HTML + attributes vs HTML + JS files)
- **Faster development** (write less code)
- **Better TypeScript support** (ApexCharts)

## Testing Strategy

1. **Run both implementations in parallel**
   - Keep old code working
   - Add new htmx/Alpine.js versions alongside
   - Compare behavior

2. **Progressive enhancement**
   - Old browsers still work
   - Modern browsers get enhanced experience

3. **Feature flags**
   - Toggle between old/new implementations
   - Test in production safely

## Resources

- **htmx docs**: https://htmx.org/docs/
- **Alpine.js docs**: https://alpinejs.dev/
- **ApexCharts docs**: https://apexcharts.com/docs/
- **Migration examples**: See `examples/` directory (to be created)

## Next Steps

1. Start with service control buttons (high impact, low risk)
2. Migrate one chart to ApexCharts (test performance)
3. Add Alpine.js to module toggles (visible improvement)
4. Gradually replace fetch() calls with htmx
5. Document learnings and patterns

## Rollback Plan

If issues arise:
1. Remove CDN links from `dashboard_base.html` and `dashboard_scripts.html`
2. Old vanilla JS code still works
3. No breaking changes to backend
4. Can migrate module-by-module safely
