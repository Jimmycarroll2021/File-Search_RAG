"""
Test script to verify API endpoints work with the database.
Tests the full flow: create store -> upload file -> query.
"""
import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"


def test_list_stores():
    """Test listing stores."""
    print("\n1. Testing GET /list_stores...")
    response = requests.get(f"{BASE_URL}/list_stores")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200


def test_create_store():
    """Test creating a new store."""
    print("\n2. Testing POST /create_store...")
    data = {
        "store_name": "api_test_store",
        "display_name": "API Test Store"
    }
    response = requests.post(f"{BASE_URL}/create_store", json=data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {result}")

    if response.status_code == 200 and result.get('success'):
        return result.get('store_name')
    return None


def test_upload_file(store_name):
    """Test uploading a file to a store."""
    print("\n3. Testing POST /upload_file...")

    # Find a test file in uploads directory
    test_file = "uploads/test.pdf"
    if not os.path.exists(test_file):
        # Try to find any PDF file
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
            if pdf_files:
                test_file = os.path.join(uploads_dir, pdf_files[0])

    if not os.path.exists(test_file):
        print(f"   WARNING: No test file found at {test_file}")
        print("   Creating a dummy test file...")
        os.makedirs("uploads", exist_ok=True)
        with open(test_file, 'w') as f:
            f.write("Test PDF content")

    print(f"   Using test file: {test_file}")

    with open(test_file, 'rb') as f:
        files = {'file': (os.path.basename(test_file), f, 'application/pdf')}
        data = {
            'store_name': store_name,
            'category': 'test'
        }
        response = requests.post(f"{BASE_URL}/upload_file", files=files, data=data)

    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {result}")
    return response.status_code == 200 and result.get('success')


def test_query(store_name):
    """Test querying documents in a store."""
    print("\n4. Testing POST /query...")
    data = {
        "question": "What is in this document?",
        "store_name": store_name,
        "response_mode": "comprehensive"
    }
    response = requests.post(f"{BASE_URL}/query", json=data)
    print(f"   Status: {response.status_code}")
    result = response.json()

    if 'answer' in result:
        print(f"   Answer preview: {result['answer'][:200]}...")
    else:
        print(f"   Response: {result}")

    return response.status_code == 200


def main():
    """Run all API tests."""
    print("=" * 60)
    print("API ENDPOINTS TEST")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")

    try:
        # Test 1: List stores
        if not test_list_stores():
            print("\nERROR: Failed to list stores")
            return False

        # Test 2: Create store
        store_name = test_create_store()
        if not store_name:
            print("\nERROR: Failed to create store")
            return False

        # Test 3: Upload file
        if not test_upload_file(store_name):
            print("\nERROR: Failed to upload file")
            return False

        # Test 4: Query
        if not test_query(store_name):
            print("\nERROR: Failed to query")
            return False

        print("\n" + "=" * 60)
        print("ALL API TESTS PASSED!")
        print("=" * 60)
        return True

    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server at", BASE_URL)
        print("Please ensure the server is running: python run.py")
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
