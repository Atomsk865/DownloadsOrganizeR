# Testing Framework Quick Start Guide

**Version:** 1.0  
**Date:** December 5, 2025

---

## Overview

This guide provides step-by-step instructions for implementing and using the comprehensive testing framework.

---

## Table of Contents

1. [Setup Instructions](#setup-instructions)
2. [Feature Flag Configuration](#feature-flag-configuration)
3. [Creating Test Suites](#creating-test-suites)
4. [Using the Test Page](#using-the-test-page)
5. [Troubleshooting](#troubleshooting)

---

## Setup Instructions

### Step 1: Enable Developer Mode

**Via Config Page:**
1. Navigate to `/config`
2. Go to "Features & Integrations" section
3. Enable "Developer Mode" toggle
4. Click "Save Features"

**Via Config File:**
```json
{
  "features": {
    "developer_mode": true
  }
}
```

### Step 2: Access Test Page

1. Navigate to `/env-test`
2. If developer mode is disabled, you'll see access denied message
3. Once enabled, you'll see the test suite dashboard

---

## Feature Flag Configuration

### Complete Feature Flags Schema

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

### Feature Descriptions

| Feature | Description | Default |
|---------|-------------|---------|
| `duplicates_enabled` | Duplicate file detection | `true` |
| `reports_enabled` | Analytics & reports | `true` |
| `virustotal_enabled` | VirusTotal integration | `false` |
| `recent_files_enabled` | Recent files tracking | `true` |
| `branding_enabled` | Custom themes/branding | `true` |
| `notifications_enabled` | Notification center | `true` |
| `watched_folders_enabled` | Multi-folder watching | `true` |
| `network_targets_enabled` | NAS/Network storage | `false` |
| `smtp_enabled` | Email alerts | `false` |
| `developer_mode` | Developer tools | `false` |

---

## Creating Test Suites

### Test Suite Template

```javascript
export class MyModuleTests {
    constructor(logger) {
        this.logger = logger;
        this.results = [];
    }
    
    async runAll() {
        this.logger.section('My Module Tests');
        
        await this.testOne();
        await this.testTwo();
        await this.testThree();
        
        return this.results;
    }
    
    async testOne() {
        this.logger.info('Testing feature one...');
        
        try {
            // Your test logic here
            const result = await API.get('/api/my-endpoint');
            
            if (result.success) {
                this.logger.success('✓ Feature one working');
                this.results.push({ test: 'FeatureOne', status: 'passed' });
            } else {
                this.logger.error('✗ Feature one failed');
                this.results.push({ test: 'FeatureOne', status: 'failed' });
            }
        } catch (error) {
            this.logger.error('✗ Test error:', error);
            this.results.push({ 
                test: 'FeatureOne', 
                status: 'failed', 
                error: error.message 
            });
        }
    }
    
    async testTwo() {
        this.logger.info('Testing feature two...');
        // Similar structure...
    }
    
    async testThree() {
        this.logger.info('Testing feature three...');
        // Similar structure...
    }
}
```

### Registering Test Suite in Orchestrator

**File:** `static/js/modules/test-orchestrator.js`

```javascript
registerTestSuites() {
    // Existing suites...
    
    // Add your new suite
    if (this.features.my_feature_enabled) {
        this.testSuites.set('mymodule', {
            name: 'My Module Tests',
            enabled: true,
            class: MyModuleTests
        });
    }
}
```

### Adding UI Button

**File:** `dash/env_test.html`

```html
<!-- Add to test suites column -->
<div class="card test-suite-card" id="suite-mymodule">
    <div class="card-body">
        <h6><i class="bi bi-star"></i> My Module</h6>
        <p class="small text-muted">Feature One, Two, Three</p>
        <button class="btn btn-sm btn-outline-primary" id="run-mymodule-tests">
            <i class="bi bi-play"></i> Run
        </button>
    </div>
</div>
```

---

## Using the Test Page

### Running All Tests

1. Click "Run All Tests" button
2. Watch as each test suite executes
3. Review verbose log output
4. Check summary at the end

**Example Output:**
```
=== COMPREHENSIVE TEST RUN ===
Date: 2025-12-05T10:30:00.000Z
Enabled suites: 5

▸ Core System Tests
ℹ Testing authentication system...
✓ Session valid
✓ CSRF token present
✓ User rights loaded: 3 roles
ℹ Testing API endpoints...
✓ /api/organizer/config responding
✓ /api/dashboard/config responding
...

=== TEST SUMMARY ===
Core System Tests: 5/5 passed
Duplicates Module: 4/5 passed
Config Modules: 6/6 passed
Overall:
✓ Passed: 15
✗ Failed: 1
Duration: 3.45s
Success Rate: 93.8%
```

### Running Individual Suites

1. Click specific suite's "Run" button
2. Only that suite will execute
3. Faster for targeted testing

### Interpreting Results

**Success (✓):**
- Green checkmark
- Test passed all assertions
- Feature working as expected

**Failure (✗):**
- Red X
- Test failed assertion
- Error details logged

**Warning (⚠):**
- Yellow triangle
- Test passed but with warnings
- May need attention

**Skipped (⊘):**
- Gray circle with slash
- Test not run (disabled feature, safety skip)
- Reason logged

### Exporting Logs

1. Click "Export" button
2. Downloads JSON file with all log entries
3. Includes timestamps, levels, messages, data

**Log Format:**
```json
[
  {
    "timestamp": "2025-12-05T10:30:00.000Z",
    "elapsed": "0.123",
    "level": "success",
    "message": "Session valid",
    "data": null
  },
  {
    "timestamp": "2025-12-05T10:30:00.500Z",
    "elapsed": "0.623",
    "level": "error",
    "message": "API endpoint failed",
    "data": {
      "endpoint": "/api/test",
      "error": "404 Not Found"
    }
  }
]
```

---

## Troubleshooting

### "Access Denied" Error

**Problem:** Cannot access `/env-test` page

**Solution:**
1. Check developer mode is enabled
2. Verify config file has `"developer_mode": true`
3. Restart dashboard if needed
4. Check user has authentication

### Test Suite Not Appearing

**Problem:** Expected test suite not showing in UI

**Solution:**
1. Check feature flag is enabled (e.g., `duplicates_enabled`)
2. Verify suite registered in `test-orchestrator.js`
3. Check browser console for import errors
4. Refresh page (Ctrl+F5)

### Tests Timing Out

**Problem:** Tests never complete or hang indefinitely

**Solution:**
1. Check API endpoints are responding
2. Verify network connectivity
3. Check browser network tab for failed requests
4. Increase timeout if needed (API utility default: 30s)

### Verbose Logs Not Showing

**Problem:** Test runs but no logs appear

**Solution:**
1. Check `test-log` div exists in HTML
2. Verify logger initialized correctly
3. Check browser console for JavaScript errors
4. Try refreshing page

### Feature Flag Not Saving

**Problem:** Changed feature flag but not persisted

**Solution:**
1. Check file permissions on `organizer_config.json`
2. Verify API endpoint `/api/update` working
3. Check backend logs for errors
4. Try manual edit of config file

### High Failure Rate

**Problem:** Many tests failing unexpectedly

**Solution:**
1. Check dashboard is fully started
2. Verify all services running
3. Check database/config files exist
4. Review individual test error messages
5. May need to update config for environment

---

## Best Practices

### When to Run Tests

- **Before deployment:** Run all tests
- **After config changes:** Run affected module tests
- **After code updates:** Run all tests
- **Weekly:** Run all tests as health check
- **After errors:** Run specific suite to diagnose

### Test Maintenance

1. Update tests when features change
2. Add new tests for new features
3. Remove tests for removed features
4. Keep test assertions up-to-date
5. Document test expectations

### Performance Tips

1. Run individual suites for faster feedback
2. Skip slow tests during development
3. Use mocking for external services
4. Cache test data when possible
5. Parallelize independent tests

### Security Considerations

1. **Never test destructive operations** (deletion, format, etc.)
2. Use test/dummy data, not production
3. Don't log sensitive data (passwords, tokens)
4. Limit test access to developers only
5. Export logs securely

---

## Quick Commands

### Enable Developer Mode (Backend)
```python
from SortNStoreDashboard.routes.features import update_features

# In your code
config['features']['developer_mode'] = True
```

### Check Feature Status (JavaScript)
```javascript
import API from '../api.js';

const config = await API.get('/api/organizer/config');
const isEnabled = config.features?.developer_mode;
```

### Add Custom Test Logger
```javascript
import { VerboseLogger } from '../test-logger.js';

const logger = new VerboseLogger('my-log-container');
logger.info('Starting test...');
logger.success('Test passed!');
logger.error('Test failed:', error);
```

### Register Custom Suite
```javascript
// In test-orchestrator.js
import { MyTests } from './tests/my-tests.js';

this.testSuites.set('my-tests', {
    name: 'My Custom Tests',
    enabled: this.features.my_feature_enabled,
    class: MyTests
});
```

---

## Integration with Setup Wizard

### Adding Feature Selection to Setup

**Step 1:** Update setup template with feature checkboxes

```html
<div class="card">
    <div class="card-header">
        <h5>Select Features</h5>
    </div>
    <div class="card-body">
        <div class="form-check">
            <input class="form-check-input" type="checkbox" 
                   id="duplicates_enabled" checked>
            <label class="form-check-label" for="duplicates_enabled">
                Duplicate Detection
            </label>
        </div>
        <!-- More checkboxes... -->
    </div>
</div>
```

**Step 2:** Save selections to config

```javascript
async function saveSetup() {
    const features = {
        duplicates_enabled: document.getElementById('duplicates_enabled').checked,
        reports_enabled: document.getElementById('reports_enabled').checked,
        // ... more features
    };
    
    await API.post('/api/update', { features });
}
```

---

## API Reference

### Get Features
```
GET /api/features
Response: { "features": { ... } }
```

### Update Features
```
POST /api/features
Body: { "features": { "developer_mode": true } }
Response: { "success": true }
```

### Run Single Test (Future)
```
POST /api/tests/run
Body: { "suite": "core" }
Response: { "results": [...] }
```

---

## Next Steps

1. ✅ Review architecture document
2. ⏳ Implement Phase 1 (core infrastructure)
3. ⏳ Create feature flag system
4. ⏳ Build test orchestrator
5. ⏳ Add test suites
6. ⏳ Update env-test page
7. ⏳ Integrate with setup wizard

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Status:** Ready for Implementation
