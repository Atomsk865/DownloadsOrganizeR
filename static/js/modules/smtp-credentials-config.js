/**
 * SMTP & Credentials Configuration Module
 * 
 * Manages email (SMTP) configuration and credential vault for secure storage.
 * Provides email testing and credentials management for notifications.
 * 
 * Features:
 * - SMTP provider templates (Gmail, Outlook, Office 365, Yahoo)
 * - Email configuration form with validation
 * - Test email functionality
 * - Credentials vault for secure password storage
 * - Add/edit/delete credentials
 * - Email address validation
 * - Template-based SMTP setup
 * 
 * Dependencies:
 * - FormValidator (utilities/form-validator.js)
 * - TableManager (utilities/table-manager.js)
 * - TemplateEngine (utilities/template-engine.js)
 * 
 * @module smtp-credentials-config
 * @version 1.0.0
 */

import { FormValidator, FormValidatorUI } from '../utilities/form-validator.js';
import { TableManager } from '../utilities/table-manager.js';
import { TemplateEngine } from '../utilities/template-engine.js';

/**
 * SMTP provider templates with connection details
 * @constant {Object.<string, Object>}
 */
const SMTP_TEMPLATES = {
    gmail: {
        name: 'Gmail',
        icon: '📧',
        host: 'smtp.gmail.com',
        port: 587,
        encryption: 'tls',
        description: 'Google Gmail SMTP',
        hints: [
            'Use your Gmail address as sender email',
            'Generate an App Password (not your regular password)',
            'Enable 2FA on your Google account first',
            'Visit myaccount.google.com/apppasswords to generate app password',
            'Use full email address as username (e.g., user@gmail.com)'
        ]
    },
    outlook: {
        name: 'Outlook.com',
        icon: '💼',
        host: 'smtp-mail.outlook.com',
        port: 587,
        encryption: 'tls',
        description: 'Microsoft Outlook.com SMTP',
        hints: [
            'Use your Outlook email address',
            'Use your Outlook password (or app password if 2FA enabled)',
            'Enable IMAP/POP access in account settings if needed',
            'Port 587 with TLS encryption',
            'Support for Outlook.com and Live.com addresses'
        ]
    },
    office365: {
        name: 'Office 365',
        icon: '☁️',
        host: 'smtp.office365.com',
        port: 587,
        encryption: 'tls',
        description: 'Microsoft Office 365 SMTP',
        hints: [
            'Use your Office 365 business email',
            'Use app password if 2FA is enabled',
            'Port 587 with TLS encryption',
            'Ensure mailbox is Exchange Online enabled',
            'Contact your admin if you cannot send mail'
        ]
    },
    yahoo: {
        name: 'Yahoo Mail',
        icon: '📬',
        host: 'smtp.mail.yahoo.com',
        port: 587,
        encryption: 'tls',
        description: 'Yahoo Mail SMTP',
        hints: [
            'Use your Yahoo email address',
            'Generate an app password (not your regular password)',
            'Enable 2FA on your Yahoo account first',
            'Visit account.yahoo.com/security to generate app password',
            'Port 587 with TLS encryption required'
        ]
    },
    custom: {
        name: 'Custom SMTP',
        icon: '⚙️',
        host: '',
        port: 587,
        encryption: 'none',
        description: 'Configure custom SMTP server',
        hints: [
            'Enter your SMTP server hostname',
            'Specify the correct port (typically 25, 465, 587, or 2525)',
            'Choose encryption: None, SSL/TLS, or STARTTLS',
            'Use full credentials for authentication',
            'Test connection before saving'
        ]
    }
};

/**
 * Encryption methods for SMTP
 * @constant {Object.<string, Object>}
 */
const ENCRYPTION_METHODS = {
    'none': { label: 'None', description: 'No encryption' },
    'tls': { label: 'STARTTLS', description: 'TLS upgrade on connection' },
    'ssl': { label: 'SSL/TLS', description: 'SSL encryption from start' }
};

/**
 * SMTP & Credentials Configuration Manager
 * 
 * Manages SMTP configuration and secure credential storage for email functionality.
 */
export class SMTPCredentialsConfig {
    /**
     * Initialize the SMTP & Credentials configuration manager
     * 
     * @param {string} containerSelector - CSS selector for container element
     * @param {Object} options - Configuration options
     * @param {string} [options.apiEndpoint='/api/dashboard/config'] - API endpoint for SMTP config
     * @param {string} [options.testEndpoint='/api/test-smtp'] - API endpoint for email testing
     * @param {Function} [options.onConfigChange] - Callback when config is modified
     */
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            throw new Error(`Container not found: ${containerSelector}`);
        }

        // Configuration options
        this.options = {
            apiEndpoint: options.apiEndpoint || '/api/dashboard/config',
            testEndpoint: options.testEndpoint || '/api/test-smtp',
            onConfigChange: options.onConfigChange || null
        };

        // State management
        this.state = {
            smtp: {}, // Current SMTP configuration
            credentials: [], // Stored credentials list
            selectedTemplate: null,
            editMode: false,
            testStatus: null,
            loading: false,
            testing: false,
            error: null
        };

        // Components
        this.validator = null;
        this.validatorUI = null;
        this.credentialsTable = null;
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
        await this.loadSMTPConfig();
        await this.loadCredentials();
    }

    /**
     * Render the UI structure
     */
    render() {
        this.container.innerHTML = `
            <div class="smtp-credentials-config">
                <!-- Header -->
                <div class="config-header mb-4">
                    <h3 class="mb-0">SMTP & Credentials</h3>
                    <p class="text-muted">Configure email server and manage credentials vault</p>
                </div>

                <!-- Error Display -->
                <div id="smtp-error-alert" class="alert alert-danger d-none" role="alert">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <span id="smtp-error-message"></span>
                </div>

                <!-- Success Display -->
                <div id="smtp-success-alert" class="alert alert-success d-none" role="alert">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    <span id="smtp-success-message"></span>
                </div>

                <!-- Two Column Layout -->
                <div class="row">
                    <!-- Left: SMTP Configuration -->
                    <div class="col-lg-5 mb-4">
                        <!-- Template Selection -->
                        <div class="card mb-3">
                            <div class="card-header">
                                <h5 class="mb-0">1. Select Email Provider</h5>
                            </div>
                            <div class="card-body">
                                <div id="smtp-template-selector" class="row g-2">
                                    ${Object.entries(SMTP_TEMPLATES).map(([key, template]) => `
                                        <div class="col-6">
                                            <button class="btn btn-outline-primary w-100 smtp-template-btn" 
                                                    data-template="${key}">
                                                <div class="template-icon fs-2">${template.icon}</div>
                                                <div class="template-name small">${template.name}</div>
                                            </button>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>

                        <!-- SMTP Configuration Form -->
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">2. Configure SMTP</h5>
                            </div>
                            <div class="card-body">
                                <form id="smtp-form">
                                    <!-- Template Info -->
                                    <div id="smtp-template-info" class="alert alert-info d-none mb-3">
                                        <div class="d-flex align-items-start">
                                            <div id="smtp-template-icon" class="me-2 fs-4"></div>
                                            <div class="flex-grow-1">
                                                <strong id="smtp-template-name"></strong>
                                                <p id="smtp-template-description" class="mb-0 small"></p>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Sender Email -->
                                    <div class="mb-3">
                                        <label for="smtp-sender-email" class="form-label">
                                            Sender Email <span class="text-danger">*</span>
                                        </label>
                                        <input type="email" class="form-control" id="smtp-sender-email" 
                                               name="sender_email" required placeholder="notifications@example.com">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Email address for sending notifications</div>
                                    </div>

                                    <!-- Sender Name -->
                                    <div class="mb-3">
                                        <label for="smtp-sender-name" class="form-label">
                                            Sender Name
                                        </label>
                                        <input type="text" class="form-control" id="smtp-sender-name" 
                                               name="sender_name" placeholder="File Organizer">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Display name for sent emails</div>
                                    </div>

                                    <!-- SMTP Host -->
                                    <div class="mb-3">
                                        <label for="smtp-host" class="form-label">
                                            SMTP Server <span class="text-danger">*</span>
                                        </label>
                                        <input type="text" class="form-control font-monospace" 
                                               id="smtp-host" name="host" required
                                               placeholder="smtp.gmail.com">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">SMTP server hostname</div>
                                    </div>

                                    <!-- Port -->
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <label for="smtp-port" class="form-label">
                                                Port <span class="text-danger">*</span>
                                            </label>
                                            <input type="number" class="form-control" id="smtp-port" 
                                                   name="port" value="587" required min="1" max="65535">
                                            <div class="invalid-feedback"></div>
                                        </div>
                                        <div class="col-md-6">
                                            <label for="smtp-encryption" class="form-label">
                                                Encryption <span class="text-danger">*</span>
                                            </label>
                                            <select class="form-select" id="smtp-encryption" 
                                                    name="encryption" required>
                                                <option value="">Select...</option>
                                                ${Object.entries(ENCRYPTION_METHODS).map(([key, enc]) => `
                                                    <option value="${key}">${enc.label}</option>
                                                `).join('')}
                                            </select>
                                            <div class="invalid-feedback"></div>
                                        </div>
                                    </div>

                                    <!-- Username -->
                                    <div class="mb-3">
                                        <label for="smtp-username" class="form-label">
                                            Username <span class="text-danger">*</span>
                                        </label>
                                        <input type="text" class="form-control" id="smtp-username" 
                                               name="username" required placeholder="user@gmail.com">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">SMTP authentication username</div>
                                    </div>

                                    <!-- Password -->
                                    <div class="mb-3">
                                        <label for="smtp-password" class="form-label">
                                            Password <span class="text-danger">*</span>
                                        </label>
                                        <div class="input-group">
                                            <input type="password" class="form-control" 
                                                   id="smtp-password" name="password" required>
                                            <button class="btn btn-outline-secondary" type="button" 
                                                    id="toggle-smtp-password">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                        </div>
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">SMTP authentication password or app password</div>
                                    </div>

                                    <!-- Hints -->
                                    <div id="smtp-template-hints" class="d-none">
                                        <div class="alert alert-light">
                                            <strong>💡 Setup Tips:</strong>
                                            <ul id="smtp-template-hints-list" class="mb-0 mt-2 small"></ul>
                                        </div>
                                    </div>

                                    <!-- Action Buttons -->
                                    <div class="d-flex gap-2">
                                        <button type="button" id="test-smtp-btn" 
                                                class="btn btn-outline-primary flex-grow-1">
                                            <i class="bi bi-send me-1"></i> Send Test Email
                                        </button>
                                        <button type="button" id="save-smtp-btn" 
                                                class="btn btn-primary flex-grow-1">
                                            <i class="bi bi-save me-1"></i> Save Configuration
                                        </button>
                                    </div>

                                    <!-- Test Result -->
                                    <div id="smtp-test-result" class="mt-3 d-none">
                                        <div class="alert" id="smtp-test-result-alert">
                                            <div class="d-flex align-items-center">
                                                <i id="smtp-test-result-icon" class="me-2"></i>
                                                <div class="flex-grow-1">
                                                    <strong id="smtp-test-result-title"></strong>
                                                    <p id="smtp-test-result-message" class="mb-0 small"></p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Credentials Vault -->
                    <div class="col-lg-7">
                        <div class="card mb-3">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">Credentials Vault</h5>
                                <button id="add-credential-btn" class="btn btn-sm btn-primary">
                                    <i class="bi bi-plus-circle me-1"></i> Add Credential
                                </button>
                            </div>
                            <div class="card-body">
                                <p class="text-muted small mb-3">
                                    Securely store email credentials for automatic sending. 
                                    Passwords are encrypted in storage.
                                </p>
                                <div id="credentials-table-container"></div>
                            </div>
                        </div>

                        <!-- Test Email Recipient -->
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Test Email Delivery</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="test-email-recipient" class="form-label">
                                        Recipient Email
                                    </label>
                                    <input type="email" class="form-control" id="test-email-recipient" 
                                           placeholder="your.email@example.com">
                                    <div class="form-text">Send test email to this address to verify SMTP setup</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Add/Edit Credential Modal -->
                <div class="modal fade" id="credentialModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="credentialModalLabel">Add Credential</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="credential-form">
                                    <div class="mb-3">
                                        <label for="cred-name" class="form-label">
                                            Name <span class="text-danger">*</span>
                                        </label>
                                        <input type="text" class="form-control" id="cred-name" 
                                               name="name" required placeholder="Work Email">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Friendly name for this credential</div>
                                    </div>

                                    <div class="mb-3">
                                        <label for="cred-email" class="form-label">
                                            Email Address <span class="text-danger">*</span>
                                        </label>
                                        <input type="email" class="form-control" id="cred-email" 
                                               name="email" required placeholder="user@example.com">
                                        <div class="invalid-feedback"></div>
                                    </div>

                                    <div class="mb-3">
                                        <label for="cred-password" class="form-label">
                                            Password <span class="text-danger">*</span>
                                        </label>
                                        <div class="input-group">
                                            <input type="password" class="form-control" id="cred-password" 
                                                   name="password" required>
                                            <button class="btn btn-outline-secondary" type="button" 
                                                    id="toggle-cred-password">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                        </div>
                                        <div class="invalid-feedback"></div>
                                    </div>

                                    <div class="mb-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" 
                                                   id="cred-active" name="active" checked>
                                            <label class="form-check-label" for="cred-active">
                                                Active
                                            </label>
                                        </div>
                                        <div class="form-text">Inactive credentials won't be used</div>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    Cancel
                                </button>
                                <button type="button" id="save-credential-btn" class="btn btn-primary">
                                    <i class="bi bi-save me-1"></i> Save
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Delete Credential Modal -->
                <div class="modal fade" id="deleteCredentialModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">Delete Credential</h5>
                                <button type="button" class="btn-close btn-close-white" 
                                        data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>Delete credential <strong id="delete-cred-name"></strong>?</p>
                                <p class="text-danger mb-0">
                                    <i class="bi bi-exclamation-triangle me-1"></i>
                                    This action cannot be undone.
                                </p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" 
                                        data-bs-dismiss="modal">Cancel</button>
                                <button type="button" id="confirm-delete-cred-btn" 
                                        class="btn btn-danger">
                                    <i class="bi bi-trash me-1"></i> Delete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Store form element references
        this.formElements = {
            form: this.container.querySelector('#smtp-form'),
            senderEmail: this.container.querySelector('#smtp-sender-email'),
            senderName: this.container.querySelector('#smtp-sender-name'),
            host: this.container.querySelector('#smtp-host'),
            port: this.container.querySelector('#smtp-port'),
            encryption: this.container.querySelector('#smtp-encryption'),
            username: this.container.querySelector('#smtp-username'),
            password: this.container.querySelector('#smtp-password'),
            testRecipient: this.container.querySelector('#test-email-recipient'),
            credentialForm: this.container.querySelector('#credential-form')
        };
    }

    /**
     * Setup form validation
     */
    setupValidator() {
        this.validator = new FormValidator();
        this.validatorUI = new FormValidatorUI(this.validator);

        // Sender email validation
        this.validator.addRule('sender_email', {
            type: 'required',
            message: 'Sender email is required'
        });
        this.validator.addRule('sender_email', {
            type: 'email',
            message: 'Please enter a valid email address'
        });

        // SMTP host validation
        this.validator.addRule('host', {
            type: 'required',
            message: 'SMTP server is required'
        });

        // Port validation
        this.validator.addRule('port', {
            type: 'port',
            message: 'Port must be between 1 and 65535'
        });

        // Encryption validation
        this.validator.addRule('encryption', {
            type: 'required',
            message: 'Please select an encryption method'
        });
        this.validator.addRule('encryption', {
            type: 'in',
            value: Object.keys(ENCRYPTION_METHODS),
            message: 'Invalid encryption method'
        });

        // Username validation
        this.validator.addRule('username', {
            type: 'required',
            message: 'Username is required'
        });

        // Password validation
        this.validator.addRule('password', {
            type: 'required',
            message: 'Password is required'
        });

        // Bind UI validation
        this.validatorUI.bindField('sender_email', this.formElements.senderEmail, {
            debounce: 300,
            showSuccess: true
        });
        this.validatorUI.bindField('host', this.formElements.host, {
            debounce: 300,
            showSuccess: true
        });
        this.validatorUI.bindField('port', this.formElements.port);
        this.validatorUI.bindField('encryption', this.formElements.encryption);
        this.validatorUI.bindField('username', this.formElements.username, {
            debounce: 300,
            showSuccess: true
        });
    }

    /**
     * Setup credentials table
     */
    setupTable() {
        this.credentialsTable = new TableManager('#credentials-table-container', {
            columns: [
                {
                    key: 'name',
                    label: 'Name',
                    sortable: true,
                    render: (value) => `<strong>${this.escapeHtml(value)}</strong>`
                },
                {
                    key: 'email',
                    label: 'Email',
                    sortable: true,
                    render: (value) => `<code class="small">${this.escapeHtml(value)}</code>`
                },
                {
                    key: 'active',
                    label: 'Status',
                    sortable: true,
                    render: (value) => {
                        return value
                            ? '<span class="badge bg-success">Active</span>'
                            : '<span class="badge bg-warning text-dark">Inactive</span>';
                    }
                },
                {
                    key: 'actions',
                    label: 'Actions',
                    sortable: false,
                    render: (value, row) => `
                        <button class="btn btn-sm btn-outline-secondary edit-credential" 
                                data-cred-id="${row.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-credential" 
                                data-cred-id="${row.id}">
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
        // SMTP template selection
        this.container.querySelectorAll('.smtp-template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const templateKey = e.currentTarget.dataset.template;
                this.selectSMTPTemplate(templateKey);
            });
        });

        // Test SMTP
        this.container.querySelector('#test-smtp-btn').addEventListener('click', () => {
            this.testSMTP();
        });

        // Save SMTP configuration
        this.container.querySelector('#save-smtp-btn').addEventListener('click', () => {
            this.saveSMTP();
        });

        // Toggle SMTP password visibility
        this.container.querySelector('#toggle-smtp-password').addEventListener('click', (e) => {
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

        // Add credential
        this.container.querySelector('#add-credential-btn').addEventListener('click', () => {
            this.openCredentialModal();
        });

        // Save credential
        this.container.querySelector('#save-credential-btn').addEventListener('click', () => {
            this.saveCredential();
        });

        // Toggle credential password visibility
        this.container.querySelector('#toggle-cred-password').addEventListener('click', (e) => {
            const input = this.container.querySelector('#cred-password');
            const icon = e.currentTarget.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });

        // Credentials table actions (edit/delete) - using event delegation
        this.container.addEventListener('click', (e) => {
            if (e.target.closest('.edit-credential')) {
                const credId = e.target.closest('.edit-credential').dataset.credId;
                this.editCredential(credId);
            } else if (e.target.closest('.delete-credential')) {
                const credId = e.target.closest('.delete-credential').dataset.credId;
                this.confirmDeleteCredential(credId);
            }
        });

        // Delete credential confirmation
        this.container.querySelector('#confirm-delete-cred-btn').addEventListener('click', () => {
            this.deleteCredential();
        });
    }

    /**
     * Select SMTP template
     * 
     * @param {string} templateKey - Template key
     */
    selectSMTPTemplate(templateKey) {
        const template = SMTP_TEMPLATES[templateKey];
        if (!template) return;

        this.state.selectedTemplate = templateKey;

        // Highlight selected button
        this.container.querySelectorAll('.smtp-template-btn').forEach(btn => {
            if (btn.dataset.template === templateKey) {
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-primary');
            } else {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
            }
        });

        // Show template info
        const infoDiv = this.container.querySelector('#smtp-template-info');
        infoDiv.classList.remove('d-none');
        this.container.querySelector('#smtp-template-icon').textContent = template.icon;
        this.container.querySelector('#smtp-template-name').textContent = template.name;
        this.container.querySelector('#smtp-template-description').textContent = template.description;

        // Update form with template values
        this.formElements.host.value = template.host;
        this.formElements.port.value = template.port;
        this.formElements.encryption.value = template.encryption;

        // Show hints
        const hintsDiv = this.container.querySelector('#smtp-template-hints');
        const hintsList = this.container.querySelector('#smtp-template-hints-list');
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
     * Load SMTP configuration from API
     */
    async loadSMTPConfig() {
        this.setLoading(true);
        try {
            const response = await fetch(this.options.apiEndpoint);
            if (!response.ok) {
                throw new Error('Failed to load SMTP configuration');
            }
            const data = await response.json();
            if (data.smtp) {
                this.state.smtp = data.smtp;
                this.populateSMTPForm(data.smtp);
            }
            this.clearError();
        } catch (error) {
            console.error('Load SMTP config error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Load credentials from API
     */
    async loadCredentials() {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/credentials`);
            if (!response.ok) {
                throw new Error('Failed to load credentials');
            }
            const data = await response.json();
            this.state.credentials = data.credentials || [];
            this.credentialsTable.setData(this.state.credentials);
        } catch (error) {
            console.error('Load credentials error:', error);
        }
    }

    /**
     * Populate SMTP form with stored configuration
     * 
     * @param {Object} smtp - SMTP configuration object
     */
    populateSMTPForm(smtp) {
        if (!smtp) return;

        this.formElements.senderEmail.value = smtp.sender_email || '';
        this.formElements.senderName.value = smtp.sender_name || '';
        this.formElements.host.value = smtp.host || '';
        this.formElements.port.value = smtp.port || 587;
        this.formElements.encryption.value = smtp.encryption || 'tls';
        this.formElements.username.value = smtp.username || '';
        this.formElements.password.value = ''; // Don't show stored password

        // Select template if applicable
        if (smtp.template) {
            this.selectSMTPTemplate(smtp.template);
        }
    }

    /**
     * Test SMTP configuration by sending test email
     */
    async testSMTP() {
        // Validate form first
        const validationResult = await this.validatorUI.validateForm();
        if (!validationResult.valid) {
            return;
        }

        const recipient = this.formElements.testRecipient.value || 
                         this.formElements.senderEmail.value;

        if (!recipient) {
            this.showError('Please enter a test email recipient');
            return;
        }

        this.setTesting(true);
        this.hideTestResult();

        try {
            const smtpData = {
                host: this.formElements.host.value,
                port: parseInt(this.formElements.port.value),
                encryption: this.formElements.encryption.value,
                username: this.formElements.username.value,
                password: this.formElements.password.value,
                sender_email: this.formElements.senderEmail.value,
                sender_name: this.formElements.senderName.value,
                recipient: recipient
            };

            const response = await fetch(this.options.testEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(smtpData)
            });

            const result = await response.json();
            this.showTestResult(result);

        } catch (error) {
            const result = {
                success: false,
                message: 'Email test failed: ' + error.message
            };
            this.showTestResult(result);
            console.error('SMTP test error:', error);
        } finally {
            this.setTesting(false);
        }
    }

    /**
     * Save SMTP configuration
     */
    async saveSMTP() {
        // Validate form
        const validationResult = await this.validatorUI.validateForm();
        if (!validationResult.valid) {
            return;
        }

        const smtpData = {
            template: this.state.selectedTemplate,
            sender_email: this.formElements.senderEmail.value,
            sender_name: this.formElements.senderName.value,
            host: this.formElements.host.value,
            port: parseInt(this.formElements.port.value),
            encryption: this.formElements.encryption.value,
            username: this.formElements.username.value,
            password: this.formElements.password.value
        };

        this.setLoading(true);
        try {
            const response = await fetch(`${this.options.apiEndpoint}/smtp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(smtpData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to save SMTP configuration');
            }

            this.state.smtp = smtpData;
            this.showSuccess('SMTP configuration saved successfully');

            if (this.options.onConfigChange) {
                this.options.onConfigChange(smtpData, 'smtp_updated');
            }
        } catch (error) {
            this.showError(error.message);
            console.error('Save SMTP error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Open credential modal for add/edit
     * 
     * @param {Object} [credential] - Credential object for edit mode
     */
    openCredentialModal(credential = null) {
        const modal = new bootstrap.Modal(this.container.querySelector('#credentialModal'));
        const modalTitle = this.container.querySelector('#credentialModalLabel');

        // Reset form
        this.formElements.credentialForm.reset();

        if (credential) {
            modalTitle.textContent = 'Edit Credential';
            this.container.querySelector('#cred-name').value = credential.name;
            this.container.querySelector('#cred-email').value = credential.email;
            this.container.querySelector('#cred-password').value = '';
            this.container.querySelector('#cred-active').checked = credential.active !== false;
            this.state.selectedCredential = credential;
        } else {
            modalTitle.textContent = 'Add Credential';
            this.state.selectedCredential = null;
        }

        modal.show();
    }

    /**
     * Edit credential
     * 
     * @param {string} credId - Credential ID
     */
    editCredential(credId) {
        const credential = this.state.credentials.find(c => c.id === credId);
        if (credential) {
            this.openCredentialModal(credential);
        }
    }

    /**
     * Save credential (create or update)
     */
    async saveCredential() {
        const name = this.container.querySelector('#cred-name').value;
        const email = this.container.querySelector('#cred-email').value;
        const password = this.container.querySelector('#cred-password').value;
        const active = this.container.querySelector('#cred-active').checked;

        if (!name || !email || !password) {
            this.showError('Please fill in all credential fields');
            return;
        }

        const credentialData = { name, email, password, active };

        this.setLoading(true);
        try {
            const url = this.state.selectedCredential
                ? `${this.options.apiEndpoint}/credentials/${this.state.selectedCredential.id}`
                : `${this.options.apiEndpoint}/credentials`;

            const method = this.state.selectedCredential ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(credentialData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to save credential');
            }

            const action = this.state.selectedCredential ? 'updated' : 'created';
            this.showSuccess(`Credential ${action} successfully`);

            // Close modal
            const modal = bootstrap.Modal.getInstance(
                this.container.querySelector('#credentialModal')
            );
            modal.hide();

            // Reload credentials
            await this.loadCredentials();

            if (this.options.onConfigChange) {
                this.options.onConfigChange(credentialData, `credential_${action}`);
            }
        } catch (error) {
            this.showError(error.message);
            console.error('Save credential error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Confirm delete credential
     * 
     * @param {string} credId - Credential ID
     */
    confirmDeleteCredential(credId) {
        this.state.selectedCredential = this.state.credentials.find(c => c.id === credId);
        if (!this.state.selectedCredential) return;

        this.container.querySelector('#delete-cred-name').textContent = 
            this.state.selectedCredential.name;

        const modal = new bootstrap.Modal(
            this.container.querySelector('#deleteCredentialModal')
        );
        modal.show();
    }

    /**
     * Delete credential
     */
    async deleteCredential() {
        if (!this.state.selectedCredential) return;

        this.setLoading(true);
        try {
            const response = await fetch(
                `${this.options.apiEndpoint}/credentials/${this.state.selectedCredential.id}`,
                { method: 'DELETE' }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to delete credential');
            }

            this.showSuccess(`Credential deleted successfully`);

            // Close modal
            const modal = bootstrap.Modal.getInstance(
                this.container.querySelector('#deleteCredentialModal')
            );
            modal.hide();

            // Reload credentials
            await this.loadCredentials();

            if (this.options.onConfigChange) {
                this.options.onConfigChange(this.state.selectedCredential, 'credential_deleted');
            }

            this.state.selectedCredential = null;
        } catch (error) {
            this.showError(error.message);
            console.error('Delete credential error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Show test result
     * 
     * @param {Object} result - Test result object
     */
    showTestResult(result) {
        const resultDiv = this.container.querySelector('#smtp-test-result');
        const alert = this.container.querySelector('#smtp-test-result-alert');
        const icon = this.container.querySelector('#smtp-test-result-icon');
        const title = this.container.querySelector('#smtp-test-result-title');
        const message = this.container.querySelector('#smtp-test-result-message');

        resultDiv.classList.remove('d-none');

        if (result.success) {
            alert.className = 'alert alert-success';
            icon.className = 'bi bi-check-circle-fill me-2';
            title.textContent = 'Email Sent Successfully';
            message.textContent = result.message || 'Test email sent successfully';
        } else {
            alert.className = 'alert alert-danger';
            icon.className = 'bi bi-x-circle-fill me-2';
            title.textContent = 'Email Send Failed';
            message.textContent = result.message || result.error || 'Unable to send email';
        }
    }

    /**
     * Hide test result
     */
    hideTestResult() {
        this.container.querySelector('#smtp-test-result').classList.add('d-none');
    }

    /**
     * Show error message
     * 
     * @param {string} message - Error message
     */
    showError(message) {
        this.state.error = message;
        const alert = this.container.querySelector('#smtp-error-alert');
        const messageEl = this.container.querySelector('#smtp-error-message');
        messageEl.textContent = message;
        alert.classList.remove('d-none');
        
        setTimeout(() => this.clearError(), 5000);
    }

    /**
     * Clear error message
     */
    clearError() {
        this.state.error = null;
        this.container.querySelector('#smtp-error-alert').classList.add('d-none');
    }

    /**
     * Show success message
     * 
     * @param {string} message - Success message
     */
    showSuccess(message) {
        const alert = this.container.querySelector('#smtp-success-alert');
        const messageEl = this.container.querySelector('#smtp-success-message');
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
        const saveBtn = this.container.querySelector('#save-smtp-btn');
        const credSaveBtn = this.container.querySelector('#save-credential-btn');
        
        if (loading) {
            saveBtn.disabled = true;
            credSaveBtn.disabled = true;
            saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';
        } else {
            saveBtn.disabled = false;
            credSaveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="bi bi-save me-1"></i> Save Configuration';
        }
    }

    /**
     * Set testing state
     * 
     * @param {boolean} testing - Testing state
     */
    setTesting(testing) {
        this.state.testing = testing;
        const testBtn = this.container.querySelector('#test-smtp-btn');
        
        if (testing) {
            testBtn.disabled = true;
            testBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Sending...';
        } else {
            testBtn.disabled = false;
            testBtn.innerHTML = '<i class="bi bi-send me-1"></i> Send Test Email';
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
        if (this.credentialsTable) {
            this.credentialsTable.setData([]);
        }
        this.container.innerHTML = '';
    }
}

// Export as default
export default SMTPCredentialsConfig;
