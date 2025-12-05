/**
 * Duplicates Module - Lazy Loaded
 * This module handles duplicate file detection and management
 */

// Store duplicates data globally for other functions to access
window.duplicatesData = null;

// Main function to load duplicates
async function loadDuplicates() {
    const btn = document.getElementById('btn-duplicates-refresh');
    const originalHtml = btn ? btn.innerHTML : '';
    const container = document.getElementById('duplicates-container');
    const countBadge = document.getElementById('duplicates-count');
    const wastedBadge = document.getElementById('wasted-space');
    
    try {
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Scanning...';
        }
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <div class="spinner-border text-primary mb-2"></div>
                    <p class="mb-0">Scanning for duplicates...</p>
                </div>`;
        }
        
        const res = await fetch('/api/duplicates', {
            credentials: 'include',
            headers: getAuthHeaders()
        });
        
        if (!res.ok) {
            let message = 'Failed to load duplicates';
            try {
                const err = await res.json();
                message = err.error || message;
            } catch (_) {}
            throw new Error(message);
        }
        
        const data = await res.json();
        window.duplicatesData = data;
        
        if (countBadge) {
            countBadge.textContent = `${data.total_duplicates} duplicate group${data.total_duplicates === 1 ? '' : 's'}`;
        }
        if (wastedBadge) {
            wastedBadge.textContent = `${data.wasted_space_human} wasted`;
        }
        if (!container) return;
        
        if (!data.duplicates || data.duplicates.length === 0) {
            container.innerHTML = `
                <div class="text-center text-success py-4">
                    <i class="bi bi-check-circle fs-1"></i>
                    <p class="mb-0">No duplicate files found!</p>
                </div>`;
            return;
        }
        
        const cards = data.duplicates.map((group, index) => {
            const files = Array.isArray(group.files) ? group.files : [];
            const fileCount = group.count || files.length;
            const totalSizeLabel = escapeHtml(group.total_size_human || '');
            const hashPreviewRaw = (group.hash || '').substring(0, 12);
            const hashPreview = hashPreviewRaw ? escapeHtml(hashPreviewRaw) : '';
            const hashDisplay = hashPreview ? `${hashPreview}...` : 'n/a';
            const fileRows = files.map((file, fileIndex) => {
                const safePath = escapeHtml(file.path || '');
                const deletePath = JSON.stringify(file.path || '');
                const sizeLabel = escapeHtml(file.size_human || '');
                const modifiedLabel = escapeHtml(file.modified_human || '');
                return `
                    <tr>
                        <td style="width: 30px;"><input type="checkbox" data-group="${index}" data-file="${fileIndex}" data-path="${safePath}"></td>
                        <td style="max-width: 250px; word-wrap: break-word; word-break: break-word;"><i class="bi bi-file-earmark"></i> ${escapeHtml(file.name || 'Unknown')}</td>
                        <td style="min-width: 70px; white-space: nowrap;">${sizeLabel || '—'}</td>
                        <td style="min-width: 130px; white-space: nowrap;"><small>${modifiedLabel || '—'}</small></td>
                        <td style="word-wrap: break-word; word-break: break-word;"><small class="text-muted">${safePath}</small></td>
                        <td style="min-width: 80px; text-align: center;">
                            <button class="btn btn-sm btn-danger" onclick="deleteSingleFile(${deletePath})" title="Delete this file">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
            
            return `
                <div class="card mb-3">
                    <div class="card-header" style="background-color: var(--bg-secondary);">
                        <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-2">
                            <div>
                                <strong>${fileCount} files</strong> - ${totalSizeLabel || 'Unknown size'}
                                <small class="text-muted">(Hash: ${hashDisplay})</small>
                            </div>
                            <div class="d-flex flex-wrap gap-2">
                                <button class="btn btn-sm btn-primary" onclick="keepNewest(${index})" title="Keep newest file, delete older duplicates">
                                    <i class="bi bi-clock"></i> Keep Newest
                                </button>
                                <button class="btn btn-sm btn-success" onclick="keepLargest(${index})" title="Keep largest file, delete smaller duplicates">
                                    <i class="bi bi-file-earmark"></i> Keep Largest
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteAllDuplicates(${index})" title="Delete all files in this group">
                                    <i class="bi bi-trash"></i> Delete All
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-sm table-hover mb-0" style="table-layout: auto; width: 100%;">
                                <thead>
                                    <tr>
                                        <th style="width: 30px;"><input type="checkbox" onchange="toggleGroupSelection(${index}, this.checked)" title="Select all files in group"></th>
                                        <th style="width: 25%;">Name</th>
                                        <th style="width: 8%; min-width: 70px;">Size</th>
                                        <th style="width: 15%; min-width: 130px;">Modified</th>
                                        <th style="width: auto;">Path</th>
                                        <th style="width: 80px; min-width: 80px; text-align: center;">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${fileRows || '<tr><td colspan="6" class="text-center text-muted">No file details available</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = cards;
    } catch (error) {
        console.error('Error loading duplicates:', error);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger mb-0">
                    <i class="bi bi-exclamation-triangle"></i> ${escapeHtml(error.message || 'Failed to load duplicates')}
                </div>`;
        }
        showNotification('Failed to load duplicates: ' + error.message, 'danger');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalHtml || '<i class="bi bi-arrow-clockwise"></i> Refresh';
        }
    }
}

async function loadWatchedFolders() {
    try {
        const res = await fetch('/api/watch_folders', {
            credentials: 'include',
            headers: { 'Authorization': window.__authHeader }
        });
        if (!res.ok) return;
        const data = await res.json();
        const folders = Array.isArray(data.folders) ? data.folders : [];
        const badge = document.getElementById('watched-folders-badge');
        const list = document.getElementById('watched-folders-list');
        const ul = document.getElementById('watched-folders-ul');
        if (badge) badge.textContent = `watching ${folders.length}`;
        if (ul) {
            ul.innerHTML = folders.map(f => `<li><small class="text-muted">${f}</small></li>`).join('');
        }
        if (list) list.style.display = folders.length ? 'block' : 'none';
    } catch (e) {
        console.error('Failed to load watched folders', e);
    }
}

function toggleGroupSelection(groupIndex, checked) {
    document.querySelectorAll(`input[data-group="${groupIndex}"]`).forEach(checkbox => {
        checkbox.checked = checked;
    });
}

async function keepNewest(groupIndex) {
    if (!window.duplicatesData) return;
    
    const group = window.duplicatesData.duplicates[groupIndex];
    if (!group || group.files.length < 2) return;
    
    // Keep first file (newest by sort), delete rest
    const filesToDelete = group.files.slice(1).map(f => f.path);
    
    if (!confirm(`Delete ${filesToDelete.length} older duplicate(s) and keep the newest?`)) {
        return;
    }
    
    await resolveDuplicates(filesToDelete);
}

async function keepLargest(groupIndex) {
    if (!window.duplicatesData) return;
    
    const group = window.duplicatesData.duplicates[groupIndex];
    if (!group || group.files.length < 2) return;
    
    // Find largest file
    let largest = group.files[0];
    group.files.forEach(f => {
        if (f.size > largest.size) largest = f;
    });
    
    // Delete all except largest
    const filesToDelete = group.files.filter(f => f.path !== largest.path).map(f => f.path);
    
    if (!confirm(`Delete ${filesToDelete.length} duplicate(s) and keep the largest (${largest.size_human})?`)) {
        return;
    }
    
    await resolveDuplicates(filesToDelete);
}

async function deleteAllDuplicates(groupIndex) {
    if (!window.duplicatesData) return;
    
    const group = window.duplicatesData.duplicates[groupIndex];
    if (!group) return;
    
    const filesToDelete = group.files.map(f => f.path);
    
    if (!confirm(`Delete ALL ${filesToDelete.length} files in this duplicate group? This cannot be undone!`)) {
        return;
    }
    
    await resolveDuplicates(filesToDelete);
}

async function deleteSingleFile(filePath) {
    if (!confirm(`Delete this file?\n${filePath}\n\nThis cannot be undone!`)) {
        return;
    }
    
    await resolveDuplicates([filePath]);
}

async function deleteSelectedFiles() {
    const selected = Array.from(document.querySelectorAll('input[data-path]:checked')).map(cb => cb.dataset.path);
    
    if (selected.length === 0) {
        showToast('No files selected', 'warning');
        return;
    }
    
    if (!confirm(`Delete ${selected.length} selected file(s)? This cannot be undone!`)) {
        return;
    }
    
    await resolveDuplicates(selected);
}

async function resolveDuplicates(filePaths) {
    try {
        const res = await fetch('/api/duplicates/resolve', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({
                action: 'delete',
                files: filePaths
            })
        });
        
        if (res.ok) {
            const result = await res.json();
            showToast(result.message, 'success');
            
            // Reload duplicates
            loadDuplicates();
        } else {
            const error = await res.json();
            showToast('Failed to delete files: ' + (error.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error resolving duplicates:', error);
        showNotification('Error: ' + error.message, 'danger');
    }
}

// Export functions to window for global access
window.loadDuplicates = loadDuplicates;
window.loadWatchedFolders = loadWatchedFolders;
window.toggleGroupSelection = toggleGroupSelection;
window.keepNewest = keepNewest;
window.keepLargest = keepLargest;
window.deleteAllDuplicates = deleteAllDuplicates;
window.deleteSingleFile = deleteSingleFile;
window.deleteSelectedFiles = deleteSelectedFiles;
window.resolveDuplicates = resolveDuplicates;

console.log('✓ Duplicates module loaded');

