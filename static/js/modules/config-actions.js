// Config Page Actions - extracted from dashboard_config.html for standalone config_page
// Provides button handlers and data loading so inline onclick handlers work.

// Utilities and state
let dashboardConfig = {};
let __authHeader = null;
let __rights = window.__rights || {};
let originalStdoutContent = '';
let originalStderrContent = '';

function ensureAuthHeader() {
  if (__authHeader) return __authHeader;
  try {
    const match = document.cookie.match(/(?:^|; )authHeader=([^;]+)/);
    if (match) __authHeader = decodeURIComponent(match[1]);
  } catch (e) {
    console.warn('Auth cookie missing or unreadable');
  }
  return __authHeader;
}

function getAuthHeaders() {
  const h = ensureAuthHeader();
  return h ? { Authorization: h } : {};
}

function showNotification(message, type = 'info') {
  // Reuse existing global if available
  if (typeof window.showNotification === 'function') {
    return window.showNotification(message, type);
  }
  let container = document.getElementById('notification-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notification-container';
    container.style.position = 'fixed';
    container.style.top = '16px';
    container.style.right = '16px';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
  }
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.innerHTML = `${message || ''}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  container.appendChild(alertDiv);
  setTimeout(() => alertDiv.remove(), 5000);
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    const json = await response.json().catch(() => null);
    return { ok: response.ok, status: response.status, json };
  }
  const text = await response.text();
  return { ok: response.ok, status: response.status, text };
}

// Feature toggles
async function loadFeaturesConfig() {
  try {
    const r = await fetch('/api/organizer/config', { credentials: 'include', cache: 'no-store', headers: getAuthHeaders() });
    if (!r.ok) return;
    const org = await r.json();
    document.getElementById('cfg-vt-api-key').value = org.vt_api_key || '';
    const feats = org.features || {};
    document.getElementById('cfg-feat-virustotal').checked = feats.virustotal_enabled !== false;
    document.getElementById('cfg-feat-duplicates').checked = feats.duplicates_enabled !== false;
    document.getElementById('cfg-feat-reports').checked = feats.reports_enabled !== false;
    document.getElementById('cfg-feat-developer-mode').checked = feats.developer_mode === true;
  } catch (e) {
    console.warn('loadFeaturesConfig failed', e);
  }
}

async function saveFeaturesConfig() {
  const vtApiKey = document.getElementById('cfg-vt-api-key').value.trim();
  const features = {
    virustotal_enabled: document.getElementById('cfg-feat-virustotal').checked,
    duplicates_enabled: document.getElementById('cfg-feat-duplicates').checked,
    reports_enabled: document.getElementById('cfg-feat-reports').checked,
    developer_mode: document.getElementById('cfg-feat-developer-mode').checked,
  };
  try {
    const r = await fetch('/api/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ vt_api_key: vtApiKey, features }),
    });
    const j = await r.json().catch(() => ({}));
    if (r.ok) {
      showNotification('Features saved', 'success');
    } else {
      showNotification('Failed to save features: ' + (j.message || r.status), 'warning');
    }
  } catch (e) {
    showNotification('Error saving features: ' + e.message, 'danger');
  }
}

// Users & Roles
function renderUsers(users) {
  const tbody = document.getElementById('users-tbody');
  if (!tbody) return;
  tbody.innerHTML = (users || [])
    .map((u) => `<tr><td><small>${u.username}</small></td><td><small>${u.role}</small></td><td><button class='btn btn-sm btn-danger' onclick="deleteUser('${u.username}')">Del</button></td></tr>`)
    .join('');
}

function renderRolesFromSources(cfg) {
  const sel = document.getElementById('new-role');
  if (!sel) return;
  let roleNames = [];
  try {
    if (cfg && cfg.roles) roleNames = Object.keys(cfg.roles || {});
    if (!roleNames.length && __rights && __rights.available_roles) roleNames = __rights.available_roles;
  } catch (e) { /* ignore */ }
  if (!roleNames || !roleNames.length) roleNames = ['admin', 'user', 'viewer'];
  sel.innerHTML = roleNames.map((r) => `<option value='${r}'>${r}</option>`).join('');
}

function filterUsers() {
  const searchTerm = (document.getElementById('search-users')?.value || '').toLowerCase();
  const rows = document.querySelectorAll('#users-tbody tr');
  rows.forEach((row) => {
    const username = row.cells[0]?.textContent.toLowerCase() || '';
    const role = row.cells[1]?.textContent.toLowerCase() || '';
    row.style.display = username.includes(searchTerm) || role.includes(searchTerm) ? '' : 'none';
  });
}

function clearUserSearch() {
  const el = document.getElementById('search-users');
  if (el) el.value = '';
  filterUsers();
}

function clearRoleSearch() {
  const el = document.getElementById('search-roles');
  if (el) el.value = '';
  filterRoles();
}

function filterRoles() {
  const searchTerm = (document.getElementById('search-roles')?.value || '').toLowerCase();
  const rows = document.querySelectorAll('#role-rights-tbody tr');
  rows.forEach((row) => {
    const role = row.cells[0]?.textContent.toLowerCase() || '';
    const rights = row.cells[1]?.textContent.toLowerCase() || '';
    row.style.display = role.includes(searchTerm) || rights.includes(searchTerm) ? '' : 'none';
  });
}

async function saveUser() {
  const username = document.getElementById('new-username').value.trim();
  const role = document.getElementById('new-role').value.trim();
  const password = document.getElementById('user-new-password').value;
  if (!username || !role) {
    showNotification('Username and role required', 'warning');
    return;
  }
  try {
    const r = await fetch('/api/dashboard/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ username, role, password: password || undefined }),
    });
    const result = await parseResponse(r);
    if (result.ok && result.json?.success) {
      showNotification('User saved', 'success');
      document.getElementById('user-new-password').value = '';
      fetchConfig();
    } else {
      const msg = result.json?.error || result.text || 'Save failed';
      showNotification(msg, 'danger');
    }
  } catch (e) {
    showNotification('Save error: ' + e.message, 'danger');
  }
}

async function deleteUser(username) {
  if (!confirm('Delete user ' + username + '?')) return;
  try {
    const r = await fetch('/api/dashboard/users/' + encodeURIComponent(username), {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    const result = await parseResponse(r);
    if (result.ok && result.json?.success) {
      showNotification('User deleted', 'success');
      fetchConfig();
    } else {
      const msg = result.json?.error || result.text || 'Delete failed';
      showNotification(msg, 'danger');
    }
  } catch (e) {
    showNotification('Delete error: ' + e.message, 'danger');
  }
}

// Network targets & credentials
function renderNetworkTargets(targets) {
  const tbody = document.getElementById('network-targets-tbody');
  if (!tbody) return;
  const rows = Object.entries(targets || {}).map(([name, cfg]) => {
    const path = (cfg && cfg.path) || '';
    const credential_key = (cfg && cfg.credential_key) || '';
    return `<tr>
      <td><small>${name}</small></td>
      <td><small>${path}</small></td>
      <td><small>${credential_key}</small></td>
      <td><button class='btn btn-sm btn-danger' onclick="deleteNetworkTarget('${name}')" title="Delete target">Del</button></td>
    </tr>`;
  }).join('');
  tbody.innerHTML = rows;
}

function addNetworkTarget() {
  const name = document.getElementById('nt-name').value.trim();
  const path = document.getElementById('nt-path').value.trim();
  const credential_key = document.getElementById('nt-cred').value.trim();
  clearInvalid('nt-name');
  clearInvalid('nt-path');
  clearInvalid('nt-cred');
  if (!name) return setInvalid('nt-name', 'Name is required.');
  if (!isValidUNC(path)) return setInvalid('nt-path', 'Provide a valid UNC path, e.g., \\server\\share');
  if (!credential_key) return setInvalid('nt-cred', 'Credential key is required.');
  dashboardConfig.network_targets = dashboardConfig.network_targets || {};
  dashboardConfig.network_targets[name] = { path, credential_key };
  renderNetworkTargets(dashboardConfig.network_targets);
}

function deleteNetworkTarget(name) {
  if (!confirm('Delete network target ' + name + '?')) return;
  if (dashboardConfig.network_targets) delete dashboardConfig.network_targets[name];
  renderNetworkTargets(dashboardConfig.network_targets || {});
}

async function saveNetworkConfig() {
  const payload = { network_targets: dashboardConfig.network_targets || {}, credentials: dashboardConfig.credentials || {} };
  const r = await fetch('/api/dashboard/update-config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(payload),
  });
  const { ok, j } = await r.json().then((j) => ({ ok: r.ok, j })).catch(() => ({ ok: false, j: {} }));
  showNotification(ok ? 'Network config saved' : j.error || 'Save failed', ok ? 'success' : 'danger');
}

async function testNAS() {
  const path = document.getElementById('nt-path').value.trim();
  const credential_key = document.getElementById('nt-cred').value.trim();
  clearInvalid('nt-path');
  if (!isValidUNC(path)) return setInvalid('nt-path', 'Provide a valid UNC path.');
  showNotification('Testing NAS path...', 'info');
  try {
    const r = await fetch('/api/test/nas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ path, credential_key }),
    });
    const { ok, j } = await r.json().then((j) => ({ ok: r.ok, j })).catch(() => ({ ok: false, j: {} }));
    showNotification(ok ? j.message || 'NAS test succeeded' : j.error || 'NAS test failed', ok ? 'success' : 'danger');
  } catch (e) {
    showNotification('NAS test error: ' + e.message, 'danger');
  }
}

// Credentials & SMTP
function renderCredentials(creds) {
  const tbody = document.getElementById('credentials-tbody');
  if (!tbody) return;
  const rows = Object.entries(creds || {}).map(([key, c]) => {
    return `<tr>
      <td><small>${key}</small></td>
      <td><small>${c.username || ''}</small></td>
      <td><small>${c.password_b64 || ''}</small></td>
      <td><button class='btn btn-sm btn-danger' onclick="deleteCredential('${key}')" title="Delete credential">Del</button></td>
    </tr>`;
  }).join('');
  tbody.innerHTML = rows;
}

function addCredential() {
  const key = document.getElementById('cred-key').value.trim();
  const username = document.getElementById('cred-user').value.trim();
  const password_b64 = document.getElementById('cred-pass-b64').value.trim();
  clearInvalid('cred-key');
  clearInvalid('cred-pass-b64');
  if (!key) return setInvalid('cred-key', 'Credential key is required.');
  if (password_b64 && !isValidBase64(password_b64)) return setInvalid('cred-pass-b64', 'Password must be base64-encoded.');
  dashboardConfig.credentials = dashboardConfig.credentials || {};
  dashboardConfig.credentials[key] = { username, password_b64 };
  renderCredentials(dashboardConfig.credentials);
}

function deleteCredential(key) {
  if (!confirm('Delete credential ' + key + '?')) return;
  if (dashboardConfig.credentials) delete dashboardConfig.credentials[key];
  renderCredentials(dashboardConfig.credentials || {});
}

function renderSmtp(smtp) {
  document.getElementById('smtp-host').value = smtp.host || '';
  document.getElementById('smtp-port').value = smtp.port || 587;
  document.getElementById('smtp-from').value = smtp.from || '';
  document.getElementById('smtp-to').value = smtp.to || '';
  document.getElementById('smtp-user').value = smtp.username || '';
  document.getElementById('smtp-pass').value = smtp.password || '';
  document.getElementById('smtp-tls').checked = smtp.tls !== false;
}

async function saveSmtpAndCredentials() {
  const smtp = {
    host: document.getElementById('smtp-host').value.trim(),
    port: parseInt(document.getElementById('smtp-port').value) || 587,
    from: document.getElementById('smtp-from').value.trim(),
    to: document.getElementById('smtp-to').value.trim(),
    username: document.getElementById('smtp-user').value.trim(),
    password: document.getElementById('smtp-pass').value,
    tls: document.getElementById('smtp-tls').checked,
  };
  clearInvalid('smtp-host');
  clearInvalid('smtp-port');
  clearInvalid('smtp-from');
  clearInvalid('smtp-to');
  if (!smtp.host) return setInvalid('smtp-host', 'SMTP host is required.');
  if (!(smtp.port >= 1 && smtp.port <= 65535)) return setInvalid('smtp-port', 'Port must be between 1 and 65535.');
  if (!isValidEmail(smtp.from)) return setInvalid('smtp-from', 'Enter a valid email address.');
  if (!validateEmails(smtp.to)) return setInvalid('smtp-to', 'Enter one or more valid email addresses.');
  const payload = { smtp, credentials: dashboardConfig.credentials || {} };
  const r = await fetch('/api/dashboard/update-config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(payload),
  });
  const { ok, j } = await r.json().then((j) => ({ ok: r.ok, j })).catch(() => ({ ok: false, j: {} }));
  showNotification(ok ? 'SMTP & credentials saved' : j.error || 'Save failed', ok ? 'success' : 'danger');
}

async function testSMTP() {
  const smtp = {
    host: document.getElementById('smtp-host').value.trim(),
    port: parseInt(document.getElementById('smtp-port').value) || 587,
    from: document.getElementById('smtp-from').value.trim(),
    to: document.getElementById('smtp-to').value.trim(),
    username: document.getElementById('smtp-user').value.trim(),
    password: document.getElementById('smtp-pass').value,
    tls: document.getElementById('smtp-tls').checked,
  };
  clearInvalid('smtp-host');
  clearInvalid('smtp-port');
  clearInvalid('smtp-from');
  clearInvalid('smtp-to');
  if (!smtp.host) return setInvalid('smtp-host', 'SMTP host is required.');
  if (!(smtp.port >= 1 && smtp.port <= 65535)) return setInvalid('smtp-port', 'Port must be between 1 and 65535.');
  if (!isValidEmail(smtp.from)) return setInvalid('smtp-from', 'Enter a valid email address.');
  if (!validateEmails(smtp.to)) return setInvalid('smtp-to', 'Enter one or more valid email addresses.');
  showNotification('Sending test email...', 'info');
  const r = await fetch('/api/test/smtp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(smtp),
  });
  const { ok, j } = await r.json().then((j) => ({ ok: r.ok, j })).catch(() => ({ ok: false, j: {} }));
  showNotification(ok ? j.message || 'SMTP test succeeded' : j.error || 'SMTP test failed', ok ? 'success' : 'danger');
}

// Watch folders
function isValidPath(p) {
  if (!p || typeof p !== 'string') return false;
  const s = p.trim();
  const replaced = s.replace(/%USERNAME%|%USER%/g, 'user');
  const isUNC = /^\\\\[^\\/]+\\[^\\/]+(\\.*)?$/.test(replaced);
  const isWinAbs = /^[A-Za-z]:[\\/].*/.test(replaced);
  const isLinuxAbs = replaced.startsWith('/');
  return isUNC || isWinAbs || isLinuxAbs;
}

function renderWatchFoldersList() {
  const ul = document.getElementById('watch-folders-config-list');
  const folders = Array.isArray(window.__watchFolders) ? window.__watchFolders : [];
  ul.innerHTML = folders
    .map((f, idx) => {
      const valid = isValidPath(f);
      const badgeClass = valid ? 'text-success' : 'text-warning';
      const badgeIcon = valid ? 'bi-check-circle' : 'bi-exclamation-triangle';
      const title = valid ? 'Valid path' : 'Invalid path';
      const liClass = valid ? 'list-group-item' : 'list-group-item list-group-item-warning';
      return `
      <li class="${liClass} d-flex justify-content-between align-items-center">
        <span>
          <code>${f}</code>
          <span class="ms-2 ${badgeClass}" title="${title}">
            <i class="bi ${badgeIcon}"></i>
          </span>
        </span>
        <div class="btn-group">
          <button class="btn btn-sm btn-info" onclick="runInitialScan(${idx})" title="Run initial scan"><i class="bi bi-play"></i></button>
          <button class="btn btn-sm btn-secondary" onclick="testWatchFolder(${idx})" title="Test folder access"><i class="bi bi-check2-circle"></i></button>
          <button class="btn btn-sm btn-danger" onclick="removeWatchFolder(${idx})" title="Remove"><i class="bi bi-trash"></i></button>
        </div>
      </li>`;
    })
    .join('');
}

function addWatchFolder() {
  const input = document.getElementById('watch-folder-input');
  const val = (input.value || '').trim();
  if (!val) return;
  window.__watchFolders = Array.isArray(window.__watchFolders) ? window.__watchFolders : [];
  window.__watchFolders.push(val);
  input.value = '';
  renderWatchFoldersList();
}

function removeWatchFolder(index) {
  if (!Array.isArray(window.__watchFolders)) return;
  window.__watchFolders.splice(index, 1);
  renderWatchFoldersList();
}

async function loadWatchFoldersConfig() {
  try {
    const r = await fetch('/api/watch_folders', { credentials: 'include', headers: getAuthHeaders() });
    const data = await r.json();
    const folders = Array.isArray(data.folders) ? data.folders : [];
    window.__watchFolders = folders;
    renderWatchFoldersList();
  } catch (e) {
    console.error('Failed to load watch folders', e);
  }
}

async function testWatchFolder(index) {
  const folders = Array.isArray(window.__watchFolders) ? window.__watchFolders : [];
  const folder = folders[index];
  if (!folder) return;
  const createIfMissing = document.getElementById('wf-create-missing')?.checked || false;
  if (createIfMissing && !confirm(`Create folder if missing?\n\n${folder}`)) return;
  const res = await fetch('/api/watch_folders/test', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ folder, create: createIfMissing }),
  });
  const data = await res.json().catch(() => ({}));
  if (res.ok) {
    const msg = data.exists ? `Exists • Readable: ${data.readable} • Writable: ${data.writable}` : data.message || 'Does not exist';
    showNotification(`Test ${folder}: ${msg}`, data.exists && data.readable && data.writable ? 'success' : 'warning');
  } else {
    showNotification('Test failed: ' + (data.error || res.status), 'danger');
  }
}

async function testSelectedWatchFolder() {
  const folders = Array.isArray(window.__watchFolders) ? window.__watchFolders : [];
  if (!folders.length) {
    showNotification('No folders to test', 'warning');
    return;
  }
  await testWatchFolder(0);
}

async function runInitialScan(index) {
  const folders = Array.isArray(window.__watchFolders) ? window.__watchFolders : [];
  const folder = folders[index];
  if (!folder) return;
  if (!isValidPath(folder)) {
    showNotification('Invalid folder path: ' + folder, 'warning');
    return;
  }
  const res = await fetch('/api/watch_folders/scan', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ folder }),
  });
  const data = await res.json().catch(() => ({}));
  if (res.ok && data.success) {
    showNotification('Initial scan completed for: ' + folder, 'success');
  } else {
    showNotification('Initial scan failed: ' + (data.error || res.status), 'danger');
  }
}

async function saveWatchFolders() {
  try {
    const folders = Array.isArray(window.__watchFolders) ? window.__watchFolders : [];
    const invalid = folders.filter((f) => !isValidPath(f));
    if (invalid.length) {
      showNotification('Invalid folder path(s): ' + invalid.join(', '), 'warning');
      return;
    }
    const res = await fetch('/api/watch_folders', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ folders }),
    });
    const resp = await res.json().catch(() => ({}));
    if (res.ok && resp.success) {
      showNotification('Watch folders saved', 'success');
      if (Array.isArray(resp.invalid) && resp.invalid.length) {
        showNotification('Some paths were rejected: ' + resp.invalid.join(', '), 'warning');
        markInvalidWatchFolders(resp.invalid);
      }
    } else {
      const serverInvalid = Array.isArray(resp.invalid) ? resp.invalid : [];
      if (serverInvalid.length) {
        showNotification('Invalid folder path(s): ' + serverInvalid.join(', '), 'danger');
        markInvalidWatchFolders(serverInvalid);
      } else {
        showNotification('Failed to save: ' + (resp.error || res.status), 'danger');
      }
    }
  } catch (e) {
    showNotification('Error saving watch folders: ' + e.message, 'danger');
  }
}

function markInvalidWatchFolders(invalidList) {
  const ul = document.getElementById('watch-folders-config-list');
  const items = ul.querySelectorAll('li');
  items.forEach((li) => {
    const codeEl = li.querySelector('code');
    const path = codeEl ? codeEl.textContent : '';
    if (invalidList.includes(path)) {
      li.classList.add('list-group-item-warning');
      const span = li.querySelector('span');
      if (span) {
        const badge = document.createElement('span');
        badge.className = 'ms-2 text-warning';
        badge.title = 'Invalid path';
        badge.innerHTML = '<i class="bi bi-exclamation-triangle"></i>';
        span.appendChild(badge);
      }
    }
  });
}

// Logs
function filterLogs() {
  const searchTerm = document.getElementById('search-logs').value;
  const stdoutLog = document.getElementById('stdout-log');
  const stderrLog = document.getElementById('stderr-log');
  if (!stdoutLog || !stderrLog) return;

  if (!originalStdoutContent && stdoutLog.textContent) originalStdoutContent = stdoutLog.textContent;
  if (!originalStderrContent && stderrLog.textContent) originalStderrContent = stderrLog.textContent;

  if (!searchTerm) {
    stdoutLog.innerHTML = escapeHtml(originalStdoutContent);
    stderrLog.innerHTML = escapeHtml(originalStderrContent);
    return;
  }

  const highlightLines = (content) => {
    if (!content) return '';
    const lines = content.split('\n');
    return lines
      .map((line) => {
        if (line.toLowerCase().includes(searchTerm.toLowerCase())) {
          return `<mark style="background-color: yellow; color: black;">${escapeHtml(line)}</mark>`;
        }
        return `<span style="opacity: 0.4;">${escapeHtml(line)}</span>`;
      })
      .join('\n');
  };

  stdoutLog.innerHTML = highlightLines(originalStdoutContent);
  stderrLog.innerHTML = highlightLines(originalStderrContent);
  const firstMatch = stdoutLog.querySelector('mark') || stderrLog.querySelector('mark');
  if (firstMatch) firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function clearLogSearch() {
  const el = document.getElementById('search-logs');
  if (el) el.value = '';
  filterLogs();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text || '';
  return div.innerHTML;
}

function streamLog(which) {
  const logElement = document.getElementById(`${which}-log`);
  if (!logElement) return;
  const eventSource = new EventSource(`/stream/${which}`);
  eventSource.onmessage = function (event) {
    if (event.data && logElement) {
      logElement.textContent += event.data + '\n';
      logElement.scrollTop = logElement.scrollHeight;
    }
  };
  eventSource.onerror = function () {
    eventSource.close();
    if (document.getElementById(`${which}-log`)) setTimeout(() => streamLog(which), 5000);
  };
}

async function clearLog(which) {
  try {
    const response = await fetch(`/clear_log/${which}`, {
      method: 'POST',
      credentials: 'include',
      headers: getAuthHeaders(),
    });
    if (response.ok) {
      const logElement = document.getElementById(`${which}-log`);
      if (logElement) logElement.textContent = '';
      showNotification(`${which.toUpperCase()} log cleared`, 'success');
    } else {
      showNotification(`Failed to clear ${which} log`, 'danger');
    }
  } catch (error) {
    showNotification(`Error: ${error.message}`, 'danger');
  }
}

// Service controls
async function installService() {
  if (!confirm('Install the Organizer service? Requires administrator privileges.')) return;
  const serviceName = document.getElementById('service-name-input').value.trim();
  const scriptsRoot = document.getElementById('scripts-root-input').value.trim();
  const memoryThreshold = parseInt(document.getElementById('memory-threshold-input').value);
  const cpuThreshold = parseInt(document.getElementById('cpu-threshold-input').value);
  showNotification('Installing service... This may take a minute.', 'info');
  try {
    const response = await fetch('/api/service/install', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ service_name: serviceName, scripts_root: scriptsRoot, memory_threshold_mb: memoryThreshold, cpu_threshold_percent: cpuThreshold }),
    });
    const result = await parseResponse(response);
    if (result.status === 401 || result.status === 403) return showNotification('Authentication required. Please login again.', 'warning');
    if (result.json && result.ok && result.json.success) {
      showNotification('Service installed successfully!', 'success');
    } else {
      showNotification(result.json?.error || result.text || 'Installation failed', 'danger');
    }
  } catch (err) {
    showNotification('Installation error: ' + err.message, 'danger');
  }
}

async function uninstallService() {
  if (!confirm('Uninstall the Organizer service? This will stop and remove it.')) return;
  const serviceName = document.getElementById('service-name-input').value.trim();
  showNotification('Uninstalling service...', 'info');
  try {
    const response = await fetch('/api/service/uninstall', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ service_name: serviceName }),
    });
    const result = await parseResponse(response);
    if (result.status === 401 || result.status === 403) return showNotification('Authentication required. Please login again.', 'warning');
    if (result.json && result.ok && result.json.success) {
      showNotification('Service uninstalled successfully!', 'success');
    } else {
      showNotification(result.json?.error || 'Uninstallation failed', 'danger');
    }
  } catch (err) {
    showNotification('Uninstallation error: ' + err.message, 'danger');
  }
}

async function reinstallService() {
  if (!confirm('Reinstall the Organizer service? Will uninstall and reinstall with current settings.')) return;
  const serviceName = document.getElementById('service-name-input').value.trim();
  const scriptsRoot = document.getElementById('scripts-root-input').value.trim();
  const memoryThreshold = parseInt(document.getElementById('memory-threshold-input').value);
  const cpuThreshold = parseInt(document.getElementById('cpu-threshold-input').value);
  showNotification('Reinstalling service... This may take a minute.', 'info');
  try {
    const response = await fetch('/api/service/reinstall', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ service_name: serviceName, scripts_root: scriptsRoot, memory_threshold_mb: memoryThreshold, cpu_threshold_percent: cpuThreshold }),
    });
    const result = await parseResponse(response);
    if (result.status === 401 || result.status === 403) return showNotification('Authentication required. Please login again.', 'warning');
    if (result.json && result.ok && result.json.success) {
      showNotification('Service reinstalled successfully!', 'success');
    } else {
      showNotification(result.json?.error || 'Reinstallation failed', 'danger');
    }
  } catch (err) {
    showNotification('Reinstallation error: ' + err.message, 'danger');
  }
}

// Config actions modal
async function openConfigActions() {
  try {
    const res = await fetch('/api/config_actions', { credentials: 'include', headers: getAuthHeaders() });
    const data = await res.json().catch(() => []);
    const body = document.getElementById('config-actions-body');
    if (Array.isArray(data) && data.length) {
      const rows = data
        .map((a) => {
          const ts = a.timestamp || '';
          const action = a.action || '';
          const folder = a.folder || '';
          const result = a.result || '';
          return `<tr><td><small>${ts}</small></td><td><small>${action}</small></td><td><small><code>${folder}</code></small></td><td><small>${result}</small></td></tr>`;
        })
        .join('');
      body.innerHTML = `<div class="table-responsive"><table class="table table-sm"><thead><tr><th>Time (UTC)</th><th>Action</th><th>Target</th><th>Result</th></tr></thead><tbody>${rows}</tbody></table></div>`;
    } else {
      body.innerHTML = '<div class="text-muted">No audit entries</div>';
    }
    const el = document.getElementById('configActionsModal');
    if (el && window.bootstrap) {
      const modal = bootstrap.Modal.getOrCreateInstance(el);
      modal.show();
    }
  } catch (e) {
    showNotification('Failed to load config actions: ' + e.message, 'danger');
  }
}

// Filtering helpers for network targets
function filterNetworkTargets() {
  const searchTerm = (document.getElementById('search-network-targets')?.value || '').toLowerCase();
  const rows = document.querySelectorAll('#network-targets-tbody tr');
  let visibleCount = 0;
  rows.forEach((row) => {
    const name = row.cells[0]?.textContent.toLowerCase() || '';
    const path = row.cells[1]?.textContent.toLowerCase() || '';
    const cred = row.cells[2]?.textContent.toLowerCase() || '';
    if (name.includes(searchTerm) || path.includes(searchTerm) || cred.includes(searchTerm)) {
      row.style.display = '';
      visibleCount++;
    } else {
      row.style.display = 'none';
    }
  });
  if (rows.length > 0 && visibleCount === 0) {
    const tbody = document.getElementById('network-targets-tbody');
    const existingMsg = tbody.querySelector('.no-results-message');
    if (!existingMsg) {
      const noResultsRow = document.createElement('tr');
      noResultsRow.className = 'no-results-message';
      noResultsRow.innerHTML = '<td colspan="4" class="text-center text-muted"><i class="bi bi-search"></i> No network targets found</td>';
      tbody.appendChild(noResultsRow);
    }
  } else {
    document.querySelector('#network-targets-tbody .no-results-message')?.remove();
  }
}

function clearNetworkTargetSearch() {
  const el = document.getElementById('search-network-targets');
  if (el) el.value = '';
  filterNetworkTargets();
}

// Validation helpers
function setInvalid(id, msg) {
  const el = document.getElementById(id);
  if (!el || !el.classList) return false;
  el.classList.add('is-invalid');
  const fb = el.parentElement ? el.parentElement.querySelector('.invalid-feedback') : null;
  if (fb && msg) fb.textContent = msg;
  return false;
}
function clearInvalid(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('is-invalid');
}
function isValidUNC(p) {
  return /^\\\\[^\\/]+\\[^\\/]+(\\.*)?$/.test(p || '');
}
function isValidEmail(e) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((e || '').trim());
}
function validateEmails(list) {
  const items = (list || '').split(/[,;]+/).map((s) => s.trim()).filter(Boolean);
  return items.length > 0 && items.every(isValidEmail);
}
function isValidBase64(s) {
  if (!s) return true;
  try {
    atob(s);
    return true;
  } catch (e) {
    return false;
  }
}

// Fetch dashboard config and hydrate UI
async function fetchConfig() {
  try {
    const r = await fetch('/api/dashboard/config', { headers: getAuthHeaders() });
    if (!r.ok) throw new Error('Failed');
    const data = await r.json();
    dashboardConfig = data || {};
    renderUsers(data.users || []);
    renderRolesFromSources(data);
    renderNetworkTargets(data.network_targets || {});
    renderCredentials(data.credentials || {});
    renderSmtp(data.smtp || {});
  } catch (err) {
    showNotification('Load failed: ' + err.message, 'danger');
  }
}

// Expose globally for onclick handlers
Object.assign(window, {
  saveFeaturesConfig,
  loadFeaturesConfig,
  filterUsers,
  clearUserSearch,
  saveUser,
  deleteUser,
  filterRoles,
  clearRoleSearch,
  installService,
  reinstallService,
  uninstallService,
  clearNetworkTargetSearch,
  filterNetworkTargets,
  addNetworkTarget,
  deleteNetworkTarget,
  testNAS,
  saveNetworkConfig,
  addCredential,
  deleteCredential,
  testSMTP,
  saveSmtpAndCredentials,
  addWatchFolder,
  saveWatchFolders,
  testSelectedWatchFolder,
  openConfigActions,
  clearLogSearch,
  clearLog,
  filterLogs,
  streamLog,
  runInitialScan,
  testWatchFolder,
  removeWatchFolder,
  loadWatchFoldersConfig,
});

// Bootstrap on page ready
function initConfigActions() {
  ensureAuthHeader();
  fetchConfig();
  loadFeaturesConfig();
  loadWatchFoldersConfig();
  streamLog('stdout');
  streamLog('stderr');
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initConfigActions);
} else {
  initConfigActions();
}
