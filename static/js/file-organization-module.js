/**
 * File Organization Module
 * Handles file movement, categorization, and organization operations
 */

window.moduleManager.register('fileOrganization', ['api', 'utils', 'notifications'], (deps) => {
    const api = deps.api;
    const utils = deps.utils;
    const notifications = deps.notifications;
    
    return {
        async getFileHistory(limit = 50) {
            try {
                return await api.get(`/api/file-history?limit=${limit}`);
            } catch (err) {
                console.error('Failed to load file history:', err);
                return [];
            }
        },
        
        async getRecentFiles() {
            try {
                return await api.get('/api/recent_files');
            } catch (err) {
                console.error('Failed to load recent files:', err);
                return [];
            }
        },
        
        async openFile(filePath) {
            try {
                await api.post('/api/open-file', { path: filePath });
                notifications.success('File opened');
            } catch (err) {
                console.error('Failed to open file:', err);
                notifications.error('Failed to open file');
            }
        },
        
        async organizeFile(filePath, targetCategory) {
            try {
                const result = await api.post('/api/organize', {
                    path: filePath,
                    category: targetCategory
                });
                notifications.success(`File moved to ${targetCategory}`);
                return result;
            } catch (err) {
                console.error('Failed to organize file:', err);
                notifications.error('Failed to organize file');
                return null;
            }
        },
        
        async batchOrganize(filePaths, targetCategory) {
            try {
                const result = await api.post('/api/organize-batch', {
                    paths: filePaths,
                    category: targetCategory
                });
                notifications.success(`${filePaths.length} files organized`);
                return result;
            } catch (err) {
                console.error('Failed to batch organize:', err);
                notifications.error('Failed to organize files');
                return null;
            }
        },
        
        renderFileHistory(files, container) {
            if (!files || files.length === 0) {
                container.innerHTML = '<p class="text-muted">No file history</p>';
                return;
            }
            
            const rows = files.map(file => `
                <tr>
                    <td>${new Date(file.timestamp * 1000).toLocaleString()}</td>
                    <td>${utils.escapeHtml(file.name)}</td>
                    <td>${utils.formatBytes(file.size)}</td>
                    <td>${utils.escapeHtml(file.destination)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="fileOrganization.openFile('${utils.escapeHtml(file.path)}')">
                            <i class="bi bi-folder"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
            container.innerHTML = `
                <table class="table table-sm table-hover">
                    <thead>
                        <tr>
                            <th>Date/Time</th>
                            <th>File</th>
                            <th>Size</th>
                            <th>Destination</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            `;
        }
    };
});
