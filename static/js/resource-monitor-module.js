/**
 * Resource Monitoring Module
 * Handles system metrics, SSE streams, and resource tracking
 */

window.moduleManager.register('resourceMonitor', ['api', 'notifications'], (deps) => {
    const api = deps.api;
    const notifications = deps.notifications;
    
    let metricsSSE = null;
    let notificationsSSE = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    
    return {
        startMetricsStream(onUpdate) {
            if (metricsSSE) {
                this.stopMetricsStream();
            }
            
            try {
                metricsSSE = new EventSource('/stream/metrics');
                
                metricsSSE.addEventListener('metrics', (e) => {
                    try {
                        const data = JSON.parse(e.data);
                        onUpdate(data);
                        reconnectAttempts = 0;
                    } catch (err) {
                        console.error('Failed to parse metrics:', err);
                    }
                });
                
                metricsSSE.addEventListener('error', (e) => {
                    console.error('Metrics stream error:', e);
                    this.stopMetricsStream();
                    
                    // Try to reconnect
                    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                        reconnectAttempts++;
                        setTimeout(() => {
                            console.log(`Reconnecting metrics stream (attempt ${reconnectAttempts})...`);
                            this.startMetricsStream(onUpdate);
                        }, 1000 * reconnectAttempts);
                    }
                });
                
                console.log('✓ Metrics stream started');
            } catch (err) {
                console.error('Failed to start metrics stream:', err);
            }
        },
        
        stopMetricsStream() {
            if (metricsSSE) {
                metricsSSE.close();
                metricsSSE = null;
                console.log('✓ Metrics stream stopped');
            }
        },
        
        startNotificationsStream(onNotification) {
            if (notificationsSSE) {
                this.stopNotificationsStream();
            }
            
            try {
                notificationsSSE = new EventSource('/stream/notifications');
                
                notificationsSSE.addEventListener('notifications', (e) => {
                    try {
                        const data = JSON.parse(e.data);
                        onNotification(data);
                    } catch (err) {
                        console.error('Failed to parse notification:', err);
                    }
                });
                
                notificationsSSE.addEventListener('error', (e) => {
                    console.error('Notifications stream error:', e);
                    this.stopNotificationsStream();
                });
                
                console.log('✓ Notifications stream started');
            } catch (err) {
                console.error('Failed to start notifications stream:', err);
            }
        },
        
        stopNotificationsStream() {
            if (notificationsSSE) {
                notificationsSSE.close();
                notificationsSSE = null;
                console.log('✓ Notifications stream stopped');
            }
        },
        
        async getSystemInfo() {
            try {
                return await api.get('/hardware');
            } catch (err) {
                console.error('Failed to get system info:', err);
                return null;
            }
        },
        
        async getDrives() {
            try {
                return await api.get('/drives');
            } catch (err) {
                console.error('Failed to get drives:', err);
                return [];
            }
        },
        
        async getTopProcesses() {
            try {
                return await api.get('/tasks');
            } catch (err) {
                console.error('Failed to get tasks:', err);
                return [];
            }
        },
        
        async getNetworkStats() {
            try {
                return await api.get('/network');
            } catch (err) {
                console.error('Failed to get network stats:', err);
                return null;
            }
        },
        
        renderDriveSpace(drives, container) {
            if (!drives || drives.length === 0) {
                container.innerHTML = '<p class="text-muted">No drives found</p>';
                return;
            }
            
            const rows = drives.map(drive => `
                <tr>
                    <td>${drive.device}</td>
                    <td>
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" 
                                 style="width: ${drive.percent}%">
                                ${drive.percent.toFixed(1)}%
                            </div>
                        </div>
                    </td>
                    <td>${(drive.used / 1024**3).toFixed(2)} GB</td>
                    <td>${(drive.total / 1024**3).toFixed(2)} GB</td>
                </tr>
            `).join('');
            
            container.innerHTML = `
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Drive</th>
                            <th>Usage</th>
                            <th>Used</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            `;
        },
        
        renderTopProcesses(processes, container) {
            if (!processes || processes.length === 0) {
                container.innerHTML = '<p class="text-muted">No processes</p>';
                return;
            }
            
            const rows = processes.map(proc => `
                <tr>
                    <td>${proc.name}</td>
                    <td><span class="badge bg-info">${proc.pid}</span></td>
                    <td>${proc.cpu.toFixed(1)}%</td>
                    <td>${proc.mem.toFixed(0)} MB</td>
                </tr>
            `).join('');
            
            container.innerHTML = `
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Process</th>
                            <th>PID</th>
                            <th>CPU</th>
                            <th>Memory</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            `;
        },
        
        cleanup() {
            this.stopMetricsStream();
            this.stopNotificationsStream();
        }
    };
});
