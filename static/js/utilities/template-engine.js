/**
 * TemplateEngine - Lightweight HTML templating with data binding
 * 
 * Features:
 * - Variable interpolation: {{variable}}
 * - Conditional blocks: {{#if condition}} {{/if}}
 * - Loops: {{#each items}} {{/each}}
 * - Nested properties: {{user.name}}
 * - Helper functions
 * - HTML escaping
 * 
 * @module TemplateEngine
 * @version 1.0.0
 */

class TemplateEngine {
    constructor(options = {}) {
        this.options = {
            escapeHtml: options.escapeHtml !== false,
            helpers: options.helpers || {},
            ...options
        };
        
        // Register built-in helpers
        this.registerBuiltInHelpers();
    }
    
    /**
     * Render template with data
     * @param {string} template - Template string
     * @param {Object} data - Data object
     * @returns {string} Rendered HTML
     */
    render(template, data = {}) {
        let result = template;
        
        // Process blocks first (if, each)
        result = this.processBlocks(result, data);
        
        // Then process variables
        result = this.processVariables(result, data);
        
        return result;
    }
    
    /**
     * Register custom helper function
     * @param {string} name - Helper name
     * @param {Function} fn - Helper function
     */
    registerHelper(name, fn) {
        this.options.helpers[name] = fn;
    }
    
    /**
     * Process block statements (if, each, etc.)
     * @private
     */
    processBlocks(template, data) {
        let result = template;
        
        // Process {{#if}} blocks
        result = this.processIfBlocks(result, data);
        
        // Process {{#each}} blocks
        result = this.processEachBlocks(result, data);
        
        // Process {{#unless}} blocks
        result = this.processUnlessBlocks(result, data);
        
        return result;
    }
    
    /**
     * Process {{#if}} conditional blocks
     * @private
     */
    processIfBlocks(template, data) {
        const ifRegex = /\{\{#if\s+([^}]+)\}\}([\s\S]*?)\{\{\/if\}\}/g;
        
        return template.replace(ifRegex, (match, condition, content) => {
            const value = this.getValue(condition.trim(), data);
            return this.isTruthy(value) ? this.render(content, data) : '';
        });
    }
    
    /**
     * Process {{#unless}} conditional blocks (opposite of if)
     * @private
     */
    processUnlessBlocks(template, data) {
        const unlessRegex = /\{\{#unless\s+([^}]+)\}\}([\s\S]*?)\{\{\/unless\}\}/g;
        
        return template.replace(unlessRegex, (match, condition, content) => {
            const value = this.getValue(condition.trim(), data);
            return !this.isTruthy(value) ? this.render(content, data) : '';
        });
    }
    
    /**
     * Process {{#each}} loop blocks
     * @private
     */
    processEachBlocks(template, data) {
        const eachRegex = /\{\{#each\s+([^}]+)\}\}([\s\S]*?)\{\{\/each\}\}/g;
        
        return template.replace(eachRegex, (match, arrayPath, content) => {
            const array = this.getValue(arrayPath.trim(), data);
            
            if (!Array.isArray(array)) {
                console.warn(`{{#each ${arrayPath}}} expects an array`);
                return '';
            }
            
            return array.map((item, index) => {
                const itemData = {
                    ...data,
                    this: item,
                    '@index': index,
                    '@first': index === 0,
                    '@last': index === array.length - 1,
                    '@length': array.length
                };
                
                // If item is object, merge its properties
                if (typeof item === 'object' && item !== null) {
                    Object.assign(itemData, item);
                }
                
                return this.render(content, itemData);
            }).join('');
        });
    }
    
    /**
     * Process {{variable}} interpolations
     * @private
     */
    processVariables(template, data) {
        // Match {{variable}} or {{helper arg1 arg2}}
        const varRegex = /\{\{([^#/][^}]*)\}\}/g;
        
        return template.replace(varRegex, (match, expression) => {
            expression = expression.trim();
            
            // Check if it's a helper call
            const helperMatch = expression.match(/^(\w+)\s+(.+)$/);
            if (helperMatch) {
                const [, helperName, argsStr] = helperMatch;
                if (this.options.helpers[helperName]) {
                    const args = this.parseArgs(argsStr, data);
                    return this.options.helpers[helperName](...args);
                }
            }
            
            // Regular variable
            const value = this.getValue(expression, data);
            return this.formatValue(value);
        });
    }
    
    /**
     * Get value from data object using dot notation
     * @private
     */
    getValue(path, data) {
        // Handle 'this' keyword
        if (path === 'this' || path === '.') {
            return data.this !== undefined ? data.this : data;
        }
        
        // Handle @ prefixed special variables
        if (path.startsWith('@')) {
            return data[path];
        }
        
        const parts = path.split('.');
        let value = data;
        
        for (const part of parts) {
            if (value === null || value === undefined) {
                return undefined;
            }
            value = value[part];
        }
        
        return value;
    }
    
    /**
     * Parse helper arguments
     * @private
     */
    parseArgs(argsStr, data) {
        // Simple argument parser (supports strings, numbers, variables)
        const args = [];
        const regex = /"([^"]*)"|'([^']*)'|([^\s]+)/g;
        let match;
        
        while ((match = regex.exec(argsStr)) !== null) {
            if (match[1] !== undefined) {
                // Double-quoted string
                args.push(match[1]);
            } else if (match[2] !== undefined) {
                // Single-quoted string
                args.push(match[2]);
            } else {
                // Number or variable
                const arg = match[3];
                if (/^\d+$/.test(arg)) {
                    args.push(parseInt(arg, 10));
                } else if (/^\d+\.\d+$/.test(arg)) {
                    args.push(parseFloat(arg));
                } else {
                    args.push(this.getValue(arg, data));
                }
            }
        }
        
        return args;
    }
    
    /**
     * Check if value is truthy
     * @private
     */
    isTruthy(value) {
        if (Array.isArray(value)) {
            return value.length > 0;
        }
        return !!value;
    }
    
    /**
     * Format value for output
     * @private
     */
    formatValue(value) {
        if (value === null || value === undefined) {
            return '';
        }
        
        const str = String(value);
        
        return this.options.escapeHtml ? this.escapeHtml(str) : str;
    }
    
    /**
     * Escape HTML to prevent XSS
     * @private
     */
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
    
    /**
     * Register built-in helper functions
     * @private
     */
    registerBuiltInHelpers() {
        // Format number with commas
        this.registerHelper('formatNumber', (num) => {
            if (typeof num !== 'number') return num;
            return num.toLocaleString();
        });
        
        // Format bytes to human-readable size
        this.registerHelper('formatBytes', (bytes) => {
            if (typeof bytes !== 'number') return bytes;
            
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
            if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
            return (bytes / 1073741824).toFixed(1) + ' GB';
        });
        
        // Format date
        this.registerHelper('formatDate', (date, format = 'default') => {
            const d = new Date(date);
            if (isNaN(d.getTime())) return date;
            
            if (format === 'short') {
                return d.toLocaleDateString();
            } else if (format === 'long') {
                return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
            } else if (format === 'iso') {
                return d.toISOString();
            }
            return d.toLocaleString();
        });
        
        // Truncate string
        this.registerHelper('truncate', (str, length = 50) => {
            if (typeof str !== 'string') return str;
            if (str.length <= length) return str;
            return str.substring(0, length) + '...';
        });
        
        // Uppercase
        this.registerHelper('upper', (str) => {
            return String(str).toUpperCase();
        });
        
        // Lowercase
        this.registerHelper('lower', (str) => {
            return String(str).toLowerCase();
        });
        
        // Capitalize first letter
        this.registerHelper('capitalize', (str) => {
            const s = String(str);
            return s.charAt(0).toUpperCase() + s.slice(1);
        });
        
        // Default value if empty
        this.registerHelper('default', (value, defaultValue) => {
            return value || defaultValue;
        });
        
        // Math operations
        this.registerHelper('add', (a, b) => Number(a) + Number(b));
        this.registerHelper('subtract', (a, b) => Number(a) - Number(b));
        this.registerHelper('multiply', (a, b) => Number(a) * Number(b));
        this.registerHelper('divide', (a, b) => Number(a) / Number(b));
        
        // Comparison
        this.registerHelper('eq', (a, b) => a === b);
        this.registerHelper('ne', (a, b) => a !== b);
        this.registerHelper('gt', (a, b) => a > b);
        this.registerHelper('gte', (a, b) => a >= b);
        this.registerHelper('lt', (a, b) => a < b);
        this.registerHelper('lte', (a, b) => a <= b);
        
        // Join array
        this.registerHelper('join', (arr, separator = ', ') => {
            if (!Array.isArray(arr)) return arr;
            return arr.join(separator);
        });
        
        // Get array length
        this.registerHelper('length', (arr) => {
            if (Array.isArray(arr)) return arr.length;
            if (typeof arr === 'string') return arr.length;
            if (typeof arr === 'object' && arr !== null) return Object.keys(arr).length;
            return 0;
        });
    }
}

/**
 * Compile template for reuse
 */
class CompiledTemplate {
    constructor(template, engine) {
        this.template = template;
        this.engine = engine;
    }
    
    render(data) {
        return this.engine.render(this.template, data);
    }
}

/**
 * TemplateLoader - Load and cache templates
 */
class TemplateLoader {
    constructor(engine) {
        this.engine = engine || new TemplateEngine();
        this.cache = new Map();
    }
    
    /**
     * Load template from script tag
     * @param {string} id - Script tag ID
     * @returns {CompiledTemplate} Compiled template
     */
    fromScript(id) {
        if (this.cache.has(id)) {
            return this.cache.get(id);
        }
        
        const scriptEl = document.getElementById(id);
        if (!scriptEl) {
            throw new Error(`Template script not found: ${id}`);
        }
        
        const template = new CompiledTemplate(scriptEl.innerHTML, this.engine);
        this.cache.set(id, template);
        
        return template;
    }
    
    /**
     * Load template from URL
     * @param {string} url - Template URL
     * @returns {Promise<CompiledTemplate>} Compiled template
     */
    async fromUrl(url) {
        if (this.cache.has(url)) {
            return this.cache.get(url);
        }
        
        const response = await fetch(url);
        const text = await response.text();
        
        const template = new CompiledTemplate(text, this.engine);
        this.cache.set(url, template);
        
        return template;
    }
    
    /**
     * Compile template from string
     * @param {string} templateStr - Template string
     * @param {string} [cacheKey] - Optional cache key
     * @returns {CompiledTemplate} Compiled template
     */
    fromString(templateStr, cacheKey = null) {
        if (cacheKey && this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        const template = new CompiledTemplate(templateStr, this.engine);
        
        if (cacheKey) {
            this.cache.set(cacheKey, template);
        }
        
        return template;
    }
    
    /**
     * Clear template cache
     */
    clearCache() {
        this.cache.clear();
    }
}

export { TemplateEngine, CompiledTemplate, TemplateLoader };
export default TemplateEngine;
