"""
Diagnostic test to identify issues with the application
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api"

def test_query_issue():
    """Test the query endpoint issue"""
    print("\n=== TESTING QUERY ENDPOINT ===\n")

    # First create a store
    print("1. Creating store...")
    store_payload = {
        "store_name": "diagnostic-store",
        "display_name": "Diagnostic Store"
    }

    store_response = requests.post(
        f"{API_BASE}/files/create_store",
        json=store_payload,
        timeout=30
    )

    store_data = store_response.json()
    if not store_data.get('success'):
        print(f"Error creating store: {store_data}")
        return

    store_id = store_data.get('store_name')
    store_name = "diagnostic-store"
    print(f"Store created: {store_id}")

    # Upload a test file
    print("\n2. Uploading test file...")
    with open('test_sample.txt', 'w') as f:
        f.write("Test content for diagnostic testing.")

    with open('test_sample.txt', 'rb') as f:
        files = {'file': ('test_sample.txt', f)}
        data = {'store_name': store_name, 'category': 'test'}
        upload_response = requests.post(
            f"{API_BASE}/files/upload_file",
            files=files,
            data=data,
            timeout=30
        )

    upload_data = upload_response.json()
    print(f"Upload response: {upload_data}")

    # Wait for indexing
    print("\n3. Waiting for file indexing...")
    import time
    time.sleep(5)

    # Test query
    print("\n4. Testing query...")
    query_payload = {
        "question": "What is this document about?",
        "store_name": store_name,
        "mode": "quick"
    }

    print(f"Query payload: {json.dumps(query_payload, indent=2)}")

    query_response = requests.post(
        f"{API_BASE}/query/query",
        json=query_payload,
        timeout=60
    )

    print(f"Query response status: {query_response.status_code}")
    print(f"Query response headers: {dict(query_response.headers)}")

    try:
        query_data = query_response.json()
        print(f"Query response JSON: {json.dumps(query_data, indent=2)}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"Query response text: {query_response.text}")

    # Check what answer value is
    if query_response.status_code == 200:
        query_data = query_response.json()
        answer = query_data.get('answer')
        print(f"\nAnswer type: {type(answer)}")
        print(f"Answer value: {repr(answer)}")
        if answer is None:
            print("ERROR: Answer is None!")
            print("This is the NoneType error we're seeing.")

if __name__ == '__main__':
    test_query_issue()
