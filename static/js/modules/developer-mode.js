/**
 * Developer Mode Module
 * 
 * Manages developer mode state and UI elements visibility.
 * Uses Store for state management and EventBus for cross-module communication.
 * 
 * @module DeveloperMode
 * @extends BaseModule
 */

import { Store, EventBus, API, UI } from './core-library.js';
import { BaseModule } from './module-system.js';

class DeveloperMode extends BaseModule {
    constructor() {
        super('developer-mode');
        
        // Initial state
        this.setState({
            enabled: false,
            loading: false
        });
    }

    /**
     * Initialize the developer mode module
     */
    async onInit() {
        console.log('[DeveloperMode] Initializing...');
        
        // Load initial developer mode state from server
        await this.loadDeveloperMode();
        
        // Subscribe to config changes
        EventBus.on('config:updated', () => this.loadDeveloperMode());
        EventBus.on('features:updated', () => this.loadDeveloperMode());
        
        // Subscribe to state changes to update UI
        this.onState('enabled', (enabled) => {
            this.applyDeveloperMode(enabled);
        });
        
        console.log('[DeveloperMode] Initialized with state:', this.getState());
    }

    /**
     * Load developer mode setting from server configuration
     */
    async loadDeveloperMode() {
        this.setState({ loading: true });
        
        try {
            const config = await API.get('/api/organizer/config', { cache: 'no-store' });
            const features = config.features || {};
            const enabled = features.developer_mode === true;
            
            this.setState({ 
                enabled,
                loading: false
            });
            
            console.log('[DeveloperMode] Loaded from server:', { enabled });
            
            // Emit event for other modules
            EventBus.emit('developer-mode:changed', { enabled });
            
        } catch (error) {
            console.warn('[DeveloperMode] Failed to load setting:', error);
            this.setState({ loading: false });
        }
    }

    /**
     * Apply developer mode to the UI
     * @param {boolean} enabled - Whether developer mode is enabled
     */
    applyDeveloperMode(enabled) {
        // Toggle body class
        if (enabled) {
            document.body.classList.add('developer-mode');
        } else {
            document.body.classList.remove('developer-mode');
        }
        
        // Show/hide developer-only elements
        const devElements = document.querySelectorAll('.dev-only-element');
        devElements.forEach(el => {
            el.style.display = enabled ? '' : 'none';
        });
        
        console.log('[DeveloperMode] Applied:', { enabled, devElementsCount: devElements.length });
    }

    /**
     * Toggle developer mode on/off
     */
    async toggle() {
        const currentState = this.getState('enabled');
        await this.setEnabled(!currentState);
    }

    /**
     * Enable developer mode
     */
    async enable() {
        await this.setEnabled(true);
    }

    /**
     * Disable developer mode
     */
    async disable() {
        await this.setEnabled(false);
    }

    /**
     * Set developer mode enabled state
     * @param {boolean} enabled - New enabled state
     */
    async setEnabled(enabled) {
        this.setState({ loading: true });
        
        try {
            // Update server configuration
            const response = await API.post('/api/organizer/config', {
                features: {
                    developer_mode: enabled
                }
            });
            
            if (response.success || response.message) {
                this.setState({ 
                    enabled,
                    loading: false
                });
                
                this.success(
                    `Developer mode ${enabled ? 'enabled' : 'disabled'}`
                );
                
                EventBus.emit('developer-mode:changed', { enabled });
            } else {
                throw new Error('Failed to update developer mode');
            }
            
        } catch (error) {
            this.error(`Failed to ${enabled ? 'enable' : 'disable'} developer mode: ${error.message}`);
            this.setState({ loading: false });
        }
    }

    /**
     * Check if developer mode is currently enabled
     * @returns {boolean}
     */
    isEnabled() {
        return this.getState('enabled');
    }

    /**
     * Get developer mode toggle button and bind click handler
     * @param {string} selector - Button selector
     */
    bindToggleButton(selector) {
        const button = document.querySelector(selector);
        if (!button) {
            console.warn('[DeveloperMode] Toggle button not found:', selector);
            return;
        }
        
        button.addEventListener('click', () => this.toggle());
        
        // Update button state
        this.onState('enabled', (enabled) => {
            button.checked = enabled;
            button.setAttribute('aria-checked', enabled.toString());
        });
        
        // Set initial state
        button.checked = this.getState('enabled');
    }

    /**
     * Cleanup on destroy
     */
    onDestroy() {
        // Remove developer mode class
        document.body.classList.remove('developer-mode');
        console.log('[DeveloperMode] Destroyed');
    }
}

// Export module instance
export default DeveloperMode;
