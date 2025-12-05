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

## Phase 2: Charts ✅ COMPLETE

### What Was Migrated
All statistics charts across dashboard and full view page

### Charts Converted (5 total)
1. **Files by Category** - Donut chart with center total
2. **Top 10 Extensions** - Bar chart with data labels
3. **Activity Timeline** - Area chart with gradient and zoom
4. **Hourly Activity** - Column chart with rounded bars  
5. **Sidebar Mini Stats** - Compact donut chart

### Before (Chart.js)
```javascript
if (chartCategory) chartCategory.destroy();
chartCategory = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: categoryData.labels || [],
        datasets: [{
            data: categoryData.data || [],
            backgroundColor: ['#0d6efd', '#6610f2', /*...*/]
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { position: 'right' } }
    }
});
```

### After (ApexCharts)
```javascript
if (chartCategory) chartCategory.destroy();
chartCategory = new ApexCharts(container, {
    chart: { 
        type: 'donut', 
        height: 300, 
        animations: { enabled: true, easing: 'easeinout', speed: 800 } 
    },
    series: categoryData.data || [],
    labels: categoryData.labels || [],
    colors: ['#0d6efd', '#6610f2', /*...*/],
    legend: { position: 'right' },
    dataLabels: { 
        enabled: true, 
        formatter: (val) => Math.round(val) + '%' 
    },
    plotOptions: {
        pie: {
            donut: {
                size: '65%',
                labels: {
                    show: true,
                    total: { show: true, label: 'Total Files' }
                }
            }
        }
    },
    tooltip: { y: { formatter: (val) => val + ' files' } }
});
chartCategory.render();
```

### Benefits Achieved
- **Better animations**: Smooth 800ms easing transitions
- **Interactive features**: 
  - Zoom/pan on timeline (mouse wheel + drag)
  - Click legend to hide/show series
  - Download charts as PNG/SVG
  - Hover tooltips with formatted values
- **Visual improvements**:
  - Gradient fills on area charts
  - Rounded corners on bars
  - Data labels showing percentages
  - Center totals in donut charts
- **Responsive**: Auto-adjusts to container size
- **Touch-friendly**: Mobile gesture support

### Files Modified
- `dash/modules/statistics.html`: Replaced canvas with divs
- `dash/dashboard.html`: Sidebar chart migrated
- `dash/statistics_full.html`: Complete page migration + CDN update
- `dash/dashboard_scripts.html`: Rewrote loadStatistics() and updateSidebarStats()

### Commit
`9a5c99f` - "Migrate statistics charts from Chart.js to ApexCharts"

---

## Phase 2: Charts ✅ COMPLETE

### Target
All statistics charts in dashboard and full view

### Previous State
- Chart.js 4.4.0 for doughnut, bar, and line charts
- Manual chart creation with destroy/recreate pattern
- Limited interactivity

### Completed Changes
- ✅ Replaced with ApexCharts 3.45.1
- ✅ Category chart: Donut with center total display
- ✅ Extensions chart: Bar with data labels and download toolbar
- ✅ Timeline chart: Area with gradient fill, zoom/pan enabled
- ✅ Hourly chart: Column bars with rounded corners
- ✅ Sidebar chart: Mini donut optimized for compact display
- ✅ Smooth animations (800ms easing)
- ✅ Interactive tooltips with formatted values

### Actual Impact
- Chart code: Cleaner API, ~15% reduction in configuration code
- Better user experience with zoom/pan on timeline
- Interactive legends with click-to-hide
- Download chart as PNG/SVG
- Gradient fills and modern aesthetics

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

### Charts (Phase 2) ✅
- [x] ApexCharts loads successfully
- [x] Category donut chart renders with live data
- [x] Extensions bar chart renders with live data
- [x] Timeline area chart renders with live data
- [x] Hourly column chart renders with live data
- [x] Sidebar mini stats chart renders
- [x] Zoom/pan interactions work on timeline
- [x] Chart.js marked as deprecated (will remove after Phase 3)

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
- **After Phase 2**: ~3890 lines (2.75% reduction total)
- **Target after Phase 3**: ~3600 lines (10% total reduction)

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
2. `git revert 9a5c99f` for Phase 2  
3. Chart.js still available as fallback
4. Test each phase independently before proceeding

---

## References
- [htmx Documentation](https://htmx.org/docs/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [ApexCharts Documentation](https://apexcharts.com/docs/)
- [FRAMEWORK_MIGRATION.md](./FRAMEWORK_MIGRATION.md) - Comprehensive migration guide
