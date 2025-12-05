/**
 * Watched Folders Configuration Module
 * 
 * Manages the list of folders that the organizer service monitors for file changes.
 * Handles path validation, placeholder resolution, and folder access testing.
 * 
 * Features:
 * - Watched folders CRUD operations
 * - Path validation (Windows, UNC, Unix formats)
 * - Placeholder resolution (%USERNAME%, %USER%)
 * - Folder access testing (readable/writable)
 * - Create missing folder option
 * - Audit log for configuration changes
 * - Batch test operations
 * 
 * Dependencies:
 * - FormValidator (utilities/form-validator.js)
 * - TableManager (utilities/table-manager.js)
 * - TemplateEngine (utilities/template-engine.js)
 * 
 * @module watched-folders-config
 * @version 1.0.0
 */

import { FormValidator, FormValidatorUI } from '../utilities/form-validator.js';
import { TableManager } from '../utilities/table-manager.js';
import { TemplateEngine } from '../utilities/template-engine.js';

/**
 * Path format validation patterns
 * @constant {Object.<string, Object>}
 */
const PATH_FORMATS = {
    windows: {
        name: 'Windows Path',
        pattern: /^[a-zA-Z]:\\(?:[^\\/:*?"<>|]+\\)*[^\\/:*?"<>|]*$/,
        placeholder: 'C:\\Users\\Downloads',
        examples: [
            'C:\\Users\\%USERNAME%\\Downloads',
            'C:\\Temp\\Files',
            'D:\\Shared\\Documents'
        ]
    },
    unc: {
        name: 'UNC Path (Network)',
        pattern: /^\\\\[^\\/:*?"<>|]+\\[^\\/:*?"<>|]+(?:\\[^\\/:*?"<>|]+)*$/,
        placeholder: '\\\\server\\share\\path',
        examples: [
            '\\\\NAS\\downloads',
            '\\\\server\\shared\\documents',
            '\\\\192.168.1.100\\backups'
        ]
    },
    unix: {
        name: 'Unix/Linux Path',
        pattern: /^\/(?:[^\/]+\/)*[^\/]*$/,
        placeholder: '/home/user/downloads',
        examples: [
            '/home/$USER/downloads',
            '/mnt/nas/backups',
            '/var/media/files'
        ]
    }
};

/**
 * Placeholder tokens that can be used in paths
 * @constant {Object.<string, string>}
 */
const PLACEHOLDER_TOKENS = {
    '%USERNAME%': 'Current Windows username',
    '%USER%': 'Current Unix/Linux username'
};

/**
 * Watched Folders Configuration Manager
 * 
 * Manages the list of folders monitored by the organizer service.
 */
export class WatchedFoldersConfig {
    /**
     * Initialize the Watched Folders configuration manager
     * 
     * @param {string} containerSelector - CSS selector for container element
     * @param {Object} options - Configuration options
     * @param {string} [options.apiEndpoint='/api/organizer/config'] - API endpoint for folder operations
     * @param {string} [options.testEndpoint='/api/test-folder'] - API endpoint for folder testing
     * @param {Function} [options.onFoldersChange] - Callback when folders are modified
     */
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            throw new Error(`Container not found: ${containerSelector}`);
        }

        // Configuration options
        this.options = {
            apiEndpoint: options.apiEndpoint || '/api/organizer/config',
            testEndpoint: options.testEndpoint || '/api/test-folder',
            onFoldersChange: options.onFoldersChange || null
        };

        // State management
        this.state = {
            folders: [],
            selectedFolder: null,
            pathInput: '',
            createIfMissing: false,
            searchQuery: '',
            testResults: new Map(), // path -> test result
            auditLog: [],
            loading: false,
            testing: false,
            error: null
        };

        // Components
        this.validator = null;
        this.validatorUI = null;
        this.foldersTable = null;
        this.templateEngine = null;
        this.formElements = {};

        // Initialize
        this.init();
    }

    /**
     * Initialize the module
     */
    async init() {
        this.templateEngine = new TemplateEngine({ escapeHtml: true });
        this.render();
        this.setupValidator();
        this.setupTable();
        this.attachEventListeners();
        await this.loadFolders();
        await this.loadAuditLog();
    }

    /**
     * Render the UI structure
     */
    render() {
        this.container.innerHTML = `
            <div class="watched-folders-config">
                <!-- Header -->
                <div class="config-header mb-4">
                    <h3 class="mb-0">Watched Folders</h3>
                    <p class="text-muted">Configure folders for real-time file organization monitoring</p>
                </div>

                <!-- Error Display -->
                <div id="folders-error-alert" class="alert alert-danger d-none" role="alert">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <span id="folders-error-message"></span>
                </div>

                <!-- Success Display -->
                <div id="folders-success-alert" class="alert alert-success d-none" role="alert">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    <span id="folders-success-message"></span>
                </div>

                <!-- Info Display -->
                <div class="alert alert-info d-none" id="folders-info-alert">
                    <i class="bi bi-info-circle me-2"></i>
                    <span id="folders-info-message"></span>
                </div>

                <!-- Two Column Layout -->
                <div class="row">
                    <!-- Left: Add Folder Form -->
                    <div class="col-lg-5 mb-4">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Add Folder</h5>
                            </div>
                            <div class="card-body">
                                <form id="folder-form">
                                    <!-- Path Format Info -->
                                    <div class="alert alert-light small mb-3">
                                        <strong>Supported Formats:</strong>
                                        <ul class="mb-0 mt-2">
                                            <li><code>C:\\path\\to\\folder</code> - Windows paths</li>
                                            <li><code>\\\\server\\share\\path</code> - Network (UNC) paths</li>
                                            <li><code>/path/to/folder</code> - Unix/Linux paths</li>
                                        </ul>
                                        <strong class="d-block mt-2">Placeholders:</strong>
                                        <ul class="mb-0 mt-2">
                                            <li><code>%USERNAME%</code> - Windows username</li>
                                            <li><code>%USER%</code> - Unix/Linux username</li>
                                        </ul>
                                    </div>

                                    <!-- Folder Path -->
                                    <div class="mb-3">
                                        <label for="folder-path" class="form-label">
                                            Folder Path <span class="text-danger">*</span>
                                        </label>
                                        <input type="text" class="form-control font-monospace" 
                                               id="folder-path" name="path" required
                                               placeholder="C:\\Users\\%USERNAME%\\Downloads">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Enter a valid folder path with optional placeholders</div>
                                    </div>

                                    <!-- Create If Missing -->
                                    <div class="mb-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" 
                                                   id="create-if-missing" name="create_if_missing">
                                            <label class="form-check-label" for="create-if-missing">
                                                Create folder if it doesn't exist
                                            </label>
                                        </div>
                                        <div class="form-text">Automatically create the folder when the service starts</div>
                                    </div>

                                    <!-- Action Buttons -->
                                    <div class="d-flex gap-2">
                                        <button type="button" id="test-folder-btn" 
                                                class="btn btn-outline-primary flex-grow-1">
                                            <i class="bi bi-folder-check me-1"></i> Test Folder
                                        </button>
                                        <button type="button" id="add-folder-btn" 
                                                class="btn btn-primary flex-grow-1">
                                            <i class="bi bi-plus-circle me-1"></i> Add Folder
                                        </button>
                                    </div>

                                    <!-- Test Result -->
                                    <div id="test-result" class="mt-3 d-none">
                                        <div class="alert" id="test-result-alert">
                                            <div class="d-flex align-items-center">
                                                <i id="test-result-icon" class="me-2"></i>
                                                <div class="flex-grow-1">
                                                    <strong id="test-result-title"></strong>
                                                    <div id="test-result-details" class="small mt-2"></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Folders List & Controls -->
                    <div class="col-lg-7">
                        <!-- Toolbar -->
                        <div class="mb-3 d-flex gap-2 align-items-center">
                            <div class="input-group" style="max-width: 300px;">
                                <span class="input-group-text">
                                    <i class="bi bi-search"></i>
                                </span>
                                <input type="text" id="folders-search" class="form-control" 
                                       placeholder="Search folders...">
                            </div>
                            <button id="test-all-btn" class="btn btn-outline-secondary">
                                <i class="bi bi-lightning-charge me-1"></i> Test All
                            </button>
                            <button id="audit-log-btn" class="btn btn-outline-info">
                                <i class="bi bi-clock-history me-1"></i> Audit Log
                            </button>
                        </div>

                        <!-- Folders Table -->
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Watched Folders</h5>
                            </div>
                            <div class="card-body">
                                <div id="folders-table-container"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Delete Confirmation Modal -->
                <div class="modal fade" id="deleteFolderModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">Remove Folder</h5>
                                <button type="button" class="btn-close btn-close-white" 
                                        data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>Remove folder from watched list?</p>
                                <p class="font-monospace small bg-light p-2 rounded">
                                    <span id="delete-folder-path"></span>
                                </p>
                                <p class="mb-0 text-muted small">
                                    The folder itself will not be deleted, only removed from monitoring.
                                </p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" 
                                        data-bs-dismiss="modal">Cancel</button>
                                <button type="button" id="confirm-delete-folder-btn" 
                                        class="btn btn-danger">
                                    <i class="bi bi-trash me-1"></i> Remove Folder
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Audit Log Modal -->
                <div class="modal fade" id="auditLogModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Folder Configuration Audit Log</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div id="audit-log-container" style="max-height: 400px; overflow-y: auto;">
                                    <!-- Audit log entries -->
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Store form element references
        this.formElements = {
            form: this.container.querySelector('#folder-form'),
            path: this.container.querySelector('#folder-path'),
            createIfMissing: this.container.querySelector('#create-if-missing')
        };
    }

    /**
     * Setup form validation
     */
    setupValidator() {
        this.validator = new FormValidator();
        this.validatorUI = new FormValidatorUI(this.validator);

        // Path validation with custom validator
        this.validator.registerValidator('folderPath', (value) => {
            if (!value || value.trim().length === 0) {
                return { valid: false, message: 'Path is required' };
            }

            // Replace placeholders for validation
            const resolvedPath = this.resolvePlaceholders(value);

            // Check if matches any valid format
            for (const format of Object.values(PATH_FORMATS)) {
                if (format.pattern.test(resolvedPath)) {
                    return { valid: true };
                }
            }

            return {
                valid: false,
                message: 'Invalid path format. Use Windows (C:\\path), UNC (\\\\server\\share), or Unix (/path) format'
            };
        });

        this.validator.addRule('path', {
            type: 'folderPath',
            message: 'Invalid path format'
        });

        // Bind UI validation
        this.validatorUI.bindField('path', this.formElements.path, {
            debounce: 300,
            showSuccess: true
        });
    }

    /**
     * Setup folders table
     */
    setupTable() {
        this.foldersTable = new TableManager('#folders-table-container', {
            columns: [
                {
                    key: 'path',
                    label: 'Path',
                    sortable: true,
                    render: (value) => `<code class="small">${this.escapeHtml(value)}</code>`
                },
                {
                    key: 'resolved_path',
                    label: 'Resolved Path',
                    sortable: false,
                    render: (value) => {
                        if (!value) return '<em class="text-muted">Not tested</em>';
                        return `<code class="small text-muted">${this.escapeHtml(value)}</code>`;
                    }
                },
                {
                    key: 'status',
                    label: 'Status',
                    sortable: false,
                    render: (value, row) => {
                        const testResult = this.state.testResults.get(row.path);
                        if (!testResult) {
                            return '<span class="badge bg-secondary">Not Tested</span>';
                        }
                        
                        if (!testResult.success) {
                            return `<span class="badge bg-danger" title="${this.escapeHtml(testResult.message)}">
                                <i class="bi bi-exclamation-triangle me-1"></i>Error
                            </span>`;
                        }

                        // Show access permissions
                        const badges = [];
                        if (testResult.readable) {
                            badges.push('<span class="badge bg-success">Read</span>');
                        }
                        if (testResult.writable) {
                            badges.push('<span class="badge bg-success">Write</span>');
                        }
                        if (!testResult.readable && !testResult.writable) {
                            badges.push('<span class="badge bg-warning">No Access</span>');
                        }
                        return badges.join(' ');
                    }
                },
                {
                    key: 'actions',
                    label: 'Actions',
                    sortable: false,
                    render: (value, row) => `
                        <button class="btn btn-sm btn-outline-primary test-folder" 
                                data-path="${this.escapeHtml(row.path)}"
                                title="Test folder access">
                            <i class="bi bi-folder-check"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-folder" 
                                data-path="${this.escapeHtml(row.path)}">
                            <i class="bi bi-trash"></i>
                        </button>
                    `
                }
            ],
            data: [],
            paginate: false,
            sortable: true
        });
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Test folder
        this.container.querySelector('#test-folder-btn').addEventListener('click', () => {
            this.testFolder();
        });

        // Add folder
        this.container.querySelector('#add-folder-btn').addEventListener('click', () => {
            this.addFolder();
        });

        // Test all folders
        this.container.querySelector('#test-all-btn').addEventListener('click', () => {
            this.testAllFolders();
        });

        // Search
        this.container.querySelector('#folders-search').addEventListener('input', (e) => {
            this.state.searchQuery = e.target.value;
            this.foldersTable.search(e.target.value);
        });

        // Audit log
        this.container.querySelector('#audit-log-btn').addEventListener('click', () => {
            this.showAuditLog();
        });

        // Table actions (test/delete) - using event delegation
        this.container.addEventListener('click', (e) => {
            if (e.target.closest('.test-folder')) {
                const path = e.target.closest('.test-folder').dataset.path;
                this.testFolderByPath(path);
            } else if (e.target.closest('.delete-folder')) {
                const path = e.target.closest('.delete-folder').dataset.path;
                this.confirmDeleteFolder(path);
            }
        });

        // Delete confirmation
        this.container.querySelector('#confirm-delete-folder-btn').addEventListener('click', () => {
            this.deleteFolder();
        });
    }

    /**
     * Resolve placeholders in path
     * 
     * @param {string} path - Path with potential placeholders
     * @returns {string} Resolved path
     */
    resolvePlaceholders(path) {
        let resolved = path;
        
        // %USERNAME% - Windows current user
        if (resolved.includes('%USERNAME%')) {
            const username = this.getUsernameFromEnv() || 'user';
            resolved = resolved.replace(/%USERNAME%/g, username);
        }
        
        // %USER% - Unix current user
        if (resolved.includes('%USER%')) {
            const username = this.getUsernameFromEnv() || 'user';
            resolved = resolved.replace(/%USER%/g, username);
        }
        
        return resolved;
    }

    /**
     * Get username from environment
     * 
     * @returns {string|null} Username or null
     */
    getUsernameFromEnv() {
        // This would normally come from the server
        // For now, we'll use a placeholder
        return null;
    }

    /**
     * Load folders from API
     */
    async loadFolders() {
        this.setLoading(true);
        try {
            const response = await fetch(this.options.apiEndpoint);
            if (!response.ok) {
                throw new Error('Failed to load watched folders');
            }
            const data = await response.json();
            
            // Extract watched_folders from config
            const folders = data.watched_folders || [];
            this.state.folders = folders.map(path => ({ path }));
            
            this.foldersTable.setData(this.state.folders);
            this.clearError();
        } catch (error) {
            this.showError('Failed to load watched folders: ' + error.message);
            console.error('Load folders error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Load audit log from API
     */
    async loadAuditLog() {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/actions`);
            if (response.ok) {
                const data = await response.json();
                this.state.auditLog = data.actions || [];
            }
        } catch (error) {
            console.error('Load audit log error:', error);
        }
    }

    /**
     * Test folder access
     */
    async testFolder() {
        // Validate path first
        const validationResult = await this.validatorUI.validateForm();
        if (!validationResult.valid) {
            return;
        }

        const path = this.formElements.path.value;
        await this.performFolderTest(path);
    }

    /**
     * Test folder by path from table
     * 
     * @param {string} path - Folder path
     */
    async testFolderByPath(path) {
        await this.performFolderTest(path);
        this.foldersTable.refresh();
    }

    /**
     * Test all folders
     */
    async testAllFolders() {
        if (this.state.folders.length === 0) {
            this.showInfo('No folders to test');
            return;
        }

        this.setTesting(true);
        const results = [];

        for (const folder of this.state.folders) {
            try {
                await this.performFolderTest(folder.path, true);
                results.push({ path: folder.path, tested: true });
            } catch (error) {
                results.push({ path: folder.path, tested: false, error: error.message });
            }
        }

        this.setTesting(false);
        this.foldersTable.refresh();
        this.showSuccess(`Tested ${results.filter(r => r.tested).length} of ${results.length} folders`);
    }

    /**
     * Perform folder test
     * 
     * @param {string} path - Folder path
     * @param {boolean} [quiet=false] - Don't show result UI
     */
    async performFolderTest(path, quiet = false) {
        if (!quiet) {
            this.setTesting(true);
            this.hideTestResult();
        }

        try {
            const resolvedPath = this.resolvePlaceholders(path);

            const response = await fetch(this.options.testEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: path,
                    resolved_path: resolvedPath
                })
            });

            const result = await response.json();
            this.state.testResults.set(path, result);

            if (!quiet) {
                this.showTestResult(result, resolvedPath);
            }

        } catch (error) {
            const result = {
                success: false,
                message: 'Folder test failed: ' + error.message
            };

            this.state.testResults.set(path, result);

            if (!quiet) {
                this.showTestResult(result, path);
            }

            console.error('Folder test error:', error);
        } finally {
            if (!quiet) {
                this.setTesting(false);
            }
        }
    }

    /**
     * Add folder
     */
    async addFolder() {
        // Validate form
        const validationResult = await this.validatorUI.validateForm();
        if (!validationResult.valid) {
            return;
        }

        const path = this.formElements.path.value;
        const createIfMissing = this.formElements.createIfMissing.checked;

        // Check for duplicates
        if (this.state.folders.some(f => f.path.toLowerCase() === path.toLowerCase())) {
            this.showError('This folder path is already being watched');
            return;
        }

        this.setLoading(true);
        try {
            // Get current folders
            const newFolders = [...this.state.folders.map(f => f.path), path];

            const response = await fetch(this.options.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    watched_folders: newFolders,
                    create_if_missing: createIfMissing
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to add folder');
            }

            // Success
            this.showSuccess(`Folder added: ${path}`);
            
            // Clear form
            this.formElements.form.reset();
            this.validator.clearErrors();
            this.clearFormValidation();
            this.hideTestResult();

            // Reload folders
            await this.loadFolders();

            // Callback
            if (this.options.onFoldersChange) {
                this.options.onFoldersChange(newFolders, 'folder_added');
            }
        } catch (error) {
            this.showError(error.message);
            console.error('Add folder error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Confirm delete folder
     * 
     * @param {string} path - Folder path
     */
    confirmDeleteFolder(path) {
        this.state.selectedFolder = path;
        this.container.querySelector('#delete-folder-path').textContent = path;
        
        const modal = new bootstrap.Modal(this.container.querySelector('#deleteFolderModal'));
        modal.show();
    }

    /**
     * Delete folder
     */
    async deleteFolder() {
        if (!this.state.selectedFolder) return;

        this.setLoading(true);
        try {
            // Get remaining folders
            const newFolders = this.state.folders
                .filter(f => f.path !== this.state.selectedFolder)
                .map(f => f.path);

            const response = await fetch(this.options.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    watched_folders: newFolders
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to remove folder');
            }

            // Success
            this.showSuccess(`Folder removed: ${this.state.selectedFolder}`);

            // Close modal
            const modal = bootstrap.Modal.getInstance(
                this.container.querySelector('#deleteFolderModal')
            );
            modal.hide();

            // Reload folders
            await this.loadFolders();

            // Callback
            if (this.options.onFoldersChange) {
                this.options.onFoldersChange(newFolders, 'folder_deleted');
            }

            this.state.selectedFolder = null;
        } catch (error) {
            this.showError(error.message);
            console.error('Delete folder error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Show audit log modal
     */
    showAuditLog() {
        const container = this.container.querySelector('#audit-log-container');
        
        if (this.state.auditLog.length === 0) {
            container.innerHTML = '<p class="text-muted small">No configuration changes recorded</p>';
        } else {
            container.innerHTML = this.state.auditLog
                .slice(-20) // Show last 20 entries
                .reverse()
                .map(entry => `
                    <div class="border-bottom pb-2 mb-2">
                        <div class="d-flex justify-content-between align-items-start">
                            <strong class="small">${this.escapeHtml(entry.action || 'Unknown')}</strong>
                            <small class="text-muted">${this.escapeHtml(entry.timestamp || 'N/A')}</small>
                        </div>
                        ${entry.details ? `<p class="small text-muted mb-0">${this.escapeHtml(entry.details)}</p>` : ''}
                    </div>
                `)
                .join('');
        }

        const modal = new bootstrap.Modal(this.container.querySelector('#auditLogModal'));
        modal.show();
    }

    /**
     * Show test result
     * 
     * @param {Object} result - Test result object
     * @param {string} path - Folder path
     */
    showTestResult(result, path) {
        const resultDiv = this.container.querySelector('#test-result');
        const alert = this.container.querySelector('#test-result-alert');
        const icon = this.container.querySelector('#test-result-icon');
        const title = this.container.querySelector('#test-result-title');
        const details = this.container.querySelector('#test-result-details');

        resultDiv.classList.remove('d-none');

        if (result.success) {
            alert.className = 'alert alert-success';
            icon.className = 'bi bi-check-circle-fill me-2';
            title.textContent = 'Folder Access OK';
            
            const detailsHtml = `
                <p><strong>Resolved Path:</strong><br><code>${this.escapeHtml(result.resolved_path || path)}</code></p>
                <p><strong>Permissions:</strong> ${result.readable ? '✓ Readable' : '✗ Not readable'} | ${result.writable ? '✓ Writable' : '✗ Not writable'}</p>
                ${result.file_count !== undefined ? `<p><strong>Files:</strong> ${result.file_count} files</p>` : ''}
                ${result.size_bytes !== undefined ? `<p><strong>Size:</strong> ${this.formatBytes(result.size_bytes)}</p>` : ''}
            `;
            details.innerHTML = detailsHtml;
        } else {
            alert.className = 'alert alert-danger';
            icon.className = 'bi bi-x-circle-fill me-2';
            title.textContent = 'Folder Access Failed';
            details.innerHTML = `<p>${this.escapeHtml(result.message || result.error || 'Unable to access folder')}</p>`;
        }
    }

    /**
     * Hide test result
     */
    hideTestResult() {
        this.container.querySelector('#test-result').classList.add('d-none');
    }

    /**
     * Clear form validation UI
     */
    clearFormValidation() {
        const inputs = this.formElements.form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');
        });
    }

    /**
     * Show error message
     * 
     * @param {string} message - Error message
     */
    showError(message) {
        this.state.error = message;
        const alert = this.container.querySelector('#folders-error-alert');
        const messageEl = this.container.querySelector('#folders-error-message');
        messageEl.textContent = message;
        alert.classList.remove('d-none');
        
        setTimeout(() => this.clearError(), 5000);
    }

    /**
     * Clear error message
     */
    clearError() {
        this.state.error = null;
        this.container.querySelector('#folders-error-alert').classList.add('d-none');
    }

    /**
     * Show success message
     * 
     * @param {string} message - Success message
     */
    showSuccess(message) {
        const alert = this.container.querySelector('#folders-success-alert');
        const messageEl = this.container.querySelector('#folders-success-message');
        messageEl.textContent = message;
        alert.classList.remove('d-none');
        
        setTimeout(() => {
            alert.classList.add('d-none');
        }, 3000);
    }

    /**
     * Show info message
     * 
     * @param {string} message - Info message
     */
    showInfo(message) {
        const alert = this.container.querySelector('#folders-info-alert');
        const messageEl = this.container.querySelector('#folders-info-message');
        messageEl.textContent = message;
        alert.classList.remove('d-none');
        
        setTimeout(() => {
            alert.classList.add('d-none');
        }, 3000);
    }

    /**
     * Set loading state
     * 
     * @param {boolean} loading - Loading state
     */
    setLoading(loading) {
        this.state.loading = loading;
        const addBtn = this.container.querySelector('#add-folder-btn');
        const deleteBtn = this.container.querySelector('#confirm-delete-folder-btn');
        
        if (loading) {
            addBtn.disabled = true;
            deleteBtn.disabled = true;
            addBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Adding...';
        } else {
            addBtn.disabled = false;
            deleteBtn.disabled = false;
            addBtn.innerHTML = '<i class="bi bi-plus-circle me-1"></i> Add Folder';
        }
    }

    /**
     * Set testing state
     * 
     * @param {boolean} testing - Testing state
     */
    setTesting(testing) {
        this.state.testing = testing;
        const testBtn = this.container.querySelector('#test-folder-btn');
        const testAllBtn = this.container.querySelector('#test-all-btn');
        
        if (testing) {
            testBtn.disabled = true;
            testAllBtn.disabled = true;
            testBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Testing...';
            testAllBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Testing...';
        } else {
            testBtn.disabled = false;
            testAllBtn.disabled = false;
            testBtn.innerHTML = '<i class="bi bi-folder-check me-1"></i> Test Folder';
            testAllBtn.innerHTML = '<i class="bi bi-lightning-charge me-1"></i> Test All';
        }
    }

    /**
     * Format bytes to human readable
     * 
     * @param {number} bytes - Bytes to format
     * @returns {string} Formatted bytes
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    /**
     * Escape HTML to prevent XSS
     * 
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Destroy the module and cleanup
     */
    destroy() {
        if (this.foldersTable) {
            this.foldersTable.setData([]);
        }
        this.container.innerHTML = '';
    }
}

// Export as default
export default WatchedFoldersConfig;
