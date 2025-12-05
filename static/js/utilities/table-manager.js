/**
 * TableManager - CRUD operations manager for data tables
 * 
 * Features:
 * - Sortable columns
 * - Filterable data
 * - Row selection (single/multiple)
 * - Inline editing
 * - Pagination
 * - Custom cell renderers
 * - Row actions
 * 
 * @module TableManager
 * @version 1.0.0
 */

class TableManager {
    constructor(containerElement, options = {}) {
        this.container = typeof containerElement === 'string' 
            ? document.querySelector(containerElement)
            : containerElement;
            
        this.options = {
            columns: options.columns || [],
            data: options.data || [],
            selectable: options.selectable || false,
            selectMode: options.selectMode || 'multiple', // 'single' or 'multiple'
            editable: options.editable || false,
            paginate: options.paginate || false,
            pageSize: options.pageSize || 10,
            sortable: options.sortable !== false,
            filterable: options.filterable || false,
            emptyMessage: options.emptyMessage || 'No data available',
            rowClass: options.rowClass || null,
            onRowClick: options.onRowClick || null,
            onRowEdit: options.onRowEdit || null,
            onRowDelete: options.onRowDelete || null,
            onRowSelect: options.onRowSelect || null,
            onSort: options.onSort || null,
            ...options
        };
        
        this.state = {
            data: [...this.options.data],
            filteredData: [],
            displayData: [],
            selectedRows: new Set(),
            sortColumn: null,
            sortDirection: 'asc',
            currentPage: 1,
            searchQuery: '',
            editingRow: null
        };
        
        this.init();
    }
    
    /**
     * Initialize table
     */
    init() {
        this.filterData();
        this.sortData();
        this.paginateData();
        this.render();
    }
    
    /**
     * Set table data
     * @param {Array} data - Array of row objects
     */
    setData(data) {
        this.state.data = [...data];
        this.state.selectedRows.clear();
        this.state.currentPage = 1;
        this.refresh();
    }
    
    /**
     * Get current data
     * @returns {Array} Current data array
     */
    getData() {
        return [...this.state.data];
    }
    
    /**
     * Add row to table
     * @param {Object} row - Row data object
     */
    addRow(row) {
        this.state.data.push(row);
        this.refresh();
    }
    
    /**
     * Update row in table
     * @param {number} index - Row index
     * @param {Object} row - Updated row data
     */
    updateRow(index, row) {
        if (index >= 0 && index < this.state.data.length) {
            this.state.data[index] = { ...this.state.data[index], ...row };
            this.refresh();
        }
    }
    
    /**
     * Delete row from table
     * @param {number} index - Row index
     */
    deleteRow(index) {
        if (index >= 0 && index < this.state.data.length) {
            const row = this.state.data[index];
            
            if (this.options.onRowDelete) {
                this.options.onRowDelete(row, index);
            }
            
            this.state.data.splice(index, 1);
            this.state.selectedRows.delete(index);
            this.refresh();
        }
    }
    
    /**
     * Get selected rows
     * @returns {Array} Selected row data
     */
    getSelected() {
        return Array.from(this.state.selectedRows).map(index => this.state.data[index]);
    }
    
    /**
     * Clear selection
     */
    clearSelection() {
        this.state.selectedRows.clear();
        this.refresh();
    }
    
    /**
     * Select row(s)
     * @param {number|Array} indices - Row index or array of indices
     */
    selectRows(indices) {
        const indexArray = Array.isArray(indices) ? indices : [indices];
        
        if (this.options.selectMode === 'single') {
            this.state.selectedRows.clear();
            if (indexArray.length > 0) {
                this.state.selectedRows.add(indexArray[0]);
            }
        } else {
            indexArray.forEach(index => this.state.selectedRows.add(index));
        }
        
        this.refresh();
        
        if (this.options.onRowSelect) {
            this.options.onRowSelect(this.getSelected());
        }
    }
    
    /**
     * Filter data by search query
     * @param {string} query - Search query
     */
    search(query) {
        this.state.searchQuery = query.toLowerCase();
        this.state.currentPage = 1;
        this.refresh();
    }
    
    /**
     * Sort data by column
     * @param {string} columnKey - Column key to sort by
     */
    sort(columnKey) {
        if (this.state.sortColumn === columnKey) {
            // Toggle direction
            this.state.sortDirection = this.state.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.state.sortColumn = columnKey;
            this.state.sortDirection = 'asc';
        }
        
        this.refresh();
        
        if (this.options.onSort) {
            this.options.onSort(columnKey, this.state.sortDirection);
        }
    }
    
    /**
     * Go to specific page
     * @param {number} page - Page number (1-indexed)
     */
    goToPage(page) {
        const totalPages = this.getTotalPages();
        if (page >= 1 && page <= totalPages) {
            this.state.currentPage = page;
            this.paginateData();
            this.render();
        }
    }
    
    /**
     * Get total number of pages
     * @returns {number} Total pages
     */
    getTotalPages() {
        if (!this.options.paginate) return 1;
        return Math.ceil(this.state.filteredData.length / this.options.pageSize);
    }
    
    /**
     * Refresh table (refilter, resort, repaginate, rerender)
     */
    refresh() {
        this.filterData();
        this.sortData();
        this.paginateData();
        this.render();
    }
    
    /**
     * Filter data based on search query
     * @private
     */
    filterData() {
        const { searchQuery } = this.state;
        
        if (!searchQuery) {
            this.state.filteredData = [...this.state.data];
            return;
        }
        
        this.state.filteredData = this.state.data.filter(row => {
            return this.options.columns.some(col => {
                const value = row[col.key];
                if (value === null || value === undefined) return false;
                return String(value).toLowerCase().includes(searchQuery);
            });
        });
    }
    
    /**
     * Sort filtered data
     * @private
     */
    sortData() {
        const { sortColumn, sortDirection } = this.state;
        
        if (!sortColumn) return;
        
        const column = this.options.columns.find(col => col.key === sortColumn);
        if (!column) return;
        
        this.state.filteredData.sort((a, b) => {
            let aVal = a[sortColumn];
            let bVal = b[sortColumn];
            
            // Custom sort function
            if (column.sort && typeof column.sort === 'function') {
                return column.sort(a, b, sortDirection);
            }
            
            // Handle null/undefined
            if (aVal === null || aVal === undefined) aVal = '';
            if (bVal === null || bVal === undefined) bVal = '';
            
            // Numeric sort
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
            }
            
            // String sort
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
            
            if (sortDirection === 'asc') {
                return aVal.localeCompare(bVal);
            } else {
                return bVal.localeCompare(aVal);
            }
        });
    }
    
    /**
     * Paginate sorted data
     * @private
     */
    paginateData() {
        if (!this.options.paginate) {
            this.state.displayData = [...this.state.filteredData];
            return;
        }
        
        const start = (this.state.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        this.state.displayData = this.state.filteredData.slice(start, end);
    }
    
    /**
     * Render table HTML
     * @private
     */
    render() {
        if (!this.container) return;
        
        const html = `
            <div class="table-wrapper">
                ${this.renderSearchBar()}
                <table class="table table-hover">
                    ${this.renderHeader()}
                    ${this.renderBody()}
                </table>
                ${this.renderPagination()}
            </div>
        `;
        
        this.container.innerHTML = html;
        this.attachEventListeners();
    }
    
    /**
     * Render search bar
     * @private
     */
    renderSearchBar() {
        if (!this.options.filterable) return '';
        
        return `
            <div class="table-search mb-3">
                <input type="search" 
                       class="form-control" 
                       placeholder="Search..." 
                       value="${this.state.searchQuery}"
                       data-table-search>
            </div>
        `;
    }
    
    /**
     * Render table header
     * @private
     */
    renderHeader() {
        const selectCell = this.options.selectable 
            ? '<th><input type="checkbox" data-select-all></th>' 
            : '';
        
        const cells = this.options.columns.map(col => {
            const sortable = col.sortable !== false && this.options.sortable;
            const isSorted = this.state.sortColumn === col.key;
            const sortIcon = isSorted 
                ? (this.state.sortDirection === 'asc' ? '↑' : '↓')
                : '';
            const sortClass = sortable ? 'sortable' : '';
            
            return `
                <th class="${sortClass}" 
                    ${sortable ? `data-sort="${col.key}"` : ''}>
                    ${col.label}
                    ${sortIcon ? `<span class="sort-icon">${sortIcon}</span>` : ''}
                </th>
            `;
        }).join('');
        
        const actionsCell = (this.options.editable || this.options.onRowDelete) 
            ? '<th>Actions</th>' 
            : '';
        
        return `
            <thead>
                <tr>
                    ${selectCell}
                    ${cells}
                    ${actionsCell}
                </tr>
            </thead>
        `;
    }
    
    /**
     * Render table body
     * @private
     */
    renderBody() {
        if (this.state.displayData.length === 0) {
            const colSpan = this.options.columns.length + 
                           (this.options.selectable ? 1 : 0) +
                           (this.options.editable || this.options.onRowDelete ? 1 : 0);
            
            return `
                <tbody>
                    <tr>
                        <td colspan="${colSpan}" class="text-center text-muted py-4">
                            ${this.options.emptyMessage}
                        </td>
                    </tr>
                </tbody>
            `;
        }
        
        const rows = this.state.displayData.map((row, index) => {
            const dataIndex = this.state.filteredData.indexOf(row);
            const isSelected = this.state.selectedRows.has(dataIndex);
            const isEditing = this.state.editingRow === dataIndex;
            const rowClass = this.options.rowClass ? this.options.rowClass(row) : '';
            
            return this.renderRow(row, dataIndex, isSelected, isEditing, rowClass);
        }).join('');
        
        return `<tbody>${rows}</tbody>`;
    }
    
    /**
     * Render single row
     * @private
     */
    renderRow(row, index, isSelected, isEditing, rowClass) {
        const selectCell = this.options.selectable 
            ? `<td><input type="checkbox" ${isSelected ? 'checked' : ''} data-select-row="${index}"></td>`
            : '';
        
        const cells = this.options.columns.map(col => {
            const value = row[col.key];
            
            if (isEditing && col.editable !== false) {
                return `<td>${this.renderEditCell(col, value, index)}</td>`;
            }
            
            const rendered = col.render 
                ? col.render(value, row, index)
                : this.escapeHtml(value);
            
            return `<td>${rendered}</td>`;
        }).join('');
        
        const actionsCell = (this.options.editable || this.options.onRowDelete)
            ? `<td>${this.renderActions(index, isEditing)}</td>`
            : '';
        
        return `
            <tr class="${rowClass} ${isSelected ? 'table-active' : ''}" 
                data-row-index="${index}">
                ${selectCell}
                ${cells}
                ${actionsCell}
            </tr>
        `;
    }
    
    /**
     * Render edit cell
     * @private
     */
    renderEditCell(col, value, index) {
        const escapedValue = this.escapeHtml(value);
        
        if (col.editType === 'select' && col.editOptions) {
            const options = col.editOptions.map(opt => 
                `<option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>${opt.label}</option>`
            ).join('');
            
            return `<select class="form-control form-control-sm" data-edit-field="${col.key}">${options}</select>`;
        }
        
        return `<input type="${col.editType || 'text'}" 
                       class="form-control form-control-sm" 
                       value="${escapedValue}"
                       data-edit-field="${col.key}">`;
    }
    
    /**
     * Render row actions
     * @private
     */
    renderActions(index, isEditing) {
        if (isEditing) {
            return `
                <button class="btn btn-sm btn-success" data-save-row="${index}">
                    <i class="bi bi-check"></i>
                </button>
                <button class="btn btn-sm btn-secondary" data-cancel-edit="${index}">
                    <i class="bi bi-x"></i>
                </button>
            `;
        }
        
        const editBtn = this.options.editable
            ? `<button class="btn btn-sm btn-outline-primary" data-edit-row="${index}">
                   <i class="bi bi-pencil"></i>
               </button>`
            : '';
        
        const deleteBtn = this.options.onRowDelete
            ? `<button class="btn btn-sm btn-outline-danger" data-delete-row="${index}">
                   <i class="bi bi-trash"></i>
               </button>`
            : '';
        
        return `${editBtn} ${deleteBtn}`;
    }
    
    /**
     * Render pagination
     * @private
     */
    renderPagination() {
        if (!this.options.paginate) return '';
        
        const totalPages = this.getTotalPages();
        if (totalPages <= 1) return '';
        
        const { currentPage } = this.state;
        const pages = [];
        
        // Previous button
        pages.push(`
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
            </li>
        `);
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                pages.push(`
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `);
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                pages.push('<li class="page-item disabled"><span class="page-link">...</span></li>');
            }
        }
        
        // Next button
        pages.push(`
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
            </li>
        `);
        
        return `
            <nav class="mt-3">
                <ul class="pagination justify-content-center">
                    ${pages.join('')}
                </ul>
            </nav>
        `;
    }
    
    /**
     * Attach event listeners to rendered elements
     * @private
     */
    attachEventListeners() {
        // Search
        const searchInput = this.container.querySelector('[data-table-search]');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.search(e.target.value);
            });
        }
        
        // Sort
        this.container.querySelectorAll('[data-sort]').forEach(th => {
            th.addEventListener('click', () => {
                this.sort(th.dataset.sort);
            });
        });
        
        // Select all
        const selectAll = this.container.querySelector('[data-select-all]');
        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                if (e.target.checked) {
                    const allIndices = this.state.displayData.map((row, i) => 
                        this.state.filteredData.indexOf(row)
                    );
                    this.selectRows(allIndices);
                } else {
                    this.clearSelection();
                }
            });
        }
        
        // Select row
        this.container.querySelectorAll('[data-select-row]').forEach(cb => {
            cb.addEventListener('change', (e) => {
                const index = parseInt(cb.dataset.selectRow);
                if (e.target.checked) {
                    this.selectRows(index);
                } else {
                    this.state.selectedRows.delete(index);
                    this.refresh();
                }
            });
        });
        
        // Row click
        if (this.options.onRowClick) {
            this.container.querySelectorAll('[data-row-index]').forEach(tr => {
                tr.addEventListener('click', (e) => {
                    // Don't trigger on checkbox/button clicks
                    if (e.target.matches('input, button, a, [data-select-row]')) return;
                    
                    const index = parseInt(tr.dataset.rowIndex);
                    const row = this.state.filteredData[index];
                    this.options.onRowClick(row, index, e);
                });
            });
        }
        
        // Edit row
        this.container.querySelectorAll('[data-edit-row]').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.editRow);
                this.state.editingRow = index;
                this.render();
            });
        });
        
        // Save row
        this.container.querySelectorAll('[data-save-row]').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.saveRow);
                const row = this.state.filteredData[index];
                const tr = btn.closest('tr');
                
                const updatedData = {};
                tr.querySelectorAll('[data-edit-field]').forEach(input => {
                    updatedData[input.dataset.editField] = input.value;
                });
                
                this.updateRow(index, updatedData);
                this.state.editingRow = null;
                
                if (this.options.onRowEdit) {
                    this.options.onRowEdit({ ...row, ...updatedData }, index);
                }
            });
        });
        
        // Cancel edit
        this.container.querySelectorAll('[data-cancel-edit]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.state.editingRow = null;
                this.render();
            });
        });
        
        // Delete row
        this.container.querySelectorAll('[data-delete-row]').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.deleteRow);
                this.deleteRow(index);
            });
        });
        
        // Pagination
        this.container.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(link.dataset.page);
                this.goToPage(page);
            });
        });
    }
    
    /**
     * Escape HTML to prevent XSS
     * @private
     */
    escapeHtml(value) {
        if (value === null || value === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(value);
        return div.innerHTML;
    }
}

export default TableManager;
