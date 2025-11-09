/**
 * Category Filter Component
 *
 * Handles multi-select category filtering with:
 * - Loading category configuration from API
 * - Loading document statistics per category
 * - Multi-select chip interface
 * - Select All / Clear All functionality
 * - Returns selected categories for query filtering
 */

class CategoryFilter {
    constructor() {
        this.categories = [];
        this.stats = {};
        this.selectedCategories = new Set();
        this.initialized = false;
    }

    /**
     * Initialize the category filter component
     */
    async init() {
        if (this.initialized) {
            console.log('CategoryFilter already initialized');
            return;
        }

        try {
            // Load categories and stats in parallel
            await Promise.all([
                this.loadCategories(),
                this.loadStats()
            ]);

            // Render the category chips
            this.render();

            // Set up event listeners
            this.setupEventListeners();

            this.initialized = true;
            console.log('CategoryFilter initialized successfully');
        } catch (error) {
            console.error('Failed to initialize CategoryFilter:', error);
            this.showError('Failed to load categories');
        }
    }

    /**
     * Load category configuration from API
     */
    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            const data = await response.json();

            if (data.success) {
                this.categories = data.categories;
                console.log(`Loaded ${this.categories.length} categories`);
            } else {
                throw new Error(data.error || 'Failed to load categories');
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            throw error;
        }
    }

    /**
     * Load document statistics per category
     */
    async loadStats() {
        try {
            const response = await fetch('/api/categories/stats');
            const data = await response.json();

            if (data.success) {
                this.stats = data.stats;
                this.totalCount = data.total_count;
                console.log(`Loaded stats for ${Object.keys(this.stats).length} categories`);
            } else {
                throw new Error(data.error || 'Failed to load statistics');
            }
        } catch (error) {
            console.error('Error loading category stats:', error);
            throw error;
        }
    }

    /**
     * Render category chips in the UI
     */
    render() {
        const container = document.getElementById('category-chips-container');
        if (!container) {
            console.error('Category chips container not found');
            return;
        }

        // Clear loading message
        container.innerHTML = '';

        // Sort categories by name
        const sortedCategories = [...this.categories].sort((a, b) =>
            a.name.localeCompare(b.name)
        );

        // Create chips for each category
        sortedCategories.forEach(category => {
            const chip = this.createChip(category);
            container.appendChild(chip);
        });

        // Update summary
        this.updateSummary();
    }

    /**
     * Create a single category chip element
     */
    createChip(category) {
        const chip = document.createElement('div');
        chip.className = 'category-chip';
        chip.dataset.category = category.name;

        const count = this.stats[category.name] || 0;

        chip.innerHTML = `
            <div class="checkbox"></div>
            <div class="category-info">
                <span class="category-icon">${category.icon}</span>
                <div class="category-details">
                    <div class="category-name">${this.formatCategoryName(category.name)}</div>
                    <div class="category-description">${category.description}</div>
                </div>
                <span class="category-count">${count}</span>
            </div>
        `;

        // Add click handler
        chip.addEventListener('click', () => this.toggleCategory(category.name));

        return chip;
    }

    /**
     * Format category name for display (replace underscores, capitalize)
     */
    formatCategoryName(name) {
        return name
            .replace(/_/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    /**
     * Toggle category selection
     */
    toggleCategory(categoryName) {
        const chip = document.querySelector(`.category-chip[data-category="${categoryName}"]`);
        if (!chip) return;

        // Add animation
        chip.classList.add('selecting');
        setTimeout(() => chip.classList.remove('selecting'), 200);

        if (this.selectedCategories.has(categoryName)) {
            this.selectedCategories.delete(categoryName);
            chip.classList.remove('selected');
        } else {
            this.selectedCategories.add(categoryName);
            chip.classList.add('selected');
        }

        this.updateSummary();
        this.onSelectionChange();
    }

    /**
     * Select all categories
     */
    selectAll() {
        this.categories.forEach(category => {
            this.selectedCategories.add(category.name);
            const chip = document.querySelector(`.category-chip[data-category="${category.name}"]`);
            if (chip) {
                chip.classList.add('selected');
            }
        });

        this.updateSummary();
        this.onSelectionChange();
    }

    /**
     * Clear all category selections
     */
    clearAll() {
        this.selectedCategories.clear();

        document.querySelectorAll('.category-chip.selected').forEach(chip => {
            chip.classList.remove('selected');
        });

        this.updateSummary();
        this.onSelectionChange();
    }

    /**
     * Update the summary display
     */
    updateSummary() {
        const selectedCountEl = document.getElementById('selected-count');
        const documentCountEl = document.getElementById('document-count');

        if (selectedCountEl) {
            selectedCountEl.textContent = this.selectedCategories.size;
        }

        if (documentCountEl) {
            const docCount = this.getSelectedDocumentCount();
            documentCountEl.textContent = docCount;
        }
    }

    /**
     * Get total document count for selected categories
     */
    getSelectedDocumentCount() {
        if (this.selectedCategories.size === 0) {
            return this.totalCount || 0;
        }

        let count = 0;
        this.selectedCategories.forEach(categoryName => {
            count += this.stats[categoryName] || 0;
        });

        return count;
    }

    /**
     * Set up event listeners for buttons
     */
    setupEventListeners() {
        const selectAllBtn = document.getElementById('select-all-categories-btn');
        const clearBtn = document.getElementById('clear-categories-btn');

        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => this.selectAll());
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAll());
        }
    }

    /**
     * Get currently selected categories
     * @returns {Array} Array of selected category names
     */
    getSelectedCategories() {
        return Array.from(this.selectedCategories);
    }

    /**
     * Called when selection changes (can be overridden)
     */
    onSelectionChange() {
        // Dispatch custom event for other components to listen to
        const event = new CustomEvent('categorySelectionChanged', {
            detail: {
                selectedCategories: this.getSelectedCategories(),
                documentCount: this.getSelectedDocumentCount()
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Show error message in the UI
     */
    showError(message) {
        const container = document.getElementById('category-chips-container');
        if (container) {
            container.innerHTML = `
                <div class="error-message" style="color: var(--danger-color, #ef4444); text-align: center; padding: 1rem;">
                    <p>${message}</p>
                    <button onclick="categoryFilter.init()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    /**
     * Refresh statistics (useful after uploading new documents)
     */
    async refreshStats() {
        try {
            await this.loadStats();
            this.render();
            console.log('Category stats refreshed');
        } catch (error) {
            console.error('Failed to refresh stats:', error);
        }
    }
}

// Global instance
let categoryFilter = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    categoryFilter = new CategoryFilter();
    categoryFilter.init();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CategoryFilter;
}
