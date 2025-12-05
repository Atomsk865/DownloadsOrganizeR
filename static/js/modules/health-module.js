/**
 * System Health Module
 * Monitors system resources and service health
 */

import { BaseModule, ModuleSystem } from './module-system.js';
import { API, Store, DOM } from './core-library.js';

export class HealthModule extends BaseModule {
    constructor() {
        super('Health', {
            refreshInterval: 10000,
            warningThresholds: {
                cpu: 80,
                memory: 85,
                disk: 90
            }
        });
        this.refreshTimer = null;
    }

    /**
     * Initialize health module
     */
    async onInit() {
        if (!this.mount('#health-container')) {
            return;
        }

        this.renderSkeleton();
        await this.loadHealth();
        this.startAutoRefresh();
    }

    /**
     * Load health data from API
     */
    async loadHealth() {
        try {
            const data = await API.get('/api/dashboard/health');
            this.setState('health', data);
            this.render(data);
        } catch (error) {
            console.error('Health data load error:', error);
        }
    }

    /**
     * Render health status
     */
    render(health = {}) {
        if (!this.container) return;

        const cpuStatus = this.getStatusBadge(health.cpu || 0);
        const memStatus = this.getStatusBadge(health.memory || 0);
        const diskStatus = this.getStatusBadge(health.disk || 0);

        const html = `
            <div class="health-grid">
                <div class="health-item">
                    <div class="health-header">
                        <span class="health-label">CPU Usage</span>
                        ${cpuStatus}
                    </div>
                    <div class="health-bar">
                        <div class="health-progress" style="width: ${health.cpu || 0}%"></div>
                    </div>
                    <div class="health-value">${health.cpu || 0}%</div>
                </div>

                <div class="health-item">
                    <div class="health-header">
                        <span class="health-label">Memory Usage</span>
                        ${memStatus}
                    </div>
                    <div class="health-bar">
                        <div class="health-progress" style="width: ${health.memory || 0}%"></div>
                    </div>
                    <div class="health-value">${health.memory || 0}%</div>
                </div>

                <div class="health-item">
                    <div class="health-header">
                        <span class="health-label">Disk Usage</span>
                        ${diskStatus}
                    </div>
                    <div class="health-bar">
                        <div class="health-progress" style="width: ${health.disk || 0}%"></div>
                    </div>
                    <div class="health-value">${health.disk || 0}%</div>
                </div>

                <div class="health-item">
                    <div class="health-header">
                        <span class="health-label">Service Status</span>
                        <span class="badge ${health.service_running ? 'bg-success' : 'bg-danger'}">
                            ${health.service_running ? 'Running' : 'Stopped'}
                        </span>
                    </div>
                    <div class="health-detail">
                        <small class="text-muted">Last check: ${new Date(health.last_check).toLocaleTimeString()}</small>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
    }

    /**
     * Get status badge for percentage value
     */
    getStatusBadge(value) {
        const cpu = this.options.warningThresholds.cpu;
        const memory = this.options.warningThresholds.memory;
        const disk = this.options.warningThresholds.disk;

        let status = 'success';
        if (value >= cpu) status = 'warning';
        if (value >= 95) status = 'danger';

        return `<span class="badge bg-${status}"></span>`;
    }

    /**
     * Render skeleton
     */
    renderSkeleton() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="health-grid">
                ${'<div class="health-item skeleton"></div>'.repeat(4)}
            </div>
        `;
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.loadHealth();
        }, this.options.refreshInterval);
    }

    /**
     * Cleanup
     */
    async onDestroy() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
    }
}

// Register module
ModuleSystem.register('Health', {
    init: () => new HealthModule().init(),
    dependencies: []
});

export default HealthModule;
