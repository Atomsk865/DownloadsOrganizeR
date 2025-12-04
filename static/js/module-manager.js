/**
 * Module Loader for Dashboard
 * Dynamically loads and manages dashboard modules
 * Supports lazy loading, dependency resolution, and module lifecycle
 */

class ModuleManager {
    constructor() {
        this.modules = new Map();
        this.loadedModules = new Set();
        this.dependencies = new Map();
        this.moduleCache = new Map();
        this.loadingPromises = new Map();
    }

    /**
     * Register a module
     * @param {string} name - Unique module name
     * @param {Array<string>} dependencies - Array of module names this depends on
     * @param {Function} factory - Function that returns module exports
     */
    register(name, dependencies = [], factory) {
        if (this.modules.has(name)) {
            console.warn(`Module "${name}" already registered, skipping`);
            return;
        }

        this.modules.set(name, factory);
        this.dependencies.set(name, dependencies);
    }

    /**
     * Load a module and its dependencies
     * @param {string} name - Module name
     * @returns {Promise} Resolves to module exports
     */
    async load(name) {
        // Return cached module if already loaded
        if (this.moduleCache.has(name)) {
            return this.moduleCache.get(name);
        }

        // Return existing loading promise to avoid duplicate loads
        if (this.loadingPromises.has(name)) {
            return this.loadingPromises.get(name);
        }

        // Create loading promise
        const loadPromise = this._loadModule(name);
        this.loadingPromises.set(name, loadPromise);

        try {
            const result = await loadPromise;
            this.loadedModules.add(name);
            this.moduleCache.set(name, result);
            return result;
        } finally {
            this.loadingPromises.delete(name);
        }
    }

    /**
     * Internal module loading with dependency resolution
     */
    async _loadModule(name) {
        const factory = this.modules.get(name);
        if (!factory) {
            throw new Error(`Module "${name}" not found`);
        }

        const deps = this.dependencies.get(name) || [];

        // Load all dependencies first
        const depValues = {};
        for (const depName of deps) {
            depValues[depName] = await this.load(depName);
        }

        // Execute factory function with resolved dependencies
        return factory(depValues);
    }

    /**
     * Load multiple modules
     */
    async loadAll(moduleNames) {
        return Promise.all(moduleNames.map(name => this.load(name)));
    }

    /**
     * Check if module is loaded
     */
    isLoaded(name) {
        return this.loadedModules.has(name);
    }

    /**
     * Get module without loading
     */
    get(name) {
        return this.moduleCache.get(name);
    }

    /**
     * Clear module cache
     */
    clear() {
        this.moduleCache.clear();
        this.loadedModules.clear();
        this.loadingPromises.clear();
    }

    /**
     * Print module status
     */
    printStatus() {
        console.log('=== Module Manager Status ===');
        console.log('Total modules registered:', this.modules.size);
        console.log('Loaded modules:', this.loadedModules.size);
        console.log('Loaded:', Array.from(this.loadedModules));
        console.log('Registered:', Array.from(this.modules.keys()));
    }
}

// Global module manager instance
window.moduleManager = new ModuleManager();

/**
 * Register core modules
 */

// Auth Module - Authentication & authorization
window.moduleManager.register('auth', [], (deps) => {
    return {
        getAuthHeaders() {
            const token = sessionStorage.getItem('auth_token');
            return token ? { 'Authorization': `Bearer ${token}` } : {};
        },
        
        isAuthenticated() {
            return !!sessionStorage.getItem('auth_token');
        },
        
        logout() {
            sessionStorage.removeItem('auth_token');
            window.location.href = '/login';
        }
    };
});

// Utilities Module - Common helper functions
window.moduleManager.register('utils', [], (deps) => {
    return {
        formatBytes(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        },
        
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },
        
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        throttle(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    };
});

// API Module - API communication
window.moduleManager.register('api', ['auth'], (deps) => {
    const auth = deps.auth;
    
    return {
        async get(endpoint) {
            const response = await fetch(endpoint, {
                credentials: 'include',
                headers: auth.getAuthHeaders()
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        },
        
        async post(endpoint, data) {
            const response = await fetch(endpoint, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    ...auth.getAuthHeaders()
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        },
        
        async patch(endpoint, data) {
            const response = await fetch(endpoint, {
                method: 'PATCH',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    ...auth.getAuthHeaders()
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        }
    };
});

// Notifications Module - User notifications
window.moduleManager.register('notifications', ['utils'], (deps) => {
    const utils = deps.utils;
    
    return {
        show(message, type = 'info', duration = 3000) {
            const toast = document.createElement('div');
            toast.className = `alert alert-${type} alert-dismissible fade show`;
            toast.innerHTML = `
                ${utils.escapeHtml(message)}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(toast);
            
            if (duration) {
                setTimeout(() => toast.remove(), duration);
            }
            
            return toast;
        },
        
        success(message, duration = 3000) {
            return this.show(message, 'success', duration);
        },
        
        error(message, duration = 5000) {
            return this.show(message, 'danger', duration);
        },
        
        warning(message, duration = 4000) {
            return this.show(message, 'warning', duration);
        },
        
        info(message, duration = 3000) {
            return this.show(message, 'info', duration);
        }
    };
});

// Theme Module - Theme management
window.moduleManager.register('theme', [], (deps) => {
    return {
        getCurrentTheme() {
            return localStorage.getItem('dashboard_theme') || 'default';
        },
        
        setTheme(theme) {
            localStorage.setItem('dashboard_theme', theme);
            document.documentElement.setAttribute('data-theme', theme);
        },
        
        getThemeColors(theme) {
            const themes = {
                'default': { primary: '#0d6efd', secondary: '#6c757d' },
                'dark': { primary: '#00d4ff', secondary: '#888888' },
                'forest': { primary: '#22a651', secondary: '#1a7e39' }
            };
            return themes[theme] || themes['default'];
        }
    };
});

// State Module - Global app state management
window.moduleManager.register('state', [], (deps) => {
    const state = {
        user: null,
        features: {},
        config: {},
        ui: {
            sidebarOpen: true,
            modalOpen: false
        }
    };
    
    const listeners = new Map();
    
    return {
        get(path) {
            return path.split('.').reduce((obj, key) => obj?.[key], state);
        },
        
        set(path, value) {
            const keys = path.split('.');
            const lastKey = keys.pop();
            const target = keys.reduce((obj, key) => obj[key] = obj[key] || {}, state);
            target[lastKey] = value;
            this.notify(path, value);
        },
        
        subscribe(path, callback) {
            if (!listeners.has(path)) {
                listeners.set(path, []);
            }
            listeners.get(path).push(callback);
        },
        
        notify(path, value) {
            listeners.get(path)?.forEach(cb => cb(value));
        },
        
        getState() {
            return JSON.parse(JSON.stringify(state));
        }
    };
});

// Charts Module - Chart rendering utilities
window.moduleManager.register('charts', [], (deps) => {
    const charts = new Map();
    
    return {
        create(elementId, config) {
            if (charts.has(elementId)) {
                charts.get(elementId).destroy();
            }
            
            const ctx = document.getElementById(elementId);
            if (!ctx) {
                console.error(`Chart element ${elementId} not found`);
                return null;
            }
            
            if (typeof Chart === 'undefined') {
                console.error('Chart.js not loaded');
                return null;
            }
            
            const chart = new Chart(ctx, config);
            charts.set(elementId, chart);
            return chart;
        },
        
        destroy(elementId) {
            if (charts.has(elementId)) {
                charts.get(elementId).destroy();
                charts.delete(elementId);
            }
        },
        
        destroyAll() {
            charts.forEach(chart => chart.destroy());
            charts.clear();
        }
    };
});

// Export module manager for use
console.log('✓ Module Manager initialized');
console.log('Available core modules: auth, utils, api, notifications, theme, state, charts');
