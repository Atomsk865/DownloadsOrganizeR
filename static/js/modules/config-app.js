/**
 * Configuration Page App Module
 * Handles theme integration and config management using modular architecture
 */

import { Store, EventBus, UI, Theme, DOM } from './core-library.js';
import { BaseModule, ModuleSystem, autoInitModules } from './module-system.js';

export class ConfigApp extends BaseModule {
    constructor() {
        super('ConfigApp');
        this.themeSystem = null;
    }

    /**
     * Initialize the config app
     */
    async onInit() {
        // Wait for theme system
        await Theme.init();
        this.themeSystem = window.ThemeSystem;

        // Setup theme integration
        this.setupThemeIntegration();

        // Setup event listeners
        this.setupEventListeners();

        // Setup auth headers
        this.setupAuthHeaders();

        UI.info('Configuration page loaded', 3000);
    }

    /**
     * Setup theme integration
     */
    setupThemeIntegration() {
        const html = document.documentElement;
        
        // Apply saved theme on load
        const savedTheme = this.themeSystem?.getSavedTheme() || 'light';
        html.setAttribute('data-theme', savedTheme);

        // Listen for theme changes
        window.addEventListener('themeChanged', (e) => {
            const theme = e.detail?.theme || 'light';
            html.setAttribute('data-theme', theme);
        });
    }

    /**
     * Toggle between light and dark theme
     */
    toggleTheme() {
        if (!this.themeSystem) return;
        this.themeSystem.toggleTheme();
        
        const currentTheme = this.themeSystem.getCurrentTheme?.() || 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
    }

    /**
     * Setup event listeners for config modules
     */
    setupEventListeners() {
        // Listen for save events from config modules
        document.addEventListener('config:save', (e) => {
            UI.success(e.detail?.message || 'Settings saved');
        });

        document.addEventListener('config:error', (e) => {
            UI.error(e.detail?.message || 'Error occurred');
        });

        // Setup theme toggle button
        const themeToggleBtn = DOM.query('.theme-toggle-btn');
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', () => this.toggleTheme());
        }
    }

    /**
     * Setup auth headers for API calls
     */
    setupAuthHeaders() {
        window.getAuthHeaders = function() {
            const headers = {};
            try {
                const match = document.cookie.match(/(?:^|; )authHeader=([^;]+)/);
                if (match) {
                    headers['Authorization'] = decodeURIComponent(match[1]);
                }
            } catch (e) {
                console.warn('Failed to get auth headers:', e);
            }
            return headers;
        };
    }

    /**
     * Cleanup on destroy
     */
    async onDestroy() {
        // Cleanup if needed
    }
}

// Export singleton instance
export const configApp = new ConfigApp();

// Auto-initialize on page load
if (typeof window !== 'undefined') {
    (async () => {
        // Register config app module
        ModuleSystem.register('ConfigApp', {
            init: () => configApp.init(),
            destroy: () => configApp.destroy()
        });

        // Auto-initialize all modules
        autoInitModules();
    })();
}
