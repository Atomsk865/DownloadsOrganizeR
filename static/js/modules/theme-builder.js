/**
 * Theme Builder Module
 * Modern, modular theme management for the dashboard
 * Replaces inline event handlers with proper event delegation
 */

import { Store, EventBus, UI } from './core-library.js';
import { ModuleSystem } from './module-system.js';

const PRESET_THEMES = {
  default: {
    name: 'Default Blue',
    colors: {
      primary: '#0d6efd',
      secondary: '#6c757d',
      success: '#198754',
      danger: '#dc3545',
      warning: '#ffc107',
      info: '#0dcaf0'
    },
    borderRadius: '6px',
    fontSize: '100%',
    shadow: 'medium',
    css: ''
  },
  dark: {
    name: 'Dark Mode',
    colors: { primary: '#495057', secondary: '#212529', success: '#1a5c34', danger: '#8b1a1a', warning: '#997404', info: '#0b5563' },
    borderRadius: '8px',
    fontSize: '100%',
    shadow: 'strong',
    css: 'body{background:#1a1d23;color:#e9ecef}.card{background:#23262d}.btn{border-radius:8px}'
  },
  forest: {
    name: 'Forest Green',
    colors: { primary: '#2d6a4f', secondary: '#52b788', success: '#40916c', danger: '#d62828', warning: '#f77f00', info: '#06a77d' },
    borderRadius: '12px',
    fontSize: '105%',
    shadow: 'medium',
    css: ''
  },
  sunset: {
    name: 'Sunset Orange',
    colors: { primary: '#ff7f50', secondary: '#ff6347', success: '#ff8c00', danger: '#d2691e', warning: '#ffa500', info: '#ff69b4' },
    borderRadius: '4px',
    fontSize: '110%',
    shadow: 'light',
    css: '.card{border:1px solid #ff7f50}'
  },
  ocean: {
    name: 'Ocean Blue',
    colors: { primary: '#006994', secondary: '#0096c7', success: '#00b4d8', danger: '#0077b6', warning: '#00b4d8', info: '#03045e' },
    borderRadius: '10px',
    fontSize: '100%',
    shadow: 'medium',
    css: '.btn-primary{background:linear-gradient(135deg, #006994, #0096c7)}'
  },
  mint: {
    name: 'Mint Fresh',
    colors: { primary: '#38ada9', secondary: '#78e08f', success: '#38ada9', danger: '#ff7675', warning: '#fdcb6e', info: '#6c5ce7' },
    borderRadius: '20px',
    fontSize: '105%',
    shadow: 'light',
    css: '.btn{border-radius:20px;font-weight:500}'
  },
  cyberpunk: {
    name: 'Cyberpunk Neon',
    colors: { primary: '#ff006e', secondary: '#8338ec', success: '#3a86ff', danger: '#fb5607', warning: '#ffbe0b', info: '#ff006e' },
    borderRadius: '4px',
    fontSize: '110%',
    shadow: 'strong',
    css: '.card{border:2px solid currentColor;background:rgba(0,0,0,0.9)}.btn{text-transform:uppercase;font-weight:bold;letter-spacing:1px}'
  }
};

const ThemeBuilder = (() => {
  let initialized = false;

  /**
   * Initialize theme builder UI and event handlers
   */
  function init() {
    if (initialized) return;

    // Bind preset theme buttons and action buttons via event delegation
    document.addEventListener('click', (e) => {
      const target = e.target.closest('button');
      if (!target) return;

      // Handle preset theme buttons
      if (target.classList.contains('preset-theme-btn')) {
        const themeName = target.dataset.theme;
        applyPresetTheme(themeName);
        e.preventDefault();
        return;
      }

      // Handle theme action buttons via data-action attribute
      const action = target.dataset.themeAction;
      if (action) {
        e.preventDefault();
        switch (action) {
          case 'save':
            saveBranding();
            break;
          case 'export':
            exportTheme();
            break;
          case 'reset':
            resetBranding();
            break;
          case 'preview':
            toggleThemePreview();
            break;
          case 'extract-logo':
            extractColorsFromLogo();
            break;
        }
      }
    });

    // Bind color input changes for live preview
    document.addEventListener('input', (e) => {
      if (
        e.target.id === 'brand-color-primary' ||
        e.target.id === 'brand-color-secondary' ||
        e.target.id === 'brand-color-success' ||
        e.target.id === 'brand-color-danger' ||
        e.target.id === 'brand-color-warning' ||
        e.target.id === 'brand-color-info'
      ) {
        updateColorSwatchBackground(e.target);
        previewTheme();
      }
    });

    // Bind theme option changes for live preview
    document.addEventListener('change', (e) => {
      if (
        e.target.id === 'brand-border-radius' ||
        e.target.id === 'brand-font-size' ||
        e.target.id === 'brand-shadow'
      ) {
        previewTheme();
      }
    });

    // Bind branding save button
    const saveBrandingBtn = document.getElementById('save-branding-btn');
    if (saveBrandingBtn) {
      saveBrandingBtn.addEventListener('click', saveBranding);
    }

    // Bind reset button
    const resetBrandingBtn = document.getElementById('reset-branding-btn');
    if (resetBrandingBtn) {
      resetBrandingBtn.addEventListener('click', resetBranding);
    }

    // Bind logo extraction button
    const extractLogoBtn = document.getElementById('extract-logo-btn');
    if (extractLogoBtn) {
      extractLogoBtn.addEventListener('click', extractColorsFromLogo);
    }

    // Load initial branding config
    loadBranding();

    initialized = true;
    console.log('✓ Theme Builder initialized');
  }

  /**
   * Apply preset theme
   */
  function applyPresetTheme(themeName) {
    const theme = PRESET_THEMES[themeName];
    if (!theme) {
      console.warn(`Preset theme "${themeName}" not found`);
      return;
    }

    // Update all form fields
    document.getElementById('brand-theme-name').value = theme.name;
    document.getElementById('brand-color-primary').value = theme.colors.primary;
    document.getElementById('brand-color-secondary').value = theme.colors.secondary;
    document.getElementById('brand-color-success').value = theme.colors.success;
    document.getElementById('brand-color-danger').value = theme.colors.danger;
    document.getElementById('brand-color-warning').value = theme.colors.warning;
    document.getElementById('brand-color-info').value = theme.colors.info;
    document.getElementById('brand-border-radius').value = theme.borderRadius;
    document.getElementById('brand-font-size').value = theme.fontSize;
    document.getElementById('brand-shadow').value = theme.shadow;
    document.getElementById('brand-css').value = theme.css || '';

    // Update color swatches
    document.querySelectorAll('[data-color-id]').forEach((el) => {
      updateColorSwatchBackground(el);
    });

    previewTheme();
    saveBranding();
    showNotification(`Preset theme "${theme.name}" applied and saved`, 'success');
  }

  /**
   * Preview theme in real-time
   */
  function previewTheme() {
    const theme = getThemeObject();
    applyThemeStyles(theme);

    // Persist to localStorage for preview
    if (typeof persistThemeLocally === 'function') {
      persistThemeLocally(theme);
    }

    // Enable custom theme override
    if (typeof enableCustomTheme === 'function') {
      enableCustomTheme();
    }
  }

  /**
   * Get theme object from form fields
   */
  function getThemeObject() {
    return {
      title: document.getElementById('brand-title')?.value || '',
      logo: document.getElementById('brand-logo')?.value || '',
      themeName: document.getElementById('brand-theme-name')?.value || '',
      colors: {
        primary: document.getElementById('brand-color-primary')?.value || '#0d6efd',
        secondary: document.getElementById('brand-color-secondary')?.value || '#6c757d',
        success: document.getElementById('brand-color-success')?.value || '#198754',
        danger: document.getElementById('brand-color-danger')?.value || '#dc3545',
        warning: document.getElementById('brand-color-warning')?.value || '#ffc107',
        info: document.getElementById('brand-color-info')?.value || '#0dcaf0'
      },
      borderRadius: document.getElementById('brand-border-radius')?.value || '6px',
      fontSize: document.getElementById('brand-font-size')?.value || '100%',
      shadow: document.getElementById('brand-shadow')?.value || 'medium',
      css: document.getElementById('brand-css')?.value || ''
    };
  }

  /**
   * Apply theme styles to page - Comprehensive theme application
   */
  function applyThemeStyles(theme) {
    const isDarkMode = theme.themeName && theme.themeName.toLowerCase().includes('dark');
    const html = document.documentElement;

    // Update data-theme attribute for light/dark mode styling
    html.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');

    // Create comprehensive theme CSS with all necessary overrides
    let themeStyleEl = document.getElementById('theme-colors-styles');
    if (!themeStyleEl) {
      themeStyleEl = document.createElement('style');
      themeStyleEl.id = 'theme-colors-styles';
      document.head.appendChild(themeStyleEl);
    }

    const colors = theme.colors;
    const borderRadius = theme.borderRadius || '6px';
    const fontSize = theme.fontSize ? (theme.fontSize.replace('%', '') / 100) : 1;
    
    // Determine text color for contrast (light text on dark bg, dark text on light bg)
    const isLightBg = isLightColor(colors.primary);
    const textColor = isLightBg ? '#000000' : '#FFFFFF';
    const textColorInverted = isLightBg ? '#FFFFFF' : '#000000';

    const css = `
      /* Root theme variables */
      :root {
        --bs-primary: ${colors.primary};
        --bs-secondary: ${colors.secondary};
        --bs-success: ${colors.success};
        --bs-danger: ${colors.danger};
        --bs-warning: ${colors.warning};
        --bs-info: ${colors.info};
        --theme-primary-rgb: ${hexToRgb(colors.primary)};
        --theme-text-color: ${isDarkMode ? '#e0e0e0' : '#212529'};
        --theme-bg-color: ${isDarkMode ? '#1a1d23' : '#ffffff'};
      }

      /* HTML element theme attribute */
      html[data-theme="dark"],
      html[data-theme="light"] {
        --bs-primary: ${colors.primary};
        --bs-secondary: ${colors.secondary};
        --bs-success: ${colors.success};
        --bs-danger: ${colors.danger};
        --bs-warning: ${colors.warning};
        --bs-info: ${colors.info};
      }

      /* Page background and text - Use secondary color for backgrounds */
      body {
        background-color: ${isDarkMode ? colors.secondary : '#f8f9fa'} !important;
        color: ${isDarkMode ? '#e0e0e0' : '#212529'} !important;
        font-size: calc(1rem * ${fontSize}) !important;
      }

      /* Primary color elements */
      .btn-primary {
        background-color: ${colors.primary} !important;
        color: ${textColor} !important;
        border: 2px solid ${colors.primary} !important;
        outline: none !important;
      }

      .btn-primary:hover,
      .btn-primary:focus {
        background-color: ${colors.primary}dd !important;
        color: ${textColor} !important;
        border: 2px solid ${colors.primary} !important;
        outline: 3px solid ${colors.primary}60 !important;
        box-shadow: 0 0 0 0.25rem ${colors.primary}30 !important;
      }

      .badge-primary,
      .alert-primary,
      .nav-link.active,
      .text-primary {
        background-color: ${colors.primary} !important;
        color: ${textColor} !important;
      }

      a {
        color: ${colors.primary} !important;
      }

      /* Secondary color elements */
      .btn-secondary, .badge-secondary, .alert-secondary {
        background-color: ${colors.secondary} !important;
        color: ${textColorInverted} !important;
      }

      /* Success color elements */
      .btn-success, .badge-success, .alert-success {
        background-color: ${colors.success} !important;
        color: ${isLightColor(colors.success) ? '#000000' : '#ffffff'} !important;
      }

      /* Danger color elements */
      .btn-danger, .badge-danger, .alert-danger {
        background-color: ${colors.danger} !important;
        color: ${isLightColor(colors.danger) ? '#000000' : '#ffffff'} !important;
      }

      /* Warning color elements */
      .btn-warning, .badge-warning, .alert-warning {
        background-color: ${colors.warning} !important;
        color: ${isLightColor(colors.warning) ? '#000000' : '#ffffff'} !important;
      }

      /* Info color elements */
      .btn-info, .badge-info, .alert-info {
        background-color: ${colors.info} !important;
        color: ${isLightColor(colors.info) ? '#000000' : '#ffffff'} !important;
      }

      /* Background color classes */
      .bg-primary { background-color: ${colors.primary} !important; color: ${textColor} !important; }
      .bg-secondary { background-color: ${colors.secondary} !important; }
      .bg-success { background-color: ${colors.success} !important; }
      .bg-danger { background-color: ${colors.danger} !important; }
      .bg-warning { background-color: ${colors.warning} !important; }
      .bg-info { background-color: ${colors.info} !important; }

      /* Navbar and header links - Secondary background with primary accents */
      .navbar {
        background-color: ${isDarkMode ? colors.secondary : '#ffffff'} !important;
        color: ${isDarkMode ? '#e0e0e0' : '#212529'} !important;
        border-bottom: 3px solid ${colors.primary} !important;
      }

      .navbar-brand {
        color: ${colors.primary} !important;
      }

      /* Dashboard back button */
      .config-header-left a {
        border-color: ${colors.primary} !important;
        color: ${isDarkMode ? '#e0e0e0' : '#212529'} !important;
      }

      .config-header-left a:hover {
        border-color: ${colors.primary} !important;
        background-color: ${colors.primary}20 !important;
      }

      /* Module headers and titles - Apply primary color */
      .module-header, .card-header, .modal-header {
        background-color: ${colors.primary} !important;
        color: ${textColor} !important;
        border: 2px solid ${colors.primary} !important;
      }

      h1, h2, h3, h4, h5, h6 {
        color: ${colors.primary} !important;
      }

      /* Tables - Apply theme colors to headers and borders */
      table, .table {
        background-color: ${isDarkMode ? colors.secondary : '#ffffff'} !important;
        color: ${isDarkMode ? '#e0e0e0' : '#212529'} !important;
        border: 2px solid ${colors.primary} !important;
      }

      .table thead th {
        background-color: ${colors.primary} !important;
        color: ${textColor} !important;
        border-bottom: 2px solid ${colors.primary} !important;
      }

      .table tbody tr {
        border-color: ${colors.primary}40 !important;
      }

      .table tbody tr:hover {
        background-color: ${colors.primary}20 !important;
      }

      .table tbody td {
        border-color: ${colors.primary}30 !important;
      }

      /* Cards - Secondary background with primary border */
      .card {
        background-color: ${isDarkMode ? colors.secondary : '#ffffff'} !important;
        border: 2px solid ${colors.primary} !important;
        color: ${isDarkMode ? '#e0e0e0' : '#212529'} !important;
      }

      .card-body {
        background-color: ${isDarkMode ? colors.secondary : '#ffffff'} !important;
      }

      /* Forms and inputs - Primary color borders and outlines */
      .form-control, .form-select, textarea, input[type="text"], input[type="password"], input[type="email"] {
        background-color: ${isDarkMode ? colors.secondary : '#ffffff'} !important;
        color: ${isDarkMode ? '#e0e0e0' : '#212529'} !important;
        border: 2px solid ${colors.primary} !important;
        outline: none !important;
      }

      .form-control:focus, .form-select:focus, textarea:focus, 
      input[type="text"]:focus, input[type="password"]:focus, input[type="email"]:focus {
        background-color: ${isDarkMode ? colors.secondary : '#ffffff'} !important;
        color: ${isDarkMode ? '#e0e0e0' : '#212529'} !important;
        border: 2px solid ${colors.primary} !important;
        outline: 3px solid ${colors.primary}60 !important;
        box-shadow: 0 0 0 0.25rem ${colors.primary}30 !important;
      }

      /* Input groups */
      .input-group-text {
        background-color: ${colors.primary} !important;
        color: ${textColor} !important;
        border: 2px solid ${colors.primary} !important;
      }

      /* Border radius global */
      .btn, .card, .modal-content, .form-control, .alert, .badge {
        border-radius: ${borderRadius} !important;
      }

      /* Additional dark mode styles */
      ${isDarkMode ? `
        [data-theme="dark"] { color-scheme: dark; }
        .dropdown-menu { background-color: #23262d !important; }
        .dropdown-item { color: #e0e0e0 !important; }
        .dropdown-item:hover { background-color: ${colors.primary} !important; color: ${textColor} !important; }
        .modal-content { background-color: #23262d !important; }
        .modal-header { border-bottom-color: ${colors.primary} !important; }
        .nav-tabs { border-bottom-color: ${colors.primary} !important; }
        .nav-tabs .nav-link.active { background-color: ${colors.primary} !important; color: ${textColor} !important; }
      ` : ''}
    `;

    themeStyleEl.textContent = css;

    // Apply custom CSS if provided
    let customStyleEl = document.getElementById('custom-theme-styles');
    if (!customStyleEl) {
      customStyleEl = document.createElement('style');
      customStyleEl.id = 'custom-theme-styles';
      document.head.appendChild(customStyleEl);
    }
    customStyleEl.textContent = theme.css || '';

    // Update theme toggle button display
    updateThemeToggleDisplay(isDarkMode);
  }

  /**
   * Helper: Check if color is light
   */
  function isLightColor(hex) {
    const rgb = parseInt(hex.slice(1), 16);
    const r = (rgb >> 16) & 255;
    const g = (rgb >> 8) & 255;
    const b = rgb & 255;
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return brightness > 155;
  }

  /**
   * Helper: Convert hex color to RGB string
   */
  function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : '0, 0, 0';
  }

  /**
   * Update theme toggle button to show correct icon
   */
  function updateThemeToggleDisplay(isDark) {
    const themeToggle = document.querySelector('.theme-toggle-btn');
    if (themeToggle) {
      const sunIcon = themeToggle.querySelector('.bi-sun-fill');
      const moonIcon = themeToggle.querySelector('.bi-moon-stars-fill');
      if (sunIcon) sunIcon.style.display = isDark ? 'inline' : 'none';
      if (moonIcon) moonIcon.style.display = isDark ? 'none' : 'inline';
    }
  }

  /**
   * Update color swatch background
   */
  function updateColorSwatchBackground(colorInput) {
    const swatchContainer = colorInput.parentElement;
    if (swatchContainer) {
      swatchContainer.style.backgroundColor = colorInput.value;
      swatchContainer.style.color = isLightColor(colorInput.value) ? '#000' : '#fff';
    }
  }


  /**
   * Save branding configuration to server
   */
  async function saveBranding() {
    const theme = getThemeObject();

    try {
      const headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      };

      // Get auth headers from cookies if available
      const authHeaders = getAuthHeadersFromCookie();
      Object.assign(headers, authHeaders);

      const response = await fetch('/api/dashboard/branding', {
        method: 'POST',
        headers,
        body: JSON.stringify(theme),
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        showNotification('Theme saved successfully', 'success');
        
        // Update the returned branding data with timestamp
        const savedTheme = data.branding || theme;
        Store.set('theme:current', savedTheme);
        EventBus.emit('theme:updated', savedTheme);
        
        // Persist theme locally and apply it across the dashboard
        if (typeof persistThemeLocally === 'function') {
          persistThemeLocally(savedTheme);
        }
        if (typeof applyThemeStyles === 'function') {
          applyThemeStyles(savedTheme);
        }
      } else {
        const error = await response.json().catch(() => ({ message: response.statusText }));
        showNotification(`Save failed: ${error.message}`, 'warning');
      }
    } catch (e) {
      console.error('Error saving branding:', e);
      showNotification(`Save error: ${e.message}`, 'danger');
    }
  }

  /**
   * Get auth headers from cookies
   */
  function getAuthHeadersFromCookie() {
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
  }

  /**
   * Load branding configuration from server
   */
  async function loadBranding() {
    try {
      const response = await fetch('/api/dashboard/branding', {
        credentials: 'include'
      });

      if (response.ok) {
        const theme = await response.json();
        applyThemeToForm(theme);
        applyThemeStyles(theme);
        Store.set('theme:current', theme);
      }
    } catch (e) {
      console.error('Error loading branding:', e);
    }
  }

  /**
   * Apply theme to form fields
   */
  function applyThemeToForm(theme) {
    if (document.getElementById('brand-title')) {
      document.getElementById('brand-title').value = theme.title || '';
    }
    if (document.getElementById('brand-logo')) {
      document.getElementById('brand-logo').value = theme.logo || '';
    }
    if (document.getElementById('brand-theme-name')) {
      document.getElementById('brand-theme-name').value = theme.themeName || '';
    }

    if (theme.colors) {
      document.getElementById('brand-color-primary').value = theme.colors.primary || '#0d6efd';
      document.getElementById('brand-color-secondary').value = theme.colors.secondary || '#6c757d';
      document.getElementById('brand-color-success').value = theme.colors.success || '#198754';
      document.getElementById('brand-color-danger').value = theme.colors.danger || '#dc3545';
      document.getElementById('brand-color-warning').value = theme.colors.warning || '#ffc107';
      document.getElementById('brand-color-info').value = theme.colors.info || '#0dcaf0';
    }

    if (document.getElementById('brand-border-radius')) {
      document.getElementById('brand-border-radius').value = theme.borderRadius || '6px';
    }
    if (document.getElementById('brand-font-size')) {
      document.getElementById('brand-font-size').value = theme.fontSize || '100%';
    }
    if (document.getElementById('brand-shadow')) {
      document.getElementById('brand-shadow').value = theme.shadow || 'medium';
    }
    if (document.getElementById('brand-css')) {
      document.getElementById('brand-css').value = theme.css || '';
    }

    // Update color swatches
    document.querySelectorAll('input[type="color"]').forEach((el) => {
      updateColorSwatchBackground(el);
    });
  }

  /**
   * Reset branding to defaults
   */
  function resetBranding() {
    if (!confirm('Reset all theme settings to defaults?')) return;

    applyPresetTheme('default');
  }

  /**
   * Extract colors from logo
   */
  async function extractColorsFromLogo() {
    const logoUrl = document.getElementById('brand-logo')?.value.trim();

    if (!logoUrl) {
      showNotification('Please enter a logo URL first', 'warning');
      return;
    }

    showNotification('Extracting colors from logo...', 'info');

    try {
      const img = new Image();
      img.crossOrigin = 'anonymous';

      img.onload = function () {
        const colors = extractDominantColors(img, 6);

        if (colors.length < 4) {
          showNotification('Could not extract enough colors from logo', 'warning');
          return;
        }

        const themeName = `Logo-Generated-${Date.now()}`;
        document.getElementById('brand-theme-name').value = themeName;
        document.getElementById('brand-color-primary').value = colors[0];
        document.getElementById('brand-color-secondary').value = colors[1];
        document.getElementById('brand-color-success').value = colors[2];
        document.getElementById('brand-color-danger').value = colors[3];
        if (colors[4]) document.getElementById('brand-color-warning').value = colors[4];
        if (colors[5]) document.getElementById('brand-color-info').value = colors[5];

        previewTheme();
        showNotification('Colors extracted from logo', 'success');
      };

      img.onerror = () => {
        showNotification('Failed to load logo image', 'warning');
      };

      img.src = logoUrl;
    } catch (e) {
      console.error('Error extracting colors:', e);
      showNotification(`Error: ${e.message}`, 'danger');
    }
  }

  /**
   * Extract dominant colors from image
   */
  function extractDominantColors(img, count = 6) {
    const canvas = document.createElement('canvas');
    canvas.width = 100;
    canvas.height = 100;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, 100, 100);

    const imageData = ctx.getImageData(0, 0, 100, 100).data;
    const colorMap = {};

    for (let i = 0; i < imageData.length; i += 4) {
      const r = imageData[i];
      const g = imageData[i + 1];
      const b = imageData[i + 2];
      const hex = rgbToHex(r, g, b);
      colorMap[hex] = (colorMap[hex] || 0) + 1;
    }

    return Object.entries(colorMap)
      .sort(([, a], [, b]) => b - a)
      .slice(0, count)
      .map(([color]) => color);
  }

  /**
   * Convert RGB to Hex
   */
  function rgbToHex(r, g, b) {
    return (
      '#' +
      [r, g, b]
        .map((x) => {
          const hex = x.toString(16);
          return hex.length === 1 ? '0' + hex : hex;
        })
        .join('')
        .toUpperCase()
    );
  }

  /**
   * Show notification (fallback if not available globally)
   */
  function showNotification(message, type = 'info') {
    if (typeof window.showNotification === 'function') {
      window.showNotification(message, type);
    } else {
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  }

  // Public API
  return {
    init,
    applyPresetTheme,
    previewTheme,
    saveBranding,
    loadBranding,
    resetBranding,
    extractColorsFromLogo,
    getThemeObject,
    applyThemeStyles,
    getPresetThemes: () => PRESET_THEMES
  };
})();

// Register as module
if (typeof ModuleSystem !== 'undefined') {
  ModuleSystem.register('ThemeBuilder', {
    init: () => ThemeBuilder.init(),
    dependencies: []
  });
}

// Export for use in other modules
export default ThemeBuilder;
export { ThemeBuilder };
