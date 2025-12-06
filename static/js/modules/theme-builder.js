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
   * Apply theme styles to page
   */
  function applyThemeStyles(theme) {
    const root = document.documentElement;

    // Apply CSS variables for colors
    root.style.setProperty('--bs-primary', theme.colors.primary);
    root.style.setProperty('--bs-secondary', theme.colors.secondary);
    root.style.setProperty('--bs-success', theme.colors.success);
    root.style.setProperty('--bs-danger', theme.colors.danger);
    root.style.setProperty('--bs-warning', theme.colors.warning);
    root.style.setProperty('--bs-info', theme.colors.info);

    // Apply border radius and font size
    root.style.setProperty('--border-radius', theme.borderRadius);
    root.style.setProperty('--font-size-base', theme.fontSize);

    // Apply custom CSS
    let customStyleEl = document.getElementById('custom-theme-styles');
    if (!customStyleEl) {
      customStyleEl = document.createElement('style');
      customStyleEl.id = 'custom-theme-styles';
      document.head.appendChild(customStyleEl);
    }
    customStyleEl.textContent = theme.css || '';
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
   * Check if color is light
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
        Store.set('theme:current', theme);
        EventBus.emit('theme:updated', theme);
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
