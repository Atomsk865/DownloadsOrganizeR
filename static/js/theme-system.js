/**
 * Universal Theme System for Organizer Dashboard
 * Manages light/dark mode and custom theme persistence across all pages
 */

const ThemeSystem = (() => {
    // Configuration
    const STORAGE_KEY = 'organizer_theme_v1';
    const CUSTOM_THEME_KEY = 'organizer_custom_theme_v1';
    const DEFAULT_THEME = 'light';
    
    // CSS variable mappings for custom themes
    const THEME_VARS = {
        primary: '--bs-primary',
        secondary: '--bs-secondary',
        success: '--bs-success',
        danger: '--bs-danger',
        warning: '--bs-warning',
        info: '--bs-info',
    };

    /**
     * Initialize theme system on page load
     */
    function init() {
        // Apply saved theme on page load
        const savedTheme = getSavedTheme();
        applyTheme(savedTheme);
        
        // Apply custom theme if active
        const customTheme = getCustomTheme();
        if (customTheme && customTheme.active) {
            applyCustomTheme(customTheme);
        }
        
        // Initialize theme toggle if it exists
        const toggleBtn = document.querySelector('.theme-toggle');
        if (toggleBtn && !toggleBtn.hasListener) {
            toggleBtn.addEventListener('click', toggleTheme);
            toggleBtn.hasListener = true;
        }
    }

    /**
     * Get saved theme mode (light/dark)
     */
    function getSavedTheme() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                const data = JSON.parse(stored);
                return data.mode || DEFAULT_THEME;
            }
        } catch (e) {
            console.warn('Failed to parse saved theme:', e);
        }
        return DEFAULT_THEME;
    }

    /**
     * Get custom theme settings
     */
    function getCustomTheme() {
        try {
            // Check new key first
            let stored = localStorage.getItem(CUSTOM_THEME_KEY);
            if (stored) {
                return JSON.parse(stored);
            }
            
            // Fallback to old key (dashboard_theme_v1) from legacy theme builder
            const oldKey = 'dashboard_theme_v1';
            stored = localStorage.getItem(oldKey);
            if (stored) {
                const oldTheme = JSON.parse(stored);
                if (oldTheme && oldTheme.theme) {
                    // Convert old format to new format
                    const newTheme = {
                        active: true,
                        colors: oldTheme.theme.colors || {},
                        borderRadius: oldTheme.theme.borderRadius,
                        fontSize: oldTheme.theme.fontSize,
                        shadow: oldTheme.theme.shadow,
                        customCss: oldTheme.theme.customCss
                    };
                    // Save to new key for future use
                    saveCustomTheme(newTheme);
                    return newTheme;
                }
            }
        } catch (e) {
            console.warn('Failed to parse custom theme:', e);
        }
        return null;
    }

    /**
     * Apply theme mode (light/dark)
     */
    function applyTheme(theme) {
        if (!theme || (theme !== 'light' && theme !== 'dark')) {
            theme = DEFAULT_THEME;
        }
        
        // Apply to HTML element
        document.documentElement.setAttribute('data-theme', theme);
        
        // Save to localStorage
        try {
            const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
            data.mode = theme;
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save theme:', e);
        }
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme, type: 'mode' }
        }));
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const current = getSavedTheme();
        const next = current === 'light' ? 'dark' : 'light';
        applyTheme(next);
        
        // Show brief notification if possible
        if (typeof showNotification === 'function') {
            showNotification(`Switched to ${next === 'light' ? 'Light' : 'Dark'} mode`, 'info');
        }
    }

    /**
     * Apply custom theme colors
     */
    function applyCustomTheme(customTheme) {
        if (!customTheme || !customTheme.colors) return;
        
        // Create or update custom theme style tag
        let styleTag = document.getElementById('custom-theme-style');
        if (!styleTag) {
            styleTag = document.createElement('style');
            styleTag.id = 'custom-theme-style';
            document.head.appendChild(styleTag);
        }
        
        // Build CSS variables
        let css = ':root {\n';
        Object.entries(customTheme.colors).forEach(([key, value]) => {
            const varName = THEME_VARS[key];
            if (varName) {
                css += `  ${varName}: ${value} !important;\n`;
            }
        });
        css += '}\n';
        
        // Apply additional custom CSS if present
        if (customTheme.css) {
            css += customTheme.css;
        }
        
        styleTag.textContent = css;
        
        // Mark as active
        customTheme.active = true;
        saveCustomTheme(customTheme);
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: customTheme, type: 'custom' }
        }));
    }

    /**
     * Save custom theme
     */
    function saveCustomTheme(customTheme) {
        try {
            localStorage.setItem(CUSTOM_THEME_KEY, JSON.stringify(customTheme));
        } catch (e) {
            console.warn('Failed to save custom theme:', e);
        }
    }

    /**
     * Reset to default theme
     */
    function resetTheme() {
        applyTheme(DEFAULT_THEME);
        try {
            localStorage.removeItem(CUSTOM_THEME_KEY);
        } catch (e) {
            console.warn('Failed to reset theme:', e);
        }
        
        // Remove custom theme style tag
        const styleTag = document.getElementById('custom-theme-style');
        if (styleTag) {
            styleTag.remove();
        }
    }

    /**
     * Get current theme mode
     */
    function getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || DEFAULT_THEME;
    }

    /**
     * Initialize theme toggle on DOMContentLoaded if not already done
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Public API
    return {
        init,
        toggleTheme,
        applyTheme,
        applyCustomTheme,
        saveCustomTheme,
        resetTheme,
        getCurrentTheme,
        getSavedTheme,
        getCustomTheme,
        STORAGE_KEY,
        CUSTOM_THEME_KEY,
    };
})();

// Global function for compatibility
function toggleTheme() {
    return ThemeSystem.toggleTheme();
}

// Auto-initialize theme system when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        ThemeSystem.init();
    });
} else {
    // DOM already loaded (e.g., with defer on deferred script)
    ThemeSystem.init();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeSystem;
}
