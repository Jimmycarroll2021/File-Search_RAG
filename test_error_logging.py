#!/usr/bin/env python3
"""
Test script to verify the improved error logging in query and upload endpoints.
This will trigger errors to ensure logging is working correctly.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_query_error_logging():
    """Test query endpoint with malformed request to trigger error logging."""
    print("\n" + "="*60)
    print("TESTING QUERY ERROR LOGGING")
    print("="*60)

    # Test 1: Query with no JSON body (should trigger validation error)
    print("\n1. Testing query with no JSON body...")
    try:
        response = requests.post(f"{BASE_URL}/api/query/query")
        print(f"   Response: {response.status_code}")
        if response.status_code == 500:
            print(f"   Error details: {response.json()}")
    except Exception as e:
        print(f"   Request failed: {e}")

    # Test 2: Query with empty question
    print("\n2. Testing query with empty question...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/query/query",
            json={"question": "", "store_name": "my-file-search-store"}
        )
        print(f"   Response: {response.status_code}")
        print(f"   Message: {response.json()}")
    except Exception as e:
        print(f"   Request failed: {e}")

    # Test 3: Query with non-existent store
    print("\n3. Testing query with non-existent store...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/query/query",
            json={
                "question": "Test question",
                "store_name": "non-existent-store-12345"
            }
        )
        print(f"   Response: {response.status_code}")
        print(f"   Message: {response.json()}")
    except Exception as e:
        print(f"   Request failed: {e}")

    # Test 4: Valid query (should work if store exists)
    print("\n4. Testing valid query...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/query/query",
            json={
                "question": "What is the purpose of this application?",
                "store_name": "my-file-search-store",
                "mode": "quick"
            }
        )
        print(f"   Response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            answer = result.get('answer', '')
            print(f"   Answer preview: {answer[:100]}..." if len(answer) > 100 else f"   Answer: {answer}")
        else:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Request failed: {e}")

def test_upload_error_logging():
    """Test upload endpoint error logging."""
    print("\n" + "="*60)
    print("TESTING UPLOAD ERROR LOGGING")
    print("="*60)

    # Test 1: Upload with no file
    print("\n1. Testing upload with no file...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/files/upload_file",
            data={"store_name": "my-file-search-store"}
        )
        print(f"   Response: {response.status_code}")
        print(f"   Message: {response.json()}")
    except Exception as e:
        print(f"   Request failed: {e}")

    # Test 2: Upload with empty file
    print("\n2. Testing upload with empty filename...")
    try:
        files = {'file': ('', '')}
        response = requests.post(
            f"{BASE_URL}/api/files/upload_file",
            files=files,
            data={"store_name": "my-file-search-store"}
        )
        print(f"   Response: {response.status_code}")
        print(f"   Message: {response.json()}")
    except Exception as e:
        print(f"   Request failed: {e}")

def check_server_status():
    """Check if the server is running."""
    print("\nChecking server status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("[OK] Server is running at", BASE_URL)
            return True
        else:
            print(f"[ERROR] Server returned status code: {response.status_code}")
            return False
    except requests.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {BASE_URL}")
        print("  Please ensure the Flask server is running: python wsgi.py")
        return False

def main():
    print("\n" + "="*60)
    print("ERROR LOGGING TEST SUITE")
    print("="*60)
    print("\nThis test will intentionally trigger errors to verify")
    print("that comprehensive logging has been added to the application.")
    print("\nCheck the server console to see detailed error logs!")

    # Check if server is running
    if not check_server_status():
        return

    # Run tests
    test_query_error_logging()
    test_upload_error_logging()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n[OK] Check the server console for detailed error logs!")
    print("[OK] You should see stack traces and context information")
    print("[OK] Errors are now properly logged for debugging")

if __name__ == "__main__":
    main()