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
        const getColumnCount = () => {
            const width = window.innerWidth;
            if (width >= 1800) return 3;
            if (width >= 1200) return 2;
            return 1;
        };

        // Initialize GridStack with responsive options
        this.grid = GridStack.init({
            column: getColumnCount(),
            cellHeight: 'auto',
            acceptWidgets: false,
            disableDrag: true, // Disabled by default, enabled per module
            disableResize: true,
            float: false,
            staticGrid: true, // Start as static, modules opt-in via pushpin
            animate: true,
            margin: '1rem',
            columnOpts: {
                breakpoints: [
                    {w: 1800, c: 3},
                    {w: 1200, c: 2},
                    {w: 0, c: 1}
                ]
            }
        }, gridContainer);

        console.log('[ConfigDragDrop] GridStack initialized:', this.grid);

        // Add grid-stack-item class to all modules
        const modules = document.querySelectorAll('.config-module');
        const currentColumns = getColumnCount();
        
        modules.forEach((module, index) => {
            module.classList.add('grid-stack-item');
            
            // Set grid attributes based on full-width class
            const isFullWidth = module.classList.contains('full-width');
            module.setAttribute('gs-w', isFullWidth ? currentColumns.toString() : '1');
            module.setAttribute('gs-h', '1');
            module.setAttribute('gs-auto-position', 'true');
            
            // Initialize drag state to false
            const moduleName = module.getAttribute('data-module');
            this.dragEnabled.set(moduleName, false);
        });
        
        // Update column count on window resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const newColumns = getColumnCount();
                if (this.grid && this.grid.getColumn() !== newColumns) {
                    this.grid.column(newColumns);
                    // Update full-width modules
                    modules.forEach(module => {
                        if (module.classList.contains('full-width')) {
                            module.setAttribute('gs-w', newColumns.toString());
                        }
                    });
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
                    // Enable drag for this module
                    icon.classList.remove('bi-pin-angle');
                    icon.classList.add('bi-pin-angle-fill');
                    toggle.style.color = 'var(--bs-primary, #0d6efd)';
                    toggle.title = 'Click to disable dragging (pin module)';
                    
                    // Make this module draggable
                    this.grid.enableMove(module, true);
                    module.style.cursor = 'move';
                } else {
                    // Disable drag for this module
                    icon.classList.remove('bi-pin-angle-fill');
                    icon.classList.add('bi-pin-angle');
                    toggle.style.color = '#6c757d';
                    toggle.title = 'Click to enable dragging (unpin module)';
                    
                    // Make this module non-draggable
                    this.grid.enableMove(module, false);
                    module.style.cursor = 'default';
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
                    module.setAttribute('gs-x', item.x);
                    module.setAttribute('gs-y', item.y);
                    module.setAttribute('gs-w', item.w);
                    module.setAttribute('gs-h', item.h);
                }
            });
            
            // Refresh grid after loading layout
            if (this.grid) {
                this.grid.load(layout.map(item => ({
                    x: item.x,
                    y: item.y,
                    w: item.w,
                    h: item.h,
                    id: item.module
                })));
            }
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
