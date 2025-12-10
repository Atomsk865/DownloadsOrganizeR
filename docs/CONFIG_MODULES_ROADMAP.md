# Config Modules Implementation Roadmap

**Phased implementation plan for systematic rollout of all 9 config modules.**

---

## Overview

**Total Scope:** 9 modules + 3 utilities + coordinator + documentation  
**Estimated Effort:** 4 weeks (1 developer full-time)  
**Lines of Code:** ~4,500 lines  
**Current Status:** Phase 1 (10% complete - features-config done)

---

## Phase 1: Foundation ✅ (10% Complete)

**Timeline:** Week 1, Days 1-2  
**Status:** ✅ FEATURES MODULE COMPLETE

### Completed ✅

- [x] **Features & Integrations Config** (200 lines)
  - VirusTotal API key management
  - Feature toggles (duplicates, reports, developer mode)
  - Real-time validation
  - EventBus integration
  - Store state management

### Deliverables ✅

```
✅ static/js/modules/features-config.js       (200 lines)
✅ Pattern established for remaining modules
✅ BaseModule integration validated
✅ API integration tested
```

---

## Phase 2: Utilities Foundation 📝

**Timeline:** Week 1, Days 3-5  
**Priority:** HIGH (Required for Phase 3)  
**Estimated Effort:** 3 days

### To Do 📝

#### 1. Form Validator Utility (Day 3)

**File:** `static/js/utilities/form-validator.js`  
**Size:** ~200 lines  
**Dependencies:** None

**Functionality:**
- Validation rules engine (required, minLength, maxLength, pattern, type)
- Real-time validation (on input, on blur, on submit)
- Error message templating with i18n support
- Custom validators support
- Form state management (pristine, dirty, valid, invalid)

**API:**
```javascript
const validator = new FormValidator({
    username: {
        required: true,
        minLength: 3,
        maxLength: 32,
        pattern: /^[a-zA-Z0-9_]+$/,
        message: 'Username: 3-32 chars, alphanumeric + underscore'
    },
    email: {
        required: true,
        type: 'email'
    },
    password: {
        required: true,
        minLength: 8,
        custom: (value) => /[A-Z]/.test(value) && /[0-9]/.test(value),
        message: 'Password: 8+ chars, 1 uppercase, 1 number'
    }
});

// Validate data
const errors = validator.validate({
    username: 'john_doe',
    email: 'john@example.com',
    password: 'Pass123'
});

// errors: []  (valid)
// errors: [{ field: 'username', message: '...' }]  (invalid)
```

**Testing:**
- Unit tests for each validation rule
- Edge cases (empty, null, undefined)
- Custom validator tests
- Message templating tests

---

#### 2. Table Manager Utility (Day 4)

**File:** `static/js/utilities/table-manager.js`  
**Size:** ~300 lines  
**Dependencies:** DOM utility

**Functionality:**
- CRUD operations (Create, Read, Update, Delete)
- Sorting (ascending, descending, multi-column)
- Filtering (client-side search)
- Row selection (single, multi, all)
- Inline editing mode
- Pagination support
- Empty state handling
- Loading state overlay

**API:**
```javascript
const table = new TableManager('#users-table', {
    columns: [
        { 
            key: 'username', 
            label: 'Username', 
            sortable: true,
            searchable: true,
            render: (value, row) => `<strong>${value}</strong>`
        },
        { 
            key: 'role', 
            label: 'Role', 
            sortable: true 
        },
        { 
            key: 'actions', 
            label: 'Actions', 
            render: (value, row) => this.renderActions(row)
        }
    ],
    searchable: true,
    selectable: true,
    pagination: { pageSize: 10 },
    emptyMessage: 'No users found',
    onRowClick: this.onRowClick.bind(this),
    onRowSelect: this.onRowSelect.bind(this),
    onRowDelete: this.onRowDelete.bind(this)
});

// Set data
table.setData(users);

// Get selected rows
const selected = table.getSelected();

// Clear selection
table.clearSelection();

// Refresh table
table.refresh();
```

**Testing:**
- Sorting tests (string, number, date)
- Search/filter tests (case-insensitive, multi-word)
- Selection tests (single, multi, toggle)
- Pagination tests (page navigation, size change)
- Performance tests (1000 rows)

---

#### 3. Template Engine Utility (Day 5)

**File:** `static/js/utilities/template-engine.js`  
**Size:** ~150 lines  
**Dependencies:** None

**Functionality:**
- HTML template rendering from strings
- Data binding with mustache-like syntax `{{ variable }}`
- Conditional rendering `{{#if condition}}...{{/if}}`
- Loop rendering `{{#each items}}...{{/each}}`
- Escape HTML by default (XSS prevention)
- Raw HTML option `{{{ rawHtml }}}`

**API:**
```javascript
const template = new TemplateEngine();

// Simple template
const html = template.render('<p>Hello {{name}}</p>', { name: 'John' });
// Result: <p>Hello John</p>

// Conditional
const html = template.render(`
    {{#if isAdmin}}
        <button>Admin Panel</button>
    {{/if}}
`, { isAdmin: true });

// Loop
const html = template.render(`
    <ul>
    {{#each users}}
        <li>{{username}} - {{role}}</li>
    {{/each}}
    </ul>
`, { users: [{ username: 'john', role: 'admin' }] });
```

**Testing:**
- Variable interpolation tests
- Conditional rendering tests
- Loop rendering tests
- HTML escaping tests
- Edge cases (undefined, null, nested objects)

---

### Phase 2 Deliverables

```
📝 static/js/utilities/form-validator.js      (200 lines)
📝 static/js/utilities/table-manager.js       (300 lines)
📝 static/js/utilities/template-engine.js     (150 lines)
📝 tests/utilities/*.test.js                  (300 lines)
```

---

## Phase 3: High-Priority Modules 📝

**Timeline:** Week 2  
**Priority:** HIGH  
**Estimated Effort:** 5 days

### Module 1: Users & Roles Config (Days 1-2)

**File:** `static/js/modules/users-roles-config.js`  
**Size:** ~400 lines  
**Dependencies:** FormValidator, TableManager

**Tasks:**
1. ✅ Create module skeleton (30 min)
2. ✅ Implement user table (2 hours)
3. ✅ Add search/filter (1 hour)
4. ✅ Implement add/edit form (2 hours)
5. ✅ Add validation (1 hour)
6. ✅ Implement delete with confirmation (1 hour)
7. ✅ Add role selector (1 hour)
8. ✅ Implement password management (2 hours)
9. ✅ Add inline editing (2 hours)
10. ✅ Write tests (2 hours)

**API Endpoints:**
- GET `/api/dashboard/config` - Load users
- POST `/api/dashboard/users` - Create/update
- DELETE `/api/dashboard/users/<username>` - Delete

**State:**
```javascript
{
    users: [],
    roles: {},
    searchQuery: '',
    selectedUser: null,
    editMode: false,
    sortField: 'username',
    sortDirection: 'asc'
}
```

**Events:**
- `users:updated` - User list changed
- `user:created` - New user added
- `user:deleted` - User removed

---

### Module 2: Network Targets Config (Days 3-4)

**File:** `static/js/modules/network-targets-config.js`  
**Size:** ~450 lines  
**Dependencies:** FormValidator, TableManager

**Tasks:**
1. ✅ Create module skeleton (30 min)
2. ✅ Implement targets table (2 hours)
3. ✅ Add template system (2 hours)
4. ✅ Implement add/edit form (2 hours)
5. ✅ Add UNC path validation (1 hour)
6. ✅ Implement test connection (2 hours)
7. ✅ Add credential key autocomplete (1 hour)
8. ✅ Add connectivity status (1 hour)
9. ✅ Write backend endpoint `/api/test-nas` (2 hours)
10. ✅ Write tests (2 hours)

**Templates:**
- Synology NAS
- QNAP NAS
- Windows Share
- Generic SMB/CIFS

**New API Endpoint:**
```python
# SortNStoreDashboard/routes/test_nas.py
@routes_test_nas.route('/api/test-nas', methods=['POST'])
@requires_right('manage_config')
def test_nas_connection():
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')
    credential_key = data.get('credential_key')
    
    # Test connection logic
    try:
        # Check if path is accessible
        # Check read/write permissions
        # Measure latency
        
        return jsonify({
            'success': True,
            'message': 'Connection successful',
            'latency_ms': 45,
            'readable': True,
            'writable': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
```

---

### Module 3: SMTP & Credentials Config (Day 5)

**File:** `static/js/modules/smtp-credentials-config.js`  
**Size:** ~500 lines  
**Dependencies:** FormValidator, TableManager

**Tasks:**
1. ✅ Create module skeleton (30 min)
2. ✅ Implement SMTP template system (2 hours)
3. ✅ Implement SMTP form (2 hours)
4. ✅ Add email validation (1 hour)
5. ✅ Implement credentials vault table (2 hours)
6. ✅ Add credential CRUD operations (2 hours)
7. ✅ Implement test email function (2 hours)
8. ✅ Add base64 encode/decode (1 hour)
9. ✅ Write backend endpoint `/api/test-smtp` (2 hours)
10. ✅ Write tests (2 hours)

**Templates:**
- Gmail
- Outlook.com
- Office 365
- Yahoo Mail
- Generic SMTP

**New API Endpoint:**
```python
# SortNStoreDashboard/routes/test_smtp.py
@routes_test_smtp.route('/api/test-smtp', methods=['POST'])
@requires_right('manage_config')
def test_smtp():
    data = request.get_json()
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText(data.get('body', 'Test email'))
        msg['Subject'] = data.get('subject', 'Test Email')
        msg['From'] = data['from']
        msg['To'] = data['to']
        
        with smtplib.SMTP(data['host'], data['port']) as server:
            if data.get('tls', True):
                server.starttls()
            
            server.login(data['user'], data['pass'])
            server.send_message(msg)
        
        return jsonify({
            'success': True,
            'message': 'Email sent successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
```

---

### Phase 3 Deliverables

```
📝 static/js/modules/users-roles-config.js        (400 lines)
📝 static/js/modules/network-targets-config.js    (450 lines)
📝 static/js/modules/smtp-credentials-config.js   (500 lines)
📝 SortNStoreDashboard/routes/test_nas.py         (100 lines)
📝 SortNStoreDashboard/routes/test_smtp.py        (100 lines)
📝 tests/modules/*.test.js                        (600 lines)
```

---

## Phase 4: Medium-Priority Modules 📝

**Timeline:** Week 3  
**Priority:** MEDIUM  
**Estimated Effort:** 5 days

### Module 1: Watched Folders Config (Days 1-2)

**File:** `static/js/modules/watched-folders-config.js`  
**Size:** ~350 lines  
**Dependencies:** FormValidator

**Tasks:**
1. ✅ Create module skeleton (30 min)
2. ✅ Implement folder list UI (2 hours)
3. ✅ Add path validation (2 hours)
4. ✅ Implement add/delete operations (2 hours)
5. ✅ Add placeholder resolution preview (2 hours)
6. ✅ Implement test folder (2 hours)
7. ✅ Add audit log viewer (2 hours)
8. ✅ Write backend endpoint `/api/test-folder` (2 hours)
9. ✅ Write tests (2 hours)

**Path Formats:**
- UNC: `\\server\share\path`
- Windows: `C:\path` or `C:/path`
- Unix: `/path/to/folder`
- Placeholders: `%USERNAME%`, `%USER%`

---

### Module 2: Service Installation Config (Day 3)

**File:** `static/js/modules/service-install-config.js`  
**Size:** ~250 lines  
**Dependencies:** None

**Tasks:**
1. ✅ Create module skeleton (30 min)
2. ✅ Add platform detection (1 hour)
3. ✅ Implement install/reinstall/uninstall (2 hours)
4. ✅ Add configuration form (1 hour)
5. ✅ Implement progress tracking (2 hours)
6. ✅ Add service status display (1 hour)
7. ✅ Write tests (2 hours)

**Platform Detection:**
```javascript
const isWindows = /Windows/i.test(navigator.userAgent) || 
                  /Win32|Win64/i.test(navigator.platform);

if (!isWindows) {
    this.container.innerHTML = `
        <div class="alert alert-warning">
            Service installation is only available on Windows.
        </div>
    `;
    return;
}
```

---

### Module 3: Role Rights Config (Day 4)

**File:** `static/js/modules/role-rights-config.js`  
**Size:** ~200 lines  
**Dependencies:** TableManager

**Tasks:**
1. ✅ Create module skeleton (30 min)
2. ✅ Implement permission matrix (2 hours)
3. ✅ Add search/filter (1 hour)
4. ✅ Add expandable rows (1 hour)
5. ✅ Implement badge indicators (1 hour)
6. ✅ Add export functionality (1 hour)
7. ✅ Write tests (2 hours)

**UI:**
- Read-only display (no editing)
- Color-coded badges (green=allowed, gray=denied)
- Expandable details
- Search by role or right
- Export to CSV/PDF

---

### Module 4: Branding & Themes Config (Day 5)

**File:** `static/js/modules/branding-config.js`  
**Size:** ~650 lines  
**Dependencies:** TemplateEngine

**Tasks:**
1. ✅ Create module skeleton (30 min)
2. ✅ Implement preset themes (2 hours)
3. ✅ Add custom theme creator (3 hours)
4. ✅ Implement color pickers (1 hour)
5. ✅ Add auto-extract from logo (3 hours)
6. ✅ Implement CSS editor (2 hours)
7. ✅ Add preview mode (2 hours)
8. ✅ Implement import/export (2 hours)
9. ✅ Write tests (2 hours)

**Color Extraction:**
```javascript
// Use color-thief library or Canvas API
async extractColorsFromLogo(logoUrl) {
    const img = await this.loadImage(logoUrl);
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const colors = this.extractDominantColors(imageData);
    
    return {
        primary: colors[0],
        secondary: colors[1],
        // Generate complementary colors
        success: this.adjustHue(colors[0], 120),
        danger: this.adjustHue(colors[0], -30),
        warning: this.adjustHue(colors[0], 60),
        info: this.adjustHue(colors[0], 180)
    };
}
```

---

### Phase 4 Deliverables

```
📝 static/js/modules/watched-folders-config.js    (350 lines)
📝 static/js/modules/service-install-config.js    (250 lines)
📝 static/js/modules/role-rights-config.js        (200 lines)
📝 static/js/modules/branding-config.js           (650 lines)
📝 SortNStoreDashboard/routes/test_folder.py      (100 lines)
📝 tests/modules/*.test.js                        (600 lines)
```

---

## Phase 5: Logs & Integration 📝

**Timeline:** Week 4  
**Priority:** HIGH (Complete system)  
**Estimated Effort:** 5 days

### Module 1: Logs Viewer Config (Days 1-2)

**File:** `static/js/modules/logs-viewer-config.js`  
**Size:** ~350 lines  
**Dependencies:** None

**Tasks:**
1. ✅ Create module skeleton (30 min)
2. ✅ Implement SSE log streaming (3 hours)
3. ✅ Add search/filter with highlighting (2 hours)
4. ✅ Implement log level filtering (1 hour)
5. ✅ Add auto-scroll toggle (1 hour)
6. ✅ Implement virtual scrolling (3 hours)
7. ✅ Add export logs (2 hours)
8. ✅ Implement log parsing (2 hours)
9. ✅ Write tests (2 hours)

**Performance:**
- Virtual scrolling for 10K+ lines
- Debounced search (300ms)
- Log rotation (max 5000 lines in memory)
- Lazy rendering (only visible lines)

---

### Module 2: Config Coordinator (Day 3)

**File:** `static/js/config-coordinator.js`  
**Size:** ~250 lines  
**Dependencies:** All config modules

**Tasks:**
1. ✅ Create coordinator class (2 hours)
2. ✅ Implement module lifecycle (2 hours)
3. ✅ Add state persistence (2 hours)
4. ✅ Implement save-all functionality (2 hours)
5. ✅ Add error handling (1 hour)
6. ✅ Write tests (2 hours)

**Functionality:**
```javascript
class ConfigCoordinator {
    constructor() {
        this.modules = new Map();
        this.initializeModules();
    }
    
    initializeModules() {
        // Register all modules
        this.register('features', new FeaturesConfig());
        this.register('users-roles', new UsersRolesConfig());
        this.register('network-targets', new NetworkTargetsConfig());
        // ... etc
    }
    
    async saveAll() {
        const results = [];
        
        for (const [name, module] of this.modules) {
            try {
                await module.save();
                results.push({ module: name, success: true });
            } catch (error) {
                results.push({ module: name, success: false, error });
            }
        }
        
        return results;
    }
    
    async loadAll() {
        for (const [name, module] of this.modules) {
            await module.load();
        }
    }
}
```

---

### Module 3: Update HTML Templates (Day 4)

**Files:**
- `dash/config_page.html`
- `dash/config_modules.html`

**Tasks:**
1. ✅ Remove inline scripts (2 hours)
2. ✅ Add module data attributes (2 hours)
3. ✅ Update markup for modern UI (3 hours)
4. ✅ Add module imports (1 hour)
5. ✅ Test all modules (2 hours)

**Changes:**
```html
<!-- Before -->
<button onclick="saveUser()">Save</button>

<!-- After -->
<button data-action="save" data-module="users-roles">Save</button>

<!-- Module imports -->
<script type="module">
    import ConfigCoordinator from './js/config-coordinator.js';
    
    // Initialize
    const coordinator = new ConfigCoordinator();
    await coordinator.loadAll();
</script>
```

---

### Module 4: Documentation (Day 5)

**Files:**
- `CONFIG_MODULES_IMPLEMENTATION_GUIDE.md`
- `CONFIG_MODULES_API_REFERENCE.md`
- `CONFIG_MODULES_MIGRATION.md`

**Tasks:**
1. ✅ Write implementation guide (3 hours)
2. ✅ Document all API endpoints (2 hours)
3. ✅ Create migration guide (2 hours)
4. ✅ Add code examples (2 hours)

---

### Phase 5 Deliverables

```
📝 static/js/modules/logs-viewer-config.js        (350 lines)
📝 static/js/config-coordinator.js                (250 lines)
📝 dash/config_page.html                          (updated)
📝 dash/config_modules.html                       (updated)
📝 CONFIG_MODULES_IMPLEMENTATION_GUIDE.md         (800 lines)
📝 CONFIG_MODULES_API_REFERENCE.md                (400 lines)
📝 CONFIG_MODULES_MIGRATION.md                    (300 lines)
```

---

## Testing Strategy

### Unit Tests (Throughout)

**Coverage Target:** 80%+

**Test Files:**
```
tests/utilities/
├── form-validator.test.js         (50 tests)
├── table-manager.test.js          (60 tests)
└── template-engine.test.js        (40 tests)

tests/modules/
├── features-config.test.js        (30 tests)
├── users-roles-config.test.js     (50 tests)
├── network-targets-config.test.js (40 tests)
├── smtp-credentials-config.test.js(50 tests)
├── watched-folders-config.test.js (40 tests)
├── service-install-config.test.js (30 tests)
├── role-rights-config.test.js     (25 tests)
├── branding-config.test.js        (60 tests)
└── logs-viewer-config.test.js     (40 tests)

tests/integration/
└── config-coordinator.test.js     (30 tests)
```

**Total:** ~500 unit tests

---

### E2E Tests (Week 4)

**Test Files:**
```
tests/e2e/
├── config-navigation.spec.js      (10 tests)
├── users-workflow.spec.js         (15 tests)
├── network-workflow.spec.js       (12 tests)
├── smtp-workflow.spec.js          (10 tests)
├── branding-workflow.spec.js      (20 tests)
└── full-config-workflow.spec.js   (15 tests)
```

**Total:** ~80 E2E tests

---

## Rollout Strategy

### Staged Deployment

**Stage 1: Alpha (Internal Testing)**
- Deploy to dev environment
- Test all modules thoroughly
- Gather feedback from dev team
- Fix critical bugs

**Stage 2: Beta (Limited Users)**
- Deploy to staging environment
- Invite 5-10 beta testers
- Monitor usage patterns
- Fix bugs and UX issues

**Stage 3: Production (Full Rollout)**
- Deploy to production
- Feature flag for gradual rollout
- Monitor error rates
- Provide user training/documentation

---

## Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking changes in BaseModule | Low | High | Comprehensive unit tests |
| API endpoint changes | Medium | High | Maintain backward compatibility |
| Browser compatibility | Low | Medium | Polyfills for older browsers |
| Performance issues | Medium | Medium | Virtual scrolling, debouncing |
| State management bugs | Medium | High | Thorough testing, error boundaries |

### Project Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | High | High | Strict adherence to phases |
| Timeline delays | Medium | Medium | Buffer time in schedule |
| Resource constraints | Low | High | Prioritize high-impact modules |
| User adoption resistance | Medium | Medium | Comprehensive documentation, training |

---

## Success Metrics

### Code Quality

- ✅ 80%+ test coverage
- ✅ 0 critical linting errors
- ✅ All modules follow BaseModule pattern
- ✅ Consistent code style

### Performance

- ✅ Page load time <2s
- ✅ Search response <100ms
- ✅ API calls <500ms
- ✅ No memory leaks

### User Experience

- ✅ WCAG 2.1 AA compliant
- ✅ Works in Chrome, Firefox, Edge
- ✅ Mobile responsive
- ✅ Intuitive navigation

### Business Impact

- ✅ Reduced config time by 50%
- ✅ Fewer user errors
- ✅ Easier onboarding
- ✅ Positive user feedback

---

## Progress Tracking

### Current Status (December 5, 2025)

**Overall Progress:** 10% Complete

| Phase | Status | Progress | ETA |
|-------|--------|----------|-----|
| Phase 1: Foundation | ✅ COMPLETE | 100% | Done |
| Phase 2: Utilities | 📝 PLANNED | 0% | Week 1 |
| Phase 3: High-Priority | 📝 PLANNED | 0% | Week 2 |
| Phase 4: Medium-Priority | 📝 PLANNED | 0% | Week 3 |
| Phase 5: Integration | 📝 PLANNED | 0% | Week 4 |

**Lines of Code:**
- ✅ Written: 200 lines (features-config.js)
- 📝 Remaining: 4,300 lines
- 📊 Total: 4,500 lines

**Modules:**
- ✅ Complete: 1/9 (Features)
- 📝 Remaining: 8/9

**Utilities:**
- ✅ Complete: 0/3
- 📝 Remaining: 3/3

---

## Next Actions

### Immediate (Next Sprint)

1. ✅ **Review Architecture** - Stakeholder sign-off
2. 📝 **Create Utilities** - FormValidator, TableManager, TemplateEngine
3. 📝 **Start Users Module** - Highest priority, most used feature
4. 📝 **Backend Endpoints** - `/api/test-nas`, `/api/test-smtp`

### Short-term (Week 2)

1. 📝 **Complete High-Priority Modules** - Users, Network, SMTP
2. 📝 **Write Tests** - Unit + integration tests
3. 📝 **Code Review** - Peer review all modules

### Long-term (Weeks 3-4)

1. 📝 **Medium-Priority Modules** - Watched, Service, Roles, Branding
2. 📝 **Logs Module** - Real-time streaming
3. 📝 **Documentation** - Complete user guides
4. 📝 **Deployment** - Staged rollout

---

## Resources

### Documentation

- [CONFIG_MODULES_ARCHITECTURE.md](./CONFIG_MODULES_ARCHITECTURE.md) - Complete architecture
- [CONFIG_MODULES_QUICK_REFERENCE.md](./CONFIG_MODULES_QUICK_REFERENCE.md) - Developer guide
- [JAVASCRIPT_MODULARIZATION.md](./JAVASCRIPT_MODULARIZATION.md) - Core patterns

### External Libraries

**Potential Dependencies:**
- **color-thief** (https://lokeshdhakar.com/projects/color-thief/) - Color extraction
- **prism.js** (https://prismjs.com/) - Syntax highlighting for CSS editor
- **virtual-scroller** (https://www.npmjs.com/package/virtual-scroller) - Performance optimization

### Team

**Primary Developer:** Assigned  
**Code Reviewer:** TBD  
**QA Tester:** TBD  
**Documentation:** TBD

---

**Last Updated:** December 5, 2025  
**Document Version:** 1.0  
**Status:** Active Development
