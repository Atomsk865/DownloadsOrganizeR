# Universal Theme System - Implementation Guide

## Overview

A comprehensive theming system that provides:
- **Persistent light/dark mode** across all pages
- **Custom theme support** with color customization
- **Automatic theme detection** and application
- **Cross-page consistency** - users' theme preference persists everywhere
- **Backward compatibility** with existing pages

## Files

### 1. **Theme System Core** (`static/js/theme-system.js`)
The central theme management engine that handles:
- Theme mode persistence (light/dark)
- Custom theme application
- CSS variable injection
- Event dispatching for theme changes

### 2. **Base Page Template** (`dash/base_page.html`)
A reusable HTML template for all new pages that:
- Includes the theme system automatically
- Provides consistent styling
- Includes a theme toggle button
- Has notification system built-in

### 3. **Updated Templates**
- `dashboard_base.html` - Updated to use theme system
- `dashboard_config_standalone.html` - Updated to use theme system

## How It Works

### Theme Storage
```javascript
// Format: organizer_theme_v1
{
  "mode": "light|dark"
}

// Format: organizer_custom_theme_v1
{
  "active": true,
  "colors": {
    "primary": "#0d6efd",
    "secondary": "#6c757d",
    "success": "#198754",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#0dcaf0"
  },
  "css": "/* custom CSS */"
}
```

### CSS Variables
All pages use CSS custom properties for theming:
```css
:root {
  --bg-primary: #f8f9fa;
  --bg-secondary: #ffffff;
  --text-primary: #212529;
  --text-secondary: #6c757d;
  --border-color: #dee2e6;
  --card-header-bg: #f8f9fa;
}

[data-theme="dark"] {
  --bg-primary: #1a1d23;
  --bg-secondary: #23262d;
  --text-primary: #e9ecef;
  --text-secondary: #adb5bd;
  --border-color: #495057;
  --card-header-bg: #2b2f37;
}
```

## Using the Base Template

### For New Pages

Create a new page extending `base_page.html`:

```html
{% extends "base_page.html" %}

{% block page_title %}
<title>My Page - Organizer</title>
{% endblock %}

{% block page_styles %}
<style>
  .my-custom-style {
    color: var(--text-primary);
    background: var(--bg-secondary);
  }
</style>
{% endblock %}

{% block page_content %}
<div class="container mt-5">
  <h1>My Page</h1>
  <p>Theme automatically syncs across all pages!</p>
</div>
{% endblock %}

{% block page_scripts %}
<script>
  function pageInit() {
    console.log('Page initialized with theme:', ThemeSystem.getCurrentTheme());
  }
</script>
{% endblock %}
```

### For Existing Pages

Add theme system to any existing page:

```html
<!-- In the <head> section -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
<script src="{{ url_for('static', filename='js/theme-system.js') }}" defer></script>

<!-- In the <body> before content -->
<div class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light mode">
    <i class="bi bi-sun-fill" style="color: #ffc107;"></i>
    <i class="bi bi-moon-stars-fill" style="color: #6ea8fe;"></i>
</div>

<!-- Use CSS variables for styling -->
<style>
  body {
    background: var(--bg-primary);
    color: var(--text-primary);
  }
  .card {
    background: var(--bg-secondary);
    border-color: var(--border-color);
  }
</style>
```

## API Reference

### ThemeSystem Object

#### Methods

**`init()`**
- Initializes theme system on page load
- Automatically called on DOMContentLoaded

**`toggleTheme()`**
- Switches between light and dark mode
- Returns: void

**`applyTheme(theme)`**
- Applies a specific theme mode
- Parameters: `theme` - "light" or "dark"
- Returns: void

**`applyCustomTheme(customTheme)`**
- Applies a custom theme with color overrides
- Parameters: `customTheme` - Object with colors and css
- Returns: void

**`saveCustomTheme(customTheme)`**
- Persists custom theme to localStorage
- Parameters: `customTheme` - Theme object
- Returns: void

**`resetTheme()`**
- Resets to default light/dark theme
- Removes custom theme
- Returns: void

**`getCurrentTheme()`**
- Gets current theme mode
- Returns: "light" or "dark"

**`getSavedTheme()`**
- Gets saved theme from localStorage
- Returns: "light" or "dark"

**`getCustomTheme()`**
- Gets saved custom theme
- Returns: Theme object or null

#### Events

Listen for theme changes:

```javascript
window.addEventListener('themeChanged', function(event) {
  const { theme, type } = event.detail;
  console.log('Theme changed to:', theme);
  console.log('Type:', type); // 'mode' or 'custom'
});
```

## Integration Examples

### Example 1: Simple Info Page

```html
{% extends "base_page.html" %}

{% block page_title %}
<title>About - Organizer</title>
{% endblock %}

{% block page_content %}
<div class="container mt-5">
  <div class="row">
    <div class="col-md-8 offset-md-2">
      <div class="card">
        <div class="card-header">
          <h5>About This Service</h5>
        </div>
        <div class="card-body">
          <p>This page automatically inherits your theme preference!</p>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

### Example 2: Page with Listening to Theme Changes

```html
{% extends "base_page.html" %}

{% block page_content %}
<div class="container mt-5">
  <h1>Dynamic Theme Page</h1>
  <div class="card" id="theme-card">
    <div class="card-body">
      <p id="theme-status">Theme: Loading...</p>
    </div>
  </div>
</div>
{% endblock %}

{% block page_scripts %}
<script>
  function pageInit() {
    updateThemeStatus();
  }
  
  function updateThemeStatus() {
    const theme = ThemeSystem.getCurrentTheme();
    document.getElementById('theme-status').textContent = 
      `Theme: ${theme === 'light' ? 'Light Mode ☀️' : 'Dark Mode 🌙'}`;
  }
  
  // Listen for theme changes
  window.addEventListener('themeChanged', updateThemeStatus);
</script>
{% endblock %}
```

### Example 3: Custom Theme Settings Page

```html
{% extends "base_page.html" %}

{% block page_content %}
<div class="container mt-5">
  <h1>Theme Settings</h1>
  <div class="card">
    <div class="card-body">
      <button class="btn btn-primary" onclick="applyCustomColors()">
        Apply Custom Theme
      </button>
      <button class="btn btn-secondary" onclick="ThemeSystem.resetTheme()">
        Reset to Default
      </button>
    </div>
  </div>
</div>
{% endblock %}

{% block page_scripts %}
<script>
  function applyCustomColors() {
    const customTheme = {
      active: true,
      colors: {
        primary: '#00a8e8',
        secondary: '#023e8a',
        success: '#52b788',
        danger: '#d62828',
        warning: '#f77f00',
        info: '#0096c7'
      }
    };
    
    ThemeSystem.applyCustomTheme(customTheme);
    showNotification('Custom theme applied!', 'success');
  }
</script>
{% endblock %}
```

## CSS Variable Reference

Use these in your stylesheets to automatically support both light and dark modes:

```css
/* Light mode (default) */
--bg-primary: #f8f9fa;        /* Page background */
--bg-secondary: #ffffff;       /* Card/container background */
--text-primary: #212529;       /* Main text color */
--text-secondary: #6c757d;     /* Secondary/muted text */
--border-color: #dee2e6;       /* Border colors */
--card-header-bg: #f8f9fa;     /* Card header background */

/* Dark mode (automatically switches) */
[data-theme="dark"] {
  --bg-primary: #1a1d23;       /* Darker page background */
  --bg-secondary: #23262d;     /* Darker card background */
  --text-primary: #e9ecef;     /* Lighter text */
  --text-secondary: #adb5bd;   /* Lighter muted text */
  --border-color: #495057;     /* Lighter borders */
  --card-header-bg: #2b2f37;   /* Darker header */
}
```

## Migration Checklist for Existing Pages

- [ ] Add Bootstrap Icons CSS link to `<head>`
- [ ] Add theme-system.js script to `<head>`
- [ ] Add theme toggle button to `<body>`
- [ ] Replace hardcoded colors with CSS variables
- [ ] Test light mode
- [ ] Test dark mode
- [ ] Test custom theme persistence
- [ ] Test theme persistence across page navigations

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- localStorage API required
- ES6 JavaScript support required

## Performance Notes

- Theme system initializes before page rendering
- CSS variables are natively fast
- No performance impact on theme switching
- Storage limited to ~5KB per theme
- Multiple themes can be stored

## Troubleshooting

### Theme not persisting
- Check browser's localStorage is enabled
- Verify no errors in browser console
- Clear localStorage: `localStorage.clear()`

### Custom theme not applying
- Ensure custom theme object has `active: true`
- Check custom theme structure matches specification
- Verify no conflicting CSS overrides

### Toggle button not visible
- Ensure Bootstrap Icons CSS is loaded
- Check z-index isn't being covered by other elements
- Verify theme-system.js loaded successfully

## Future Enhancements

- [ ] Server-side theme storage
- [ ] Theme sync across devices
- [ ] Additional preset themes
- [ ] Accessibility contrast checker
- [ ] Theme scheduling (auto dark mode at night)
- [ ] System theme detection
