/**
 * Module Initialization System
 * Handles module discovery, loading, and lifecycle
 */

import { Store, EventBus, UI, Theme } from './core-library.js';

export const ModuleSystem = (() => {
    const modules = new Map();
    const initialized = new Set();

    /**
     * Register a module
     */
    function register(name, config) {
        if (modules.has(name)) {
            console.warn(`Module "${name}" already registered`);
            return false;
        }

        modules.set(name, {
            name,
            init: config.init || (() => {}),
            destroy: config.destroy || (() => {}),
            dependencies: config.dependencies || [],
            ...config
        });

        return true;
    }

    /**
     * Initialize a module
     */
    async function init(name) {
        if (initialized.has(name)) {
            return; // Already initialized
        }

        const module = modules.get(name);
        if (!module) {
            console.error(`Module "${name}" not found`);
            return;
        }

        // Initialize dependencies first
        for (const dep of module.dependencies) {
            await init(dep);
        }

        try {
            await module.init?.();
            initialized.add(name);
            EventBus.emit(`module:${name}:initialized`);
            console.log(`✓ Module "${name}" initialized`);
        } catch (error) {
            console.error(`✗ Module "${name}" initialization failed:`, error);
            EventBus.emit(`module:${name}:error`, error);
        }
    }

    /**
     * Initialize all registered modules
     */
    async function initAll() {
        for (const [name] of modules) {
            await init(name);
        }
    }

    /**
     * Destroy a module
     */
    async function destroy(name) {
        if (!initialized.has(name)) return;

        const module = modules.get(name);
        if (!module) return;

        try {
            await module.destroy?.();
            initialized.delete(name);
            EventBus.emit(`module:${name}:destroyed`);
        } catch (error) {
            console.error(`Error destroying module "${name}":`, error);
        }
    }

    /**
     * Get module
     */
    function get(name) {
        return modules.get(name);
    }

    /**
     * Check if module is initialized
     */
    function isInitialized(name) {
        return initialized.has(name);
    }

    return {
        register,
        init,
        initAll,
        destroy,
        get,
        isInitialized
    };
})();

/**
 * Base Module Class
 * Provides common functionality for all modules
 */
export class BaseModule {
    constructor(name, options = {}) {
        this.name = name;
        this.options = options;
        this.container = null;
        this.isInitialized = false;
    }

    /**
     * Initialize module
     */
    async init() {
        this.isInitialized = true;
        this.onInit?.();
        return this;
    }

    /**
     * Destroy module
     */
    async destroy() {
        this.isInitialized = false;
        this.onDestroy?.();
    }

    /**
     * Mount module to container
     */
    mount(selector) {
        this.container = document.querySelector(selector);
        if (!this.container) {
            console.warn(`Container "${selector}" not found for module "${this.name}"`);
            return false;
        }
        return true;
    }

    /**
     * Get state
     */
    getState(key, defaultValue) {
        return Store.get(`${this.name}:${key}`, defaultValue);
    }

    /**
     * Set state
     */
    setState(key, value) {
        Store.set(`${this.name}:${key}`, value);
    }

    /**
     * Subscribe to state changes
     */
    onState(key, callback) {
        return Store.subscribe(`${this.name}:${key}`, callback);
    }

    /**
     * Emit event
     */
    emit(event, data) {
        EventBus.emit(`${this.name}:${event}`, data);
    }

    /**
     * Listen to event
     */
    on(event, callback) {
        return EventBus.on(`${this.name}:${event}`, callback);
    }

    /**
     * Show notification
     */
    notify(message, type = 'info', duration = 5000) {
        return UI.notify(message, type, duration);
    }

    /**
     * Show success notification
     */
    success(message, duration = 5000) {
        return this.notify(message, 'success', duration);
    }

    /**
     * Show error notification
     */
    error(message, duration = 5000) {
        return this.notify(message, 'error', duration);
    }

    /**
     * Show warning notification
     */
    warning(message, duration = 5000) {
        return this.notify(message, 'warning', duration);
    }
}

/**
 * Auto-initialize modules on DOM ready
 */
export function autoInitModules() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', async () => {
            await Theme.init();
            await ModuleSystem.initAll();
        });
    } else {
        (async () => {
            await Theme.init();
            await ModuleSystem.initAll();
        })();
    }
}
