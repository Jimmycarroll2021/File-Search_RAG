/**
 * Automated Dark Mode Tests
 * Run these tests in the browser console to verify functionality
 */

class ThemeTest {
  constructor() {
    this.results = [];
    this.themeManager = window.themeManager;
  }

  /**
   * Run all tests
   */
  async runAll() {
    console.log('🧪 Running Dark Mode Test Suite...\n');

    this.testThemeManagerExists();
    this.testGetCurrentTheme();
    this.testToggleFunction();
    this.testLocalStorage();
    this.testSystemPreference();
    this.testDOMUpdate();
    this.testToggleButton();
    this.testTransitions();

    this.printResults();
  }

  /**
   * Test 1: Theme Manager exists
   */
  testThemeManagerExists() {
    const testName = 'ThemeManager instance exists';
    try {
      if (this.themeManager && this.themeManager instanceof ThemeManager) {
        this.pass(testName);
      } else {
        this.fail(testName, 'ThemeManager not found on window object');
      }
    } catch (error) {
      this.fail(testName, error.message);
    }
  }

  /**
   * Test 2: Get current theme
   */
  testGetCurrentTheme() {
    const testName = 'getCurrentTheme returns valid theme';
    try {
      const theme = this.themeManager.getCurrentTheme();
      if (theme === 'light' || theme === 'dark') {
        this.pass(testName, `Current theme: ${theme}`);
      } else {
        this.fail(testName, `Invalid theme returned: ${theme}`);
      }
    } catch (error) {
      this.fail(testName, error.message);
    }
  }

  /**
   * Test 3: Toggle function works
   */
  testToggleFunction() {
    const testName = 'Toggle function switches themes';
    try {
      const initialTheme = this.themeManager.getCurrentTheme();
      this.themeManager.toggle();
      const newTheme = this.themeManager.getCurrentTheme();

      if (initialTheme !== newTheme) {
        this.pass(testName, `Switched from ${initialTheme} to ${newTheme}`);
        // Toggle back to original
        this.themeManager.toggle();
      } else {
        this.fail(testName, 'Theme did not change after toggle');
      }
    } catch (error) {
      this.fail(testName, error.message);
    }
  }

  /**
   * Test 4: localStorage persistence
   */
  testLocalStorage() {
    const testName = 'localStorage saves theme preference';
    try {
      const testTheme = 'dark';
      this.themeManager.applyTheme(testTheme);

      const savedTheme = localStorage.getItem('theme');
      if (savedTheme === testTheme) {
        this.pass(testName, `Theme saved: ${savedTheme}`);
      } else {
        this.fail(testName, `Expected '${testTheme}', got '${savedTheme}'`);
      }
    } catch (error) {
      this.fail(testName, error.message);
    }
  }

  /**
   * Test 5: System preference detection
   */
  testSystemPreference() {
    const testName = 'System preference detection works';
    try {
      const systemPref = this.themeManager.getSystemPreference();
      if (systemPref === 'light' || systemPref === 'dark') {
        this.pass(testName, `System prefers: ${systemPref}`);
      } else {
        this.fail(testName, `Invalid system preference: ${systemPref}`);
      }
    } catch (error) {
      this.fail(testName, error.message);
    }
  }

  /**
   * Test 6: DOM update on theme change
   */
  testDOMUpdate() {
    const testName = 'data-theme attribute updates on toggle';
    try {
      const htmlElement = document.documentElement;
      this.themeManager.applyTheme('light');

      if (htmlElement.getAttribute('data-theme') === 'light') {
        this.themeManager.applyTheme('dark');
        if (htmlElement.getAttribute('data-theme') === 'dark') {
          this.pass(testName);
        } else {
          this.fail(testName, 'data-theme not updated to dark');
        }
      } else {
        this.fail(testName, 'data-theme not updated to light');
      }
    } catch (error) {
      this.fail(testName, error.message);
    }
  }

  /**
   * Test 7: Toggle button exists
   */
  testToggleButton() {
    const testName = 'Theme toggle button exists in DOM';
    try {
      const button = document.getElementById('theme-toggle');
      if (button) {
        const hasAriaLabel = button.hasAttribute('aria-label');
        const hasSunIcon = button.querySelector('.theme-icon.sun');
        const hasMoonIcon = button.querySelector('.theme-icon.moon');

        if (hasAriaLabel && hasSunIcon && hasMoonIcon) {
          this.pass(testName, 'Button properly configured with icons and ARIA');
        } else {
          this.fail(testName, 'Button missing required elements');
        }
      } else {
        this.fail(testName, 'Toggle button not found');
      }
    } catch (error) {
      this.fail(testName, error.message);
    }
  }

  /**
   * Test 8: CSS transitions are defined
   */
  testTransitions() {
    const testName = 'CSS transitions are defined';
    try {
      const testElement = document.createElement('div');
      document.body.appendChild(testElement);

      const styles = window.getComputedStyle(testElement);
      const transition = styles.transition;

      document.body.removeChild(testElement);

      if (transition && transition !== 'all 0s ease 0s') {
        this.pass(testName, 'Transitions configured');
      } else {
        this.fail(testName, 'No transitions found');
      }
    } catch (error) {
      this.fail(testName, error.message);
    }
  }

  /**
   * Record a passing test
   */
  pass(testName, details = '') {
    this.results.push({
      status: 'PASS',
      name: testName,
      details
    });
  }

  /**
   * Record a failing test
   */
  fail(testName, error = '') {
    this.results.push({
      status: 'FAIL',
      name: testName,
      error
    });
  }

  /**
   * Print test results
   */
  printResults() {
    console.log('\n📊 Test Results:\n');
    console.log('═'.repeat(60));

    let passed = 0;
    let failed = 0;

    this.results.forEach((result, index) => {
      const icon = result.status === 'PASS' ? '✅' : '❌';
      console.log(`${icon} Test ${index + 1}: ${result.name}`);

      if (result.details) {
        console.log(`   └─ ${result.details}`);
      }
      if (result.error) {
        console.log(`   └─ Error: ${result.error}`);
      }

      if (result.status === 'PASS') passed++;
      else failed++;
    });

    console.log('═'.repeat(60));
    console.log(`\n✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📈 Success Rate: ${((passed / this.results.length) * 100).toFixed(1)}%\n`);

    if (failed === 0) {
      console.log('🎉 All tests passed! Dark mode is working perfectly.');
    } else {
      console.log('⚠️  Some tests failed. Please review the errors above.');
    }
  }
}

// Auto-run tests when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const tester = new ThemeTest();
    tester.runAll();
  });
} else {
  const tester = new ThemeTest();
  tester.runAll();
}

// Make available globally for manual testing
window.ThemeTest = ThemeTest;
