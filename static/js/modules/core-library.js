/**
 * Core Library - Foundation for all modules
 * Provides utilities, state management, and event system
 */

// ===== STATE MANAGEMENT =====
export const Store = (() => {
    const state = new Map();
    const subscribers = new Map();

    return {
        /**
         * Get state value
         */
        get(key, defaultValue = null) {
            return state.has(key) ? state.get(key) : defaultValue;
        },

        /**
         * Set state value and notify subscribers
         */
        set(key, value) {
            const oldValue = state.get(key);
            if (oldValue === value) return; // No change

            state.set(key, value);
            
            if (subscribers.has(key)) {
                subscribers.get(key).forEach(callback => {
                    try {
                        callback(value, oldValue);
                    } catch (e) {
                        console.error(`Error in state subscriber for "${key}":`, e);
                    }
                });
            }
        },

        /**
         * Subscribe to state changes
         */
        subscribe(key, callback) {
            if (!subscribers.has(key)) {
                subscribers.set(key, new Set());
            }
            subscribers.get(key).add(callback);

            // Return unsubscribe function
            return () => {
                subscribers.get(key).delete(callback);
            };
        },

        /**
         * Get all state
         */
        getAll() {
            return Object.fromEntries(state);
        },

        /**
         * Clear state
         */
        clear() {
            state.clear();
            subscribers.clear();
        }
    };
})();

// ===== EVENT SYSTEM =====
export const EventBus = (() => {
    const listeners = new Map();

    return {
        /**
         * Emit an event
         */
        emit(eventName, data = null) {
            if (!listeners.has(eventName)) return;

            listeners.get(eventName).forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error(`Error in event listener for "${eventName}":`, e);
                }
            });
        },

        /**
         * Listen to an event
         */
        on(eventName, callback) {
            if (!listeners.has(eventName)) {
                listeners.set(eventName, new Set());
            }
            listeners.get(eventName).add(callback);

            // Return unsubscribe function
            return () => {
                listeners.get(eventName).delete(callback);
            };
        },

        /**
         * Listen to event once
         */
        once(eventName, callback) {
            const unsubscribe = this.on(eventName, (data) => {
                unsubscribe();
                callback(data);
            });
            return unsubscribe;
        },

        /**
         * Remove all listeners for an event
         */
        off(eventName) {
            listeners.delete(eventName);
        },

        /**
         * Clear all listeners
         */
        clear() {
            listeners.clear();
        }
    };
})();

// ===== HTTP/FETCH UTILITIES =====
export const API = (() => {
    /**
     * Get auth headers from cookies
     */
    function getAuthHeaders() {
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
     * Make HTTP request
     */
    async function request(url, options = {}) {
        const {
            method = 'GET',
            data = null,
            headers = {},
            credentials = 'include'
        } = options;

        const config = {
            method,
            credentials,
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
                ...headers
            }
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType?.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    return {
        get: (url, options) => request(url, { ...options, method: 'GET' }),
        post: (url, data, options) => request(url, { ...options, method: 'POST', data }),
        put: (url, data, options) => request(url, { ...options, method: 'PUT', data }),
        delete: (url, options) => request(url, { ...options, method: 'DELETE' }),
        request
    };
})();

// ===== UI UTILITIES =====
export const UI = (() => {
    /**
     * Show notification
     */
    function notify(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notification-container') || createNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="bi ${getNotificationIcon(type)}"></i>
                <div class="notification-message">${escapeHtml(message)}</div>
            </div>
        `;

        container.appendChild(notification);

        if (duration > 0) {
            setTimeout(() => {
                notification.classList.add('notification-hide');
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }

        return {
            close() {
                notification.classList.add('notification-hide');
                setTimeout(() => notification.remove(), 300);
            }
        };
    }

    /**
     * Create notification container if it doesn't exist
     */
    function createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Get icon for notification type
     */
    function getNotificationIcon(type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        return icons[type] || icons.info;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Toggle loading state
     */
    function setLoading(element, isLoading) {
        if (isLoading) {
            element.classList.add('is-loading');
            element.disabled = true;
        } else {
            element.classList.remove('is-loading');
            element.disabled = false;
        }
    }

    /**
     * Confirm dialog
     */
    function confirm(message, title = 'Confirm') {
        return new Promise(resolve => {
            if (window.confirm(`${title}\n\n${message}`)) {
                resolve(true);
            } else {
                resolve(false);
            }
        });
    }

    return {
        notify,
        success: (msg, duration) => notify(msg, 'success', duration),
        error: (msg, duration) => notify(msg, 'error', duration),
        warning: (msg, duration) => notify(msg, 'warning', duration),
        info: (msg, duration) => notify(msg, 'info', duration),
        setLoading,
        confirm
    };
})();

// ===== THEME UTILITIES =====
export const Theme = (() => {
    let themeSystem = null;

    /**
     * Initialize theme utilities
     */
    function init() {
        // Wait for theme system to be available
        return new Promise(resolve => {
            const waitInterval = setInterval(() => {
                if (typeof window.ThemeSystem !== 'undefined') {
                    clearInterval(waitInterval);
                    themeSystem = window.ThemeSystem;
                    resolve();
                }
            }, 100);

            // Timeout after 5 seconds
            setTimeout(() => {
                clearInterval(waitInterval);
                resolve();
            }, 5000);
        });
    }

    return {
        init,
        toggle: () => themeSystem?.toggleTheme(),
        apply: (theme) => themeSystem?.applyTheme(theme),
        getCurrent: () => themeSystem?.getCurrentTheme() || 'light',
        getSaved: () => themeSystem?.getSavedTheme() || 'light',
        applyCustom: (customTheme) => themeSystem?.applyCustomTheme(customTheme),
        reset: () => themeSystem?.resetTheme()
    };
})();

// ===== DOM UTILITIES =====
export const DOM = (() => {
    return {
        /**
         * Query selector
         */
        query: (selector, context = document) => {
            return context.querySelector(selector);
        },

        /**
         * Query selector all
         */
        queryAll: (selector, context = document) => {
            return Array.from(context.querySelectorAll(selector));
        },

        /**
         * Create element
         */
        create(tag, options = {}) {
            const element = document.createElement(tag);
            
            if (options.className) {
                element.className = options.className;
            }
            
            if (options.id) {
                element.id = options.id;
            }
            
            if (options.html) {
                element.innerHTML = options.html;
            }
            
            if (options.text) {
                element.textContent = options.text;
            }
            
            if (options.attributes) {
                Object.entries(options.attributes).forEach(([key, value]) => {
                    element.setAttribute(key, value);
                });
            }
            
            if (options.styles) {
                Object.assign(element.style, options.styles);
            }

            if (options.parent) {
                options.parent.appendChild(element);
            }

            return element;
        },

        /**
         * Remove element
         */
        remove(element) {
            element?.remove();
        },

        /**
         * Add class
         */
        addClass(element, className) {
            element.classList.add(className);
        },

        /**
         * Remove class
         */
        removeClass(element, className) {
            element.classList.remove(className);
        },

        /**
         * Toggle class
         */
        toggleClass(element, className) {
            element.classList.toggle(className);
        },

        /**
         * Has class
         */
        hasClass(element, className) {
            return element.classList.contains(className);
        }
    };
})();

// ===== UTILITIES =====
export const Utils = (() => {
    return {
        /**
         * Debounce function
         */
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Throttle function
         */
        throttle(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        /**
         * Deep clone object
         */
        clone(obj) {
            return JSON.parse(JSON.stringify(obj));
        },

        /**
         * Merge objects
         */
        merge(target, source) {
            return { ...target, ...source };
        },

        /**
         * Format file size
         */
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        },

        /**
         * Format date
         */
        formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
            const d = new Date(date);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            const hours = String(d.getHours()).padStart(2, '0');
            const minutes = String(d.getMinutes()).padStart(2, '0');
            const seconds = String(d.getSeconds()).padStart(2, '0');

            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day)
                .replace('HH', hours)
                .replace('mm', minutes)
                .replace('ss', seconds);
        },

        /**
         * Wait for condition
         */
        waitFor(condition, timeout = 10000, interval = 100) {
            return new Promise((resolve, reject) => {
                const checkInterval = setInterval(() => {
                    if (condition()) {
                        clearInterval(checkInterval);
                        clearTimeout(timeoutHandle);
                        resolve();
                    }
                }, interval);

                const timeoutHandle = setTimeout(() => {
                    clearInterval(checkInterval);
                    reject(new Error('Wait condition timeout'));
                }, timeout);
            });
        }
    };
})();
