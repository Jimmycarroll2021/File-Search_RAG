/**
 * Endpoint Validation Tests
 * 
 * Tests to verify that JavaScript files are using the correct API endpoints
 * These tests can be run in Node.js or a browser environment
 */

/**
 * Test Suite: API Endpoint Validation
 */
const EndpointValidationTests = {
    
    /**
     * Test that main.js uses correct query endpoint
     */
    testMainJsQueryEndpoint: function() {
        const testName = 'main.js uses /api/query/query endpoint';
        const mainJsCode = this.readFileSync('static/js/main.js');
        const hasCorrectEndpoint = mainJsCode.includes("fetch('/api/query/query'");
        const hasOldEndpoint = mainJsCode.includes("fetch('/query'");
        
        if (hasCorrectEndpoint && !hasOldEndpoint) {
            console.log(`✓ PASS: ${testName}`);
            return true;
        } else {
            console.error(`✗ FAIL: ${testName}`);
            if (!hasCorrectEndpoint) console.error('  - Missing /api/query/query endpoint');
            if (hasOldEndpoint) console.error('  - Still using old /query endpoint');
            return false;
        }
    },

    /**
     * Test that main.js uses correct upload endpoint
     */
    testMainJsUploadEndpoint: function() {
        const testName = 'main.js uses /api/files/upload_file endpoint';
        const mainJsCode = this.readFileSync('static/js/main.js');
        const hasCorrectEndpoint = mainJsCode.includes("fetch('/api/files/upload_file'");
        const hasOldEndpoint = mainJsCode.includes("fetch('/upload_file'");
        
        if (hasCorrectEndpoint && !hasOldEndpoint) {
            console.log(`✓ PASS: ${testName}`);
            return true;
        } else {
            console.error(`✗ FAIL: ${testName}`);
            if (!hasCorrectEndpoint) console.error('  - Missing /api/files/upload_file endpoint');
            if (hasOldEndpoint) console.error('  - Still using old /upload_file endpoint');
            return false;
        }
    },

    /**
     * Test that bulk-upload.js uses correct bulk_upload endpoint
     */
    testBulkUploadEndpoint: function() {
        const testName = 'bulk-upload.js uses /api/files/bulk_upload endpoint';
        const bulkJsCode = this.readFileSync('static/js/bulk-upload.js');
        const hasCorrectEndpoint = bulkJsCode.includes("fetch('/api/files/bulk_upload'");
        
        if (hasCorrectEndpoint) {
            console.log(`✓ PASS: ${testName}`);
            return true;
        } else {
            console.error(`✗ FAIL: ${testName}`);
            console.error('  - Missing /api/files/bulk_upload endpoint');
            return false;
        }
    },

    /**
     * Test that bulk-upload.js uses correct list_stores endpoint
     */
    testListStoresEndpoint: function() {
        const testName = 'bulk-upload.js uses /api/files/list_stores endpoint';
        const bulkJsCode = this.readFileSync('static/js/bulk-upload.js');
        const hasCorrectEndpoint = bulkJsCode.includes("fetch('/api/files/list_stores'");
        
        if (hasCorrectEndpoint) {
            console.log(`✓ PASS: ${testName}`);
            return true;
        } else {
            console.error(`✗ FAIL: ${testName}`);
            console.error('  - Missing /api/files/list_stores endpoint');
            return false;
        }
    },

    /**
     * Test that category-filter.js uses correct endpoints
     */
    testCategoryFilterEndpoints: function() {
        const testName = 'category-filter.js uses /api/categories endpoints';
        const catJsCode = this.readFileSync('static/js/category-filter.js');
        const hasCorrectEndpoint1 = catJsCode.includes("fetch('/api/categories'");
        const hasCorrectEndpoint2 = catJsCode.includes("fetch('/api/categories/stats'");
        
        if (hasCorrectEndpoint1 && hasCorrectEndpoint2) {
            console.log(`✓ PASS: ${testName}`);
            return true;
        } else {
            console.error(`✗ FAIL: ${testName}`);
            if (!hasCorrectEndpoint1) console.error('  - Missing /api/categories endpoint');
            if (!hasCorrectEndpoint2) console.error('  - Missing /api/categories/stats endpoint');
            return false;
        }
    },

    /**
     * Run all tests
     */
    runAll: function() {
        console.log('\n=== API Endpoint Validation Tests ===\n');
        
        const tests = [
            this.testMainJsQueryEndpoint.bind(this),
            this.testMainJsUploadEndpoint.bind(this),
            this.testBulkUploadEndpoint.bind(this),
            this.testListStoresEndpoint.bind(this),
            this.testCategoryFilterEndpoints.bind(this)
        ];

        let passed = 0;
        let failed = 0;

        tests.forEach(test => {
            try {
                if (test()) {
                    passed++;
                } else {
                    failed++;
                }
            } catch (error) {
                console.error(`✗ ERROR: ${error.message}`);
                failed++;
            }
        });

        console.log(`\n=== Results ===`);
        console.log(`Passed: ${passed}`);
        console.log(`Failed: ${failed}`);
        console.log(`Total: ${passed + failed}\n`);

        return failed === 0;
    },

    /**
     * Helper to read file contents (for Node.js)
     */
    readFileSync: function(filePath) {
        try {
            // For Node.js environment
            const fs = require('fs');
            return fs.readFileSync(filePath, 'utf-8');
        } catch (e) {
            // For browser environment or if file not found
            console.warn(`Could not read file: ${filePath}`);
            return '';
        }
    }
};

// Export for use in different environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EndpointValidationTests;
}

// Auto-run if in Node.js
if (typeof require !== 'undefined' && require.main === module) {
    const result = EndpointValidationTests.runAll();
    process.exit(result ? 0 : 1);
}
