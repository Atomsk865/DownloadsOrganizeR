/**
 * Statistics Module
 * Handles file organization statistics and chart rendering
 */

window.moduleManager.register('statistics', ['api', 'utils', 'charts', 'notifications'], (deps) => {
    const api = deps.api;
    const utils = deps.utils;
    const charts = deps.charts;
    const notifications = deps.notifications;
    
    let chartsByCategory = null;
    let chartsByExtension = null;
    let chartTimeline = null;
    let chartHourly = null;
    
    return {
        async loadOverview() {
            try {
                const data = await api.get('/api/statistics/overview');
                return data;
            } catch (err) {
                console.error('Failed to load statistics overview:', err);
                notifications.error('Failed to load statistics');
                return null;
            }
        },
        
        async loadByCategory() {
            try {
                const data = await api.get('/api/statistics/by-category');
                return data;
            } catch (err) {
                console.error('Failed to load category statistics:', err);
                return null;
            }
        },
        
        async loadByExtension() {
            try {
                const data = await api.get('/api/statistics/by-extension');
                return data;
            } catch (err) {
                console.error('Failed to load extension statistics:', err);
                return null;
            }
        },
        
        async loadTimeline() {
            try {
                const data = await api.get('/api/statistics/timeline');
                return data;
            } catch (err) {
                console.error('Failed to load timeline:', err);
                return null;
            }
        },
        
        async loadHourlyActivity() {
            try {
                const data = await api.get('/api/statistics/hourly-activity');
                return data;
            } catch (err) {
                console.error('Failed to load hourly activity:', err);
                return null;
            }
        },
        
        async renderCharts(config) {
            try {
                // Category chart
                if (config.showByCategory) {
                    const categoryData = await this.loadByCategory();
                    if (categoryData) {
                        chartsByCategory = charts.create('chart-category', {
                            type: 'doughnut',
                            data: {
                                labels: categoryData.categories || [],
                                datasets: [{
                                    data: categoryData.counts || [],
                                    backgroundColor: [
                                        '#0d6efd', '#198754', '#dc3545',
                                        '#ffc107', '#17a2b8', '#6f42c1'
                                    ]
                                }]
                            },
                            options: {
                                responsive: true,
                                plugins: {
                                    legend: { position: 'bottom' }
                                }
                            }
                        });
                    }
                }
                
                // Extension chart
                if (config.showByExtension) {
                    const extData = await this.loadByExtension();
                    if (extData) {
                        chartsByExtension = charts.create('chart-extension', {
                            type: 'bar',
                            data: {
                                labels: extData.extensions || [],
                                datasets: [{
                                    label: 'Files',
                                    data: extData.counts || [],
                                    backgroundColor: '#0d6efd'
                                }]
                            },
                            options: {
                                responsive: true,
                                scales: {
                                    y: { beginAtZero: true }
                                }
                            }
                        });
                    }
                }
                
                // Timeline chart
                if (config.showTimeline) {
                    const timelineData = await this.loadTimeline();
                    if (timelineData) {
                        chartTimeline = charts.create('chart-timeline', {
                            type: 'line',
                            data: {
                                labels: timelineData.labels || [],
                                datasets: [{
                                    label: 'Files Organized',
                                    data: timelineData.data || [],
                                    borderColor: '#198754',
                                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                                    fill: true,
                                    tension: 0.4
                                }]
                            },
                            options: {
                                responsive: true,
                                scales: {
                                    y: { beginAtZero: true }
                                }
                            }
                        });
                    }
                }
                
                // Hourly chart
                if (config.showHourly) {
                    const hourlyData = await this.loadHourlyActivity();
                    if (hourlyData) {
                        chartHourly = charts.create('chart-hourly', {
                            type: 'bar',
                            data: {
                                labels: hourlyData.labels || [],
                                datasets: [{
                                    label: 'Files',
                                    data: hourlyData.data || [],
                                    backgroundColor: '#0dcaf0'
                                }]
                            },
                            options: {
                                responsive: true,
                                scales: {
                                    y: { beginAtZero: true }
                                }
                            }
                        });
                    }
                }
                
                return true;
            } catch (err) {
                console.error('Failed to render charts:', err);
                return false;
            }
        },
        
        destroyCharts() {
            charts.destroy('chart-category');
            charts.destroy('chart-extension');
            charts.destroy('chart-timeline');
            charts.destroy('chart-hourly');
        }
    };
});
