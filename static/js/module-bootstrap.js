/**
 * Module Loading Bootstrap
 * Orchestrates module loading and initialization
 */

class ModuleBootstrap {
    constructor() {
        this.modules = [];
        this.loadingState = 'idle'; // idle, loading, ready, error
        this.errors = [];
    }

    /**
     * Phase 1: Load core modules (required for everything)
     */
    async loadCoreModules() {
        console.log('📦 Loading core modules...');
        this.loadingState = 'loading';
        
        const coreModules = ['utils', 'auth', 'api', 'notifications', 'theme', 'state', 'charts'];
        
        try {
            await window.moduleManager.loadAll(coreModules);
            console.log('✓ Core modules loaded');
            return true;
        } catch (err) {
            console.error('✗ Failed to load core modules:', err);
            this.errors.push(`Core modules: ${err.message}`);
            this.loadingState = 'error';
            return false;
        }
    }

    /**
     * Phase 2: Load feature modules on demand
     */
    registerFeatureModules() {
        console.log('📋 Registering feature modules...');
        
        // Register feature modules with proper dependencies
        const features = [
            {
                name: 'statistics',
                file: '/static/js/statistics-module.js?v=' + window.assetVersion,
                deps: ['api', 'utils', 'charts', 'notifications']
            },
            {
                name: 'fileOrganization',
                file: '/static/js/file-organization-module.js?v=' + window.assetVersion,
                deps: ['api', 'utils', 'notifications']
            },
            {
                name: 'resourceMonitor',
                file: '/static/js/resource-monitor-module.js?v=' + window.assetVersion,
                deps: ['api', 'notifications']
            },
            {
                name: 'duplicates',
                file: '/static/js/duplicates-module.js?v=' + window.assetVersion,
                deps: ['api', 'utils', 'notifications']
            }
        ];
        
        features.forEach(feature => {
            this.registerLazyModule(feature.name, feature.file, feature.deps);
        });
    }

    /**
     * Register a lazy-loaded module from external script
     */
    registerLazyModule(name, scriptUrl, deps = []) {
        window.moduleManager.register(name, deps, async (depValues) => {
            // Load the script if not already loaded
            if (!document.querySelector(`script[src="${scriptUrl}"]`)) {
                await this.loadScript(scriptUrl);
            }
            
            // Module should have registered itself
            // If not found, try to load it again
            if (!window.moduleManager.get(name)) {
                throw new Error(`Module ${name} failed to register after loading ${scriptUrl}`);
            }
            
            return window.moduleManager.get(name);
        });
    }

    /**
     * Load external script
     */
    loadScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.async = true;
            
            script.onload = () => {
                console.log(`✓ Loaded: ${url.split('/').pop()}`);
                resolve();
            };
            
            script.onerror = () => {
                const error = new Error(`Failed to load script: ${url}`);
                console.error(error);
                reject(error);
            };
            
            document.head.appendChild(script);
        });
    }

    /**
     * Initialize dashboard after core modules ready
     */
    async initializeDashboard() {
        console.log('🚀 Initializing dashboard...');
        
        try {
            const state = window.moduleManager.get('state');
            const api = window.moduleManager.get('api');
            
            // Fetch app configuration
            const config = await api.get('/api/config');
            state.set('config', config);
            
            // Fetch user info
            const auth = await api.get('/auth/session');
            state.set('user', auth.user);
            
            // Set initial theme
            const theme = window.moduleManager.get('theme');
            theme.setTheme(localStorage.getItem('dashboard_theme') || 'default');
            
            this.loadingState = 'ready';
            console.log('✓ Dashboard initialized and ready');
            
            // Show ready indicator
            document.dispatchEvent(new CustomEvent('modulesReady', {
                detail: { state, api }
            }));
            
            return true;
        } catch (err) {
            console.error('✗ Dashboard initialization failed:', err);
            this.errors.push(`Dashboard init: ${err.message}`);
            this.loadingState = 'error';
            return false;
        }
    }

    /**
     * Load and initialize specific feature
     */
    async loadFeature(featureName) {
        try {
            console.log(`📂 Loading feature: ${featureName}`);
            const module = await window.moduleManager.load(featureName);
            console.log(`✓ Feature loaded: ${featureName}`);
            return module;
        } catch (err) {
            console.error(`✗ Failed to load feature ${featureName}:`, err);
            this.errors.push(`${featureName}: ${err.message}`);
            return null;
        }
    }

    /**
     * Get bootstrap status
     */
    getStatus() {
        return {
            state: this.loadingState,
            errors: this.errors,
            coreReady: window.moduleManager.isLoaded('utils'),
            featuresRegistered: [
                'statistics',
                'fileOrganization',
                'resourceMonitor',
                'duplicates'
            ].map(name => ({
                name,
                loaded: window.moduleManager.isLoaded(name)
            }))
        };
    }

    /**
     * Print detailed status
     */
    printStatus() {
        const status = this.getStatus();
        console.group('📊 Module Bootstrap Status');
        console.log('State:', status.state);
        console.log('Errors:', status.errors.length ? status.errors : 'none');
        console.log('Features:', status.featuresRegistered);
        console.groupEnd();
    }
}

// Create global bootstrap instance
window.bootstrap = new ModuleBootstrap();

/**
 * Main initialization flow
 */
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🔧 Starting module bootstrap...');
    
    try {
        // Phase 1: Load core modules
        if (!await window.bootstrap.loadCoreModules()) {
            console.error('Failed to load core modules, aborting');
            return;
        }
        
        // Phase 2: Register feature modules
        window.bootstrap.registerFeatureModules();
        
        // Phase 3: Initialize dashboard
        if (!await window.bootstrap.initializeDashboard()) {
            console.error('Failed to initialize dashboard');
            // Could show error UI here
        }
        
    } catch (err) {
        console.error('🔴 Bootstrap failed:', err);
        window.bootstrap.errors.push(`Bootstrap: ${err.message}`);
    }
    
    // Print final status
    window.bootstrap.printStatus();
});

// Export bootstrap for debugging
console.log('✓ Module Bootstrap loaded');
console.log('Access: window.bootstrap, window.moduleManager');
