/**
 * Features Configuration Module
 * 
 * Manages dashboard feature toggles including VirusTotal integration,
 * duplicate detection, reports & analytics, and developer mode.
 * 
 * @module FeaturesConfig
 * @extends BaseModule
 */

import { Store, EventBus, API, UI, DOM } from './core-library.js';
import { BaseModule } from './module-system.js';

class FeaturesConfig extends BaseModule {
    constructor() {
        super('features-config');
        
        // Initial state
        this.setState({
            loading: false,
            virustotal_enabled: true,
            vt_api_key: '',
            duplicates_enabled: true,
            reports_enabled: true,
            developer_mode: false
        });
    }

    /**
     * Initialize the features config module
     */
    async onInit() {
        console.log('[FeaturesConfig] Initializing...');
        
        // Bind UI elements
        this.bindUI();
        
        // Load current configuration
        await this.loadConfig();
        
        console.log('[FeaturesConfig] Initialized');
    }

    /**
     * Bind UI event handlers
     */
    bindUI() {
        // VirusTotal API Key
        const vtKeyInput = DOM.query('#cfg-vt-api-key');
        if (vtKeyInput) {
            vtKeyInput.addEventListener('input', (e) => {
                this.setState({ vt_api_key: e.target.value });
            });
        }
        
        // Feature toggles
        this.bindToggle('#cfg-feat-virustotal', 'virustotal_enabled');
        this.bindToggle('#cfg-feat-duplicates', 'duplicates_enabled');
        this.bindToggle('#cfg-feat-reports', 'reports_enabled');
        this.bindToggle('#cfg-feat-developer-mode', 'developer_mode');
        
        // Save button
        const saveBtn = DOM.query('#btn-save-features, button[onclick="saveFeaturesConfig()"]');
        if (saveBtn) {
            saveBtn.onclick = () => this.save();
        }
    }

    /**
     * Bind a checkbox toggle to state
     * @param {string} selector - Checkbox selector
     * @param {string} stateKey - State key to bind to
     */
    bindToggle(selector, stateKey) {
        const checkbox = DOM.query(selector);
        if (!checkbox) return;
        
        // Update state when checkbox changes
        checkbox.addEventListener('change', (e) => {
            this.setState({ [stateKey]: e.target.checked });
            
            // Emit specific events for other modules
            if (stateKey === 'developer_mode') {
                EventBus.emit('developer-mode:changed', { enabled: e.target.checked });
            }
        });
        
        // Update checkbox when state changes
        this.onState(stateKey, (value) => {
            checkbox.checked = value;
        });
    }

    /**
     * Load current configuration from server
     */
    async loadConfig() {
        this.setState({ loading: true });
        
        try {
            const config = await API.get('/api/organizer/config');
            const features = config.features || {};
            
            this.setState({
                virustotal_enabled: features.virustotal_enabled !== false,
                vt_api_key: config.vt_api_key || config.virustotal_api_key || '',
                duplicates_enabled: features.duplicates_enabled !== false,
                reports_enabled: features.reports_enabled !== false,
                developer_mode: features.developer_mode === true,
                loading: false
            });
            
            // Update UI
            this.updateUI();
            
            console.log('[FeaturesConfig] Loaded:', this.getState());
            
        } catch (error) {
            this.error(`Failed to load configuration: ${error.message}`);
            this.setState({ loading: false });
        }
    }

    /**
     * Update UI with current state
     */
    updateUI() {
        const state = this.getState();
        
        // VT API Key
        const vtKeyInput = DOM.query('#cfg-vt-api-key');
        if (vtKeyInput) {
            vtKeyInput.value = state.vt_api_key;
        }
        
        // Feature toggles (already bound via onState)
        // Just need to trigger initial update
        const checkboxes = {
            '#cfg-feat-virustotal': state.virustotal_enabled,
            '#cfg-feat-duplicates': state.duplicates_enabled,
            '#cfg-feat-reports': state.reports_enabled,
            '#cfg-feat-developer-mode': state.developer_mode
        };
        
        Object.entries(checkboxes).forEach(([selector, value]) => {
            const checkbox = DOM.query(selector);
            if (checkbox) checkbox.checked = value;
        });
    }

    /**
     * Save configuration to server
     */
    async save() {
        const state = this.getState();
        
        this.setState({ loading: true });
        
        try {
            const payload = {
                vt_api_key: state.vt_api_key || null,
                virustotal_api_key: state.vt_api_key || null,  // Backwards compatibility
                features: {
                    virustotal_enabled: state.virustotal_enabled,
                    duplicates_enabled: state.duplicates_enabled,
                    reports_enabled: state.reports_enabled,
                    developer_mode: state.developer_mode
                }
            };
            
            const response = await API.post('/api/update', payload);
            
            if (response.success || response.message) {
                this.success('Features configuration saved successfully');
                
                // Emit events for dependent modules
                EventBus.emit('config:updated', payload);
                EventBus.emit('features:updated', payload.features);
                
                // Reload to ensure sync
                await this.loadConfig();
            } else {
                throw new Error('Failed to save configuration');
            }
            
        } catch (error) {
            this.error(`Failed to save configuration: ${error.message}`);
        } finally {
            this.setState({ loading: false });
        }
    }

    /**
     * Get feature state
     * @param {string} feature - Feature name
     * @returns {boolean} Feature enabled state
     */
    isFeatureEnabled(feature) {
        const featureMap = {
            'virustotal': 'virustotal_enabled',
            'duplicates': 'duplicates_enabled',
            'reports': 'reports_enabled',
            'developer': 'developer_mode'
        };
        
        const stateKey = featureMap[feature] || feature + '_enabled';
        return this.getState(stateKey) === true;
    }

    /**
     * Toggle a feature on/off
     * @param {string} feature - Feature name
     */
    async toggleFeature(feature) {
        const featureMap = {
            'virustotal': 'virustotal_enabled',
            'duplicates': 'duplicates_enabled',
            'reports': 'reports_enabled',
            'developer': 'developer_mode'
        };
        
        const stateKey = featureMap[feature] || feature + '_enabled';
        const currentValue = this.getState(stateKey);
        
        this.setState({ [stateKey]: !currentValue });
        await this.save();
    }

    /**
     * Cleanup on destroy
     */
    onDestroy() {
        console.log('[FeaturesConfig] Destroyed');
    }
}

// Export module
export default FeaturesConfig;
