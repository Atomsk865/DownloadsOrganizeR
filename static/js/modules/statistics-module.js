/**
 * Statistics Module
 * Displays dashboard statistics and metrics
 */

import { BaseModule, ModuleSystem } from './module-system.js';
import { API, DOM, Utils } from './core-library.js';

export class StatisticsModule extends BaseModule {
    constructor() {
        super('Statistics', {
            refreshInterval: 5000
        });
        this.refreshTimer = null;
    }

    /**
     * Initialize statistics module
     */
    async onInit() {
        if (!this.mount('#statistics-container')) {
            return;
        }

        this.renderSkeleton();
        await this.loadStats();
        this.startAutoRefresh();
    }

    /**
     * Load statistics from API
     */
    async loadStats() {
        try {
            const data = await API.get('/api/dashboard/statistics');
            this.setState('stats', data);
            this.render(data);
        } catch (error) {
            this.error('Failed to load statistics');
            console.error('Statistics load error:', error);
        }
    }

    /**
     * Render statistics
     */
    render(stats = {}) {
        if (!this.container) return;

        const html = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon" style="background: #d1ecf1;">
                        <i class="bi bi-folder" style="color: #0dcaf0;"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value">${stats.folders || 0}</div>
                        <div class="stat-label">Organized Folders</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon" style="background: #d1e7dd;">
                        <i class="bi bi-file-earmark" style="color: #198754;"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value">${stats.files || 0}</div>
                        <div class="stat-label">Files Organized</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon" style="background: #f8d7da;">
                        <i class="bi bi-diagram-3" style="color: #dc3545;"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value">${Utils.formatFileSize(stats.space_saved || 0)}</div>
                        <div class="stat-label">Storage Used</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon" style="background: #fff3cd;">
                        <i class="bi bi-clock-history" style="color: #ffc107;"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value">${stats.uptime || 'N/A'}</div>
                        <div class="stat-label">Service Uptime</div>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
    }

    /**
     * Render loading skeleton
     */
    renderSkeleton() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="stats-grid">
                ${'<div class="stat-card skeleton"></div>'.repeat(4)}
            </div>
        `;
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.loadStats();
        }, this.options.refreshInterval);
    }

    /**
     * Cleanup on destroy
     */
    async onDestroy() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
    }
}

// Register module
ModuleSystem.register('Statistics', {
    init: () => new StatisticsModule().init(),
    dependencies: []
});

export default StatisticsModule;
