/**
 * Network Targets Configuration Module
 * 
 * Manages NAS/SMB network share connections with templates for common platforms.
 * Provides connection testing and credential management for remote file destinations.
 * 
 * Features:
 * - NAS platform templates (Synology, QNAP, Windows, Generic)
 * - Connection testing with backend validation
 * - UNC path management
 * - Credential storage and editing
 * - Target list with CRUD operations
 * - Real-time connection status
 * 
 * Dependencies:
 * - FormValidator (utilities/form-validator.js)
 * - TableManager (utilities/table-manager.js)
 * - TemplateEngine (utilities/template-engine.js)
 * 
 * @module network-targets-config
 * @version 1.0.0
 */

import { FormValidator, FormValidatorUI } from '../utilities/form-validator.js';
import { TableManager } from '../utilities/table-manager.js';
import { TemplateEngine } from '../utilities/template-engine.js';

/**
 * NAS platform templates with connection details
 * @constant {Object.<string, Object>}
 */
const NAS_TEMPLATES = {
    synology: {
        name: 'Synology NAS',
        icon: '🔷',
        defaultPort: 445,
        pathPattern: '\\\\{hostname}\\{share}',
        pathPlaceholder: '\\\\synology.local\\downloads',
        authRequired: true,
        description: 'Synology DiskStation or RackStation',
        hints: [
            'Enable SMB service in Control Panel > File Services',
            'Create a shared folder in Control Panel > Shared Folder',
            'Use your DSM username and password',
            'Common share names: homes, downloads, backup'
        ]
    },
    qnap: {
        name: 'QNAP NAS',
        icon: '🔶',
        defaultPort: 445,
        pathPattern: '\\\\{hostname}\\{share}',
        pathPlaceholder: '\\\\qnap.local\\downloads',
        authRequired: true,
        description: 'QNAP Turbo NAS',
        hints: [
            'Enable SMB service in Control Panel > Network Services > SMB/CIFS',
            'Create a shared folder in Control Panel > Privilege > Shared Folders',
            'Use your QTS username and password',
            'Common share names: Public, Downloads, Multimedia'
        ]
    },
    windows: {
        name: 'Windows Share',
        icon: '💻',
        defaultPort: 445,
        pathPattern: '\\\\{hostname}\\{share}',
        pathPlaceholder: '\\\\server\\shared-folder',
        authRequired: true,
        description: 'Windows network share',
        hints: [
            'Share folders via File Explorer > Properties > Sharing',
            'Use domain\\username or computer\\username format',
            'For workgroups, use computer name as domain',
            'Enable Network Discovery in Network Settings'
        ]
    },
    generic: {
        name: 'Generic SMB',
        icon: '📁',
        defaultPort: 445,
        pathPattern: '\\\\{hostname}\\{share}',
        pathPlaceholder: '\\\\nas-device\\share',
        authRequired: false,
        description: 'Generic SMB/CIFS network share',
        hints: [
            'Works with any SMB-compatible device',
            'Use UNC path format: \\\\hostname\\share',
            'Authentication may be required depending on share settings',
            'Test connection to verify access'
        ]
    }
};

/**
 * Network Targets Configuration Manager
 * 
 * Manages NAS/SMB network share connections including templates,
 * connection testing, and credential management.
 */
export class NetworkTargetsConfig {
    /**
     * Initialize the Network Targets configuration manager
     * 
     * @param {string} containerSelector - CSS selector for container element
     * @param {Object} options - Configuration options
     * @param {string} [options.apiEndpoint='/api/dashboard/config'] - API endpoint for target operations
     * @param {string} [options.testEndpoint='/api/test-nas'] - API endpoint for connection testing
     * @param {Function} [options.onTargetChange] - Callback when targets are modified
     */
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            throw new Error(`Container not found: ${containerSelector}`);
        }

        // Configuration options
        this.options = {
            apiEndpoint: options.apiEndpoint || '/api/dashboard/config',
            testEndpoint: options.testEndpoint || '/api/test-nas',
            onTargetChange: options.onTargetChange || null
        };

        // State management
        this.state = {
            targets: [],
            selectedTemplate: null,
            selectedTarget: null,
            editMode: false,
            testResults: new Map(), // targetId -> test result
            loading: false,
            testing: false,
            error: null
        };

        // Components
        this.validator = null;
        this.validatorUI = null;
        this.targetTable = null;
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
        await this.loadTargets();
    }

    /**
     * Render the UI structure
     */
    render() {
        this.container.innerHTML = `
            <div class="network-targets-config">
                <!-- Header -->
                <div class="config-header mb-4">
                    <h3 class="mb-0">Network Targets</h3>
                    <p class="text-muted">Configure NAS and SMB network share connections</p>
                </div>

                <!-- Error Display -->
                <div id="target-error-alert" class="alert alert-danger d-none" role="alert">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <span id="target-error-message"></span>
                </div>

                <!-- Success Display -->
                <div id="target-success-alert" class="alert alert-success d-none" role="alert">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    <span id="target-success-message"></span>
                </div>

                <!-- Two Column Layout -->
                <div class="row">
                    <!-- Left: Templates & Form -->
                    <div class="col-lg-5 mb-4">
                        <!-- Template Selection -->
                        <div class="card mb-3">
                            <div class="card-header">
                                <h5 class="mb-0">1. Select Platform</h5>
                            </div>
                            <div class="card-body">
                                <div id="template-selector" class="row g-2">
                                    ${Object.entries(NAS_TEMPLATES).map(([key, template]) => `
                                        <div class="col-6">
                                            <button class="btn btn-outline-primary w-100 template-btn" 
                                                    data-template="${key}">
                                                <div class="template-icon fs-2">${template.icon}</div>
                                                <div class="template-name small">${template.name}</div>
                                            </button>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>

                        <!-- Connection Form -->
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">2. Configure Connection</h5>
                            </div>
                            <div class="card-body">
                                <form id="target-form">
                                    <!-- Template Info -->
                                    <div id="template-info" class="alert alert-info d-none mb-3">
                                        <div class="d-flex align-items-start">
                                            <div id="template-icon-display" class="me-2 fs-4"></div>
                                            <div class="flex-grow-1">
                                                <strong id="template-name-display"></strong>
                                                <p id="template-description" class="mb-0 small"></p>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Target Name -->
                                    <div class="mb-3">
                                        <label for="target-name" class="form-label">
                                            Connection Name <span class="text-danger">*</span>
                                        </label>
                                        <input type="text" class="form-control" id="target-name" 
                                               name="name" required placeholder="My NAS">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Friendly name to identify this connection</div>
                                    </div>

                                    <!-- UNC Path -->
                                    <div class="mb-3">
                                        <label for="target-path" class="form-label">
                                            UNC Path <span class="text-danger">*</span>
                                        </label>
                                        <input type="text" class="form-control font-monospace" 
                                               id="target-path" name="path" required
                                               placeholder="\\\\hostname\\share">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Network path in UNC format</div>
                                    </div>

                                    <!-- Username -->
                                    <div class="mb-3">
                                        <label for="target-username" class="form-label">
                                            Username
                                        </label>
                                        <input type="text" class="form-control" id="target-username" 
                                               name="username" placeholder="domain\\username">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Leave blank for guest/anonymous access</div>
                                    </div>

                                    <!-- Password -->
                                    <div class="mb-3">
                                        <label for="target-password" class="form-label">
                                            Password
                                        </label>
                                        <div class="input-group">
                                            <input type="password" class="form-control" 
                                                   id="target-password" name="password">
                                            <button class="btn btn-outline-secondary" type="button" 
                                                    id="toggle-target-password">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                        </div>
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Leave blank for guest/anonymous access</div>
                                    </div>

                                    <!-- Port -->
                                    <div class="mb-3">
                                        <label for="target-port" class="form-label">
                                            Port
                                        </label>
                                        <input type="number" class="form-control" id="target-port" 
                                               name="port" value="445" min="1" max="65535">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Default SMB port is 445</div>
                                    </div>

                                    <!-- Hints -->
                                    <div id="template-hints" class="d-none">
                                        <div class="alert alert-light">
                                            <strong>💡 Tips:</strong>
                                            <ul id="template-hints-list" class="mb-0 mt-2 small"></ul>
                                        </div>
                                    </div>

                                    <!-- Action Buttons -->
                                    <div class="d-flex gap-2">
                                        <button type="button" id="test-connection-btn" 
                                                class="btn btn-outline-primary flex-grow-1">
                                            <i class="bi bi-plug me-1"></i> Test Connection
                                        </button>
                                        <button type="button" id="save-target-btn" 
                                                class="btn btn-primary flex-grow-1">
                                            <i class="bi bi-save me-1"></i> Save Target
                                        </button>
                                    </div>

                                    <!-- Test Result -->
                                    <div id="test-result" class="mt-3 d-none">
                                        <div class="alert" id="test-result-alert">
                                            <div class="d-flex align-items-center">
                                                <i id="test-result-icon" class="me-2"></i>
                                                <div class="flex-grow-1">
                                                    <strong id="test-result-title"></strong>
                                                    <p id="test-result-message" class="mb-0 small"></p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Saved Targets -->
                    <div class="col-lg-7">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">Saved Targets</h5>
                                <button id="clear-form-btn" class="btn btn-sm btn-outline-secondary">
                                    <i class="bi bi-plus-circle me-1"></i> New Target
                                </button>
                            </div>
                            <div class="card-body">
                                <div id="targets-table-container"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Delete Confirmation Modal -->
                <div class="modal fade" id="deleteTargetModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">Delete Target</h5>
                                <button type="button" class="btn-close btn-close-white" 
                                        data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>Are you sure you want to delete target 
                                   <strong id="delete-target-name"></strong>?</p>
                                <p class="text-danger mb-0">
                                    <i class="bi bi-exclamation-triangle me-1"></i>
                                    This will remove the connection configuration.
                                </p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" 
                                        data-bs-dismiss="modal">Cancel</button>
                                <button type="button" id="confirm-delete-target-btn" 
                                        class="btn btn-danger">
                                    <i class="bi bi-trash me-1"></i> Delete Target
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Store form element references
        this.formElements = {
            form: this.container.querySelector('#target-form'),
            name: this.container.querySelector('#target-name'),
            path: this.container.querySelector('#target-path'),
            username: this.container.querySelector('#target-username'),
            password: this.container.querySelector('#target-password'),
            port: this.container.querySelector('#target-port')
        };
    }

    /**
     * Setup form validation
     */
    setupValidator() {
        this.validator = new FormValidator();
        this.validatorUI = new FormValidatorUI(this.validator);

        // Target name validation
        this.validator.addRule('name', {
            type: 'required',
            message: 'Connection name is required'
        });
        this.validator.addRule('name', {
            type: 'minLength',
            value: 2,
            message: 'Name must be at least 2 characters'
        });

        // UNC path validation
        this.validator.addRule('path', {
            type: 'required',
            message: 'UNC path is required'
        });
        this.validator.addRule('path', {
            type: 'uncPath',
            message: 'Invalid UNC path format. Use \\\\hostname\\share'
        });

        // Port validation
        this.validator.addRule('port', {
            type: 'port',
            message: 'Port must be between 1 and 65535'
        });

        // Bind UI validation
        this.validatorUI.bindField('name', this.formElements.name, { 
            debounce: 300,
            showSuccess: true
        });
        this.validatorUI.bindField('path', this.formElements.path, { 
            debounce: 300,
            showSuccess: true
        });
        this.validatorUI.bindField('port', this.formElements.port);
    }

    /**
     * Setup targets table
     */
    setupTable() {
        this.targetTable = new TableManager('#targets-table-container', {
            columns: [
                {
                    key: 'name',
                    label: 'Name',
                    sortable: true,
                    render: (value, row) => {
                        const template = NAS_TEMPLATES[row.template];
                        const icon = template?.icon || '📁';
                        return `${icon} <strong>${this.escapeHtml(value)}</strong>`;
                    }
                },
                {
                    key: 'path',
                    label: 'Path',
                    sortable: true,
                    render: (value) => `<code class="small">${this.escapeHtml(value)}</code>`
                },
                {
                    key: 'username',
                    label: 'Username',
                    sortable: true,
                    render: (value) => value 
                        ? this.escapeHtml(value)
                        : '<em class="text-muted">Guest</em>'
                },
                {
                    key: 'status',
                    label: 'Status',
                    sortable: false,
                    render: (value, row) => {
                        const testResult = this.state.testResults.get(row.id);
                        if (!testResult) {
                            return '<span class="badge bg-secondary">Not Tested</span>';
                        }
                        if (testResult.success) {
                            return '<span class="badge bg-success">Connected</span>';
                        } else {
                            return '<span class="badge bg-danger" title="' + 
                                   this.escapeHtml(testResult.message) + '">Failed</span>';
                        }
                    }
                },
                {
                    key: 'actions',
                    label: 'Actions',
                    sortable: false,
                    render: (value, row) => `
                        <button class="btn btn-sm btn-outline-primary test-target" 
                                data-target-id="${row.id}">
                            <i class="bi bi-plug"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary edit-target" 
                                data-target-id="${row.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-target" 
                                data-target-id="${row.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    `
                }
            ],
            data: [],
            paginate: true,
            pageSize: 5,
            sortable: true
        });
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Template selection
        this.container.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const templateKey = e.currentTarget.dataset.template;
                this.selectTemplate(templateKey);
            });
        });

        // Test connection
        this.container.querySelector('#test-connection-btn').addEventListener('click', () => {
            this.testConnection();
        });

        // Save target
        this.container.querySelector('#save-target-btn').addEventListener('click', () => {
            this.saveTarget();
        });

        // Clear form (new target)
        this.container.querySelector('#clear-form-btn').addEventListener('click', () => {
            this.clearForm();
        });

        // Toggle password visibility
        this.container.querySelector('#toggle-target-password').addEventListener('click', (e) => {
            const input = this.formElements.password;
            const icon = e.currentTarget.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });

        // Table row actions (test/edit/delete) - using event delegation
        this.container.addEventListener('click', (e) => {
            if (e.target.closest('.test-target')) {
                const targetId = e.target.closest('.test-target').dataset.targetId;
                this.testTargetById(targetId);
            } else if (e.target.closest('.edit-target')) {
                const targetId = e.target.closest('.edit-target').dataset.targetId;
                this.editTarget(targetId);
            } else if (e.target.closest('.delete-target')) {
                const targetId = e.target.closest('.delete-target').dataset.targetId;
                this.confirmDeleteTarget(targetId);
            }
        });

        // Delete confirmation
        this.container.querySelector('#confirm-delete-target-btn').addEventListener('click', () => {
            this.deleteTarget();
        });
    }

    /**
     * Select a NAS template
     * 
     * @param {string} templateKey - Template key
     */
    selectTemplate(templateKey) {
        const template = NAS_TEMPLATES[templateKey];
        if (!template) return;

        this.state.selectedTemplate = templateKey;

        // Highlight selected button
        this.container.querySelectorAll('.template-btn').forEach(btn => {
            if (btn.dataset.template === templateKey) {
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-primary');
            } else {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
            }
        });

        // Show template info
        const infoDiv = this.container.querySelector('#template-info');
        infoDiv.classList.remove('d-none');
        this.container.querySelector('#template-icon-display').textContent = template.icon;
        this.container.querySelector('#template-name-display').textContent = template.name;
        this.container.querySelector('#template-description').textContent = template.description;

        // Update form placeholders
        this.formElements.path.placeholder = template.pathPlaceholder;
        this.formElements.port.value = template.defaultPort;

        // Show hints
        const hintsDiv = this.container.querySelector('#template-hints');
        const hintsList = this.container.querySelector('#template-hints-list');
        if (template.hints && template.hints.length > 0) {
            hintsDiv.classList.remove('d-none');
            hintsList.innerHTML = template.hints
                .map(hint => `<li>${this.escapeHtml(hint)}</li>`)
                .join('');
        } else {
            hintsDiv.classList.add('d-none');
        }
    }

    /**
     * Load targets from API
     */
    async loadTargets() {
        this.setLoading(true);
        try {
            const response = await fetch(this.options.apiEndpoint);
            if (!response.ok) {
                throw new Error('Failed to load network targets');
            }
            const data = await response.json();
            this.state.targets = data.network_targets || [];
            this.targetTable.setData(this.state.targets);
            this.clearError();
        } catch (error) {
            this.showError('Failed to load targets: ' + error.message);
            console.error('Load targets error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Test connection with current form values
     */
    async testConnection() {
        // Validate form first
        const validationResult = await this.validatorUI.validateForm();
        if (!validationResult.valid) {
            return;
        }

        const formData = this.getFormData();
        await this.performConnectionTest(formData);
    }

    /**
     * Test a saved target by ID
     * 
     * @param {string} targetId - Target ID
     */
    async testTargetById(targetId) {
        const target = this.state.targets.find(t => t.id === targetId);
        if (!target) return;

        await this.performConnectionTest(target);
        
        // Refresh table to show updated status
        this.targetTable.refresh();
    }

    /**
     * Perform connection test
     * 
     * @param {Object} targetData - Target data to test
     */
    async performConnectionTest(targetData) {
        this.setTesting(true);
        this.hideTestResult();

        try {
            const response = await fetch(this.options.testEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: targetData.path,
                    username: targetData.username || null,
                    password: targetData.password || null,
                    port: targetData.port || 445
                })
            });

            const result = await response.json();

            if (targetData.id) {
                this.state.testResults.set(targetData.id, result);
            }

            this.showTestResult(result);

        } catch (error) {
            const result = {
                success: false,
                message: 'Connection test failed: ' + error.message,
                error: error.message
            };

            if (targetData.id) {
                this.state.testResults.set(targetData.id, result);
            }

            this.showTestResult(result);
            console.error('Connection test error:', error);
        } finally {
            this.setTesting(false);
        }
    }

    /**
     * Save target (create or update)
     */
    async saveTarget() {
        // Validate form
        const validationResult = await this.validatorUI.validateForm();
        if (!validationResult.valid) {
            return;
        }

        const targetData = this.getFormData();

        this.setLoading(true);
        try {
            const url = this.state.editMode
                ? `${this.options.apiEndpoint}/network-targets/${this.state.selectedTarget.id}`
                : `${this.options.apiEndpoint}/network-targets`;
            
            const method = this.state.editMode ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(targetData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to save target');
            }

            // Success
            const action = this.state.editMode ? 'updated' : 'created';
            this.showSuccess(`Target ${targetData.name} ${action} successfully`);

            // Clear form
            this.clearForm();

            // Reload targets
            await this.loadTargets();

            // Callback
            if (this.options.onTargetChange) {
                this.options.onTargetChange(targetData, action);
            }
        } catch (error) {
            this.showError(error.message);
            console.error('Save target error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Edit target
     * 
     * @param {string} targetId - Target ID
     */
    editTarget(targetId) {
        const target = this.state.targets.find(t => t.id === targetId);
        if (!target) return;

        this.state.editMode = true;
        this.state.selectedTarget = target;

        // Select template
        if (target.template) {
            this.selectTemplate(target.template);
        }

        // Fill form
        this.formElements.name.value = target.name;
        this.formElements.path.value = target.path;
        this.formElements.username.value = target.username || '';
        this.formElements.password.value = ''; // Don't show stored password
        this.formElements.port.value = target.port || 445;

        // Scroll to form
        this.container.querySelector('.card').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    /**
     * Confirm delete target
     * 
     * @param {string} targetId - Target ID
     */
    confirmDeleteTarget(targetId) {
        this.state.selectedTarget = this.state.targets.find(t => t.id === targetId);
        if (!this.state.selectedTarget) return;

        this.container.querySelector('#delete-target-name').textContent = 
            this.state.selectedTarget.name;
        
        const modal = new bootstrap.Modal(this.container.querySelector('#deleteTargetModal'));
        modal.show();
    }

    /**
     * Delete target
     */
    async deleteTarget() {
        if (!this.state.selectedTarget) return;

        this.setLoading(true);
        try {
            const response = await fetch(
                `${this.options.apiEndpoint}/network-targets/${this.state.selectedTarget.id}`,
                { method: 'DELETE' }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to delete target');
            }

            // Success
            this.showSuccess(`Target ${this.state.selectedTarget.name} deleted successfully`);

            // Close modal
            const modal = bootstrap.Modal.getInstance(
                this.container.querySelector('#deleteTargetModal')
            );
            modal.hide();

            // Clear if editing this target
            if (this.state.editMode && 
                this.state.selectedTarget.id === this.state.selectedTarget?.id) {
                this.clearForm();
            }

            // Reload targets
            await this.loadTargets();

            // Callback
            if (this.options.onTargetChange) {
                this.options.onTargetChange(this.state.selectedTarget, 'deleted');
            }

            this.state.selectedTarget = null;
        } catch (error) {
            this.showError(error.message);
            console.error('Delete target error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Clear form and reset to new target mode
     */
    clearForm() {
        this.state.editMode = false;
        this.state.selectedTarget = null;
        this.formElements.form.reset();
        this.validator.clearErrors();
        this.clearFormValidation();
        this.hideTestResult();

        // Deselect template
        this.container.querySelectorAll('.template-btn').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-primary');
        });
        this.container.querySelector('#template-info').classList.add('d-none');
        this.container.querySelector('#template-hints').classList.add('d-none');
    }

    /**
     * Get form data
     * 
     * @returns {Object} Form data
     */
    getFormData() {
        return {
            template: this.state.selectedTemplate,
            name: this.formElements.name.value,
            path: this.formElements.path.value,
            username: this.formElements.username.value || null,
            password: this.formElements.password.value || null,
            port: parseInt(this.formElements.port.value) || 445
        };
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
     * Show test result
     * 
     * @param {Object} result - Test result object
     */
    showTestResult(result) {
        const resultDiv = this.container.querySelector('#test-result');
        const alert = this.container.querySelector('#test-result-alert');
        const icon = this.container.querySelector('#test-result-icon');
        const title = this.container.querySelector('#test-result-title');
        const message = this.container.querySelector('#test-result-message');

        resultDiv.classList.remove('d-none');

        if (result.success) {
            alert.className = 'alert alert-success';
            icon.className = 'bi bi-check-circle-fill me-2';
            title.textContent = 'Connection Successful';
            message.textContent = result.message || 'Network share is accessible';
        } else {
            alert.className = 'alert alert-danger';
            icon.className = 'bi bi-x-circle-fill me-2';
            title.textContent = 'Connection Failed';
            message.textContent = result.message || result.error || 'Unable to connect';
        }
    }

    /**
     * Hide test result
     */
    hideTestResult() {
        this.container.querySelector('#test-result').classList.add('d-none');
    }

    /**
     * Show error message
     * 
     * @param {string} message - Error message
     */
    showError(message) {
        this.state.error = message;
        const alert = this.container.querySelector('#target-error-alert');
        const messageEl = this.container.querySelector('#target-error-message');
        messageEl.textContent = message;
        alert.classList.remove('d-none');
        
        setTimeout(() => this.clearError(), 5000);
    }

    /**
     * Clear error message
     */
    clearError() {
        this.state.error = null;
        this.container.querySelector('#target-error-alert').classList.add('d-none');
    }

    /**
     * Show success message
     * 
     * @param {string} message - Success message
     */
    showSuccess(message) {
        const alert = this.container.querySelector('#target-success-alert');
        const messageEl = this.container.querySelector('#target-success-message');
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
        const saveBtn = this.container.querySelector('#save-target-btn');
        const deleteBtn = this.container.querySelector('#confirm-delete-target-btn');
        
        if (loading) {
            saveBtn.disabled = true;
            deleteBtn.disabled = true;
            saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';
        } else {
            saveBtn.disabled = false;
            deleteBtn.disabled = false;
            saveBtn.innerHTML = '<i class="bi bi-save me-1"></i> Save Target';
        }
    }

    /**
     * Set testing state
     * 
     * @param {boolean} testing - Testing state
     */
    setTesting(testing) {
        this.state.testing = testing;
        const testBtn = this.container.querySelector('#test-connection-btn');
        
        if (testing) {
            testBtn.disabled = true;
            testBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Testing...';
        } else {
            testBtn.disabled = false;
            testBtn.innerHTML = '<i class="bi bi-plug me-1"></i> Test Connection';
        }
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
        if (this.targetTable) {
            this.targetTable.setData([]);
        }
        this.container.innerHTML = '';
    }
}

// Export as default
export default NetworkTargetsConfig;
