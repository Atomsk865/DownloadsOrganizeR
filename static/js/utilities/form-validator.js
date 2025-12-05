/**
 * FormValidator - Validation rules engine for config forms
 * 
 * Features:
 * - Real-time validation
 * - Custom validation rules
 * - Error message templating
 * - Field-level and form-level validation
 * - Async validation support
 * 
 * @module FormValidator
 * @version 1.0.0
 */

class FormValidator {
    constructor(options = {}) {
        this.rules = new Map();
        this.errors = new Map();
        this.customValidators = new Map();
        this.options = {
            showErrorsImmediately: options.showErrorsImmediately !== false,
            errorClass: options.errorClass || 'is-invalid',
            errorMessageClass: options.errorMessageClass || 'invalid-feedback',
            validClass: options.validClass || 'is-valid',
            ...options
        };
        
        // Register built-in validators
        this.registerBuiltInValidators();
    }
    
    /**
     * Add validation rule for a field
     * @param {string} fieldName - Field identifier
     * @param {Object} rule - Validation rule configuration
     */
    addRule(fieldName, rule) {
        if (!this.rules.has(fieldName)) {
            this.rules.set(fieldName, []);
        }
        this.rules.get(fieldName).push(rule);
    }
    
    /**
     * Register custom validator function
     * @param {string} name - Validator name
     * @param {Function} validator - Validator function
     */
    registerValidator(name, validator) {
        this.customValidators.set(name, validator);
    }
    
    /**
     * Validate single field
     * @param {string} fieldName - Field identifier
     * @param {any} value - Field value
     * @returns {Object} Validation result { valid: boolean, errors: string[] }
     */
    async validateField(fieldName, value) {
        const rules = this.rules.get(fieldName);
        if (!rules) {
            return { valid: true, errors: [] };
        }
        
        const errors = [];
        
        for (const rule of rules) {
            const result = await this.executeRule(rule, value, fieldName);
            if (!result.valid) {
                errors.push(result.message);
                if (rule.stopOnError) break;
            }
        }
        
        if (errors.length > 0) {
            this.errors.set(fieldName, errors);
            return { valid: false, errors };
        } else {
            this.errors.delete(fieldName);
            return { valid: true, errors: [] };
        }
    }
    
    /**
     * Validate entire form data
     * @param {Object} data - Form data object
     * @returns {Object} Validation result { valid: boolean, errors: Object }
     */
    async validate(data) {
        this.errors.clear();
        
        const validationPromises = [];
        
        for (const [fieldName, value] of Object.entries(data)) {
            validationPromises.push(
                this.validateField(fieldName, value)
            );
        }
        
        await Promise.all(validationPromises);
        
        const isValid = this.errors.size === 0;
        const errorObject = {};
        
        for (const [field, errors] of this.errors.entries()) {
            errorObject[field] = errors;
        }
        
        return {
            valid: isValid,
            errors: errorObject
        };
    }
    
    /**
     * Execute validation rule
     * @private
     */
    async executeRule(rule, value, fieldName) {
        const validator = this.getValidator(rule.type);
        
        if (!validator) {
            console.warn(`Unknown validator type: ${rule.type}`);
            return { valid: true };
        }
        
        const isValid = await validator(value, rule, fieldName);
        
        return {
            valid: isValid,
            message: isValid ? '' : this.formatMessage(rule.message, rule, value, fieldName)
        };
    }
    
    /**
     * Get validator function by type
     * @private
     */
    getValidator(type) {
        // Check custom validators first
        if (this.customValidators.has(type)) {
            return this.customValidators.get(type);
        }
        
        // Check built-in validators
        const methodName = `validate${type.charAt(0).toUpperCase()}${type.slice(1)}`;
        if (typeof this[methodName] === 'function') {
            return this[methodName].bind(this);
        }
        
        return null;
    }
    
    /**
     * Format error message with placeholders
     * @private
     */
    formatMessage(template, rule, value, fieldName) {
        if (!template) {
            return `Validation failed for ${fieldName}`;
        }
        
        return template
            .replace('{field}', fieldName)
            .replace('{value}', value)
            .replace('{min}', rule.min)
            .replace('{max}', rule.max)
            .replace('{length}', rule.length)
            .replace('{pattern}', rule.pattern);
    }
    
    /**
     * Get all validation errors
     * @returns {Object} Error object
     */
    getErrors() {
        const errorObject = {};
        for (const [field, errors] of this.errors.entries()) {
            errorObject[field] = errors;
        }
        return errorObject;
    }
    
    /**
     * Clear all errors
     */
    clearErrors() {
        this.errors.clear();
    }
    
    /**
     * Clear errors for specific field
     * @param {string} fieldName - Field identifier
     */
    clearFieldErrors(fieldName) {
        this.errors.delete(fieldName);
    }
    
    /**
     * Check if form has any errors
     * @returns {boolean}
     */
    hasErrors() {
        return this.errors.size > 0;
    }
    
    // ==================== Built-in Validators ====================
    
    registerBuiltInValidators() {
        // Required validator
        this.customValidators.set('required', (value) => {
            if (typeof value === 'string') {
                return value.trim().length > 0;
            }
            return value !== null && value !== undefined && value !== '';
        });
        
        // Custom function validator
        this.customValidators.set('custom', async (value, rule) => {
            if (typeof rule.validator === 'function') {
                return await rule.validator(value, rule);
            }
            return true;
        });
    }
    
    /**
     * Validate minimum length
     */
    validateMinLength(value, rule) {
        if (!value) return true; // Allow empty unless required
        return String(value).length >= rule.min;
    }
    
    /**
     * Validate maximum length
     */
    validateMaxLength(value, rule) {
        if (!value) return true;
        return String(value).length <= rule.max;
    }
    
    /**
     * Validate exact length
     */
    validateLength(value, rule) {
        if (!value) return true;
        return String(value).length === rule.length;
    }
    
    /**
     * Validate pattern (regex)
     */
    validatePattern(value, rule) {
        if (!value) return true;
        const regex = rule.pattern instanceof RegExp ? rule.pattern : new RegExp(rule.pattern);
        return regex.test(String(value));
    }
    
    /**
     * Validate email format
     */
    validateEmail(value) {
        if (!value) return true;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(String(value));
    }
    
    /**
     * Validate URL format
     */
    validateUrl(value) {
        if (!value) return true;
        try {
            new URL(String(value));
            return true;
        } catch {
            return false;
        }
    }
    
    /**
     * Validate numeric value
     */
    validateNumeric(value) {
        if (!value) return true;
        return !isNaN(Number(value));
    }
    
    /**
     * Validate integer value
     */
    validateInteger(value) {
        if (!value) return true;
        return Number.isInteger(Number(value));
    }
    
    /**
     * Validate minimum value
     */
    validateMin(value, rule) {
        if (!value) return true;
        return Number(value) >= rule.min;
    }
    
    /**
     * Validate maximum value
     */
    validateMax(value, rule) {
        if (!value) return true;
        return Number(value) <= rule.max;
    }
    
    /**
     * Validate value is in allowed list
     */
    validateIn(value, rule) {
        if (!value) return true;
        return rule.values.includes(value);
    }
    
    /**
     * Validate value is NOT in disallowed list
     */
    validateNotIn(value, rule) {
        if (!value) return true;
        return !rule.values.includes(value);
    }
    
    /**
     * Validate IP address (IPv4)
     */
    validateIpv4(value) {
        if (!value) return true;
        const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
        if (!ipv4Regex.test(value)) return false;
        
        const parts = value.split('.');
        return parts.every(part => {
            const num = parseInt(part, 10);
            return num >= 0 && num <= 255;
        });
    }
    
    /**
     * Validate port number
     */
    validatePort(value) {
        if (!value) return true;
        const num = Number(value);
        return Number.isInteger(num) && num >= 1 && num <= 65535;
    }
    
    /**
     * Validate UNC path
     */
    validateUncPath(value) {
        if (!value) return true;
        const uncRegex = /^\\\\[^\\/]+\\[^\\/]+/;
        return uncRegex.test(String(value));
    }
    
    /**
     * Validate file path (Windows or Unix)
     */
    validatePath(value) {
        if (!value) return true;
        const windowsPath = /^[a-zA-Z]:[\\\/]/ || /^\\\\/;
        const unixPath = /^\//;
        return windowsPath.test(value) || unixPath.test(value);
    }
    
    /**
     * Validate alphanumeric (letters and numbers only)
     */
    validateAlphanumeric(value) {
        if (!value) return true;
        return /^[a-zA-Z0-9]+$/.test(String(value));
    }
    
    /**
     * Validate username format
     */
    validateUsername(value) {
        if (!value) return true;
        // Allow letters, numbers, underscore, hyphen, dot
        return /^[a-zA-Z0-9._-]+$/.test(String(value));
    }
    
    /**
     * Validate password strength
     */
    validatePassword(value, rule) {
        if (!value) return true;
        
        const strength = rule.strength || 'medium';
        const str = String(value);
        
        if (strength === 'weak') {
            return str.length >= 6;
        }
        
        if (strength === 'medium') {
            // At least 8 chars, 1 letter, 1 number
            return str.length >= 8 && /[a-zA-Z]/.test(str) && /\d/.test(str);
        }
        
        if (strength === 'strong') {
            // At least 12 chars, 1 uppercase, 1 lowercase, 1 number, 1 special
            return str.length >= 12 &&
                   /[a-z]/.test(str) &&
                   /[A-Z]/.test(str) &&
                   /\d/.test(str) &&
                   /[^a-zA-Z0-9]/.test(str);
        }
        
        return true;
    }
}

/**
 * FormValidatorUI - Helper class for UI integration
 */
class FormValidatorUI {
    constructor(validator, formElement) {
        this.validator = validator;
        this.form = formElement;
        this.boundFields = new Map();
    }
    
    /**
     * Bind validator to form field with real-time validation
     * @param {string} fieldName - Field identifier
     * @param {HTMLElement} inputElement - Input element
     * @param {Object} options - Binding options
     */
    bindField(fieldName, inputElement, options = {}) {
        const {
            validateOn = ['blur', 'input'],
            debounce = 300,
            showSuccess = true
        } = options;
        
        this.boundFields.set(fieldName, { inputElement, options });
        
        let debounceTimer;
        
        const validateHandler = async () => {
            clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(async () => {
                const value = inputElement.value;
                const result = await this.validator.validateField(fieldName, value);
                
                this.updateFieldUI(inputElement, result, showSuccess);
            }, debounce);
        };
        
        validateOn.forEach(event => {
            inputElement.addEventListener(event, validateHandler);
        });
    }
    
    /**
     * Update field UI based on validation result
     * @private
     */
    updateFieldUI(inputElement, result, showSuccess) {
        const { errorClass, validClass, errorMessageClass } = this.validator.options;
        
        // Remove existing classes
        inputElement.classList.remove(errorClass, validClass);
        
        // Remove existing error messages
        const existingError = inputElement.parentElement.querySelector(`.${errorMessageClass}`);
        if (existingError) {
            existingError.remove();
        }
        
        if (!result.valid) {
            // Add error class
            inputElement.classList.add(errorClass);
            
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = errorMessageClass;
            errorDiv.textContent = result.errors[0]; // Show first error
            inputElement.parentElement.appendChild(errorDiv);
        } else if (showSuccess && inputElement.value) {
            // Add success class
            inputElement.classList.add(validClass);
        }
    }
    
    /**
     * Validate entire form and show all errors
     * @returns {Object} Validation result
     */
    async validateForm() {
        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData.entries());
        
        const result = await this.validator.validate(data);
        
        // Update UI for all bound fields
        for (const [fieldName, { inputElement, options }] of this.boundFields.entries()) {
            const fieldResult = {
                valid: !result.errors[fieldName],
                errors: result.errors[fieldName] || []
            };
            
            this.updateFieldUI(inputElement, fieldResult, options.showSuccess);
        }
        
        return result;
    }
    
    /**
     * Clear all error displays
     */
    clearErrors() {
        const { errorClass, validClass, errorMessageClass } = this.validator.options;
        
        for (const { inputElement } of this.boundFields.values()) {
            inputElement.classList.remove(errorClass, validClass);
            
            const errorDiv = inputElement.parentElement.querySelector(`.${errorMessageClass}`);
            if (errorDiv) {
                errorDiv.remove();
            }
        }
        
        this.validator.clearErrors();
    }
}

export { FormValidator, FormValidatorUI };
export default FormValidator;
