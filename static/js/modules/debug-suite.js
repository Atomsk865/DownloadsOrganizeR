/**
 * Debug Suite Module
 * 
 * Comprehensive debugging and testing interface for the dashboard.
 * Includes API testing, environment checks, pytest integration, and smart self-tests.
 * 
 * @module DebugSuite
 * @extends BaseModule
 */

import { Store, EventBus, API, UI, DOM, Utils } from './core-library.js';
import { BaseModule } from './module-system.js';

class DebugSuite extends BaseModule {
    constructor() {
        super('debug-suite');
        
        // Initial state
        this.setState({
            tests: [],
            running: false,
            results: {
                passed: 0,
                failed: 0,
                warnings: 0,
                total: 0
            },
            lastRun: null
        });
        
        // Test definitions
        this.testDefinitions = [
            {
                name: 'API Health',
                method: 'GET',
                url: '/api/env/ping',
                expected: 'Status 200, {"pong": true}'
            },
            {
                name: 'Config Endpoint',
                method: 'GET',
                url: '/api/organizer/config',
                expected: 'Status 200, valid config JSON'
            },
            {
                name: 'Recent Files',
                method: 'GET',
                url: '/api/recent_files',
                expected: 'Status 200, array of files'
            },
            {
                name: 'Service Status',
                method: 'GET',
                url: '/status',
                expected: 'Status 200, service information'
            },
            {
                name: 'Duplicates Endpoint',
                method: 'GET',
                url: '/api/duplicates',
                expected: 'Status 200 or 403'
            }
        ];
    }

    /**
     * Initialize the debug suite
     */
    async onInit() {
        console.log('[DebugSuite] Initializing...');
        
        // Bind UI elements
        this.bindUI();
        
        // Subscribe to developer mode changes
        EventBus.on('developer-mode:changed', ({ enabled }) => {
            console.log('[DebugSuite] Developer mode changed:', enabled);
        });
        
        console.log('[DebugSuite] Initialized');
    }

    /**
     * Bind UI event handlers
     */
    bindUI() {
        // Run all tests button
        const runAllBtn = DOM.query('#run-all-tests');
        if (runAllBtn) {
            runAllBtn.addEventListener('click', () => this.runAllTests());
        }
        
        // Run pytest button
        const runPytestBtn = DOM.query('#run-pytests');
        if (runPytestBtn) {
            runPytestBtn.addEventListener('click', () => this.runPytests());
        }
        
        // Run smart self-test button
        const runSelfTestBtn = DOM.query('#run-self-test');
        if (runSelfTestBtn) {
            runSelfTestBtn.addEventListener('click', () => this.runSmartSelfTest());
        }
        
        // Clear log button
        const clearLogBtn = DOM.query('#clear-log');
        if (clearLogBtn) {
            clearLogBtn.addEventListener('click', () => this.clearLog());
        }
    }

    /**
     * Run all API endpoint tests
     */
    async runAllTests() {
        this.setState({ running: true });
        this.clearLog();
        
        this.logInfo('Starting endpoint tests...');
        
        const results = {
            passed: 0,
            failed: 0,
            warnings: 0,
            total: this.testDefinitions.length
        };
        
        for (const test of this.testDefinitions) {
            const result = await this.runSingleTest(test);
            
            if (result.success) {
                results.passed++;
            } else if (result.warning) {
                results.warnings++;
            } else {
                results.failed++;
            }
        }
        
        this.setState({ 
            running: false,
            results,
            lastRun: new Date().toISOString()
        });
        
        // Show summary
        this.logSummary(results);
    }

    /**
     * Run a single API test
     * @param {Object} test - Test definition
     * @returns {Object} Test result
     */
    async runSingleTest(test) {
        const { name, method, url, expected } = test;
        
        try {
            const startTime = performance.now();
            const response = await fetch(url, {
                method,
                credentials: 'include'
            });
            const duration = Math.round(performance.now() - startTime);
            
            const ok = response.ok;
            const status = response.status;
            
            // Try to parse response
            let body = '';
            try {
                const json = await response.json();
                body = JSON.stringify(json, null, 2);
            } catch {
                body = await response.text();
            }
            
            // Determine success/warning/failure
            const success = ok && status >= 200 && status < 300;
            const warning = status === 403 || status === 401; // Auth issues are warnings
            
            // Log result
            this.logTestResult({
                name,
                method,
                url,
                expected,
                status,
                ok: success,
                warning,
                duration,
                body: body.substring(0, 500) // Truncate long responses
            });
            
            return { success, warning, error: null };
            
        } catch (error) {
            // Network or other error
            this.logTestResult({
                name,
                method,
                url,
                expected,
                status: 'ERROR',
                ok: false,
                warning: false,
                error: error.message,
                body: ''
            });
            
            return { success: false, warning: false, error: error.message };
        }
    }

    /**
     * Run pytest test suite
     */
    async runPytests() {
        this.setState({ running: true });
        this.logInfo('Running pytest suite...');
        
        try {
            const result = await API.post('/env-test/run-tests');
            
            const success = result.success && result.exit_code === 0;
            const body = [
                `Exit Code: ${result.exit_code}`,
                '',
                'STDOUT:',
                result.stdout || '',
                '',
                'STDERR:',
                result.stderr || ''
            ].join('\n');
            
            this.logTestResult({
                name: 'Pytest Suite',
                method: 'POST',
                url: '/env-test/run-tests',
                expected: 'Exit code 0; stdout shows passed tests',
                status: success ? 200 : 500,
                ok: success,
                warning: false,
                body
            });
            
            if (success) {
                this.success('Pytest suite passed');
            } else {
                this.error('Pytest suite failed');
            }
            
        } catch (error) {
            this.logTestResult({
                name: 'Pytest Suite',
                method: 'POST',
                url: '/env-test/run-tests',
                expected: 'Exit code 0; stdout shows passed tests',
                status: 'ERROR',
                ok: false,
                warning: false,
                error: error.message,
                body: ''
            });
            
            this.error(`Pytest error: ${error.message}`);
        } finally {
            this.setState({ running: false });
        }
    }

    /**
     * Run smart self-test suite
     */
    async runSmartSelfTest() {
        this.setState({ running: true });
        this.clearLog();
        
        const results = {
            passed: [],
            warnings: [],
            errors: [],
            info: []
        };
        
        // Test 1: Authentication
        await this.testAuthentication(results);
        
        // Test 2: API Health
        await this.testAPIHealth(results);
        
        // Test 3: Dashboard Features
        await this.testDashboardFeatures(results);
        
        // Test 4: Browser Storage
        await this.testBrowserStorage(results);
        
        // Test 5: Session/Cookie Support
        await this.testSessionSupport(results);
        
        // Test 6: Network Connectivity
        await this.testNetworkConnectivity(results);
        
        // Show summary
        await Utils.waitFor(500);
        this.displaySelfTestSummary(results);
        
        this.setState({ running: false });
    }

    /**
     * Test authentication status
     */
    async testAuthentication(results) {
        this.addResult(results, 'info', 'Testing Authentication...');
        
        try {
            const response = await fetch('/api/env/ping', { credentials: 'include' });
            
            if (response.ok) {
                this.addResult(results, 'passed', 'Authentication', 'API accessible with current auth headers');
            } else if (response.status === 401) {
                this.addResult(results, 'warnings', 'Authentication', 'Not authenticated (401) - some features may be limited');
            } else {
                this.addResult(results, 'errors', 'Authentication', `Unexpected status: ${response.status}`);
            }
        } catch (error) {
            this.addResult(results, 'errors', 'Authentication', error.message);
        }
    }

    /**
     * Test API endpoint health
     */
    async testAPIHealth(results) {
        this.addResult(results, 'info', 'Checking API Health...');
        
        const endpoints = [
            { name: 'Ping', url: '/api/env/ping' },
            { name: 'Config', url: '/api/organizer/config' },
            { name: 'Recent Files', url: '/api/recent_files' },
            { name: 'Duplicates', url: '/api/duplicates' }
        ];
        
        let healthy = 0;
        
        for (const endpoint of endpoints) {
            try {
                const response = await fetch(endpoint.url, { credentials: 'include' });
                const responding = response.ok || [400, 403, 401].includes(response.status);
                
                if (responding) {
                    healthy++;
                    this.addResult(results, 'passed', `API: ${endpoint.name}`, 'Responding');
                } else {
                    this.addResult(results, 'warnings', `API: ${endpoint.name}`, `Status: ${response.status}`);
                }
            } catch (error) {
                this.addResult(results, 'errors', `API: ${endpoint.name}`, error.message);
            }
        }
        
        if (healthy === endpoints.length) {
            this.addResult(results, 'passed', 'API Health', `All ${healthy} endpoints responding`);
        } else if (healthy > 0) {
            this.addResult(results, 'warnings', 'API Health', `Only ${healthy}/${endpoints.length} endpoints responding`);
        } else {
            this.addResult(results, 'errors', 'API Health', 'No API endpoints responding');
        }
    }

    /**
     * Test dashboard features availability
     */
    async testDashboardFeatures(results) {
        this.addResult(results, 'info', 'Checking Dashboard Features...');
        
        const features = {
            'Core Library': typeof window.CoreLibrary !== 'undefined',
            'Module System': typeof window.ModuleSystem !== 'undefined',
            'Theme System': typeof window.ThemeSystem !== 'undefined',
            'Notifications': typeof UI !== 'undefined',
            'Event Bus': typeof EventBus !== 'undefined',
            'API Client': typeof API !== 'undefined'
        };
        
        Object.entries(features).forEach(([feature, available]) => {
            if (available) {
                this.addResult(results, 'passed', `Feature: ${feature}`, 'Loaded');
            } else {
                this.addResult(results, 'warnings', `Feature: ${feature}`, 'Not available');
            }
        });
    }

    /**
     * Test browser storage
     */
    async testBrowserStorage(results) {
        this.addResult(results, 'info', 'Testing Browser Storage...');
        
        try {
            const testKey = '__debug_test_' + Date.now();
            localStorage.setItem(testKey, 'test');
            const retrieved = localStorage.getItem(testKey);
            localStorage.removeItem(testKey);
            
            if (retrieved === 'test') {
                this.addResult(results, 'passed', 'Browser Storage', 'localStorage working');
            } else {
                this.addResult(results, 'errors', 'Browser Storage', 'localStorage not working properly');
            }
        } catch (error) {
            this.addResult(results, 'warnings', 'Browser Storage', 'localStorage disabled or blocked');
        }
    }

    /**
     * Test session/cookie support
     */
    async testSessionSupport(results) {
        try {
            const response = await fetch('/api/env/ping', { credentials: 'include' });
            if (response.ok) {
                this.addResult(results, 'passed', 'Cookies/Sessions', 'Credentials mode working');
            } else {
                this.addResult(results, 'warnings', 'Cookies/Sessions', 'Response not OK');
            }
        } catch (error) {
            this.addResult(results, 'warnings', 'Cookies/Sessions', 'May have CORS issues');
        }
    }

    /**
     * Test network connectivity and latency
     */
    async testNetworkConnectivity(results) {
        try {
            const start = performance.now();
            const response = await fetch('/api/env/ping', { credentials: 'include' });
            const latency = Math.round(performance.now() - start);
            
            if (latency < 100) {
                this.addResult(results, 'passed', 'Network Latency', `${latency}ms (excellent)`);
            } else if (latency < 500) {
                this.addResult(results, 'passed', 'Network Latency', `${latency}ms (good)`);
            } else {
                this.addResult(results, 'warnings', 'Network Latency', `${latency}ms (high latency)`);
            }
        } catch (error) {
            this.addResult(results, 'errors', 'Network Latency', 'Could not measure');
        }
    }

    /**
     * Add a test result to the results object
     */
    addResult(results, type, title, details = '') {
        const msg = details ? `${title}: ${details}` : title;
        results[type].push(msg);
        
        const badge = {
            passed: '<span class="badge bg-success">✓ PASS</span>',
            warnings: '<span class="badge bg-warning">⚠ WARN</span>',
            errors: '<span class="badge bg-danger">✗ FAIL</span>',
            info: '<span class="badge bg-info">ℹ INFO</span>'
        }[type];
        
        this.logEntry(`
            <div class="mb-2 p-2 rounded">
                <div><b>${title}</b> ${badge}</div>
                ${details ? `<div><small>${Utils.escapeHtml(details)}</small></div>` : ''}
            </div>
        `);
    }

    /**
     * Display self-test summary
     */
    displaySelfTestSummary(results) {
        const totalTests = results.passed.length + results.warnings.length + results.errors.length - results.info.length;
        const passRate = totalTests > 0 ? Math.round((results.passed.length / totalTests) * 100) : 0;
        
        let alertClass = 'alert-success';
        let title = '✓ System Healthy';
        
        if (results.errors.length > 0) {
            alertClass = 'alert-danger';
            title = '✗ Critical Issues Found';
        } else if (results.warnings.length > 0) {
            alertClass = 'alert-warning';
            title = '⚠ Issues Found';
        }
        
        const recommendations = results.errors.length > 0 ? `
            <div class="mt-2 small text-danger">
                <b>Recommendations:</b>
                <ul class="mb-0">
                    <li>Check API server status</li>
                    <li>Verify network connectivity</li>
                    <li>Clear browser cache and reload</li>
                    <li>Check console for JS errors (F12)</li>
                </ul>
            </div>
        ` : '';
        
        const summaryHtml = `
            <div class="alert ${alertClass} p-3 mt-3">
                <div><b>${title}</b></div>
                <div class="small mt-2">
                    <div>✓ Passed: ${results.passed.length}/${totalTests} (${passRate}%)</div>
                    ${results.warnings.length > 0 ? `<div>⚠ Warnings: ${results.warnings.length}</div>` : ''}
                    ${results.errors.length > 0 ? `<div>✗ Errors: ${results.errors.length}</div>` : ''}
                </div>
                ${recommendations}
            </div>
        `;
        
        const logContainer = DOM.query('#env-log');
        if (logContainer) {
            logContainer.insertAdjacentHTML('afterbegin', summaryHtml);
        }
    }

    /**
     * Log a test result entry
     */
    logTestResult(result) {
        const { name, method, url, expected, status, ok, warning, duration, error, body } = result;
        
        const statusClass = ok ? 'success' : warning ? 'warning' : 'danger';
        const statusBadge = ok ? '✓ PASS' : warning ? '⚠ WARN' : '✗ FAIL';
        
        const html = `
            <div class="test-result mb-3 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0"><i class="bi bi-arrow-right-circle me-2"></i>${Utils.escapeHtml(name)}</h6>
                    <span class="badge bg-${statusClass}">${statusBadge}</span>
                </div>
                <div class="small">
                    <div><b>Method:</b> ${Utils.escapeHtml(method)}</div>
                    <div><b>URL:</b> <code>${Utils.escapeHtml(url)}</code></div>
                    <div><b>Expected:</b> ${Utils.escapeHtml(expected)}</div>
                    <div><b>Status:</b> <span class="badge bg-${statusClass}">${status}</span></div>
                    ${duration ? `<div><b>Duration:</b> ${duration}ms</div>` : ''}
                    ${error ? `<div class="text-danger"><b>Error:</b> ${Utils.escapeHtml(error)}</div>` : ''}
                    ${body ? `<div class="mt-2"><b>Response:</b><pre class="bg-light p-2 rounded mt-1 small">${Utils.escapeHtml(body)}</pre></div>` : ''}
                </div>
            </div>
        `;
        
        this.logEntry(html);
    }

    /**
     * Log an info message
     */
    logInfo(message) {
        this.logEntry(`
            <div class="alert alert-info py-2 px-3 mb-2">
                <i class="bi bi-info-circle me-2"></i>${Utils.escapeHtml(message)}
            </div>
        `);
    }

    /**
     * Log a summary of test results
     */
    logSummary(results) {
        const { passed, failed, warnings, total } = results;
        const passRate = Math.round((passed / total) * 100);
        
        let alertClass = 'alert-success';
        let title = '✓ All Tests Passed';
        
        if (failed > 0) {
            alertClass = 'alert-danger';
            title = `✗ ${failed} Test${failed > 1 ? 's' : ''} Failed`;
        } else if (warnings > 0) {
            alertClass = 'alert-warning';
            title = `⚠ ${warnings} Warning${warnings > 1 ? 's' : ''}`;
        }
        
        const html = `
            <div class="alert ${alertClass} p-3 mt-3">
                <h5 class="mb-3">${title}</h5>
                <div>
                    <div><b>Passed:</b> ${passed}/${total} (${passRate}%)</div>
                    ${warnings > 0 ? `<div><b>Warnings:</b> ${warnings}</div>` : ''}
                    ${failed > 0 ? `<div><b>Failed:</b> ${failed}</div>` : ''}
                </div>
            </div>
        `;
        
        this.logEntry(html);
    }

    /**
     * Log an entry to the test log
     */
    logEntry(html) {
        const logContainer = DOM.query('#env-log');
        if (!logContainer) {
            console.warn('[DebugSuite] Log container #env-log not found');
            return;
        }
        
        logContainer.insertAdjacentHTML('beforeend', html);
        
        // Auto-scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    /**
     * Clear the test log
     */
    clearLog() {
        const logContainer = DOM.query('#env-log');
        if (logContainer) {
            logContainer.innerHTML = '';
        }
    }

    /**
     * Cleanup on destroy
     */
    onDestroy() {
        console.log('[DebugSuite] Destroyed');
    }
}

// Utility to escape HTML for safe rendering
Utils.escapeHtml = function(text) {
    if (typeof text !== 'string') return text;
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// Export module
export default DebugSuite;
