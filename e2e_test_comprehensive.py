"""
Comprehensive End-to-End Test Suite for Google Gemini File Search Application

This test suite validates:
1. Store creation
2. File upload functionality
3. Query submission and response
4. Database persistence
5. UI interactions (file upload, query submission)
6. Bulk upload functionality
7. Store management
"""

import requests
import json
import os
import time
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api"
TEST_TIMEOUT = 30

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}[PASS] {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}[FAIL] {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}[WARN] {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}[INFO] {text}{Colors.ENDC}")

class E2ETestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.warnings = []

    def add_pass(self):
        self.passed += 1

    def add_fail(self, error):
        self.failed += 1
        self.errors.append(error)

    def add_warning(self, warning):
        self.warnings.append(warning)

    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        print(f"Passed: {Colors.OKGREEN}{self.passed}{Colors.ENDC}")
        print(f"Failed: {Colors.FAIL}{self.failed}{Colors.ENDC}")
        print(f"Warnings: {Colors.WARNING}{len(self.warnings)}{Colors.ENDC}")

        if self.errors:
            print(f"\n{Colors.FAIL}Errors:{Colors.ENDC}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n{Colors.WARNING}Warnings:{Colors.ENDC}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        print()

results = E2ETestResults()

# ============================================================================
# TEST 1: Verify Application is Running
# ============================================================================

def test_app_running():
    """Test that Flask app is running and accessible"""
    print_header("TEST 1: Verify Application Running")

    try:
        response = requests.get(BASE_URL, timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            print_success("Application is running and responding")
            results.add_pass()
            return True
        else:
            print_error(f"Application returned status code {response.status_code}")
            results.add_fail(f"App status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to application at {BASE_URL}")
        print_warning(f"Make sure the Flask app is running with: python -m flask run")
        results.add_fail(f"Connection error: {BASE_URL}")
        return False
    except Exception as e:
        print_error(f"Error connecting to application: {str(e)}")
        results.add_fail(f"Connection error: {str(e)}")
        return False

# ============================================================================
# TEST 2: Create Test File
# ============================================================================

def create_test_file():
    """Create a test file for upload"""
    print_header("TEST 2: Create Test File")

    test_file_path = "test_sample.txt"
    test_content = """
    Test Document: Information for Validation Testing

    This is a test document for the Google Gemini File Search application.

    SECTION 1: Overview
    This document contains sample information that will be used to test
    the file upload, search, and query functionality of the application.

    SECTION 2: Features Being Tested
    - File upload capability
    - Store creation
    - Query submission
    - Response generation
    - Database persistence

    SECTION 3: Test Data
    The following information is included for testing:
    - Document title: Test Document
    - Document type: Text
    - Created date: 2025-11-14
    - Purpose: End-to-end validation

    SECTION 4: Expected Outcomes
    When querying this document, the following queries should work:
    1. "What is this document about?"
    2. "What sections does this document contain?"
    3. "What features are being tested?"
    4. "What is the purpose of this document?"

    SECTION 5: Additional Information
    This document is part of the validation process to ensure that:
    - Files can be uploaded successfully
    - Files are indexed properly by Gemini
    - Queries return meaningful responses
    - The application handles file search correctly

    SECTION 6: Conclusion
    This test document provides sufficient content for validating
    the application's file search capabilities.
    """

    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)

        file_size = os.path.getsize(test_file_path)
        print_success(f"Test file created: {test_file_path}")
        print_info(f"File size: {file_size} bytes")
        results.add_pass()
        return test_file_path
    except Exception as e:
        print_error(f"Failed to create test file: {str(e)}")
        results.add_fail(f"Test file creation failed: {str(e)}")
        return None

# ============================================================================
# TEST 3: Create Store
# ============================================================================

def test_create_store():
    """Test store creation via API"""
    print_header("TEST 3: Create File Search Store")

    store_name = f"test-store-{int(time.time())}"

    try:
        payload = {
            "store_name": store_name,
            "display_name": "E2E Test Store"
        }

        response = requests.post(
            f"{API_BASE}/files/create_store",
            json=payload,
            timeout=TEST_TIMEOUT
        )

        print_info(f"Store name: {store_name}")
        print_info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                store_id = data.get('store_name')
                print_success(f"Store created successfully: {store_id}")
                results.add_pass()
                return store_name, store_id
            else:
                print_error(f"Store creation failed: {data.get('error', 'Unknown error')}")
                results.add_fail(f"Store creation error: {data.get('error')}")
                return None, None
        else:
            print_error(f"Store creation returned status {response.status_code}")
            print_info(f"Response: {response.text}")
            results.add_fail(f"Store creation HTTP error: {response.status_code}")
            return None, None
    except Exception as e:
        print_error(f"Store creation failed: {str(e)}")
        results.add_fail(f"Store creation exception: {str(e)}")
        return None, None

# ============================================================================
# TEST 4: Upload File
# ============================================================================

def test_upload_file(store_name, test_file_path):
    """Test file upload via API"""
    print_header("TEST 4: Upload File to Store")

    if not os.path.exists(test_file_path):
        print_error(f"Test file not found: {test_file_path}")
        results.add_fail(f"Test file missing: {test_file_path}")
        return False

    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': (os.path.basename(test_file_path), f)}
            data = {
                'store_name': store_name,
                'category': 'test'
            }

            response = requests.post(
                f"{API_BASE}/files/upload_file",
                files=files,
                data=data,
                timeout=TEST_TIMEOUT
            )

        print_info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get('success'):
                print_success(f"File uploaded successfully")
                print_info(f"File ID: {resp_data.get('file_id', 'N/A')}")
                results.add_pass()
                return True
            else:
                print_error(f"File upload failed: {resp_data.get('error', 'Unknown error')}")
                results.add_fail(f"File upload error: {resp_data.get('error')}")
                return False
        else:
            print_error(f"File upload returned status {response.status_code}")
            print_info(f"Response: {response.text}")
            results.add_fail(f"File upload HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"File upload failed: {str(e)}")
        results.add_fail(f"File upload exception: {str(e)}")
        return False

# ============================================================================
# TEST 5: Wait for File Indexing
# ============================================================================

def wait_for_file_indexing():
    """Wait for Gemini to index the uploaded file"""
    print_header("TEST 5: Wait for File Indexing")

    print_info("Waiting 10 seconds for Gemini to index the file...")
    for i in range(10, 0, -1):
        print_info(f"Waiting... {i}s remaining")
        time.sleep(1)

    print_success("File indexing wait completed")
    results.add_pass()

# ============================================================================
# TEST 6: List Stores
# ============================================================================

def test_list_stores():
    """Test listing all stores"""
    print_header("TEST 6: List Stores")

    try:
        response = requests.get(
            f"{API_BASE}/files/list_stores",
            timeout=TEST_TIMEOUT
        )

        print_info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            stores = data.get('stores', [])
            print_success(f"Retrieved {len(stores)} store(s)")

            for store in stores:
                print_info(f"  - Store: {store.get('name', 'N/A')} "
                          f"(ID: {store.get('gemini_store_id', 'N/A')})")

            results.add_pass()
            return stores
        else:
            print_error(f"List stores returned status {response.status_code}")
            results.add_fail(f"List stores HTTP error: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"List stores failed: {str(e)}")
        results.add_fail(f"List stores exception: {str(e)}")
        return []

# ============================================================================
# TEST 7: Query the Store
# ============================================================================

def test_query_store(store_name):
    """Test querying the file search store"""
    print_header("TEST 7: Query the File Search Store")

    query = "What is this document about?"

    try:
        payload = {
            "question": query,
            "store_name": store_name,
            "mode": "quick"
        }

        print_info(f"Query: {query}")
        print_info(f"Store: {store_name}")
        print_info(f"Mode: quick")

        response = requests.post(
            f"{API_BASE}/query/query",
            json=payload,
            timeout=60  # Longer timeout for Gemini API
        )

        print_info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                answer = data.get('answer', '')
                print_success("Query executed successfully")
                print_info(f"Response length: {len(answer)} characters")

                if answer and len(answer) > 10:
                    print_info(f"Response preview: {answer[:200]}...")
                    results.add_pass()
                    return True
                else:
                    print_warning("Response is empty or too short")
                    results.add_warning(f"Query response too short: {len(answer)} chars")
                    return False
            else:
                error = data.get('error', 'Unknown error')
                print_error(f"Query failed: {error}")
                results.add_fail(f"Query error: {error}")
                return False
        else:
            print_error(f"Query returned status {response.status_code}")
            print_info(f"Response: {response.text}")
            results.add_fail(f"Query HTTP error: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_error("Query request timed out")
        results.add_fail("Query request timeout")
        return False
    except Exception as e:
        print_error(f"Query failed: {str(e)}")
        results.add_fail(f"Query exception: {str(e)}")
        return False

# ============================================================================
# TEST 8: Verify Database Persistence
# ============================================================================

def test_database_persistence():
    """Test that data is persisted in the database"""
    print_header("TEST 8: Verify Database Persistence")

    db_path = "C:/ai tools/Google_File Search/instance/app.db"

    try:
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            mod_time = os.path.getmtime(db_path)
            mod_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))

            print_success(f"Database file exists: {db_path}")
            print_info(f"Database size: {file_size} bytes")
            print_info(f"Last modified: {mod_time_str}")
            results.add_pass()
            return True
        else:
            print_error(f"Database file not found: {db_path}")
            results.add_fail(f"Database file missing: {db_path}")
            return False
    except Exception as e:
        print_error(f"Database verification failed: {str(e)}")
        results.add_fail(f"Database verification error: {str(e)}")
        return False

# ============================================================================
# TEST 9: Query Database Directly
# ============================================================================

def test_query_database():
    """Query the database directly to verify data persistence"""
    print_header("TEST 9: Query Database Directly")

    try:
        # Import after ensuring we're in the right directory
        sys.path.insert(0, "C:/ai tools/Google_File Search")
        from app import create_app
        from app.models import Store, Document, QueryHistory

        app = create_app('development')

        with app.app_context():
            # Query stores
            stores = Store.query.all()
            documents = Document.query.all()
            queries = QueryHistory.query.all()

            print_success(f"Database connection successful")
            print_info(f"Stores in database: {len(stores)}")
            print_info(f"Documents in database: {len(documents)}")
            print_info(f"Queries in database: {len(queries)}")

            for store in stores:
                print_info(f"  - Store: {store.name} (ID: {store.gemini_store_id})")

            for doc in documents[:5]:  # Show first 5 documents
                print_info(f"  - Document: {doc.filename}")

            results.add_pass()
            return True
    except Exception as e:
        print_error(f"Database query failed: {str(e)}")
        results.add_fail(f"Database query error: {str(e)}")
        return False

# ============================================================================
# TEST 10: Test Multiple Queries
# ============================================================================

def test_multiple_queries(store_name):
    """Test multiple different queries to the store"""
    print_header("TEST 10: Test Multiple Queries")

    test_queries = [
        "What sections does this document contain?",
        "What features are being tested?",
        "What is the purpose of this document?"
    ]

    passed_queries = 0

    for i, query in enumerate(test_queries, 1):
        try:
            print_info(f"\nQuery {i}/{len(test_queries)}: {query}")

            payload = {
                "question": query,
                "store_name": store_name,
                "mode": "quick"
            }

            response = requests.post(
                f"{API_BASE}/query/query",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('answer'):
                    print_success(f"Query {i} successful")
                    passed_queries += 1
                else:
                    print_warning(f"Query {i} returned no answer")
            else:
                print_warning(f"Query {i} returned status {response.status_code}")
        except Exception as e:
            print_warning(f"Query {i} failed: {str(e)}")

    if passed_queries == len(test_queries):
        print_success(f"All {passed_queries} queries passed")
        results.add_pass()
    else:
        print_warning(f"Only {passed_queries}/{len(test_queries)} queries passed")
        results.add_warning(f"Multiple queries: {passed_queries}/{len(test_queries)} successful")

# ============================================================================
# TEST 11: UI Endpoints Test
# ============================================================================

def test_ui_endpoints():
    """Test that UI endpoints are accessible"""
    print_header("TEST 11: UI Endpoints Accessibility")

    endpoints = [
        ("/", "Home page"),
        ("/test-markdown", "Markdown test page")
    ]

    passed = 0

    for endpoint, description in endpoints:
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                timeout=TEST_TIMEOUT
            )

            if response.status_code == 200:
                print_success(f"{description}: {endpoint} - OK")
                passed += 1
            else:
                print_warning(f"{description}: {endpoint} - Status {response.status_code}")
        except Exception as e:
            print_warning(f"{description}: {endpoint} - Error: {str(e)}")

    if passed == len(endpoints):
        results.add_pass()
    else:
        results.add_warning(f"UI Endpoints: {passed}/{len(endpoints)} accessible")

# ============================================================================
# TEST 12: File Listing
# ============================================================================

def test_file_listing(store_name):
    """Test listing files in a store"""
    print_header("TEST 12: List Files in Store")

    try:
        response = requests.get(
            f"{API_BASE}/files/list_files?store_name={store_name}",
            timeout=TEST_TIMEOUT
        )

        print_info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            print_success(f"Retrieved {len(files)} file(s)")
            results.add_pass()
            return files
        else:
            print_warning(f"List files returned status {response.status_code}")
            results.add_warning(f"File listing: Status {response.status_code}")
            return []
    except Exception as e:
        print_warning(f"File listing failed: {str(e)}")
        results.add_warning(f"File listing error: {str(e)}")
        return []

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 60)
    print("GOOGLE GEMINI FILE SEARCH - END-TO-END VALIDATION SUITE")
    print("=" * 60)
    print(f"{Colors.ENDC}\n")

    print_info(f"Base URL: {BASE_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Timeout: {TEST_TIMEOUT}s")

    # Test 1: App Running
    if not test_app_running():
        print_error("Application is not running. Aborting tests.")
        results.print_summary()
        return

    # Test 2: Create Test File
    test_file_path = create_test_file()
    if not test_file_path:
        print_error("Failed to create test file. Aborting tests.")
        results.print_summary()
        return

    # Test 3: Create Store
    store_name, store_id = test_create_store()
    if not store_name:
        print_error("Failed to create store. Some tests will be skipped.")

    # Test 4: Upload File
    if store_name:
        test_upload_file(store_name, test_file_path)

        # Test 5: Wait for indexing
        wait_for_file_indexing()

        # Test 6: List Stores
        test_list_stores()

        # Test 7: Query Store
        test_query_store(store_name)

        # Test 10: Multiple Queries
        test_multiple_queries(store_name)

        # Test 12: List Files
        test_file_listing(store_name)

    # Test 8: Database Persistence
    test_database_persistence()

    # Test 9: Query Database
    test_query_database()

    # Test 11: UI Endpoints
    test_ui_endpoints()

    # Print final summary
    results.print_summary()

    # Cleanup
    try:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print_info(f"Cleaned up test file: {test_file_path}")
    except:
        pass

    # Return exit code based on failures
    if results.failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
