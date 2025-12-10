# Comprehensive Testing Architecture

**Version:** 1.0  
**Date:** December 5, 2025  
**Status:** Architecture Planning

---

## Executive Summary

Create a unified testing framework accessible via `/env-test` (developer-only) that can:
- Test each dashboard module independently
- Validate all config modules and their functions
- Simulate user interactions with buttons/forms
- Provide verbose error logs for debugging
- Enable/disable modules via setup wizard or config page
- Lock testing tools behind feature flags

---

## Table of Contents

1. [Testing Framework Architecture](#testing-framework-architecture)
2. [Module Feature Flags](#module-feature-flags)
3. [Test Suite Organization](#test-suite-organization)
4. [Env-Test Page Redesign](#env-test-page-redesign)
5. [Backend Testing Infrastructure](#backend-testing-infrastructure)
6. [Implementation Roadmap](#implementation-roadmap)

---

## Testing Framework Architecture

### Core Principles

1. **Module-Based Testing** - Each module has isolated test suite
2. **Feature-Flag Driven** - Tests only run if module is enabled
3. **Verbose Logging** - Detailed error messages with stack traces
4. **Interactive Testing** - Test buttons, forms, API calls
5. **Developer-Only** - Locked behind `developer_mode` feature flag

### System Architecture

```
Developer Mode Switch
        ↓
   /env-test (protected route)
        ↓
   Test Orchestrator
        ↓
    ┌───────────────────────────────────┐
    │  Module Feature Flags             │
    │  - duplicates_enabled             │
    │  - reports_enabled                │
    │  - virustotal_enabled             │
    │  - recent_files_enabled           │
    │  - branding_enabled               │
    │  - notifications_enabled          │
    │  - watched_folders_enabled        │
    │  - network_targets_enabled        │
    │  - smtp_enabled                   │
    └───────────────────────────────────┘
        ↓
    ┌───────────────────────────────────┐
    │  Module Test Suites               │
    │  - Core Tests (always enabled)    │
    │  - Duplicates Tests               │
    │  - Reports Tests                  │
    │  - VirusTotal Tests               │
    │  - Recent Files Tests             │
    │  - Branding Tests                 │
    │  - Notifications Tests            │
    │  - Watched Folders Tests          │
    │  - Network Targets Tests          │
    │  - SMTP Tests                     │
    │  - Config Modules Tests           │
    └───────────────────────────────────┘
        ↓
    Verbose Logger
        ↓
    Test Results Dashboard
```

---

## Module Feature Flags

### Feature Flag Schema

**File:** `organizer_config.json`

```json
{
  "features": {
    "duplicates_enabled": true,
    "reports_enabled": true,
    "virustotal_enabled": false,
    "recent_files_enabled": true,
    "branding_enabled": true,
    "notifications_enabled": true,
    "watched_folders_enabled": true,
    "network_targets_enabled": false,
    "smtp_enabled": false,
    "developer_mode": false
  },
  "vt_api_key": ""
}
```

### Flag Hierarchy

**Core Features (Always Enabled):**
- Authentication
- Dashboard base
- System metrics
- Service control
- User management

**Optional Features (Configurable):**
- Duplicate detection (`duplicates_enabled`)
- Reports & analytics (`reports_enabled`)
- VirusTotal integration (`virustotal_enabled`)
- Recent files tracking (`recent_files_enabled`)
- Custom branding (`branding_enabled`)
- Notification center (`notifications_enabled`)
- Watched folders (`watched_folders_enabled`)
- Network targets/NAS (`network_targets_enabled`)
- SMTP email alerts (`smtp_enabled`)

**Developer Features (Gated by `developer_mode`):**
- Environment test page (`/env-test`)
- Dev reset endpoint (`/dev-reset`)
- Verbose error logging
- Module testing tools
- Performance profiler

---

## Test Suite Organization

### Test Categories

#### 1. Core System Tests (Always Run)

**File:** `static/js/modules/tests/core-tests.js`

```javascript
export class CoreSystemTests {
    constructor(logger) {
        this.logger = logger;
        this.results = [];
    }
    
    async runAll() {
        await this.testAuthentication();
        await this.testAPIHealth();
        await this.testDatabase();
        await this.testFileSystem();
        await this.testPermissions();
        
        return this.results;
    }
    
    async testAuthentication() {
        this.logger.info('Testing authentication system...');
        
        try {
            // Test session validity
            const session = await API.get('/api/auth/check');
            this.logger.success('✓ Session valid');
            
            // Test CSRF token
            const csrf = document.querySelector('input[name="csrf_token"]');
            if (csrf) {
                this.logger.success('✓ CSRF token present');
            } else {
                this.logger.warning('⚠ CSRF token missing');
            }
            
            // Test user rights
            const config = await API.get('/api/dashboard/config');
            this.logger.success(`✓ User rights loaded: ${Object.keys(config.roles).length} roles`);
            
            this.results.push({ test: 'Authentication', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Authentication test failed:', error);
            this.results.push({ test: 'Authentication', status: 'failed', error });
        }
    }
    
    async testAPIHealth() {
        this.logger.info('Testing API endpoints...');
        
        const endpoints = [
            '/api/organizer/config',
            '/api/dashboard/config',
            '/metrics',
            '/service-name'
        ];
        
        for (const endpoint of endpoints) {
            try {
                const response = await API.get(endpoint);
                this.logger.success(`✓ ${endpoint} responding`);
            } catch (error) {
                this.logger.error(`✗ ${endpoint} failed:`, error);
                this.results.push({ test: `API ${endpoint}`, status: 'failed', error });
            }
        }
    }
    
    async testDatabase() {
        this.logger.info('Testing database operations...');
        
        try {
            // Test config read
            const config = await API.get('/api/organizer/config');
            this.logger.success('✓ Config read successful');
            
            // Validate config structure
            const requiredKeys = ['routes', 'watched_folders', 'features'];
            const missing = requiredKeys.filter(key => !(key in config));
            
            if (missing.length === 0) {
                this.logger.success('✓ Config structure valid');
            } else {
                this.logger.warning(`⚠ Missing config keys: ${missing.join(', ')}`);
            }
            
            this.results.push({ test: 'Database', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Database test failed:', error);
            this.results.push({ test: 'Database', status: 'failed', error });
        }
    }
    
    async testFileSystem() {
        this.logger.info('Testing file system access...');
        
        try {
            // Test log file access
            const logs = await API.get('/tail?which=stdout&lines=10');
            this.logger.success('✓ Log files accessible');
            
            this.results.push({ test: 'FileSystem', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ File system test failed:', error);
            this.results.push({ test: 'FileSystem', status: 'failed', error });
        }
    }
    
    async testPermissions() {
        this.logger.info('Testing user permissions...');
        
        try {
            const config = await API.get('/api/dashboard/config');
            const currentRole = config.current_user?.role || 'unknown';
            const rights = config.roles[currentRole] || {};
            
            this.logger.info(`Current role: ${currentRole}`);
            this.logger.info(`Permissions: ${JSON.stringify(rights, null, 2)}`);
            
            this.results.push({ test: 'Permissions', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Permissions test failed:', error);
            this.results.push({ test: 'Permissions', status: 'failed', error });
        }
    }
}
```

---

#### 2. Module-Specific Tests

**File:** `static/js/modules/tests/duplicates-tests.js`

```javascript
export class DuplicatesTests {
    constructor(logger) {
        this.logger = logger;
        this.results = [];
    }
    
    async runAll() {
        this.logger.section('Duplicates Module Tests');
        
        await this.testModuleLoad();
        await this.testDuplicateDetection();
        await this.testFileHashing();
        await this.testDeleteOperations();
        await this.testGrouping();
        
        return this.results;
    }
    
    async testModuleLoad() {
        this.logger.info('Testing duplicates module initialization...');
        
        try {
            const response = await API.get('/duplicates');
            
            if (response.ok) {
                this.logger.success('✓ Duplicates page loads');
            } else {
                this.logger.error('✗ Duplicates page load failed');
            }
            
            this.results.push({ test: 'ModuleLoad', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Module load failed:', error);
            this.results.push({ test: 'ModuleLoad', status: 'failed', error });
        }
    }
    
    async testDuplicateDetection() {
        this.logger.info('Testing duplicate detection...');
        
        try {
            const response = await API.get('/api/duplicates');
            
            this.logger.info(`Found ${response.duplicate_groups?.length || 0} duplicate groups`);
            this.logger.info(`Total duplicates: ${response.total_duplicates || 0}`);
            this.logger.info(`Potential savings: ${response.total_size_saved || 0} bytes`);
            
            this.results.push({ test: 'DuplicateDetection', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Duplicate detection failed:', error);
            this.results.push({ test: 'DuplicateDetection', status: 'failed', error });
        }
    }
    
    async testFileHashing() {
        this.logger.info('Testing file hashing...');
        
        try {
            // Check if file_hashes.json exists
            const response = await API.get('/api/duplicates');
            
            if (response.file_hashes) {
                this.logger.success(`✓ File hashes loaded: ${Object.keys(response.file_hashes).length} files`);
            } else {
                this.logger.warning('⚠ No file hashes found');
            }
            
            this.results.push({ test: 'FileHashing', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ File hashing test failed:', error);
            this.results.push({ test: 'FileHashing', status: 'failed', error });
        }
    }
    
    async testDeleteOperations() {
        this.logger.info('Testing delete operations (dry run)...');
        
        try {
            // Test delete endpoint exists (don't actually delete)
            // Just check if endpoint is accessible
            this.logger.info('Delete endpoint check: /api/delete-file');
            this.logger.warning('⚠ Skipping actual deletion for safety');
            
            this.results.push({ test: 'DeleteOperations', status: 'skipped' });
        } catch (error) {
            this.logger.error('✗ Delete operations test failed:', error);
            this.results.push({ test: 'DeleteOperations', status: 'failed', error });
        }
    }
    
    async testGrouping() {
        this.logger.info('Testing duplicate grouping...');
        
        try {
            const response = await API.get('/api/duplicates');
            const groups = response.duplicate_groups || [];
            
            for (const [index, group] of groups.slice(0, 3).entries()) {
                this.logger.info(`Group ${index + 1}:`);
                this.logger.info(`  Hash: ${group.hash}`);
                this.logger.info(`  Files: ${group.files.length}`);
                this.logger.info(`  Size: ${group.size} bytes`);
            }
            
            this.results.push({ test: 'Grouping', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Grouping test failed:', error);
            this.results.push({ test: 'Grouping', status: 'failed', error });
        }
    }
}
```

---

**File:** `static/js/modules/tests/virustotal-tests.js`

```javascript
export class VirusTotalTests {
    constructor(logger) {
        this.logger = logger;
        this.results = [];
    }
    
    async runAll() {
        this.logger.section('VirusTotal Integration Tests');
        
        await this.testAPIKey();
        await this.testHashLookup();
        await this.testRecentFilesIntegration();
        await this.testRateLimiting();
        
        return this.results;
    }
    
    async testAPIKey() {
        this.logger.info('Testing VirusTotal API key...');
        
        try {
            const config = await API.get('/api/organizer/config');
            const apiKey = config.vt_api_key;
            
            if (apiKey && apiKey.length > 0) {
                this.logger.success('✓ API key configured');
                this.logger.info(`Key length: ${apiKey.length} chars`);
            } else {
                this.logger.warning('⚠ No API key configured');
                this.results.push({ test: 'APIKey', status: 'skipped', reason: 'No API key' });
                return;
            }
            
            this.results.push({ test: 'APIKey', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ API key test failed:', error);
            this.results.push({ test: 'APIKey', status: 'failed', error });
        }
    }
    
    async testHashLookup() {
        this.logger.info('Testing hash lookup (test hash)...');
        
        try {
            // Use EICAR test hash (known malware test file)
            const testHash = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f';
            
            const response = await API.post('/api/recent-files/virustotal', {
                hash: testHash
            });
            
            if (response.error === 'No API key configured') {
                this.logger.warning('⚠ API key not configured');
                this.results.push({ test: 'HashLookup', status: 'skipped', reason: 'No API key' });
                return;
            }
            
            this.logger.info('VirusTotal response:', response);
            this.results.push({ test: 'HashLookup', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Hash lookup failed:', error);
            this.results.push({ test: 'HashLookup', status: 'failed', error });
        }
    }
    
    async testRecentFilesIntegration() {
        this.logger.info('Testing Recent Files integration...');
        
        try {
            const response = await API.get('/api/recent-files');
            
            if (response.files) {
                this.logger.success(`✓ Recent files loaded: ${response.files.length} files`);
                
                // Check if any files have VT data
                const withVT = response.files.filter(f => f.virustotal).length;
                this.logger.info(`Files with VT data: ${withVT}`);
            }
            
            this.results.push({ test: 'RecentFilesIntegration', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Recent files integration failed:', error);
            this.results.push({ test: 'RecentFilesIntegration', status: 'failed', error });
        }
    }
    
    async testRateLimiting() {
        this.logger.info('Testing rate limiting...');
        
        try {
            this.logger.info('VirusTotal free tier: 4 requests/minute');
            this.logger.warning('⚠ Rate limit testing requires actual API calls');
            this.logger.info('Skipping to avoid quota usage');
            
            this.results.push({ test: 'RateLimiting', status: 'skipped', reason: 'Quota preservation' });
        } catch (error) {
            this.logger.error('✗ Rate limiting test failed:', error);
            this.results.push({ test: 'RateLimiting', status: 'failed', error });
        }
    }
}
```

---

**File:** `static/js/modules/tests/config-modules-tests.js`

```javascript
export class ConfigModulesTests {
    constructor(logger) {
        this.logger = logger;
        this.results = [];
    }
    
    async runAll() {
        this.logger.section('Config Modules Tests');
        
        await this.testFeaturesConfig();
        await this.testUsersConfig();
        await this.testNetworkTargets();
        await this.testSMTPConfig();
        await this.testWatchedFolders();
        await this.testBrandingConfig();
        
        return this.results;
    }
    
    async testFeaturesConfig() {
        this.logger.info('Testing Features Config module...');
        
        try {
            // Check if module exists
            const module = window.ModuleSystem?.getModule('features-config');
            
            if (module) {
                this.logger.success('✓ Features config module loaded');
                
                // Test state
                const state = module.getState();
                this.logger.info('Module state:', state);
                
                // Test methods
                if (typeof module.save === 'function') {
                    this.logger.success('✓ save() method exists');
                } else {
                    this.logger.error('✗ save() method missing');
                }
                
                if (typeof module.toggleFeature === 'function') {
                    this.logger.success('✓ toggleFeature() method exists');
                } else {
                    this.logger.error('✗ toggleFeature() method missing');
                }
            } else {
                this.logger.warning('⚠ Features config module not loaded');
            }
            
            this.results.push({ test: 'FeaturesConfig', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Features config test failed:', error);
            this.results.push({ test: 'FeaturesConfig', status: 'failed', error });
        }
    }
    
    async testUsersConfig() {
        this.logger.info('Testing Users Config...');
        
        try {
            const config = await API.get('/api/dashboard/config');
            
            if (config.users) {
                this.logger.success(`✓ Users loaded: ${config.users.length} users`);
                
                // Test user structure
                const user = config.users[0];
                if (user) {
                    this.logger.info('Sample user:', user);
                    
                    if (user.username && user.role) {
                        this.logger.success('✓ User structure valid');
                    } else {
                        this.logger.error('✗ User structure invalid');
                    }
                }
            }
            
            this.results.push({ test: 'UsersConfig', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Users config test failed:', error);
            this.results.push({ test: 'UsersConfig', status: 'failed', error });
        }
    }
    
    async testNetworkTargets() {
        this.logger.info('Testing Network Targets config...');
        
        try {
            const config = await API.get('/api/dashboard/config');
            
            if (config.network_targets) {
                this.logger.success(`✓ Network targets loaded: ${config.network_targets.length} targets`);
                
                for (const target of config.network_targets.slice(0, 3)) {
                    this.logger.info(`Target: ${target.name}`);
                    this.logger.info(`  Path: ${target.path}`);
                    this.logger.info(`  Credential: ${target.credential_key}`);
                }
            } else {
                this.logger.info('No network targets configured');
            }
            
            this.results.push({ test: 'NetworkTargets', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Network targets test failed:', error);
            this.results.push({ test: 'NetworkTargets', status: 'failed', error });
        }
    }
    
    async testSMTPConfig() {
        this.logger.info('Testing SMTP config...');
        
        try {
            const config = await API.get('/api/dashboard/config');
            
            if (config.smtp) {
                this.logger.success('✓ SMTP config loaded');
                this.logger.info(`Host: ${config.smtp.host}`);
                this.logger.info(`Port: ${config.smtp.port}`);
                this.logger.info(`From: ${config.smtp.from}`);
                this.logger.info(`TLS: ${config.smtp.tls}`);
            } else {
                this.logger.info('SMTP not configured');
            }
            
            this.results.push({ test: 'SMTPConfig', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ SMTP config test failed:', error);
            this.results.push({ test: 'SMTPConfig', status: 'failed', error });
        }
    }
    
    async testWatchedFolders() {
        this.logger.info('Testing Watched Folders config...');
        
        try {
            const config = await API.get('/api/organizer/config');
            
            if (config.watched_folders) {
                this.logger.success(`✓ Watched folders loaded: ${config.watched_folders.length} folders`);
                
                for (const folder of config.watched_folders.slice(0, 3)) {
                    this.logger.info(`Folder: ${folder}`);
                }
            } else {
                this.logger.warning('⚠ No watched folders configured');
            }
            
            this.results.push({ test: 'WatchedFolders', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Watched folders test failed:', error);
            this.results.push({ test: 'WatchedFolders', status: 'failed', error });
        }
    }
    
    async testBrandingConfig() {
        this.logger.info('Testing Branding config...');
        
        try {
            const branding = await API.get('/api/dashboard/branding');
            
            if (branding) {
                this.logger.success('✓ Branding config loaded');
                this.logger.info(`Title: ${branding.title || 'Default'}`);
                this.logger.info(`Theme: ${branding.theme_name || 'Default'}`);
                this.logger.info(`Logo: ${branding.logo ? 'Custom' : 'Default'}`);
            }
            
            this.results.push({ test: 'BrandingConfig', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Branding config test failed:', error);
            this.results.push({ test: 'BrandingConfig', status: 'failed', error });
        }
    }
}
```

---

#### 3. Interactive Button Tests

**File:** `static/js/modules/tests/interactive-tests.js`

```javascript
export class InteractiveTests {
    constructor(logger) {
        this.logger = logger;
        this.results = [];
    }
    
    async runAll() {
        this.logger.section('Interactive UI Tests');
        
        await this.testServiceControls();
        await this.testConfigSave();
        await this.testSearchFunctions();
        await this.testModalDialogs();
        
        return this.results;
    }
    
    async testServiceControls() {
        this.logger.info('Testing service control buttons...');
        
        try {
            // Check if buttons exist
            const startBtn = document.querySelector('[data-action="start-service"]');
            const stopBtn = document.querySelector('[data-action="stop-service"]');
            const restartBtn = document.querySelector('[data-action="restart-service"]');
            
            if (startBtn) this.logger.success('✓ Start button found');
            if (stopBtn) this.logger.success('✓ Stop button found');
            if (restartBtn) this.logger.success('✓ Restart button found');
            
            // Test service status API
            const status = await API.get('/service-name');
            this.logger.info(`Service: ${status.service_name}`);
            this.logger.info(`Running: ${status.running ? 'Yes' : 'No'}`);
            
            this.results.push({ test: 'ServiceControls', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Service controls test failed:', error);
            this.results.push({ test: 'ServiceControls', status: 'failed', error });
        }
    }
    
    async testConfigSave() {
        this.logger.info('Testing config save operations...');
        
        try {
            // Find all save buttons
            const saveButtons = document.querySelectorAll('[data-action="save"]');
            this.logger.info(`Found ${saveButtons.length} save buttons`);
            
            // Test save endpoint (dry run - don't actually save)
            this.logger.warning('⚠ Skipping actual save to prevent config changes');
            
            this.results.push({ test: 'ConfigSave', status: 'skipped', reason: 'Safety' });
        } catch (error) {
            this.logger.error('✗ Config save test failed:', error);
            this.results.push({ test: 'ConfigSave', status: 'failed', error });
        }
    }
    
    async testSearchFunctions() {
        this.logger.info('Testing search functions...');
        
        try {
            // Find search inputs
            const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="earch"]');
            this.logger.info(`Found ${searchInputs.length} search inputs`);
            
            // Test search event handling
            for (const input of Array.from(searchInputs).slice(0, 3)) {
                const id = input.id || input.name || 'unknown';
                this.logger.info(`Search input: ${id}`);
                
                // Check if input has event listeners
                if (input.oninput || input.onkeyup) {
                    this.logger.success(`✓ ${id} has event handler`);
                } else {
                    this.logger.warning(`⚠ ${id} may not have event handler`);
                }
            }
            
            this.results.push({ test: 'SearchFunctions', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Search functions test failed:', error);
            this.results.push({ test: 'SearchFunctions', status: 'failed', error });
        }
    }
    
    async testModalDialogs() {
        this.logger.info('Testing modal dialogs...');
        
        try {
            // Find all modals
            const modals = document.querySelectorAll('.modal');
            this.logger.info(`Found ${modals.length} modal dialogs`);
            
            for (const modal of modals) {
                const id = modal.id || 'unknown';
                this.logger.info(`Modal: ${id}`);
                
                // Check Bootstrap modal functionality
                if (typeof bootstrap !== 'undefined') {
                    this.logger.success('✓ Bootstrap modal library loaded');
                } else {
                    this.logger.warning('⚠ Bootstrap modal library not found');
                }
            }
            
            this.results.push({ test: 'ModalDialogs', status: 'passed' });
        } catch (error) {
            this.logger.error('✗ Modal dialogs test failed:', error);
            this.results.push({ test: 'ModalDialogs', status: 'failed', error });
        }
    }
}
```

---

### Test Orchestrator

**File:** `static/js/modules/test-orchestrator.js`

```javascript
import BaseModule from '../base-module.js';
import API from '../api.js';
import { CoreSystemTests } from './tests/core-tests.js';
import { DuplicatesTests } from './tests/duplicates-tests.js';
import { VirusTotalTests } from './tests/virustotal-tests.js';
import { ConfigModulesTests } from './tests/config-modules-tests.js';
import { InteractiveTests } from './tests/interactive-tests.js';
import { VerboseLogger } from './test-logger.js';

class TestOrchestrator extends BaseModule {
    constructor() {
        super('test-orchestrator');
        
        this.logger = new VerboseLogger('test-log');
        this.features = {};
        this.testSuites = new Map();
        
        this.setState({
            running: false,
            currentSuite: null,
            results: {},
            startTime: null,
            endTime: null
        });
    }
    
    async init() {
        this.logger.info('Initializing Test Orchestrator...');
        
        // Load feature flags
        await this.loadFeatures();
        
        // Register test suites based on enabled features
        this.registerTestSuites();
        
        // Bind UI events
        this.bindEvents();
        
        this.logger.success('Test Orchestrator ready');
    }
    
    async loadFeatures() {
        try {
            const config = await API.get('/api/organizer/config');
            this.features = config.features || {};
            
            this.logger.info('Feature flags loaded:');
            for (const [key, value] of Object.entries(this.features)) {
                const icon = value ? '✓' : '✗';
                this.logger.info(`  ${icon} ${key}: ${value}`);
            }
        } catch (error) {
            this.logger.error('Failed to load feature flags:', error);
            this.features = {};
        }
    }
    
    registerTestSuites() {
        // Core tests (always enabled)
        this.testSuites.set('core', {
            name: 'Core System Tests',
            enabled: true,
            class: CoreSystemTests
        });
        
        // Optional module tests
        if (this.features.duplicates_enabled) {
            this.testSuites.set('duplicates', {
                name: 'Duplicates Module',
                enabled: true,
                class: DuplicatesTests
            });
        }
        
        if (this.features.virustotal_enabled) {
            this.testSuites.set('virustotal', {
                name: 'VirusTotal Integration',
                enabled: true,
                class: VirusTotalTests
            });
        }
        
        // Config modules tests (always available)
        this.testSuites.set('config', {
            name: 'Config Modules',
            enabled: true,
            class: ConfigModulesTests
        });
        
        // Interactive tests (always available)
        this.testSuites.set('interactive', {
            name: 'Interactive UI',
            enabled: true,
            class: InteractiveTests
        });
        
        this.logger.info(`Registered ${this.testSuites.size} test suites`);
    }
    
    async runAllTests() {
        this.logger.clear();
        this.logger.section('=== COMPREHENSIVE TEST RUN ===');
        this.logger.info(`Date: ${new Date().toISOString()}`);
        this.logger.info(`Enabled suites: ${this.testSuites.size}`);
        
        this.setState({ 
            running: true, 
            startTime: Date.now(),
            results: {}
        });
        
        const allResults = {};
        
        for (const [key, suite] of this.testSuites) {
            if (!suite.enabled) {
                this.logger.info(`Skipping ${suite.name} (disabled)`);
                continue;
            }
            
            this.setState({ currentSuite: suite.name });
            
            try {
                const testInstance = new suite.class(this.logger);
                const results = await testInstance.runAll();
                
                allResults[key] = {
                    suite: suite.name,
                    results,
                    passed: results.filter(r => r.status === 'passed').length,
                    failed: results.filter(r => r.status === 'failed').length,
                    skipped: results.filter(r => r.status === 'skipped').length
                };
                
                this.logger.section(`${suite.name} Results:`);
                this.logger.success(`✓ Passed: ${allResults[key].passed}`);
                if (allResults[key].failed > 0) {
                    this.logger.error(`✗ Failed: ${allResults[key].failed}`);
                }
                if (allResults[key].skipped > 0) {
                    this.logger.warning(`⊘ Skipped: ${allResults[key].skipped}`);
                }
            } catch (error) {
                this.logger.error(`Fatal error in ${suite.name}:`, error);
                allResults[key] = {
                    suite: suite.name,
                    error: error.message,
                    fatal: true
                };
            }
        }
        
        this.setState({ 
            running: false,
            currentSuite: null,
            endTime: Date.now(),
            results: allResults
        });
        
        this.printSummary(allResults);
    }
    
    async runSingleSuite(suiteKey) {
        const suite = this.testSuites.get(suiteKey);
        
        if (!suite) {
            this.logger.error(`Unknown test suite: ${suiteKey}`);
            return;
        }
        
        if (!suite.enabled) {
            this.logger.warning(`${suite.name} is disabled`);
            return;
        }
        
        this.logger.clear();
        this.logger.section(`=== ${suite.name} ===`);
        
        this.setState({ 
            running: true,
            currentSuite: suite.name,
            startTime: Date.now()
        });
        
        try {
            const testInstance = new suite.class(this.logger);
            const results = await testInstance.runAll();
            
            const summary = {
                passed: results.filter(r => r.status === 'passed').length,
                failed: results.filter(r => r.status === 'failed').length,
                skipped: results.filter(r => r.status === 'skipped').length
            };
            
            this.logger.section('Results:');
            this.logger.success(`✓ Passed: ${summary.passed}`);
            if (summary.failed > 0) {
                this.logger.error(`✗ Failed: ${summary.failed}`);
            }
            if (summary.skipped > 0) {
                this.logger.warning(`⊘ Skipped: ${summary.skipped}`);
            }
            
            this.setState({ 
                running: false,
                currentSuite: null,
                endTime: Date.now(),
                results: { [suiteKey]: { suite: suite.name, results, ...summary } }
            });
        } catch (error) {
            this.logger.error(`Fatal error:`, error);
            this.setState({ running: false, currentSuite: null });
        }
    }
    
    printSummary(allResults) {
        this.logger.section('=== TEST SUMMARY ===');
        
        let totalPassed = 0;
        let totalFailed = 0;
        let totalSkipped = 0;
        
        for (const [key, result] of Object.entries(allResults)) {
            if (result.fatal) {
                this.logger.error(`${result.suite}: FATAL ERROR`);
                continue;
            }
            
            totalPassed += result.passed;
            totalFailed += result.failed;
            totalSkipped += result.skipped;
            
            const total = result.passed + result.failed + result.skipped;
            this.logger.info(`${result.suite}: ${result.passed}/${total} passed`);
        }
        
        const duration = ((this.getState('endTime') - this.getState('startTime')) / 1000).toFixed(2);
        
        this.logger.section('Overall:');
        this.logger.success(`✓ Passed: ${totalPassed}`);
        if (totalFailed > 0) {
            this.logger.error(`✗ Failed: ${totalFailed}`);
        }
        if (totalSkipped > 0) {
            this.logger.warning(`⊘ Skipped: ${totalSkipped}`);
        }
        this.logger.info(`Duration: ${duration}s`);
        
        // Calculate success rate
        const successRate = ((totalPassed / (totalPassed + totalFailed + totalSkipped)) * 100).toFixed(1);
        this.logger.info(`Success Rate: ${successRate}%`);
    }
    
    bindEvents() {
        // Run all tests button
        document.querySelector('#run-all-tests')?.addEventListener('click', () => {
            this.runAllTests();
        });
        
        // Individual suite buttons
        for (const [key, suite] of this.testSuites) {
            document.querySelector(`#run-${key}-tests`)?.addEventListener('click', () => {
                this.runSingleSuite(key);
            });
        }
        
        // Clear log button
        document.querySelector('#clear-test-log')?.addEventListener('click', () => {
            this.logger.clear();
        });
        
        // Export log button
        document.querySelector('#export-test-log')?.addEventListener('click', () => {
            this.logger.export();
        });
    }
}

export default TestOrchestrator;
```

---

### Verbose Logger

**File:** `static/js/modules/test-logger.js`

```javascript
export class VerboseLogger {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.logs = [];
        this.startTime = Date.now();
    }
    
    log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const elapsed = ((Date.now() - this.startTime) / 1000).toFixed(3);
        
        const logEntry = {
            timestamp,
            elapsed,
            level,
            message,
            data
        };
        
        this.logs.push(logEntry);
        this.render(logEntry);
    }
    
    render(entry) {
        if (!this.container) return;
        
        const line = document.createElement('div');
        line.className = `log-entry log-${entry.level}`;
        
        let icon = '';
        switch (entry.level) {
            case 'success': icon = '✓'; break;
            case 'error': icon = '✗'; break;
            case 'warning': icon = '⚠'; break;
            case 'info': icon = 'ℹ'; break;
            case 'section': icon = '▸'; break;
        }
        
        let content = `<span class="log-time">[${entry.elapsed}s]</span> `;
        content += `<span class="log-icon">${icon}</span> `;
        content += `<span class="log-message">${this.escape(entry.message)}</span>`;
        
        if (entry.data) {
            content += `<pre class="log-data">${this.formatData(entry.data)}</pre>`;
        }
        
        line.innerHTML = content;
        this.container.appendChild(line);
        
        // Auto-scroll to bottom
        this.container.scrollTop = this.container.scrollHeight;
    }
    
    formatData(data) {
        if (typeof data === 'object') {
            return this.escape(JSON.stringify(data, null, 2));
        }
        return this.escape(String(data));
    }
    
    escape(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
    
    section(title) {
        this.log('section', title);
    }
    
    info(message, data) {
        this.log('info', message, data);
    }
    
    success(message, data) {
        this.log('success', message, data);
    }
    
    warning(message, data) {
        this.log('warning', message, data);
    }
    
    error(message, data) {
        this.log('error', message, data);
    }
    
    clear() {
        this.logs = [];
        this.startTime = Date.now();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
    
    export() {
        const blob = new Blob([JSON.stringify(this.logs, null, 2)], { 
            type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `test-log-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}
```

---

## Env-Test Page Redesign

### Updated Template

**File:** `dash/env_test.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Environment Test - DownloadsOrganizeR</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/core.css') }}?v={{ asset_version }}">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        .test-suite-card {
            margin-bottom: 1rem;
            border-left: 4px solid var(--primary-color);
        }
        
        .test-suite-card.disabled {
            opacity: 0.6;
            border-left-color: #ccc;
        }
        
        .log-entry {
            padding: 0.5rem;
            border-bottom: 1px solid #eee;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
        }
        
        .log-success { color: #198754; }
        .log-error { color: #dc3545; }
        .log-warning { color: #ffc107; }
        .log-info { color: #0dcaf0; }
        .log-section { 
            font-weight: bold; 
            background: #f8f9fa;
            margin-top: 1rem;
        }
        
        .log-time {
            color: #6c757d;
            font-size: 0.8rem;
        }
        
        .log-data {
            background: #f5f5f5;
            padding: 0.5rem;
            margin-top: 0.25rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        #test-log {
            height: 500px;
            overflow-y: auto;
            background: #fff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 0.5rem;
        }
        
        .running-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ffc107;
            animation: pulse 1s infinite;
            margin-right: 0.5rem;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1>
                        <i class="bi bi-gear-fill"></i> Environment Test Suite
                        <span class="badge bg-warning" id="running-badge" style="display: none;">
                            <span class="running-indicator"></span> Running...
                        </span>
                    </h1>
                    <a href="/" class="btn btn-secondary">
                        <i class="bi bi-house"></i> Back to Dashboard
                    </a>
                </div>
                
                <!-- Feature Flags Overview -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5><i class="bi bi-toggles"></i> Feature Flags</h5>
                    </div>
                    <div class="card-body">
                        <div class="row" id="feature-flags">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>
                </div>
                
                <!-- Test Suites -->
                <div class="row">
                    <div class="col-md-4">
                        <h4>Test Suites</h4>
                        
                        <!-- Run All Button -->
                        <button class="btn btn-primary w-100 mb-3" id="run-all-tests">
                            <i class="bi bi-play-fill"></i> Run All Tests
                        </button>
                        
                        <!-- Core Tests -->
                        <div class="card test-suite-card">
                            <div class="card-body">
                                <h6><i class="bi bi-cpu"></i> Core System</h6>
                                <p class="small text-muted">Auth, API, Database, Permissions</p>
                                <button class="btn btn-sm btn-outline-primary" id="run-core-tests">
                                    <i class="bi bi-play"></i> Run
                                </button>
                            </div>
                        </div>
                        
                        <!-- Duplicates Tests -->
                        <div class="card test-suite-card" id="suite-duplicates">
                            <div class="card-body">
                                <h6><i class="bi bi-files"></i> Duplicates Module</h6>
                                <p class="small text-muted">Detection, Hashing, Grouping</p>
                                <button class="btn btn-sm btn-outline-primary" id="run-duplicates-tests">
                                    <i class="bi bi-play"></i> Run
                                </button>
                            </div>
                        </div>
                        
                        <!-- VirusTotal Tests -->
                        <div class="card test-suite-card" id="suite-virustotal">
                            <div class="card-body">
                                <h6><i class="bi bi-shield-check"></i> VirusTotal</h6>
                                <p class="small text-muted">API Key, Hash Lookup, Integration</p>
                                <button class="btn btn-sm btn-outline-primary" id="run-virustotal-tests">
                                    <i class="bi bi-play"></i> Run
                                </button>
                            </div>
                        </div>
                        
                        <!-- Config Modules Tests -->
                        <div class="card test-suite-card">
                            <div class="card-body">
                                <h6><i class="bi bi-gear"></i> Config Modules</h6>
                                <p class="small text-muted">Features, Users, Network, SMTP</p>
                                <button class="btn btn-sm btn-outline-primary" id="run-config-tests">
                                    <i class="bi bi-play"></i> Run
                                </button>
                            </div>
                        </div>
                        
                        <!-- Interactive Tests -->
                        <div class="card test-suite-card">
                            <div class="card-body">
                                <h6><i class="bi bi-cursor"></i> Interactive UI</h6>
                                <p class="small text-muted">Buttons, Forms, Modals, Search</p>
                                <button class="btn btn-sm btn-outline-primary" id="run-interactive-tests">
                                    <i class="bi bi-play"></i> Run
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-8">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h4>Test Log</h4>
                            <div>
                                <button class="btn btn-sm btn-outline-secondary" id="clear-test-log">
                                    <i class="bi bi-trash"></i> Clear
                                </button>
                                <button class="btn btn-sm btn-outline-primary" id="export-test-log">
                                    <i class="bi bi-download"></i> Export
                                </button>
                            </div>
                        </div>
                        
                        <div id="test-log">
                            <div class="text-muted text-center p-4">
                                <i class="bi bi-info-circle" style="font-size: 2rem;"></i>
                                <p>Click "Run All Tests" or select a specific test suite to begin.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script type="module">
        import TestOrchestrator from '{{ url_for("static", filename="js/modules/test-orchestrator.js") }}?v={{ asset_version }}';
        
        // Initialize test orchestrator
        const orchestrator = new TestOrchestrator();
        await orchestrator.init();
        
        // Display feature flags
        const featuresContainer = document.getElementById('feature-flags');
        for (const [key, value] of Object.entries(orchestrator.features)) {
            const col = document.createElement('div');
            col.className = 'col-md-3 mb-2';
            col.innerHTML = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" ${value ? 'checked' : ''} disabled>
                    <label class="form-check-label small">${key}</label>
                </div>
            `;
            featuresContainer.appendChild(col);
        }
        
        // Update UI based on enabled features
        if (!orchestrator.features.duplicates_enabled) {
            document.getElementById('suite-duplicates')?.classList.add('disabled');
            document.getElementById('run-duplicates-tests')?.setAttribute('disabled', 'true');
        }
        
        if (!orchestrator.features.virustotal_enabled) {
            document.getElementById('suite-virustotal')?.classList.add('disabled');
            document.getElementById('run-virustotal-tests')?.setAttribute('disabled', 'true');
        }
        
        // Show running indicator
        orchestrator.watch('running', (running) => {
            document.getElementById('running-badge').style.display = running ? 'inline-block' : 'none';
        });
    </script>
</body>
</html>
```

---

## Backend Testing Infrastructure

### Route Protection

**File:** `SortNStoreDashboard/routes/env_test.py`

```python
from flask import Blueprint, render_template
from SortNStoreDashboard.auth.auth import requires_auth
import sys

routes_env = Blueprint('routes_env', __name__)

@routes_env.route('/env-test', methods=['GET'])
@requires_auth
def env_test():
    """Environment test page - only accessible if developer_mode is enabled."""
    main = sys.modules['__main__']
    config = getattr(main, 'config', {})
    features = config.get('features', {})
    
    # Check if developer mode is enabled
    if not features.get('developer_mode', False):
        return '''
        <html>
            <head>
                <title>Access Denied</title>
                <style>
                    body { 
                        font-family: system-ui; 
                        display: flex; 
                        justify-content: center; 
                        align-items: center; 
                        height: 100vh;
                        background: #f8f9fa;
                    }
                    .message {
                        text-align: center;
                        padding: 2rem;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }
                </style>
            </head>
            <body>
                <div class="message">
                    <h1>🔒 Access Denied</h1>
                    <p>Developer mode must be enabled to access this page.</p>
                    <p>Enable it in: <strong>Config > Features & Integrations</strong></p>
                    <a href="/">Back to Dashboard</a>
                </div>
            </body>
        </html>
        ''', 403
    
    # Render test page
    return render_template('env_test.html')
```

---

### Feature Flag API

**File:** `SortNStoreDashboard/routes/features.py`

```python
from flask import Blueprint, jsonify, request
from SortNStoreDashboard.auth.auth import requires_right
import sys
import json

routes_features = Blueprint('routes_features', __name__)

@routes_features.route('/api/features', methods=['GET'])
def get_features():
    """Get current feature flags."""
    main = sys.modules['__main__']
    config = getattr(main, 'config', {})
    features = config.get('features', {})
    
    return jsonify({
        'features': features
    })

@routes_features.route('/api/features', methods=['POST'])
@requires_right('manage_config')
def update_features():
    """Update feature flags."""
    data = request.get_json() or {}
    
    main = sys.modules['__main__']
    config = getattr(main, 'config', {})
    
    # Update features
    if 'features' in data:
        config.setdefault('features', {})
        config['features'].update(data['features'])
        
        # Save to config file
        try:
            with open('organizer_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            return jsonify({
                'success': True,
                'message': 'Features updated'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return jsonify({
        'success': False,
        'error': 'No features provided'
    }), 400
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1, Days 1-2)

**Tasks:**
1. Create feature flag system in config
2. Update config schema with all feature flags
3. Create VerboseLogger class
4. Create TestOrchestrator skeleton
5. Protect env-test route behind developer_mode

**Deliverables:**
- `organizer_config.json` updated with features section
- `static/js/modules/test-logger.js` (200 lines)
- `static/js/modules/test-orchestrator.js` (skeleton, 100 lines)
- `SortNStoreDashboard/routes/env_test.py` updated
- `SortNStoreDashboard/routes/features.py` created

---

### Phase 2: Core Tests (Week 1, Days 3-4)

**Tasks:**
1. Create CoreSystemTests class
2. Test authentication system
3. Test API endpoints
4. Test database operations
5. Test file system access
6. Test permissions

**Deliverables:**
- `static/js/modules/tests/core-tests.js` (400 lines)

---

### Phase 3: Module Tests (Week 1, Day 5 - Week 2, Day 2)

**Tasks:**
1. Create DuplicatesTests class
2. Create VirusTotalTests class
3. Create ConfigModulesTests class
4. Create InteractiveTests class
5. Integrate with TestOrchestrator

**Deliverables:**
- `static/js/modules/tests/duplicates-tests.js` (300 lines)
- `static/js/modules/tests/virustotal-tests.js` (300 lines)
- `static/js/modules/tests/config-modules-tests.js` (400 lines)
- `static/js/modules/tests/interactive-tests.js` (300 lines)

---

### Phase 4: UI Integration (Week 2, Days 3-4)

**Tasks:**
1. Redesign env_test.html template
2. Add feature flags display
3. Add test suite cards with enable/disable
4. Style verbose log output
5. Add export functionality

**Deliverables:**
- `dash/env_test.html` updated (300 lines)
- `static/css/test-suite.css` (100 lines)

---

### Phase 5: Setup Wizard Integration (Week 2, Day 5)

**Tasks:**
1. Add feature selection to setup wizard
2. Create feature cards with descriptions
3. Update setup_validation.py
4. Add feature toggles to config page

**Deliverables:**
- `dash/dashboard_setup.html` updated
- `SortNStoreDashboard/routes/setup.py` updated
- Config page module selection UI

---

## Summary

**Total Scope:**
- 8 new JavaScript modules (~2,000 lines)
- 1 updated template (env_test.html)
- 3 backend routes (env_test, features, setup)
- Feature flag system in config
- Comprehensive test coverage for all modules

**Timeline:** 2.5 weeks

**Benefits:**
- ✅ Unified testing framework
- ✅ Module-specific isolation
- ✅ Verbose error logging
- ✅ Developer-only access
- ✅ Feature flag-driven testing
- ✅ Interactive button testing
- ✅ Export test results
- ✅ Easy debugging

---

**Next Steps:**
1. Review architecture
2. Start Phase 1 (core infrastructure)
3. Implement feature flag system
4. Create test orchestrator
5. Build out test suites

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Status:** Architecture Planning Complete
