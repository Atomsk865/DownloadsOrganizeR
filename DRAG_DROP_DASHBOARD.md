# Drag-and-Drop Dashboard Feature

## Overview

The dashboard now supports drag-and-drop functionality for all modules, allowing users to customize their dashboard layout. Each user's layout is saved independently using localStorage based on their authentication credentials.



### 1. Draggable Modules

All dashboard cards are now draggable modules with the following attributes:
- `data-module` - Unique identifier for each module
- `draggable="true"` - Enables HTML5 drag-and-drop
### 2. Module List

The following modules can be rearranged:
- **Settings** - `data-module="settings"`

 - **File Categories** - `data-module="file-categories"`
 - **Tag Routes** - `data-module="tag-routes"`

 - **Custom Widget** - `data-module="custom-widget"`

### 3. Non-Draggable Modules

A special module that allows users to add their own content:
- Click "Edit" button to open prompt dialog
- Enter custom HTML, embed codes, iframes, or text
- Content is saved per-user in localStorage
- Perfect for adding:

  - Embedded widgets (weather, calendar, etc.)
  - Quick links
  - Custom HTML/CSS
  - Iframe embeds (YouTube, Google Calendar, etc.)



Each module has a grip icon (☰) in the top-right corner:
 - Hover over the handle to see cursor change
 - Click and drag to reorder modules


Located in the dashboard header (visible after login):

- Resets dashboard to default layout
- Clears custom widget content
## Technical Implementation


### HTML Structure

```html
<div class="col-12 col-xl-6 dashboard-module" data-module="MODULE_ID" draggable="true">
    <div class="card mb-3">
        <div class="card-header d-flex align-items-center">
            <b>Module Title</b>
            <span class="drag-handle ms-auto">
                <i class="bi bi-grip-vertical"></i>
            </span>
        </div>
        <div class="card-body">
            <!-- Content -->
        </div>
    </div>
</div>
```

### CSS Styling

```css
.dashboard-module {
    cursor: move;
    transition: transform 0.2s, box-shadow 0.2s;
}

.dashboard-module:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.dashboard-module.dragging {
    opacity: 0.5;
}

.drag-handle {
    cursor: move;
    padding: 2px 8px;
    font-size: 0.9rem;
    color: #6c757d;
}

.custom-widget-content {
    min-height: 100px;
}
```

### JavaScript Functions

#### Core Drag-and-Drop

- `initDragAndDrop()` - Initializes event listeners on all draggable modules
- `handleDragStart(e)` - Sets dragged element and adds visual feedback
- `handleDragOver(e)` - Allows drop by preventing default
- `handleDrop(e)` - Reorders modules and saves layout
- `handleDragEnd(e)` - Removes visual feedback

#### Layout Persistence

- `saveDashboardLayout()` - Saves current module order to localStorage
- `loadDashboardLayout()` - Restores saved layout on page load
- `resetDashboardLayout()` - Clears saved layout and reloads page

#### Custom Widget

- `editCustomWidget()` - Opens prompt dialog to edit widget content
- `loadCustomWidget()` - Loads saved widget content from localStorage

### localStorage Keys

Layout and content are stored per-user:
- `dashboardLayout_{authHeader}` - Array of module IDs in order
- `customWidget_{authHeader}` - HTML content of custom widget

## Usage Examples

### Reordering Modules

1. Login to dashboard
2. Hover over any module's drag handle (☰)
3. Click and drag the module
4. Drop it in the desired position
5. Layout is automatically saved

### Adding Custom Widget Content

1. Locate the "Custom Widget" module
2. Click the "Edit" button
3. Enter HTML, text, or embed code in the prompt
4. Click OK to save
5. Content displays immediately

### Example Custom Widget Content

```html
<!-- Embed a YouTube video -->
<iframe width="100%" height="315" 
    src="https://www.youtube.com/embed/VIDEO_ID" 
    frameborder="0" allowfullscreen>
</iframe>

<!-- Add quick links -->
<ul>
    <li><a href="https://example.com">Quick Link 1</a></li>
    <li><a href="https://example.com">Quick Link 2</a></li>
</ul>

<!-- Custom styled content -->
<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
    <h6>Custom Section</h6>
    <p>Any HTML content works here!</p>
</div>
```

### Resetting Layout

1. Click "Reset Layout" button in header
2. Confirm the action
3. Page reloads with default layout
4. Custom widget content is also cleared

## Browser Compatibility

- HTML5 Drag and Drop API (all modern browsers)
- localStorage (all modern browsers)
- Bootstrap 5.3.2 grid system
- No additional dependencies required

## Security Considerations

- Custom widget content is stored in localStorage (client-side only)
- HTML is rendered directly - users should only add trusted content
- No server-side storage of layout/widget data
- Layout is tied to authentication credentials

## Future Enhancements

- Visual editor for custom widget (WYSIWYG)
- Module visibility toggle (show/hide modules)
- Multiple layout presets
- Server-side layout storage
- Module resize options
- Drag-and-drop between columns

## Troubleshooting

### Layout Not Saving

- Ensure browser allows localStorage
- Check browser console for JavaScript errors
- Verify login is successful (authHeader set)

### Custom Widget Not Loading

- Check localStorage is enabled
- Clear browser cache and try again
- Verify content is valid HTML

### Modules Not Dragging

- Ensure `draggable="true"` attribute exists
- Check for JavaScript errors in console
- Verify Bootstrap 5 CSS is loaded

## Related Files

- `dash/dashboard.html` - HTML structure with draggable modules
- `dash/dashboard_scripts.html` - Drag-and-drop JavaScript implementation
- `requirements.txt` - No changes needed (uses browser APIs)
