/**
 * Config Module Drag and Drop using GridStack.js
 * Provides pushpin toggle to enable/disable dragging per module
 */

export const ConfigDragDrop = {
    grid: null,
    dragEnabled: new Map(), // Track which modules have drag enabled

    /**
     * Initialize GridStack on config-grid container
     */
    init() {
        console.log('[ConfigDragDrop] Initializing...');
        
        // Wait for GridStack to be loaded
        if (typeof GridStack === 'undefined') {
            console.warn('[ConfigDragDrop] GridStack not loaded yet, retrying...');
            setTimeout(() => this.init(), 100);
            return;
        }

        const gridContainer = document.querySelector('.config-grid');
        if (!gridContainer) {
            console.error('[ConfigDragDrop] No .config-grid container found');
            return;
        }

        // Determine responsive column count based on viewport width
        // More columns = less vertical scrolling, adjusted to prevent horizontal scrolling
        const getColumnCount = () => {
            const width = window.innerWidth;
            if (width >= 2200) return 4;
            if (width >= 1600) return 3;
            if (width >= 1100) return 2;
            return 1;
        };

        // Initialize GridStack with responsive options
        this.grid = GridStack.init({
            column: getColumnCount(),
            cellHeight: 220, // consistent row height to avoid squish/overlap
            minRow: 1,
            acceptWidgets: false,
            disableDrag: false, // Enable drag capability, controlled per-item
            disableResize: true,
            float: true, // Allow compact arrangement
            staticGrid: false, // Allow grid updates
            animate: true,
            margin: 25,
            columnOpts: {
                breakpoints: [
                    {w: 2200, c: 4},
                    {w: 1600, c: 3},
                    {w: 1100, c: 2},
                    {w: 0, c: 1}
                ]
            }
        }, gridContainer);

        console.log('[ConfigDragDrop] GridStack initialized:', this.grid);

        // Prepare modules for GridStack
        const modules = document.querySelectorAll('.config-module');
        const currentColumns = getColumnCount();
        
        modules.forEach((module) => {
            // Add grid-stack-item class
            module.classList.add('grid-stack-item');

            // Calculate width (full-width spans all columns)
            const isFullWidth = module.classList.contains('full-width');
            const width = isFullWidth ? currentColumns : 1;

            // Lock by default
            module.setAttribute('gs-no-resize', 'true');
            module.setAttribute('gs-no-move', 'true');

            // Initialize drag state to false (locked/docked)
            const moduleName = module.getAttribute('data-module');
            this.dragEnabled.set(moduleName, false);

            // Set initial pushpin state to docked (red, solid)
            const toggle = module.querySelector('.drag-toggle');
            if (toggle) {
                toggle.classList.add('docked');
                toggle.classList.remove('undocked');
            }

            // Add widget with auto-positioning
            this.grid.addWidget(module, { w: width, h: 1, autoPosition: true, noResize: true, noMove: true });
        });
        this.grid.compact();
        
        // Update column count on window resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const newColumns = getColumnCount();
                if (this.grid && this.grid.getColumn() !== newColumns) {
                    this.grid.column(newColumns);
                    // Update full-width modules
                    const allModules = document.querySelectorAll('.config-module');
                    allModules.forEach(module => {
                        if (module.classList.contains('full-width')) {
                            this.grid.update(module, {w: newColumns, autoPosition: true});
                        }
                    });
                    this.grid.compact();
                }
            }, 250);
        });

        // Setup pushpin click handlers
        this.setupPushpinToggles();

        // Load saved layout if exists
        this.loadLayout();

        console.log('[ConfigDragDrop] Setup complete');
    },

    /**
     * Setup click handlers for pushpin icons
     */
    setupPushpinToggles() {
        const toggles = document.querySelectorAll('.drag-toggle');
        
        toggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const module = toggle.closest('.config-module');
                const moduleName = module.getAttribute('data-module');
                const icon = toggle.querySelector('i');
                
                // Toggle drag state
                const currentState = this.dragEnabled.get(moduleName) || false;
                const newState = !currentState;
                this.dragEnabled.set(moduleName, newState);
                
                if (newState) {
                    // Enable drag for this module (UNDOCKED - dotted outline)
                    icon.classList.remove('bi-pin-angle-fill');
                    icon.classList.add('bi-pin-angle');
                    toggle.classList.add('undocked');
                    toggle.classList.remove('docked');
                    toggle.title = 'Click to lock module (dock)';
                    
                    // Make this module draggable
                    const gridItem = module.closest('.grid-stack-item');
                    if (gridItem) {
                        this.grid.enableMove(gridItem, true);
                        gridItem.removeAttribute('gs-no-move');
                        gridItem.style.cursor = 'move';
                    }
                } else {
                    // Disable drag for this module (DOCKED - solid red)
                    icon.classList.remove('bi-pin-angle');
                    icon.classList.add('bi-pin-angle-fill');
                    toggle.classList.add('docked');
                    toggle.classList.remove('undocked');
                    toggle.title = 'Click to unlock module (undock)';
                    
                    // Make this module non-draggable
                    const gridItem = module.closest('.grid-stack-item');
                    if (gridItem) {
                        this.grid.enableMove(gridItem, false);
                        gridItem.setAttribute('gs-no-move', 'true');
                        gridItem.style.cursor = 'default';
                    }
                }
                
                console.log(`[ConfigDragDrop] Module ${moduleName} drag ${newState ? 'enabled' : 'disabled'}`);
            });
        });
    },

    /**
     * Save current layout to localStorage
     */
    saveLayout() {
        if (!this.grid) return;
        
        const layout = [];
        const modules = document.querySelectorAll('.config-module');
        
        modules.forEach((module, index) => {
            const moduleName = module.getAttribute('data-module');
            const gsItem = module.getAttribute('gs-x') !== null;
            
            layout.push({
                module: moduleName,
                x: gsItem ? parseInt(module.getAttribute('gs-x')) : 0,
                y: gsItem ? parseInt(module.getAttribute('gs-y')) : index,
                w: gsItem ? parseInt(module.getAttribute('gs-w')) : (module.classList.contains('full-width') ? 2 : 1),
                h: 1
            });
        });
        
        localStorage.setItem('configModuleLayout', JSON.stringify(layout));
        console.log('[ConfigDragDrop] Layout saved:', layout);
    },

    /**
     * Load saved layout from localStorage
     */
    loadLayout() {
        const saved = localStorage.getItem('configModuleLayout');
        if (!saved) {
            console.log('[ConfigDragDrop] No saved layout found');
            return;
        }
        
        try {
            const layout = JSON.parse(saved);
            console.log('[ConfigDragDrop] Loading saved layout:', layout);
            
                layout.forEach(item => {
                    const module = document.querySelector(`.config-module[data-module="${item.module}"]`);
                    if (module) {
                        this.grid.update(module, {
                            x: item.x,
                            y: item.y,
                            w: item.w,
                            h: item.h,
                            autoPosition: false,
                            noResize: true,
                            noMove: !this.dragEnabled.get(item.module)
                        });
                    }
                });
                this.grid.compact();
        } catch (e) {
            console.error('[ConfigDragDrop] Error loading layout:', e);
        }
    },

    /**
     * Reset layout to default
     */
    resetLayout() {
        localStorage.removeItem('configModuleLayout');
        location.reload();
    }
};

// Auto-initialize when DOM is ready and GridStack is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Wait for GridStack to load
        const checkGridStack = setInterval(() => {
            if (typeof GridStack !== 'undefined') {
                clearInterval(checkGridStack);
                ConfigDragDrop.init();
                
                // Setup save on drag stop
                setTimeout(() => {
                    if (ConfigDragDrop.grid) {
                        ConfigDragDrop.grid.on('change', () => {
                            ConfigDragDrop.saveLayout();
                        });
                    }
                }, 500);
            }
        }, 100);
    });
} else {
    // Already loaded, check for GridStack
    if (typeof GridStack !== 'undefined') {
        ConfigDragDrop.init();
        setTimeout(() => {
            if (ConfigDragDrop.grid) {
                ConfigDragDrop.grid.on('change', () => {
                    ConfigDragDrop.saveLayout();
                });
            }
        }, 500);
    }
}

// Make available globally for console debugging
window.ConfigDragDrop = ConfigDragDrop;
