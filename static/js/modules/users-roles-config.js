/**
 * Users & Roles Configuration Module
 * 
 * Manages user accounts and role assignments with full CRUD operations.
 * Uses FormValidator for input validation and TableManager for user list.
 * 
 * Features:
 * - User CRUD operations (Create, Read, Update, Delete)
 * - Role assignment with predefined roles
 * - Password management with strength validation
 * - Search and filter users
 * - Inline editing support
 * - Bulk operations (future)
 * 
 * Dependencies:
 * - FormValidator (utilities/form-validator.js)
 * - TableManager (utilities/table-manager.js)
 * 
 * @module users-roles-config
 * @version 1.0.0
 */

import { FormValidator, FormValidatorUI } from '../utilities/form-validator.js';
import { TableManager } from '../utilities/table-manager.js';

/**
 * Predefined user roles with descriptions and permissions
 * @constant {Object.<string, Object>}
 */
const USER_ROLES = {
    'admin': {
        label: 'Administrator',
        description: 'Full system access including user management',
        permissions: ['*']
    },
    'power_user': {
        label: 'Power User',
        description: 'Advanced features and configuration access',
        permissions: ['config', 'rules', 'stats', 'logs']
    },
    'user': {
        label: 'Standard User',
        description: 'Basic file organization and monitoring',
        permissions: ['monitor', 'stats']
    },
    'readonly': {
        label: 'Read Only',
        description: 'View-only access to dashboard',
        permissions: ['monitor']
    }
};

/**
 * Password strength requirements
 * @constant {Object}
 */
const PASSWORD_REQUIREMENTS = {
    weak: {
        minLength: 6,
        description: 'At least 6 characters'
    },
    medium: {
        minLength: 8,
        requireUppercase: true,
        requireLowercase: true,
        requireNumbers: true,
        description: 'At least 8 characters with uppercase, lowercase, and numbers'
    },
    strong: {
        minLength: 12,
        requireUppercase: true,
        requireLowercase: true,
        requireNumbers: true,
        requireSpecialChars: true,
        description: 'At least 12 characters with uppercase, lowercase, numbers, and special characters'
    }
};

/**
 * Users & Roles Configuration Manager
 * 
 * Manages the entire users and roles configuration interface including
 * the user table, add/edit forms, and all CRUD operations.
 */
export class UsersRolesConfig {
    /**
     * Initialize the Users & Roles configuration manager
     * 
     * @param {string} containerSelector - CSS selector for container element
     * @param {Object} options - Configuration options
     * @param {string} [options.apiEndpoint='/api/dashboard/config'] - API endpoint for user operations
     * @param {string} [options.passwordStrength='medium'] - Default password strength requirement
     * @param {boolean} [options.allowSelfDelete=false] - Allow users to delete themselves
     * @param {Function} [options.onUserChange] - Callback when users are modified
     */
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            throw new Error(`Container not found: ${containerSelector}`);
        }

        // Configuration options
        this.options = {
            apiEndpoint: options.apiEndpoint || '/api/dashboard/config',
            passwordStrength: options.passwordStrength || 'medium',
            allowSelfDelete: options.allowSelfDelete || false,
            onUserChange: options.onUserChange || null
        };

        // State management
        this.state = {
            users: [],
            currentUser: null, // Currently logged-in user
            selectedUser: null, // User being edited
            editMode: false,
            searchQuery: '',
            loading: false,
            error: null
        };

        // Components
        this.validator = null;
        this.validatorUI = null;
        this.userTable = null;
        this.formElements = {};

        // Initialize
        this.init();
    }

    /**
     * Initialize the module
     */
    async init() {
        this.render();
        this.setupValidator();
        this.setupTable();
        this.attachEventListeners();
        await this.loadUsers();
        await this.loadCurrentUser();
    }

    /**
     * Render the UI structure
     */
    render() {
        this.container.innerHTML = `
            <div class="users-roles-config">
                <!-- Header -->
                <div class="config-header mb-4">
                    <h3 class="mb-0">Users & Roles</h3>
                    <p class="text-muted">Manage user accounts and role assignments</p>
                </div>

                <!-- Error Display -->
                <div id="user-error-alert" class="alert alert-danger d-none" role="alert">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <span id="user-error-message"></span>
                </div>

                <!-- Success Display -->
                <div id="user-success-alert" class="alert alert-success d-none" role="alert">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    <span id="user-success-message"></span>
                </div>

                <!-- Actions Bar -->
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div class="input-group" style="max-width: 300px;">
                        <span class="input-group-text">
                            <i class="bi bi-search"></i>
                        </span>
                        <input type="text" id="user-search" class="form-control" 
                               placeholder="Search users...">
                    </div>
                    <button id="add-user-btn" class="btn btn-primary">
                        <i class="bi bi-person-plus me-1"></i> Add User
                    </button>
                </div>

                <!-- User Table -->
                <div id="users-table-container" class="mb-4"></div>

                <!-- Add/Edit User Form Modal -->
                <div class="modal fade" id="userFormModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="userFormModalLabel">Add User</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="user-form">
                                    <!-- Username -->
                                    <div class="mb-3">
                                        <label for="user-username" class="form-label">
                                            Username <span class="text-danger">*</span>
                                        </label>
                                        <input type="text" class="form-control" id="user-username" 
                                               name="username" required>
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">3-32 characters, alphanumeric and underscores only</div>
                                    </div>

                                    <!-- Password (only for new users or when changing) -->
                                    <div class="mb-3" id="password-group">
                                        <label for="user-password" class="form-label">
                                            Password <span class="text-danger" id="password-required">*</span>
                                        </label>
                                        <div class="input-group">
                                            <input type="password" class="form-control" id="user-password" 
                                                   name="password">
                                            <button class="btn btn-outline-secondary" type="button" 
                                                    id="toggle-password">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                        </div>
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text" id="password-help"></div>
                                        <!-- Password Strength Meter -->
                                        <div class="progress mt-2" style="height: 4px;">
                                            <div id="password-strength-bar" class="progress-bar" 
                                                 style="width: 0%"></div>
                                        </div>
                                    </div>

                                    <!-- Change Password Checkbox (edit mode) -->
                                    <div class="mb-3 d-none" id="change-password-group">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" 
                                                   id="change-password-check">
                                            <label class="form-check-label" for="change-password-check">
                                                Change password
                                            </label>
                                        </div>
                                    </div>

                                    <!-- Role -->
                                    <div class="mb-3">
                                        <label for="user-role" class="form-label">
                                            Role <span class="text-danger">*</span>
                                        </label>
                                        <select class="form-select" id="user-role" name="role" required>
                                            <option value="">Select a role...</option>
                                            ${Object.entries(USER_ROLES).map(([key, role]) => `
                                                <option value="${key}">${role.label}</option>
                                            `).join('')}
                                        </select>
                                        <div class="invalid-feedback"></div>
                                        <div id="role-description" class="form-text"></div>
                                    </div>

                                    <!-- Email (optional) -->
                                    <div class="mb-3">
                                        <label for="user-email" class="form-label">Email</label>
                                        <input type="email" class="form-control" id="user-email" 
                                               name="email">
                                        <div class="invalid-feedback"></div>
                                        <div class="form-text">Optional - for notifications</div>
                                    </div>

                                    <!-- Full Name (optional) -->
                                    <div class="mb-3">
                                        <label for="user-fullname" class="form-label">Full Name</label>
                                        <input type="text" class="form-control" id="user-fullname" 
                                               name="fullname">
                                        <div class="invalid-feedback"></div>
                                    </div>

                                    <!-- Active Status -->
                                    <div class="mb-3">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" 
                                                   id="user-active" name="active" checked>
                                            <label class="form-check-label" for="user-active">
                                                Active
                                            </label>
                                        </div>
                                        <div class="form-text">Inactive users cannot log in</div>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    Cancel
                                </button>
                                <button type="button" id="save-user-btn" class="btn btn-primary">
                                    <i class="bi bi-save me-1"></i> Save User
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Delete Confirmation Modal -->
                <div class="modal fade" id="deleteUserModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">Delete User</h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>Are you sure you want to delete user <strong id="delete-user-name"></strong>?</p>
                                <p class="text-danger mb-0">
                                    <i class="bi bi-exclamation-triangle me-1"></i>
                                    This action cannot be undone.
                                </p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    Cancel
                                </button>
                                <button type="button" id="confirm-delete-btn" class="btn btn-danger">
                                    <i class="bi bi-trash me-1"></i> Delete User
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Store form element references
        this.formElements = {
            form: this.container.querySelector('#user-form'),
            username: this.container.querySelector('#user-username'),
            password: this.container.querySelector('#user-password'),
            role: this.container.querySelector('#user-role'),
            email: this.container.querySelector('#user-email'),
            fullname: this.container.querySelector('#user-fullname'),
            active: this.container.querySelector('#user-active'),
            changePasswordCheck: this.container.querySelector('#change-password-check')
        };
    }

    /**
     * Setup form validation
     */
    setupValidator() {
        this.validator = new FormValidator();
        this.validatorUI = new FormValidatorUI(this.validator);

        const strength = this.options.passwordStrength;
        const requirements = PASSWORD_REQUIREMENTS[strength];

        // Username validation
        this.validator.addRule('username', {
            type: 'required',
            message: 'Username is required'
        });
        this.validator.addRule('username', {
            type: 'minLength',
            value: 3,
            message: 'Username must be at least 3 characters'
        });
        this.validator.addRule('username', {
            type: 'maxLength',
            value: 32,
            message: 'Username cannot exceed 32 characters'
        });
        this.validator.addRule('username', {
            type: 'pattern',
            value: /^[a-zA-Z0-9_]+$/,
            message: 'Username can only contain letters, numbers, and underscores'
        });

        // Password validation (conditional based on mode)
        this.validator.addRule('password', {
            type: 'password',
            strength: strength,
            message: requirements.description
        });

        // Role validation
        this.validator.addRule('role', {
            type: 'required',
            message: 'Please select a role'
        });
        this.validator.addRule('role', {
            type: 'in',
            value: Object.keys(USER_ROLES),
            message: 'Invalid role selected'
        });

        // Email validation (optional)
        this.validator.addRule('email', {
            type: 'email',
            message: 'Please enter a valid email address'
        });

        // Bind UI validation
        this.validatorUI.bindField('username', this.formElements.username, { 
            debounce: 300,
            showSuccess: true
        });
        this.validatorUI.bindField('password', this.formElements.password, { 
            debounce: 300,
            showSuccess: false,
            onChange: (value) => this.updatePasswordStrength(value)
        });
        this.validatorUI.bindField('role', this.formElements.role, {
            onChange: (value) => this.updateRoleDescription(value)
        });
        this.validatorUI.bindField('email', this.formElements.email, { 
            debounce: 300 
        });
    }

    /**
     * Setup user table
     */
    setupTable() {
        this.userTable = new TableManager('#users-table-container', {
            columns: [
                {
                    key: 'username',
                    label: 'Username',
                    sortable: true,
                    render: (value, row) => {
                        const currentBadge = row.username === this.state.currentUser?.username
                            ? '<span class="badge bg-info ms-2">You</span>'
                            : '';
                        return `<strong>${this.escapeHtml(value)}</strong>${currentBadge}`;
                    }
                },
                {
                    key: 'role',
                    label: 'Role',
                    sortable: true,
                    render: (value) => {
                        const role = USER_ROLES[value];
                        const badgeClass = {
                            'admin': 'bg-danger',
                            'power_user': 'bg-primary',
                            'user': 'bg-success',
                            'readonly': 'bg-secondary'
                        }[value] || 'bg-secondary';
                        return `<span class="badge ${badgeClass}">${role?.label || value}</span>`;
                    }
                },
                {
                    key: 'fullname',
                    label: 'Full Name',
                    sortable: true,
                    render: (value) => value || '<em class="text-muted">Not set</em>'
                },
                {
                    key: 'email',
                    label: 'Email',
                    sortable: true,
                    render: (value) => value || '<em class="text-muted">Not set</em>'
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
                    render: (value, row) => {
                        const isSelf = row.username === this.state.currentUser?.username;
                        const canDelete = this.options.allowSelfDelete || !isSelf;
                        return `
                            <button class="btn btn-sm btn-outline-primary edit-user" 
                                    data-username="${this.escapeHtml(row.username)}">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-user ${!canDelete ? 'disabled' : ''}" 
                                    data-username="${this.escapeHtml(row.username)}"
                                    ${!canDelete ? 'disabled title="Cannot delete yourself"' : ''}>
                                <i class="bi bi-trash"></i>
                            </button>
                        `;
                    }
                }
            ],
            data: [],
            paginate: true,
            pageSize: 10,
            sortable: true,
            filterable: true
        });
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Search
        const searchInput = this.container.querySelector('#user-search');
        searchInput.addEventListener('input', (e) => {
            this.state.searchQuery = e.target.value;
            this.userTable.search(e.target.value);
        });

        // Add user button
        this.container.querySelector('#add-user-btn').addEventListener('click', () => {
            this.openUserForm();
        });

        // Save user button
        this.container.querySelector('#save-user-btn').addEventListener('click', () => {
            this.saveUser();
        });

        // Table row actions (edit/delete) - using event delegation
        this.container.addEventListener('click', (e) => {
            if (e.target.closest('.edit-user')) {
                const username = e.target.closest('.edit-user').dataset.username;
                this.editUser(username);
            } else if (e.target.closest('.delete-user') && !e.target.closest('.delete-user').disabled) {
                const username = e.target.closest('.delete-user').dataset.username;
                this.confirmDeleteUser(username);
            }
        });

        // Delete confirmation
        this.container.querySelector('#confirm-delete-btn').addEventListener('click', () => {
            this.deleteUser();
        });

        // Toggle password visibility
        this.container.querySelector('#toggle-password').addEventListener('click', (e) => {
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

        // Change password checkbox (edit mode)
        this.formElements.changePasswordCheck.addEventListener('change', (e) => {
            const passwordGroup = this.container.querySelector('#password-group');
            if (e.target.checked) {
                passwordGroup.classList.remove('d-none');
                this.formElements.password.required = true;
            } else {
                passwordGroup.classList.add('d-none');
                this.formElements.password.required = false;
                this.formElements.password.value = '';
            }
        });

        // Update password help text based on strength setting
        this.updatePasswordHelp();
    }

    /**
     * Load users from API
     */
    async loadUsers() {
        this.setLoading(true);
        try {
            const response = await fetch(this.options.apiEndpoint);
            if (!response.ok) {
                throw new Error('Failed to load users');
            }
            const data = await response.json();
            this.state.users = data.users || [];
            this.userTable.setData(this.state.users);
            this.clearError();
        } catch (error) {
            this.showError('Failed to load users: ' + error.message);
            console.error('Load users error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Load current user info
     */
    async loadCurrentUser() {
        try {
            const response = await fetch('/api/dashboard/current-user');
            if (response.ok) {
                this.state.currentUser = await response.json();
            }
        } catch (error) {
            console.error('Failed to load current user:', error);
        }
    }

    /**
     * Open user form modal (add or edit mode)
     * 
     * @param {Object} [user] - User object for edit mode
     */
    openUserForm(user = null) {
        this.state.editMode = !!user;
        this.state.selectedUser = user;

        const modal = new bootstrap.Modal(this.container.querySelector('#userFormModal'));
        const modalTitle = this.container.querySelector('#userFormModalLabel');
        const changePasswordGroup = this.container.querySelector('#change-password-group');
        const passwordRequired = this.container.querySelector('#password-required');

        // Reset form
        this.formElements.form.reset();
        this.validator.clearErrors();
        this.clearFormValidation();

        if (user) {
            // Edit mode
            modalTitle.textContent = 'Edit User';
            this.formElements.username.value = user.username;
            this.formElements.username.disabled = true; // Cannot change username
            this.formElements.role.value = user.role;
            this.formElements.email.value = user.email || '';
            this.formElements.fullname.value = user.fullname || '';
            this.formElements.active.checked = user.active !== false;

            // Hide password field initially, show checkbox
            this.container.querySelector('#password-group').classList.add('d-none');
            changePasswordGroup.classList.remove('d-none');
            this.formElements.changePasswordCheck.checked = false;
            this.formElements.password.required = false;
            passwordRequired.classList.add('d-none');
        } else {
            // Add mode
            modalTitle.textContent = 'Add User';
            this.formElements.username.disabled = false;
            this.container.querySelector('#password-group').classList.remove('d-none');
            changePasswordGroup.classList.add('d-none');
            this.formElements.password.required = true;
            passwordRequired.classList.remove('d-none');
        }

        modal.show();
    }

    /**
     * Edit user
     * 
     * @param {string} username - Username to edit
     */
    editUser(username) {
        const user = this.state.users.find(u => u.username === username);
        if (user) {
            this.openUserForm(user);
        }
    }

    /**
     * Save user (create or update)
     */
    async saveUser() {
        // Validate form
        const formData = new FormData(this.formElements.form);
        const userData = Object.fromEntries(formData);
        
        // Handle checkbox
        userData.active = this.formElements.active.checked;

        // In edit mode, only validate password if changing it
        if (this.state.editMode && !this.formElements.changePasswordCheck.checked) {
            delete userData.password;
        }

        // Validate
        const validationResult = await this.validatorUI.validateForm();
        if (!validationResult.valid) {
            return;
        }

        this.setLoading(true);
        try {
            const url = this.state.editMode
                ? `${this.options.apiEndpoint}/users/${this.state.selectedUser.username}`
                : `${this.options.apiEndpoint}/users`;
            
            const method = this.state.editMode ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to save user');
            }

            // Success
            const action = this.state.editMode ? 'updated' : 'created';
            this.showSuccess(`User ${userData.username} ${action} successfully`);

            // Close modal
            const modal = bootstrap.Modal.getInstance(this.container.querySelector('#userFormModal'));
            modal.hide();

            // Reload users
            await this.loadUsers();

            // Callback
            if (this.options.onUserChange) {
                this.options.onUserChange(userData, action);
            }
        } catch (error) {
            this.showError(error.message);
            console.error('Save user error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Confirm delete user
     * 
     * @param {string} username - Username to delete
     */
    confirmDeleteUser(username) {
        this.state.selectedUser = this.state.users.find(u => u.username === username);
        if (!this.state.selectedUser) {
            return;
        }

        this.container.querySelector('#delete-user-name').textContent = username;
        const modal = new bootstrap.Modal(this.container.querySelector('#deleteUserModal'));
        modal.show();
    }

    /**
     * Delete user
     */
    async deleteUser() {
        if (!this.state.selectedUser) {
            return;
        }

        this.setLoading(true);
        try {
            const response = await fetch(
                `${this.options.apiEndpoint}/users/${this.state.selectedUser.username}`,
                { method: 'DELETE' }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to delete user');
            }

            // Success
            this.showSuccess(`User ${this.state.selectedUser.username} deleted successfully`);

            // Close modal
            const modal = bootstrap.Modal.getInstance(this.container.querySelector('#deleteUserModal'));
            modal.hide();

            // Reload users
            await this.loadUsers();

            // Callback
            if (this.options.onUserChange) {
                this.options.onUserChange(this.state.selectedUser, 'deleted');
            }

            this.state.selectedUser = null;
        } catch (error) {
            this.showError(error.message);
            console.error('Delete user error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Update password strength meter
     * 
     * @param {string} password - Password value
     */
    updatePasswordStrength(password) {
        const strengthBar = this.container.querySelector('#password-strength-bar');
        
        if (!password) {
            strengthBar.style.width = '0%';
            strengthBar.className = 'progress-bar';
            return;
        }

        let strength = 0;
        let strengthClass = '';
        
        // Length
        if (password.length >= 8) strength += 20;
        if (password.length >= 12) strength += 20;
        
        // Character types
        if (/[a-z]/.test(password)) strength += 15;
        if (/[A-Z]/.test(password)) strength += 15;
        if (/[0-9]/.test(password)) strength += 15;
        if (/[^a-zA-Z0-9]/.test(password)) strength += 15;

        // Set color based on strength
        if (strength < 40) {
            strengthClass = 'bg-danger';
        } else if (strength < 70) {
            strengthClass = 'bg-warning';
        } else {
            strengthClass = 'bg-success';
        }

        strengthBar.style.width = strength + '%';
        strengthBar.className = `progress-bar ${strengthClass}`;
    }

    /**
     * Update role description
     * 
     * @param {string} roleKey - Role key
     */
    updateRoleDescription(roleKey) {
        const descElement = this.container.querySelector('#role-description');
        const role = USER_ROLES[roleKey];
        
        if (role) {
            descElement.textContent = role.description;
            descElement.classList.remove('text-danger');
            descElement.classList.add('text-muted');
        } else {
            descElement.textContent = '';
        }
    }

    /**
     * Update password help text
     */
    updatePasswordHelp() {
        const helpText = this.container.querySelector('#password-help');
        const requirements = PASSWORD_REQUIREMENTS[this.options.passwordStrength];
        helpText.textContent = requirements.description;
    }

    /**
     * Clear form validation UI
     */
    clearFormValidation() {
        const inputs = this.formElements.form.querySelectorAll('.form-control, .form-select');
        inputs.forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');
            const feedback = input.parentElement.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = '';
            }
        });
    }

    /**
     * Show error message
     * 
     * @param {string} message - Error message
     */
    showError(message) {
        this.state.error = message;
        const alert = this.container.querySelector('#user-error-alert');
        const messageEl = this.container.querySelector('#user-error-message');
        messageEl.textContent = message;
        alert.classList.remove('d-none');
        
        // Auto-hide after 5 seconds
        setTimeout(() => this.clearError(), 5000);
    }

    /**
     * Clear error message
     */
    clearError() {
        this.state.error = null;
        this.container.querySelector('#user-error-alert').classList.add('d-none');
    }

    /**
     * Show success message
     * 
     * @param {string} message - Success message
     */
    showSuccess(message) {
        const alert = this.container.querySelector('#user-success-alert');
        const messageEl = this.container.querySelector('#user-success-message');
        messageEl.textContent = message;
        alert.classList.remove('d-none');
        
        // Auto-hide after 3 seconds
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
        const saveBtn = this.container.querySelector('#save-user-btn');
        const deleteBtn = this.container.querySelector('#confirm-delete-btn');
        
        if (loading) {
            saveBtn.disabled = true;
            deleteBtn.disabled = true;
            saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';
        } else {
            saveBtn.disabled = false;
            deleteBtn.disabled = false;
            saveBtn.innerHTML = '<i class="bi bi-save me-1"></i> Save User';
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
        if (this.userTable) {
            // TableManager doesn't have destroy method yet, but we can clear data
            this.userTable.setData([]);
        }
        this.container.innerHTML = '';
    }
}

// Export as default
export default UsersRolesConfig;
