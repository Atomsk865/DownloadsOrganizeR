# htmx Migration Progress Tracker

## Overview
Progressive migration from vanilla JavaScript to modern frameworks (htmx, Alpine.js, ApexCharts) while maintaining Flask server-rendering architecture.

## Phase 1: Service Controls ✅ COMPLETE

### What Was Migrated
Service control buttons (Start/Stop/Restart) in dashboard sidebar

### Before (60+ lines)
```javascript
async function startService() {
    await serviceAction('start');
}

async function stopService() {
    await serviceAction('stop');
}

async function restartService() {
    await serviceAction('restart');
}

async function serviceAction(action) {
    try {
        if (!__authHeader) {
            showNotification('Please login...', 'warning');
            return;
        }
        const response = await fetch(`/${action}`, {
            method: 'POST',
            credentials: 'include',
            headers: getAuthHeaders()
        });
        const data = await response.json();
        if (response.ok) {
            const pastTense = {...}[action];
            showNotification(`Service ${pastTense} successfully`, 'success');
            setTimeout(updateServiceStatus, 1000);
        } else {
            showNotification(data.message || `Failed to ${action}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

async function updateServiceStatus() {
    try {
        const response = await fetch('/metrics');
        const data = await response.json();
        const badge = document.getElementById('service-badge');
        const badgeSidebar = document.getElementById('service-badge-sidebar');
        // ...update logic
    } catch (error) {
        console.error('Error updating service status:', error);
    }
}
```

### After (HTML attributes only)
```html
<button id="btn-start-service" class="btn btn-success btn-sm"
        hx-post="/start"
        hx-trigger="click"
        hx-swap="none"
        hx-on::after-request="if(event.detail.successful){setTimeout(()=>htmx.trigger('#service-badge-sidebar','refresh-status'),1000)}">
    <span class="htmx-indicator"><i class="bi bi-arrow-clockwise spinner"></i></span>
    Start
</button>
```

Status badge with refresh trigger:
```html
<span id="service-badge-sidebar" class="badge bg-success ms-1"
      hx-get="/metrics"
      hx-trigger="refresh-status from:body"
      hx-swap="none"
      hx-on::after-request="
        const data = JSON.parse(event.detail.xhr.response);
        const badge = document.getElementById('service-badge-sidebar');
        const mainBadge = document.getElementById('service-badge');
        const statusClass = data.service_status === 'Running' ? 'bg-success' : 'bg-danger';
        if(badge){badge.textContent=data.service_status;badge.className='badge '+statusClass+' ms-1';badge.style.fontSize='0.7rem';}
        if(mainBadge){mainBadge.textContent=data.service_status;mainBadge.className='badge '+statusClass+' ms-1';}
      ">
    {{ service_status }}
</span>
```

### Benefits Achieved
- **Code reduction**: ~90% (60 lines → 6 attributes)
- **Loading states**: Built-in spinner animation with htmx-indicator
- **Error handling**: Automatic via global htmx:responseError handler
- **Success notifications**: Automatic via global htmx:afterRequest handler
- **Status refresh**: Event-driven via htmx.trigger()
- **Auth headers**: Automatic via htmx:configRequest handler
- **No click handlers**: Declarative HTML attributes only

### Files Modified
- `dash/dashboard.html`: Added htmx attributes, spinner CSS animation
- `dash/dashboard_scripts.html`: Removed service control functions, added htmx notification handlers

### Commit
`3124944` - "Migrate service control buttons to htmx"

---

## Phase 2: Charts (Next Up)

### Target
CPU and Memory charts in Resource Monitor module

### Current State
- Chart.js 4.4.0 for line charts
- Manual data updates via setInterval

### Planned Changes
- Replace with ApexCharts 3.45.1
- Use htmx polling for data updates (`hx-get="/metrics" hx-trigger="every 3s"`)
- Better animations, zoom/pan, interactive legends

### Estimated Impact
- Chart code reduction: ~40%
- Better user experience with smoother animations
- Interactive tooltips and legends

---

## Phase 3: Module Toggles

### Target
Show/hide module functionality across all dashboard modules

### Current State
- Manual DOM manipulation with classList.toggle
- Click handlers in JavaScript

### Planned Changes
- Alpine.js `x-data="{ open: true }"` on cards
- `@click="open = !open"` on headers
- `x-show="open"` on bodies

### Estimated Impact
- Toggle code reduction: ~70%
- Declarative UI state management
- Automatic reactivity

---

## Testing Checklist

### Service Controls (Phase 1) ✅
- [x] Start button shows spinner during request
- [x] Stop button shows spinner during request
- [x] Restart button shows spinner during request
- [x] Success notification appears on successful action
- [x] Error notification appears on failed action
- [x] Status badge updates after action (both sidebar and main)
- [x] Auth headers attached to requests automatically
- [x] No JavaScript console errors

### Charts (Phase 2) ⏳
- [ ] ApexCharts loads successfully
- [ ] CPU chart renders with live data
- [ ] Memory chart renders with live data
- [ ] htmx polling updates charts every 3s
- [ ] Zoom/pan interactions work
- [ ] Chart.js removed after migration

### Module Toggles (Phase 3) ⏳
- [ ] Alpine.js initializes successfully
- [ ] Module headers toggle body visibility
- [ ] State persists during session
- [ ] No conflicts with GridStack drag-drop

---

## Performance Metrics

### JavaScript Bundle Size
- **Before migration**: ~4000 lines vanilla JS
- **After Phase 1**: ~3940 lines (1.5% reduction)
- **Target after Phase 2**: ~3550 lines (11% reduction)
- **Target after Phase 3**: ~3200 lines (20% total reduction)

### Framework Overhead
- htmx: 14KB (gzipped)
- Alpine.js: 15KB (gzipped)
- ApexCharts: 144KB (gzipped)
- **Total added**: 173KB
- **Total removed** (estimated after all phases): ~800 lines = ~60KB

### Net Impact
- Cleaner, more maintainable code
- Better error handling and loading states
- Enhanced user experience (animations, interactivity)
- Faster development for new features

---

## Rollback Plan

If issues arise, rollback is straightforward:
1. `git revert 3124944` for Phase 1
2. Keep Chart.js alongside ApexCharts during Phase 2 transition
3. Test each phase independently before proceeding

---

## References
- [htmx Documentation](https://htmx.org/docs/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [ApexCharts Documentation](https://apexcharts.com/docs/)
- [FRAMEWORK_MIGRATION.md](./FRAMEWORK_MIGRATION.md) - Comprehensive migration guide
