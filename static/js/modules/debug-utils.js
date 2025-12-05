/**
 * Debug Utilities Module
 * 
 * Advanced debugging tools including console logger, network monitor,
 * state inspector, performance profiler, and error tracker.
 * 
 * @module DebugUtils
 * @extends BaseModule
 */

import { Store, EventBus, API, UI, DOM, Utils } from './core-library.js';
import { BaseModule } from './module-system.js';

class DebugUtils extends BaseModule {
    constructor() {
        super('debug-utils');
        
        // Initial state
        this.setState({
            logging: {
                enabled: false,
                level: 'info', // debug, info, warn, error
                buffer: [],
                maxBufferSize: 1000
            },
            network: {
                monitoring: false,
                requests: [],
                maxRequests: 100
            },
            performance: {
                tracking: false,
                marks: {},
                measures: []
            },
            errors: {
                tracking: true,
                errors: [],
                maxErrors: 50
            }
        });
        
        // Log levels with priorities
        this.logLevels = {
            debug: { priority: 0, color: '#6c757d', icon: '🐛' },
            info: { priority: 1, color: '#0dcaf0', icon: 'ℹ️' },
            warn: { priority: 2, color: '#ffc107', icon: '⚠️' },
            error: { priority: 3, color: '#dc3545', icon: '❌' }
        };
    }

    /**
     * Initialize debug utilities
     */
    async onInit() {
        console.log('[DebugUtils] Initializing...');
        
        // Setup error tracking
        this.setupErrorTracking();
        
        // Setup network monitoring
        this.setupNetworkMonitoring();
        
        // Setup performance tracking
        this.setupPerformanceTracking();
        
        // Subscribe to developer mode changes
        EventBus.on('developer-mode:changed', ({ enabled }) => {
            if (enabled) {
                this.enable();
            } else {
                this.disable();
            }
        });
        
        console.log('[DebugUtils] Initialized');
    }

    // ==================== Console Logger ====================

    /**
     * Enable console logging
     * @param {string} level - Minimum log level (debug, info, warn, error)
     */
    enableLogging(level = 'info') {
        this.setState({
            logging: {
                ...this.getState('logging'),
                enabled: true,
                level
            }
        });
        
        console.log(`[DebugUtils] Logging enabled at level: ${level}`);
    }

    /**
     * Disable console logging
     */
    disableLogging() {
        this.setState({
            logging: {
                ...this.getState('logging'),
                enabled: false
            }
        });
        
        console.log('[DebugUtils] Logging disabled');
    }

    /**
     * Log a message
     * @param {string} level - Log level
     * @param {string} message - Log message
     * @param {*} data - Additional data
     */
    log(level, message, data = null) {
        const loggingState = this.getState('logging');
        
        if (!loggingState.enabled) return;
        
        const logLevel = this.logLevels[level];
        const currentLevel = this.logLevels[loggingState.level];
        
        // Check if this log level should be displayed
        if (logLevel.priority < currentLevel.priority) return;
        
        const entry = {
            level,
            message,
            data,
            timestamp: new Date().toISOString(),
            icon: logLevel.icon,
            color: logLevel.color
        };
        
        // Add to buffer
        const buffer = [...loggingState.buffer, entry];
        if (buffer.length > loggingState.maxBufferSize) {
            buffer.shift(); // Remove oldest entry
        }
        
        this.setState({
            logging: {
                ...loggingState,
                buffer
            }
        });
        
        // Console output with styling
        const style = `color: ${logLevel.color}; font-weight: bold;`;
        console.log(
            `%c${logLevel.icon} [${level.toUpperCase()}]`,
            style,
            message,
            data || ''
        );
        
        // Emit event for log viewers
        EventBus.emit('debug:log', entry);
    }

    /**
     * Log debug message
     */
    debug(message, data) {
        this.log('debug', message, data);
    }

    /**
     * Log info message
     */
    info(message, data) {
        this.log('info', message, data);
    }

    /**
     * Log warning
     */
    warn(message, data) {
        this.log('warn', message, data);
    }

    /**
     * Log error
     */
    error(message, data) {
        this.log('error', message, data);
    }

    /**
     * Get log buffer
     * @returns {Array} Log entries
     */
    getLogBuffer() {
        return this.getState('logging').buffer;
    }

    /**
     * Clear log buffer
     */
    clearLogBuffer() {
        this.setState({
            logging: {
                ...this.getState('logging'),
                buffer: []
            }
        });
        
        console.log('[DebugUtils] Log buffer cleared');
    }

    // ==================== Network Monitor ====================

    /**
     * Setup network monitoring
     */
    setupNetworkMonitoring() {
        // Intercept fetch calls
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            const networkState = this.getState('network');
            
            if (networkState.monitoring) {
                const startTime = performance.now();
                const [url, options = {}] = args;
                
                const requestInfo = {
                    url: url.toString(),
                    method: options.method || 'GET',
                    timestamp: new Date().toISOString(),
                    startTime
                };
                
                try {
                    const response = await originalFetch(...args);
                    const duration = Math.round(performance.now() - startTime);
                    
                    const requestData = {
                        ...requestInfo,
                        status: response.status,
                        statusText: response.statusText,
                        duration,
                        success: response.ok
                    };
                    
                    this.recordNetworkRequest(requestData);
                    
                    return response;
                    
                } catch (error) {
                    const duration = Math.round(performance.now() - startTime);
                    
                    const requestData = {
                        ...requestInfo,
                        status: 0,
                        statusText: 'Network Error',
                        duration,
                        success: false,
                        error: error.message
                    };
                    
                    this.recordNetworkRequest(requestData);
                    
                    throw error;
                }
            }
            
            return originalFetch(...args);
        };
    }

    /**
     * Record network request
     * @param {Object} requestData - Request information
     */
    recordNetworkRequest(requestData) {
        const networkState = this.getState('network');
        
        const requests = [...networkState.requests, requestData];
        if (requests.length > networkState.maxRequests) {
            requests.shift(); // Remove oldest request
        }
        
        this.setState({
            network: {
                ...networkState,
                requests
            }
        });
        
        // Log network request
        const statusColor = requestData.success ? '#28a745' : '#dc3545';
        console.log(
            `%c🌐 ${requestData.method} ${requestData.url}`,
            `color: ${statusColor}`,
            `${requestData.status} (${requestData.duration}ms)`
        );
        
        // Emit event
        EventBus.emit('debug:network-request', requestData);
    }

    /**
     * Enable network monitoring
     */
    enableNetworkMonitoring() {
        this.setState({
            network: {
                ...this.getState('network'),
                monitoring: true
            }
        });
        
        console.log('[DebugUtils] Network monitoring enabled');
    }

    /**
     * Disable network monitoring
     */
    disableNetworkMonitoring() {
        this.setState({
            network: {
                ...this.getState('network'),
                monitoring: false
            }
        });
        
        console.log('[DebugUtils] Network monitoring disabled');
    }

    /**
     * Get network requests
     * @returns {Array} Network requests
     */
    getNetworkRequests() {
        return this.getState('network').requests;
    }

    /**
     * Clear network requests
     */
    clearNetworkRequests() {
        this.setState({
            network: {
                ...this.getState('network'),
                requests: []
            }
        });
        
        console.log('[DebugUtils] Network requests cleared');
    }

    // ==================== State Inspector ====================

    /**
     * Inspect global Store state
     * @returns {Object} Current state
     */
    inspectStore() {
        const state = Store.getAll ? Store.getAll() : Store.state || {};
        console.table(state);
        return state;
    }

    /**
     * Watch a Store key for changes
     * @param {string} key - Store key to watch
     * @param {Function} callback - Callback function
     */
    watchStore(key, callback) {
        Store.subscribe(key, (value) => {
            console.log(`%c📊 Store[${key}] changed:`, 'color: #0d6efd; font-weight: bold;', value);
            if (callback) callback(value);
        });
        
        console.log(`[DebugUtils] Watching Store key: ${key}`);
    }

    /**
     * Get all registered modules
     * @returns {Array} Module names
     */
    inspectModules() {
        if (typeof ModuleSystem === 'undefined') {
            console.warn('[DebugUtils] ModuleSystem not available');
            return [];
        }
        
        const modules = window.ModuleSystem.getAll ? window.ModuleSystem.getAll() : {};
        console.table(modules);
        return Object.keys(modules);
    }

    /**
     * Inspect a specific module
     * @param {string} moduleName - Module name
     */
    inspectModule(moduleName) {
        if (typeof ModuleSystem === 'undefined') {
            console.warn('[DebugUtils] ModuleSystem not available');
            return;
        }
        
        const module = window.ModuleSystem.get(moduleName);
        if (!module) {
            console.warn(`[DebugUtils] Module not found: ${moduleName}`);
            return;
        }
        
        console.group(`Module: ${moduleName}`);
        console.log('State:', module.getState());
        console.log('Instance:', module);
        console.groupEnd();
        
        return module;
    }

    // ==================== Performance Profiler ====================

    /**
     * Setup performance tracking
     */
    setupPerformanceTracking() {
        // Performance observer for long tasks
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) { // Log tasks longer than 50ms
                            console.warn(
                                `⏱️ Long task detected: ${entry.name} (${Math.round(entry.duration)}ms)`
                            );
                        }
                    }
                });
                
                observer.observe({ entryTypes: ['measure', 'navigation'] });
            } catch (error) {
                console.warn('[DebugUtils] PerformanceObserver not fully supported');
            }
        }
    }

    /**
     * Mark performance point
     * @param {string} name - Mark name
     */
    mark(name) {
        if ('performance' in window && performance.mark) {
            performance.mark(name);
            
            const performanceState = this.getState('performance');
            this.setState({
                performance: {
                    ...performanceState,
                    marks: {
                        ...performanceState.marks,
                        [name]: performance.now()
                    }
                }
            });
            
            console.log(`⏱️ Performance mark: ${name}`);
        }
    }

    /**
     * Measure performance between two marks
     * @param {string} name - Measure name
     * @param {string} startMark - Start mark name
     * @param {string} endMark - End mark name (optional, defaults to now)
     */
    measure(name, startMark, endMark = null) {
        if ('performance' in window && performance.measure) {
            try {
                if (endMark) {
                    performance.measure(name, startMark, endMark);
                } else {
                    performance.measure(name, startMark);
                }
                
                const measure = performance.getEntriesByName(name, 'measure')[0];
                const duration = Math.round(measure.duration);
                
                const performanceState = this.getState('performance');
                const measures = [...performanceState.measures, {
                    name,
                    startMark,
                    endMark,
                    duration,
                    timestamp: new Date().toISOString()
                }];
                
                this.setState({
                    performance: {
                        ...performanceState,
                        measures
                    }
                });
                
                console.log(`⏱️ Performance measure: ${name} = ${duration}ms`);
                
                return duration;
                
            } catch (error) {
                console.warn(`[DebugUtils] Failed to measure: ${error.message}`);
            }
        }
    }

    /**
     * Get performance metrics
     * @returns {Object} Performance data
     */
    getPerformanceMetrics() {
        const performanceState = this.getState('performance');
        
        const metrics = {
            marks: performanceState.marks,
            measures: performanceState.measures,
            navigation: null,
            memory: null
        };
        
        // Navigation timing
        if ('performance' in window && performance.timing) {
            const timing = performance.timing;
            metrics.navigation = {
                domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                loadComplete: timing.loadEventEnd - timing.navigationStart,
                domReady: timing.domInteractive - timing.navigationStart
            };
        }
        
        // Memory usage (Chrome only)
        if ('memory' in performance) {
            metrics.memory = {
                usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1048576), // MB
                totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1048576),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576)
            };
        }
        
        console.table(metrics);
        return metrics;
    }

    // ==================== Error Tracker ====================

    /**
     * Setup error tracking
     */
    setupErrorTracking() {
        const errorsState = this.getState('errors');
        
        if (!errorsState.tracking) return;
        
        // Global error handler
        window.addEventListener('error', (event) => {
            this.recordError({
                type: 'error',
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                stack: event.error?.stack,
                timestamp: new Date().toISOString()
            });
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.recordError({
                type: 'unhandledRejection',
                message: event.reason?.message || event.reason,
                stack: event.reason?.stack,
                timestamp: new Date().toISOString()
            });
        });
        
        console.log('[DebugUtils] Error tracking enabled');
    }

    /**
     * Record an error
     * @param {Object} errorData - Error information
     */
    recordError(errorData) {
        const errorsState = this.getState('errors');
        
        const errors = [...errorsState.errors, errorData];
        if (errors.length > errorsState.maxErrors) {
            errors.shift(); // Remove oldest error
        }
        
        this.setState({
            errors: {
                ...errorsState,
                errors
            }
        });
        
        console.error('❌ Error tracked:', errorData);
        
        // Emit event
        EventBus.emit('debug:error', errorData);
        
        // Show notification for critical errors
        if (errorData.type === 'error') {
            UI.error(`JavaScript Error: ${errorData.message}`);
        }
    }

    /**
     * Get tracked errors
     * @returns {Array} Error records
     */
    getErrors() {
        return this.getState('errors').errors;
    }

    /**
     * Clear error records
     */
    clearErrors() {
        this.setState({
            errors: {
                ...this.getState('errors'),
                errors: []
            }
        });
        
        console.log('[DebugUtils] Error records cleared');
    }

    // ==================== Utilities ====================

    /**
     * Enable all debug utilities
     */
    enable() {
        this.enableLogging('debug');
        this.enableNetworkMonitoring();
        this.success('Debug utilities enabled');
    }

    /**
     * Disable all debug utilities
     */
    disable() {
        this.disableLogging();
        this.disableNetworkMonitoring();
        this.info('Debug utilities disabled');
    }

    /**
     * Export debug data
     * @returns {Object} All debug data
     */
    exportData() {
        return {
            logs: this.getLogBuffer(),
            networkRequests: this.getNetworkRequests(),
            errors: this.getErrors(),
            performance: this.getPerformanceMetrics(),
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Download debug data as JSON
     */
    downloadData() {
        const data = this.exportData();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `debug-data-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        this.success('Debug data downloaded');
    }

    /**
     * Cleanup on destroy
     */
    onDestroy() {
        console.log('[DebugUtils] Destroyed');
    }
}

// Export module
export default DebugUtils;
