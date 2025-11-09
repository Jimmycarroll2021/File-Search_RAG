/**
 * Theme Manager
 * Handles dark/light mode switching with localStorage persistence and system preference detection
 */

class ThemeManager {
  constructor() {
    this.STORAGE_KEY = 'theme';
    this.DARK = 'dark';
    this.LIGHT = 'light';
    this.htmlElement = document.documentElement;

    // Initialize theme on load
    this.init();
  }

  /**
   * Initialize theme system
   */
  init() {
    // Apply theme immediately (before DOM loads) to prevent flash
    const savedTheme = this.getSavedTheme();
    const theme = savedTheme || this.getSystemPreference();
    this.applyTheme(theme, false);

    // Setup toggle button when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupToggle());
    } else {
      this.setupToggle();
    }
  }

  /**
   * Get theme from localStorage
   * @returns {string|null} Saved theme or null
   */
  getSavedTheme() {
    try {
      return localStorage.getItem(this.STORAGE_KEY);
    } catch (e) {
      console.warn('localStorage not available:', e);
      return null;
    }
  }

  /**
   * Save theme to localStorage
   * @param {string} theme - Theme to save
   */
  saveTheme(theme) {
    try {
      localStorage.setItem(this.STORAGE_KEY, theme);
    } catch (e) {
      console.warn('Failed to save theme:', e);
    }
  }

  /**
   * Detect system color scheme preference
   * @returns {string} 'dark' or 'light'
   */
  getSystemPreference() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return this.DARK;
    }
    return this.LIGHT;
  }

  /**
   * Apply theme to document
   * @param {string} theme - Theme to apply ('dark' or 'light')
   * @param {boolean} save - Whether to save to localStorage (default: true)
   */
  applyTheme(theme, save = true) {
    // Update HTML data-theme attribute
    this.htmlElement.setAttribute('data-theme', theme);

    // Save to localStorage
    if (save) {
      this.saveTheme(theme);
    }

    // Dispatch custom event for other scripts
    window.dispatchEvent(new CustomEvent('themechange', {
      detail: { theme }
    }));
  }

  /**
   * Toggle between light and dark themes
   */
  toggle() {
    const currentTheme = this.htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === this.DARK ? this.LIGHT : this.DARK;
    this.applyTheme(newTheme);
  }

  /**
   * Setup toggle button event listener
   */
  setupToggle() {
    const toggleButton = document.getElementById('theme-toggle');

    if (!toggleButton) {
      console.warn('Theme toggle button not found');
      return;
    }

    // Add click handler
    toggleButton.addEventListener('click', () => {
      this.toggle();
    });

    // Add keyboard support
    toggleButton.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.toggle();
      }
    });
  }

  /**
   * Listen for system preference changes
   */
  watchSystemPreference() {
    if (!window.matchMedia) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', (e) => {
        // Only apply if user hasn't manually set a preference
        if (!this.getSavedTheme()) {
          this.applyTheme(e.matches ? this.DARK : this.LIGHT, false);
        }
      });
    }
    // Legacy browsers
    else if (mediaQuery.addListener) {
      mediaQuery.addListener((e) => {
        if (!this.getSavedTheme()) {
          this.applyTheme(e.matches ? this.DARK : this.LIGHT, false);
        }
      });
    }
  }

  /**
   * Get current theme
   * @returns {string} Current theme ('dark' or 'light')
   */
  getCurrentTheme() {
    return this.htmlElement.getAttribute('data-theme') || this.LIGHT;
  }
}

// Initialize theme manager immediately
const themeManager = new ThemeManager();

// Watch for system preference changes
themeManager.watchSystemPreference();

// Export for use in other scripts if needed
window.themeManager = themeManager;
