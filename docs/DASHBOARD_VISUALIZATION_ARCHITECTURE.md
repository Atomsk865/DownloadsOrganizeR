# Dashboard Visualization Architecture

**Version:** 1.0  
**Date:** December 5, 2025  
**Status:** Architecture Planning

---

## Executive Summary

Design and implement a modern, data visualization-inspired dashboard with draggable module containers, real-time previews, and persistent layouts. Inspired by analytics dashboards, this system provides:

- **Drag-and-drop module positioning** with visual previews
- **Grid-based layout system** with responsive breakpoints
- **Module library** with 15+ pre-built widgets
- **Live preview** showing drop zones and layout changes
- **Persistent layouts** saved per user
- **Export/Import** dashboard configurations
- **Fullscreen mode** for presentations

---

## Table of Contents

1. [Design Inspiration & UI Patterns](#design-inspiration--ui-patterns)
2. [Grid System Architecture](#grid-system-architecture)
3. [Module Library](#module-library)
4. [Drag & Drop Implementation](#drag--drop-implementation)
5. [Layout Persistence](#layout-persistence)
6. [Implementation Roadmap](#implementation-roadmap)

---

## Design Inspiration & UI Patterns

### Visual Style (Based on Attached Image)

**Color Palette:**
- **Dark Background:** `#0a1628` (base)
- **Card Background:** `#132337` (containers)
- **Accent Blue:** `#3b82f6` (primary actions)
- **Accent Cyan:** `#06b6d4` (data viz)
- **Accent Purple:** `#8b5cf6` (secondary)
- **Accent Yellow:** `#fbbf24` (warnings/highlights)
- **Text Primary:** `#f8fafc`
- **Text Secondary:** `#94a3b8`

**Typography:**
- **Headers:** Inter or Poppins (sans-serif, 600 weight)
- **Metrics:** Tabular numbers, 700 weight
- **Body:** System UI, 400 weight
- **Monospace:** Courier New for code/logs

**Layout Patterns:**
1. **Metric Cards** - Large numbers with sparklines
2. **Charts** - Bar, line, area, donut, scatter
3. **Maps** - Geographic/heat maps with overlays
4. **Tables** - Sortable data grids with inline actions
5. **Gauges** - Circular progress indicators
6. **Timelines** - Horizontal time-series data

---

## Grid System Architecture

### Grid Configuration

**File:** `static/js/modules/dashboard-grid.js`

```javascript
import BaseModule from '../base-module.js';
import EventBus from '../event-bus.js';
import Store from '../store.js';

class DashboardGrid extends BaseModule {
    constructor() {
        super('dashboard-grid');
        
        this.setState({
            layout: [],
            gridSize: { cols: 12, rows: 'auto' },
            cellSize: { width: 100, height: 80 },
            gap: 16,
            breakpoints: {
                xl: { minWidth: 1920, cols: 12 },
                lg: { minWidth: 1280, cols: 12 },
                md: { minWidth: 768, cols: 8 },
                sm: { minWidth: 640, cols: 4 },
                xs: { minWidth: 0, cols: 2 }
            },
            currentBreakpoint: 'xl',
            isDragging: false,
            draggedModule: null,
            dropPreview: null
        });
    }
    
    async init() {
        this.container = document.getElementById('dashboard-grid-container');
        
        // Load saved layout
        await this.loadLayout();
        
        // Setup responsive breakpoints
        this.setupBreakpoints();
        
        // Initialize drag and drop
        this.initDragDrop();
        
        // Render grid
        this.render();
        
        this.logger.success('Dashboard grid initialized');
    }
    
    async loadLayout() {
        try {
            const response = await API.get('/api/dashboard/layout');
            
            if (response.layout && response.layout.length > 0) {
                this.setState({ layout: response.layout });
            } else {
                // Load default layout
                this.setState({ layout: this.getDefaultLayout() });
            }
        } catch (error) {
            this.logger.error('Failed to load layout:', error);
            this.setState({ layout: this.getDefaultLayout() });
        }
    }
    
    getDefaultLayout() {
        return [
            // Top row - Metric cards
            { id: 'metric-files', x: 0, y: 0, w: 3, h: 2, module: 'MetricCard' },
            { id: 'metric-size', x: 3, y: 0, w: 3, h: 2, module: 'MetricCard' },
            { id: 'metric-duplicates', x: 6, y: 0, w: 3, h: 2, module: 'MetricCard' },
            { id: 'metric-recent', x: 9, y: 0, w: 3, h: 2, module: 'MetricCard' },
            
            // Second row - Charts
            { id: 'chart-activity', x: 0, y: 2, w: 6, h: 4, module: 'ActivityChart' },
            { id: 'chart-categories', x: 6, y: 2, w: 6, h: 4, module: 'CategoryChart' },
            
            // Third row - Mixed
            { id: 'recent-files', x: 0, y: 6, w: 8, h: 4, module: 'RecentFilesTable' },
            { id: 'system-health', x: 8, y: 6, w: 4, h: 4, module: 'SystemHealth' },
            
            // Fourth row - Full width
            { id: 'file-distribution', x: 0, y: 10, w: 12, h: 3, module: 'FileDistributionMap' }
        ];
    }
    
    setupBreakpoints() {
        const observer = new ResizeObserver(() => {
            const width = window.innerWidth;
            let newBreakpoint = 'xs';
            
            for (const [name, config] of Object.entries(this.getState('breakpoints'))) {
                if (width >= config.minWidth) {
                    newBreakpoint = name;
                }
            }
            
            if (newBreakpoint !== this.getState('currentBreakpoint')) {
                this.setState({ currentBreakpoint: newBreakpoint });
                this.adjustLayoutForBreakpoint(newBreakpoint);
            }
        });
        
        observer.observe(this.container);
    }
    
    adjustLayoutForBreakpoint(breakpoint) {
        const config = this.getState('breakpoints')[breakpoint];
        const currentLayout = this.getState('layout');
        
        // Adjust module widths to fit new column count
        const adjustedLayout = currentLayout.map(item => {
            const newW = Math.min(item.w, config.cols);
            const newX = Math.min(item.x, config.cols - newW);
            
            return { ...item, w: newW, x: newX };
        });
        
        this.setState({ layout: adjustedLayout });
        this.render();
    }
    
    render() {
        const layout = this.getState('layout');
        const { cols } = this.getState('gridSize');
        const { width: cellWidth, height: cellHeight } = this.getState('cellSize');
        const gap = this.getState('gap');
        
        // Clear existing modules
        this.container.innerHTML = '';
        
        // Render each module
        for (const item of layout) {
            const moduleEl = this.createModuleElement(item);
            this.container.appendChild(moduleEl);
        }
        
        // Update container height
        const maxY = Math.max(...layout.map(item => item.y + item.h));
        this.container.style.height = `${maxY * (cellHeight + gap) + gap}px`;
    }
    
    createModuleElement(item) {
        const { width: cellWidth, height: cellHeight } = this.getState('cellSize');
        const gap = this.getState('gap');
        
        const el = document.createElement('div');
        el.className = 'dashboard-module';
        el.dataset.id = item.id;
        el.dataset.module = item.module;
        
        // Calculate position and size
        const left = item.x * (cellWidth + gap) + gap;
        const top = item.y * (cellHeight + gap) + gap;
        const width = item.w * cellWidth + (item.w - 1) * gap;
        const height = item.h * cellHeight + (item.h - 1) * gap;
        
        el.style.cssText = `
            position: absolute;
            left: ${left}px;
            top: ${top}px;
            width: ${width}px;
            height: ${height}px;
            background: var(--card-background, #132337);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        `;
        
        // Add drag handle
        el.innerHTML = `
            <div class="module-header" data-drag-handle>
                <h6 class="module-title">${this.getModuleTitle(item.module)}</h6>
                <div class="module-actions">
                    <button class="btn-icon" data-action="settings">
                        <i class="bi bi-gear"></i>
                    </button>
                    <button class="btn-icon" data-action="remove">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            </div>
            <div class="module-content" id="module-content-${item.id}">
                Loading...
            </div>
        `;
        
        // Make draggable
        this.makeDraggable(el);
        
        // Load module content
        this.loadModuleContent(item);
        
        return el;
    }
    
    getModuleTitle(moduleType) {
        const titles = {
            'MetricCard': 'Metric',
            'ActivityChart': 'Activity Over Time',
            'CategoryChart': 'Categories',
            'RecentFilesTable': 'Recent Files',
            'SystemHealth': 'System Health',
            'FileDistributionMap': 'File Distribution'
        };
        
        return titles[moduleType] || moduleType;
    }
    
    async loadModuleContent(item) {
        const contentEl = document.getElementById(`module-content-${item.id}`);
        
        try {
            // Dynamically import and render module
            const ModuleClass = await import(`./viz/${item.module.toLowerCase()}.js`);
            const moduleInstance = new ModuleClass.default(contentEl, item);
            await moduleInstance.render();
        } catch (error) {
            contentEl.innerHTML = `<div class="error">Failed to load module: ${error.message}</div>`;
        }
    }
    
    initDragDrop() {
        // Implemented in next section
    }
    
    async saveLayout() {
        const layout = this.getState('layout');
        
        try {
            await API.post('/api/dashboard/layout', { layout });
            this.logger.success('Layout saved');
            
            EventBus.emit('layout:saved');
        } catch (error) {
            this.logger.error('Failed to save layout:', error);
        }
    }
}

export default DashboardGrid;
```

### CSS Grid Styling

**File:** `static/css/dashboard-grid.css`

```css
:root {
    --dark-bg: #0a1628;
    --card-bg: #132337;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-purple: #8b5cf6;
    --accent-yellow: #fbbf24;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --border-color: rgba(255, 255, 255, 0.1);
}

body.dashboard-view {
    background: var(--dark-bg);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

#dashboard-grid-container {
    position: relative;
    width: 100%;
    padding: 16px;
    transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dashboard-module {
    cursor: move;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.dashboard-module:hover {
    border-color: var(--accent-blue);
    box-shadow: 0 8px 12px rgba(59, 130, 246, 0.2);
}

.dashboard-module.dragging {
    opacity: 0.5;
    cursor: grabbing;
    z-index: 1000;
}

.dashboard-module.drop-preview {
    background: rgba(59, 130, 246, 0.2);
    border: 2px dashed var(--accent-blue);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.6; }
}

.module-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    background: rgba(255, 255, 255, 0.02);
}

.module-title {
    margin: 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.module-actions {
    display: flex;
    gap: 8px;
}

.btn-icon {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
}

.btn-icon:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-primary);
}

.module-content {
    padding: 16px;
    height: calc(100% - 48px);
    overflow: auto;
}

/* Drop zone indicators */
.drop-zone {
    position: absolute;
    background: rgba(59, 130, 246, 0.1);
    border: 2px solid var(--accent-blue);
    border-radius: 4px;
    pointer-events: none;
    z-index: 999;
    transition: all 0.2s;
}

.drop-zone.active {
    background: rgba(59, 130, 246, 0.3);
    animation: glow 1s infinite;
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 10px rgba(59, 130, 246, 0.5); }
    50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.8); }
}

/* Responsive adjustments */
@media (max-width: 1280px) {
    .module-title {
        font-size: 0.75rem;
    }
    
    .module-content {
        padding: 12px;
    }
}

@media (max-width: 768px) {
    #dashboard-grid-container {
        padding: 8px;
    }
    
    .module-header {
        padding: 8px 12px;
    }
}
```

---

## Module Library

### Pre-Built Visualization Modules

#### 1. Metric Card Module

**File:** `static/js/modules/viz/metriccard.js`

```javascript
export default class MetricCard {
    constructor(container, config) {
        this.container = container;
        this.config = config;
    }
    
    async render() {
        const data = await this.fetchData();
        
        this.container.innerHTML = `
            <div class="metric-card">
                <div class="metric-label">${data.label}</div>
                <div class="metric-value">${data.value}</div>
                <div class="metric-change ${data.change >= 0 ? 'positive' : 'negative'}">
                    <i class="bi bi-arrow-${data.change >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.change)}% ${data.period}
                </div>
                <div class="metric-sparkline" id="sparkline-${this.config.id}"></div>
            </div>
        `;
        
        // Render sparkline
        this.renderSparkline(data.history);
    }
    
    async fetchData() {
        // Fetch data based on config
        const response = await API.get(`/api/metrics/${this.config.id}`);
        return response;
    }
    
    renderSparkline(data) {
        const canvas = document.createElement('canvas');
        canvas.width = 200;
        canvas.height = 40;
        
        const ctx = canvas.getContext('2d');
        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min;
        
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        data.forEach((value, index) => {
            const x = (index / (data.length - 1)) * canvas.width;
            const y = canvas.height - ((value - min) / range) * canvas.height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        document.getElementById(`sparkline-${this.config.id}`).appendChild(canvas);
    }
}
```

#### 2. Activity Chart Module

**File:** `static/js/modules/viz/activitychart.js`

```javascript
export default class ActivityChart {
    constructor(container, config) {
        this.container = container;
        this.config = config;
    }
    
    async render() {
        const data = await this.fetchData();
        
        this.container.innerHTML = `
            <div class="chart-container">
                <canvas id="activity-chart-${this.config.id}"></canvas>
            </div>
            <div class="chart-legend" id="legend-${this.config.id}"></div>
        `;
        
        this.renderChart(data);
    }
    
    async fetchData() {
        const response = await API.get('/api/analytics/activity');
        return response;
    }
    
    renderChart(data) {
        const canvas = document.getElementById(`activity-chart-${this.config.id}`);
        const ctx = canvas.getContext('2d');
        
        // Use Chart.js or similar library
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Files Organized',
                    data: data.values,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { 
                        beginAtZero: true,
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false }
                    }
                }
            }
        });
    }
}
```

#### 3. Category Distribution (Donut Chart)

**File:** `static/js/modules/viz/categorychart.js`

```javascript
export default class CategoryChart {
    constructor(container, config) {
        this.container = container;
        this.config = config;
    }
    
    async render() {
        const data = await this.fetchData();
        
        this.container.innerHTML = `
            <div class="category-chart-wrapper">
                <canvas id="category-chart-${this.config.id}"></canvas>
                <div class="chart-center-label">
                    <div class="total">${data.total}</div>
                    <div class="label">Total Files</div>
                </div>
            </div>
            <div class="category-list" id="category-list-${this.config.id}"></div>
        `;
        
        this.renderChart(data);
        this.renderList(data);
    }
    
    async fetchData() {
        const response = await API.get('/api/analytics/categories');
        return response;
    }
    
    renderChart(data) {
        const canvas = document.getElementById(`category-chart-${this.config.id}`);
        const ctx = canvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.categories.map(c => c.name),
                datasets: [{
                    data: data.categories.map(c => c.count),
                    backgroundColor: [
                        '#3b82f6', '#8b5cf6', '#06b6d4', '#fbbf24',
                        '#f87171', '#34d399', '#fb923c', '#a78bfa'
                    ],
                    borderWidth: 2,
                    borderColor: '#0a1628'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '70%',
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
    
    renderList(data) {
        const list = document.getElementById(`category-list-${this.config.id}`);
        
        list.innerHTML = data.categories.map((cat, index) => `
            <div class="category-item">
                <span class="category-color" style="background: ${this.getColor(index)}"></span>
                <span class="category-name">${cat.name}</span>
                <span class="category-count">${cat.count}</span>
                <span class="category-percent">${((cat.count / data.total) * 100).toFixed(1)}%</span>
            </div>
        `).join('');
    }
    
    getColor(index) {
        const colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#fbbf24', '#f87171', '#34d399', '#fb923c', '#a78bfa'];
        return colors[index % colors.length];
    }
}
```

#### 4. Recent Files Table

**File:** `static/js/modules/viz/recentfilestable.js`

```javascript
export default class RecentFilesTable {
    constructor(container, config) {
        this.container = container;
        this.config = config;
    }
    
    async render() {
        const data = await this.fetchData();
        
        this.container.innerHTML = `
            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Category</th>
                            <th>Size</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="recent-files-tbody-${this.config.id}">
                    </tbody>
                </table>
            </div>
        `;
        
        this.renderRows(data.files);
    }
    
    async fetchData() {
        const response = await API.get('/api/recent-files?limit=10');
        return response;
    }
    
    renderRows(files) {
        const tbody = document.getElementById(`recent-files-tbody-${this.config.id}`);
        
        tbody.innerHTML = files.map(file => `
            <tr>
                <td>
                    <div class="file-info">
                        <i class="bi bi-file-earmark ${this.getFileIcon(file.category)}"></i>
                        <span class="file-name">${file.name}</span>
                    </div>
                </td>
                <td><span class="badge badge-${file.category.toLowerCase()}">${file.category}</span></td>
                <td>${this.formatSize(file.size)}</td>
                <td>${this.formatDate(file.date)}</td>
                <td>
                    <button class="btn-icon" onclick="openFile('${file.path}')">
                        <i class="bi bi-folder-open"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    getFileIcon(category) {
        const icons = {
            'Images': 'bi-file-image',
            'Videos': 'bi-file-play',
            'Documents': 'bi-file-text',
            'Archives': 'bi-file-zip'
        };
        return icons[category] || 'bi-file-earmark';
    }
    
    formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
        return (bytes / 1073741824).toFixed(1) + ' GB';
    }
    
    formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
}
```

#### 5. System Health Gauges

**File:** `static/js/modules/viz/systemhealth.js`

```javascript
export default class SystemHealth {
    constructor(container, config) {
        this.container = container;
        this.config = config;
    }
    
    async render() {
        const data = await this.fetchData();
        
        this.container.innerHTML = `
            <div class="health-metrics">
                <div class="gauge-container">
                    <canvas id="cpu-gauge-${this.config.id}" width="120" height="120"></canvas>
                    <div class="gauge-label">CPU</div>
                </div>
                <div class="gauge-container">
                    <canvas id="memory-gauge-${this.config.id}" width="120" height="120"></canvas>
                    <div class="gauge-label">Memory</div>
                </div>
                <div class="gauge-container">
                    <canvas id="disk-gauge-${this.config.id}" width="120" height="120"></canvas>
                    <div class="gauge-label">Disk</div>
                </div>
            </div>
            <div class="health-status" id="status-${this.config.id}"></div>
        `;
        
        this.renderGauges(data);
        this.startAutoRefresh();
    }
    
    async fetchData() {
        const response = await API.get('/metrics');
        return response;
    }
    
    renderGauges(data) {
        this.renderGauge('cpu-gauge', data.cpu_percent, '#3b82f6');
        this.renderGauge('memory-gauge', data.memory_percent, '#8b5cf6');
        this.renderGauge('disk-gauge', data.disk_percent, '#06b6d4');
        
        // Update status
        const status = document.getElementById(`status-${this.config.id}`);
        status.innerHTML = `
            <div class="status-item">
                <span class="status-label">Service:</span>
                <span class="status-value ${data.running ? 'running' : 'stopped'}">
                    ${data.running ? 'Running' : 'Stopped'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">Uptime:</span>
                <span class="status-value">${this.formatUptime(data.uptime)}</span>
            </div>
        `;
    }
    
    renderGauge(canvasId, value, color) {
        const canvas = document.getElementById(`${canvasId}-${this.config.id}`);
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 50;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Background arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, 2.25 * Math.PI);
        ctx.lineWidth = 10;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.stroke();
        
        // Value arc
        const endAngle = 0.75 * Math.PI + (1.5 * Math.PI * (value / 100));
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, endAngle);
        ctx.strokeStyle = color;
        ctx.stroke();
        
        // Center text
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 24px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${value}%`, centerX, centerY);
    }
    
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) return `${days}d ${hours}h`;
        if (hours > 0) return `${hours}h ${minutes}m`;
        return `${minutes}m`;
    }
    
    startAutoRefresh() {
        setInterval(async () => {
            const data = await this.fetchData();
            this.renderGauges(data);
        }, 5000); // Refresh every 5 seconds
    }
}
```

#### 6. File Distribution Map

**File:** `static/js/modules/viz/filedistributionmap.js`

```javascript
export default class FileDistributionMap {
    constructor(container, config) {
        this.container = container;
        this.config = config;
    }
    
    async render() {
        const data = await this.fetchData();
        
        this.container.innerHTML = `
            <div class="map-container">
                <canvas id="distribution-map-${this.config.id}"></canvas>
            </div>
            <div class="map-legend" id="map-legend-${this.config.id}"></div>
        `;
        
        this.renderMap(data);
    }
    
    async fetchData() {
        const response = await API.get('/api/analytics/distribution');
        return response;
    }
    
    renderMap(data) {
        // Treemap or heat map showing file distribution by folder/category
        const canvas = document.getElementById(`distribution-map-${this.config.id}`);
        const ctx = canvas.getContext('2d');
        
        // Use D3.js treemap or custom implementation
        this.renderTreemap(ctx, data.folders, canvas.width, canvas.height);
    }
    
    renderTreemap(ctx, data, width, height) {
        // Simplified treemap rendering
        // In production, use D3.js for proper treemap layout
        
        let currentY = 0;
        const total = data.reduce((sum, folder) => sum + folder.size, 0);
        
        data.forEach((folder, index) => {
            const blockHeight = (folder.size / total) * height;
            const color = this.getColor(index);
            
            ctx.fillStyle = color;
            ctx.fillRect(0, currentY, width, blockHeight);
            
            // Add label
            ctx.fillStyle = '#f8fafc';
            ctx.font = '14px sans-serif';
            ctx.fillText(folder.name, 10, currentY + 20);
            ctx.font = '12px sans-serif';
            ctx.fillText(this.formatSize(folder.size), 10, currentY + 40);
            
            currentY += blockHeight;
        });
    }
    
    getColor(index) {
        const colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#fbbf24', '#f87171', '#34d399'];
        return colors[index % colors.length];
    }
    
    formatSize(bytes) {
        if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
        return (bytes / 1073741824).toFixed(1) + ' GB';
    }
}
```

### Complete Module Library List

| Module | Type | Size (W×H) | Data Source |
|--------|------|-----------|-------------|
| MetricCard | Number + Sparkline | 3×2 | `/api/metrics/{id}` |
| ActivityChart | Line Chart | 6×4 | `/api/analytics/activity` |
| CategoryChart | Donut Chart | 6×4 | `/api/analytics/categories` |
| RecentFilesTable | Data Table | 8×4 | `/api/recent-files` |
| SystemHealth | Gauges | 4×4 | `/metrics` |
| FileDistributionMap | Treemap | 12×3 | `/api/analytics/distribution` |
| DuplicatesList | Table | 6×4 | `/api/duplicates` |
| VirusTotalStatus | Badge Grid | 4×3 | `/api/recent-files/virustotal` |
| LogViewer | Scrollable Text | 12×4 | `/tail?which=stdout` |
| NotificationCenter | List | 4×5 | `/api/notifications` |
| WatchedFolders | Icon Grid | 6×3 | `/api/organizer/config` |
| UserActivity | Timeline | 6×4 | `/api/analytics/user-activity` |
| StorageBreakdown | Stacked Bar | 6×3 | `/api/analytics/storage` |
| ServiceStatus | Status Board | 4×2 | `/service-name` |
| QuickActions | Button Grid | 3×3 | N/A (static) |

---

## Drag & Drop Implementation

### Drag & Drop System

**File:** `static/js/modules/dashboard-drag-drop.js`

```javascript
class DragDropManager {
    constructor(gridInstance) {
        this.grid = gridInstance;
        this.draggedElement = null;
        this.draggedItem = null;
        this.placeholder = null;
        this.dropPreview = null;
    }
    
    init() {
        // Will be called by DashboardGrid
        this.setupEventListeners();
    }
    
    makeDraggable(element) {
        const handle = element.querySelector('[data-drag-handle]');
        
        handle.addEventListener('mousedown', (e) => {
            if (e.button !== 0) return; // Only left click
            
            e.preventDefault();
            this.startDrag(element, e);
        });
        
        handle.style.cursor = 'grab';
    }
    
    startDrag(element, event) {
        this.draggedElement = element;
        this.draggedItem = this.grid.getState('layout').find(
            item => item.id === element.dataset.id
        );
        
        // Add dragging class
        element.classList.add('dragging');
        
        // Create placeholder
        this.createPlaceholder();
        
        // Store initial mouse position
        this.initialMouseX = event.clientX;
        this.initialMouseY = event.clientY;
        this.initialElementX = parseInt(element.style.left);
        this.initialElementY = parseInt(element.style.top);
        
        // Add global listeners
        document.addEventListener('mousemove', this.onDragMove);
        document.addEventListener('mouseup', this.onDragEnd);
        
        // Update state
        this.grid.setState({ isDragging: true, draggedModule: this.draggedItem });
    }
    
    createPlaceholder() {
        this.placeholder = document.createElement('div');
        this.placeholder.className = 'dashboard-module drop-preview';
        this.placeholder.style.cssText = this.draggedElement.style.cssText;
        
        this.grid.container.appendChild(this.placeholder);
    }
    
    onDragMove = (event) => {
        if (!this.draggedElement) return;
        
        // Calculate new position
        const deltaX = event.clientX - this.initialMouseX;
        const deltaY = event.clientY - this.initialMouseY;
        
        const newX = this.initialElementX + deltaX;
        const newY = this.initialElementY + deltaY;
        
        // Update dragged element position
        this.draggedElement.style.left = newX + 'px';
        this.draggedElement.style.top = newY + 'px';
        
        // Calculate grid position
        const { width: cellWidth, height: cellHeight } = this.grid.getState('cellSize');
        const gap = this.grid.getState('gap');
        
        const gridX = Math.round((newX - gap) / (cellWidth + gap));
        const gridY = Math.round((newY - gap) / (cellHeight + gap));
        
        // Check for valid drop position
        const canDrop = this.checkDropPosition(gridX, gridY);
        
        if (canDrop) {
            this.updateDropPreview(gridX, gridY);
        } else {
            this.clearDropPreview();
        }
    }
    
    checkDropPosition(x, y) {
        const { cols } = this.grid.getState('gridSize');
        const layout = this.grid.getState('layout');
        const w = this.draggedItem.w;
        const h = this.draggedItem.h;
        
        // Check boundaries
        if (x < 0 || x + w > cols || y < 0) {
            return false;
        }
        
        // Check collisions with other modules
        for (const item of layout) {
            if (item.id === this.draggedItem.id) continue;
            
            const collision = !(
                x + w <= item.x ||
                x >= item.x + item.w ||
                y + h <= item.y ||
                y >= item.y + item.h
            );
            
            if (collision) {
                return false;
            }
        }
        
        return true;
    }
    
    updateDropPreview(x, y) {
        const { width: cellWidth, height: cellHeight } = this.grid.getState('cellSize');
        const gap = this.grid.getState('gap');
        const w = this.draggedItem.w;
        const h = this.draggedItem.h;
        
        if (!this.dropPreview) {
            this.dropPreview = document.createElement('div');
            this.dropPreview.className = 'drop-zone active';
            this.grid.container.appendChild(this.dropPreview);
        }
        
        const left = x * (cellWidth + gap) + gap;
        const top = y * (cellHeight + gap) + gap;
        const width = w * cellWidth + (w - 1) * gap;
        const height = h * cellHeight + (h - 1) * gap;
        
        this.dropPreview.style.cssText = `
            left: ${left}px;
            top: ${top}px;
            width: ${width}px;
            height: ${height}px;
        `;
        
        // Store preview position for drop
        this.previewX = x;
        this.previewY = y;
    }
    
    clearDropPreview() {
        if (this.dropPreview) {
            this.dropPreview.remove();
            this.dropPreview = null;
        }
        this.previewX = null;
        this.previewY = null;
    }
    
    onDragEnd = (event) => {
        if (!this.draggedElement) return;
        
        // Remove dragging class
        this.draggedElement.classList.remove('dragging');
        
        // Check if valid drop position
        if (this.previewX !== null && this.previewY !== null) {
            // Update layout
            this.updateLayout(this.previewX, this.previewY);
        } else {
            // Snap back to original position
            this.snapBack();
        }
        
        // Cleanup
        this.cleanup();
    }
    
    updateLayout(x, y) {
        const layout = this.grid.getState('layout');
        const itemIndex = layout.findIndex(item => item.id === this.draggedItem.id);
        
        if (itemIndex !== -1) {
            layout[itemIndex].x = x;
            layout[itemIndex].y = y;
            
            this.grid.setState({ layout });
            this.grid.render();
            this.grid.saveLayout();
            
            EventBus.emit('layout:changed', { module: this.draggedItem });
        }
    }
    
    snapBack() {
        const { width: cellWidth, height: cellHeight } = this.grid.getState('cellSize');
        const gap = this.grid.getState('gap');
        
        const left = this.draggedItem.x * (cellWidth + gap) + gap;
        const top = this.draggedItem.y * (cellHeight + gap) + gap;
        
        this.draggedElement.style.left = left + 'px';
        this.draggedElement.style.top = top + 'px';
    }
    
    cleanup() {
        // Remove event listeners
        document.removeEventListener('mousemove', this.onDragMove);
        document.removeEventListener('mouseup', this.onDragEnd);
        
        // Remove placeholder and preview
        if (this.placeholder) {
            this.placeholder.remove();
            this.placeholder = null;
        }
        
        this.clearDropPreview();
        
        // Reset state
        this.draggedElement = null;
        this.draggedItem = null;
        this.grid.setState({ isDragging: false, draggedModule: null });
    }
}

export default DragDropManager;
```

### Integration with Grid

**Update to `dashboard-grid.js`:**

```javascript
import DragDropManager from './dashboard-drag-drop.js';

class DashboardGrid extends BaseModule {
    // ... existing code ...
    
    initDragDrop() {
        this.dragDropManager = new DragDropManager(this);
        this.dragDropManager.init();
    }
    
    makeDraggable(element) {
        this.dragDropManager.makeDraggable(element);
    }
    
    // ... rest of code ...
}
```

---

## Layout Persistence

### Save/Load Layout System

**Backend Endpoint:** `SortNStoreDashboard/routes/dashboard_layout.py`

```python
from flask import Blueprint, jsonify, request
from SortNStoreDashboard.auth.auth import requires_auth
import sys
import json

routes_layout = Blueprint('routes_layout', __name__)

@routes_layout.route('/api/dashboard/layout', methods=['GET'])
@requires_auth
def get_layout():
    """Get user's saved dashboard layout."""
    main = sys.modules['__main__']
    config = getattr(main, 'config', {})
    
    # Get current user
    from flask import session
    username = session.get('username', 'default')
    
    # Load layout from config
    layouts = config.get('dashboard_layouts', {})
    user_layout = layouts.get(username, [])
    
    return jsonify({
        'layout': user_layout,
        'username': username
    })

@routes_layout.route('/api/dashboard/layout', methods=['POST'])
@requires_auth
def save_layout():
    """Save user's dashboard layout."""
    data = request.get_json() or {}
    
    if 'layout' not in data:
        return jsonify({'error': 'No layout provided'}), 400
    
    main = sys.modules['__main__']
    config = getattr(main, 'config', {})
    
    # Get current user
    from flask import session
    username = session.get('username', 'default')
    
    # Save layout
    config.setdefault('dashboard_layouts', {})
    config['dashboard_layouts'][username] = data['layout']
    
    # Persist to file
    try:
        with open('organizer_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Layout saved'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@routes_layout.route('/api/dashboard/layout/export', methods=['GET'])
@requires_auth
def export_layout():
    """Export dashboard layout as JSON."""
    from flask import session
    username = session.get('username', 'default')
    
    main = sys.modules['__main__']
    config = getattr(main, 'config', {})
    layouts = config.get('dashboard_layouts', {})
    user_layout = layouts.get(username, [])
    
    return jsonify({
        'version': '1.0',
        'username': username,
        'exported_at': datetime.now().isoformat(),
        'layout': user_layout
    })

@routes_layout.route('/api/dashboard/layout/import', methods=['POST'])
@requires_auth
def import_layout():
    """Import dashboard layout from JSON."""
    data = request.get_json() or {}
    
    if 'layout' not in data:
        return jsonify({'error': 'No layout provided'}), 400
    
    from flask import session
    username = session.get('username', 'default')
    
    main = sys.modules['__main__']
    config = getattr(main, 'config', {})
    
    config.setdefault('dashboard_layouts', {})
    config['dashboard_layouts'][username] = data['layout']
    
    try:
        with open('organizer_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Layout imported'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@routes_layout.route('/api/dashboard/layout/reset', methods=['POST'])
@requires_auth
def reset_layout():
    """Reset dashboard to default layout."""
    from flask import session
    username = session.get('username', 'default')
    
    main = sys.modules['__main__']
    config = getattr(main, 'config', {})
    
    if 'dashboard_layouts' in config and username in config['dashboard_layouts']:
        del config['dashboard_layouts'][username]
        
        try:
            with open('organizer_config.json', 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            pass
    
    return jsonify({
        'success': True,
        'message': 'Layout reset to default'
    })
```

### Export/Import UI

**File:** `static/js/modules/layout-manager.js`

```javascript
import BaseModule from '../base-module.js';
import API from '../api.js';
import EventBus from '../event-bus.js';

class LayoutManager extends BaseModule {
    constructor() {
        super('layout-manager');
    }
    
    async exportLayout() {
        try {
            const response = await API.get('/api/dashboard/layout/export');
            
            const blob = new Blob([JSON.stringify(response, null, 2)], {
                type: 'application/json'
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dashboard-layout-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.logger.success('Layout exported');
        } catch (error) {
            this.logger.error('Failed to export layout:', error);
        }
    }
    
    async importLayout() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'application/json';
        
        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            try {
                const text = await file.text();
                const data = JSON.parse(text);
                
                if (!data.layout) {
                    throw new Error('Invalid layout file');
                }
                
                await API.post('/api/dashboard/layout/import', data);
                
                this.logger.success('Layout imported');
                EventBus.emit('layout:imported');
                
                // Reload page to apply
                window.location.reload();
            } catch (error) {
                this.logger.error('Failed to import layout:', error);
            }
        });
        
        input.click();
    }
    
    async resetLayout() {
        if (!confirm('Reset dashboard to default layout? This cannot be undone.')) {
            return;
        }
        
        try {
            await API.post('/api/dashboard/layout/reset');
            
            this.logger.success('Layout reset');
            EventBus.emit('layout:reset');
            
            // Reload page to apply
            window.location.reload();
        } catch (error) {
            this.logger.error('Failed to reset layout:', error);
        }
    }
}

export default LayoutManager;
```

---

## Implementation Roadmap

### Phase 1: Core Grid System (Week 1)

**Days 1-2: Grid Foundation**
- Create `dashboard-grid.js` module (300 lines)
- Implement responsive breakpoints
- Build grid rendering engine
- Create CSS styling

**Deliverables:**
- Grid system with 12-column layout
- Responsive breakpoints (xl/lg/md/sm/xs)
- Module container rendering
- Basic styling

---

### Phase 2: Drag & Drop (Week 1, Days 3-5)

**Day 3: Drag System**
- Create `dashboard-drag-drop.js` (400 lines)
- Implement mouse event handling
- Add drag placeholder

**Day 4: Drop System**
- Build collision detection
- Create drop zone previews
- Add snap-to-grid logic

**Day 5: Polish**
- Add animations and transitions
- Implement touch support (mobile)
- Test drag performance

**Deliverables:**
- Full drag-and-drop system
- Visual drop previews
- Smooth animations
- Touch device support

---

### Phase 3: Visualization Modules (Week 2)

**Day 1: Metric Cards & Charts**
- MetricCard module (150 lines)
- ActivityChart module (200 lines)
- CategoryChart module (250 lines)

**Day 2: Tables & Gauges**
- RecentFilesTable module (200 lines)
- SystemHealth module (250 lines)

**Day 3: Maps & Advanced Viz**
- FileDistributionMap module (300 lines)
- DuplicatesList module (200 lines)

**Day 4: Utility Modules**
- LogViewer module (150 lines)
- NotificationCenter module (200 lines)
- ServiceStatus module (100 lines)

**Day 5: Polish & Testing**
- Test all modules
- Add error handling
- Performance optimization

**Deliverables:**
- 15+ visualization modules
- Chart.js integration
- D3.js treemap
- Real-time data updates

---

### Phase 4: Layout Persistence (Week 2, Weekend)

**Tasks:**
- Backend layout API (5 endpoints)
- Save/load functionality
- Export/import system
- Reset to default

**Deliverables:**
- User-specific layouts
- Export as JSON
- Import from file
- Reset functionality

---

### Phase 5: UI/UX Polish (Week 3, Days 1-2)

**Tasks:**
- Add module library sidebar
- Create layout presets
- Add fullscreen mode
- Implement keyboard shortcuts
- Add help tooltips

**Deliverables:**
- Module library panel
- 5+ layout presets
- Fullscreen presentation mode
- Keyboard navigation
- Contextual help

---

### Phase 6: Integration & Testing (Week 3, Days 3-5)

**Day 3: Integration**
- Connect to existing dashboard
- Add navigation toggle
- Migrate existing data sources

**Day 4: Testing**
- Cross-browser testing
- Mobile responsiveness
- Performance benchmarks
- User acceptance testing

**Day 5: Documentation**
- User guide
- Developer docs
- Video tutorial
- Deployment guide

**Deliverables:**
- Complete dashboard integration
- Full test coverage
- User documentation
- Deployment ready

---

## Summary

**Total Scope:**
- 1 grid system module (300 lines)
- 1 drag-drop manager (400 lines)
- 15 visualization modules (~3,000 lines)
- 1 layout manager (200 lines)
- Backend API (5 endpoints, 200 lines)
- CSS styling (500 lines)
- HTML template (300 lines)

**Timeline:** 3 weeks

**Dependencies:**
- Chart.js (charts)
- D3.js (treemap, optional)
- Sortable.js (alternative drag-drop library, optional)

**Benefits:**
- ✅ Modern data visualization UI
- ✅ Fully customizable layouts
- ✅ Drag-and-drop positioning
- ✅ Real-time data updates
- ✅ Responsive design
- ✅ Export/import layouts
- ✅ Per-user customization
- ✅ Professional analytics dashboard

---

**Next Steps:**
1. Review architecture
2. Approve design direction
3. Start Phase 1 (grid system)
4. Implement drag-and-drop
5. Build visualization modules
6. Deploy to production

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Status:** Architecture Complete - Ready for Implementation
