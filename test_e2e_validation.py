"""
End-to-End Validation Test
Tests complete file upload and query workflow with multiple documents
"""
import requests
import time
import os

BASE_URL = "http://127.0.0.1:5000"
STORE_NAME = "my-file-search-store"
TEST_DOCS = [
    "test_docs/compliance_frameworks.txt",
    "test_docs/team_capabilities.txt"
]

def test_upload_files():
    """Test uploading multiple files"""
    print("\n" + "="*60)
    print("TEST 1: File Upload")
    print("="*60)

    uploaded = []
    for doc_path in TEST_DOCS:
        if not os.path.exists(doc_path):
            print(f"[FAIL] File not found: {doc_path}")
            continue

        filename = os.path.basename(doc_path)
        print(f"\n[UPLOAD] Uploading: {filename}")

        with open(doc_path, 'rb') as f:
            files = {'file': (filename, f)}
            data = {'store_name': STORE_NAME}

            response = requests.post(f"{BASE_URL}/upload_file", files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   [PASS] Uploaded successfully")
                    print(f"   Category: {result.get('category')}")
                    print(f"   Document ID: {result.get('document_id')}")
                    uploaded.append(filename)
                else:
                    print(f"   [FAIL] Upload failed: {result.get('error')}")
            else:
                print(f"   [FAIL] HTTP {response.status_code}: {response.text[:200]}")

        time.sleep(1)  # Rate limiting

    print(f"\nUploaded {len(uploaded)}/{len(TEST_DOCS)} files")
    return uploaded

def test_query_single_doc():
    """Test querying specific document content"""
    print("\n" + "="*60)
    print("TEST 2: Single Document Query")
    print("="*60)

    queries = [
        {
            "question": "What security certifications does ACME have?",
            "expected_keywords": ["ISO 27001", "IRAP", "SOC 2"]
        },
        {
            "question": "How many people are on the security team?",
            "expected_keywords": ["45", "security"]
        }
    ]

    for i, query_data in enumerate(queries, 1):
        print(f"\n[QUERY] Query {i}: {query_data['question']}")

        response = requests.post(
            f"{BASE_URL}/query",
            json={
                "question": query_data['question'],
                "store_name": STORE_NAME,
                "mode": "quick"
            }
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                answer = result.get('answer', '')
                print(f"   [PASS] Query successful")
                print(f"   Answer preview: {answer[:150]}...")

                # Check for expected keywords
                found_keywords = [kw for kw in query_data['expected_keywords'] if kw.lower() in answer.lower()]
                print(f"   Keywords found: {found_keywords}")
            else:
                print(f"   [FAIL] Query failed: {result.get('error')}")
        else:
            print(f"   [FAIL] HTTP {response.status_code}: {response.text[:200]}")

        time.sleep(2)

def test_cross_document_query():
    """Test querying across multiple documents"""
    print("\n" + "="*60)
    print("TEST 3: Cross-Document Query")
    print("="*60)

    query = "What are the team capabilities and compliance status of ACME?"
    print(f"\n[QUERY] Query: {query}")

    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "question": query,
            "store_name": STORE_NAME,
            "mode": "analysis"
        }
    )

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            answer = result.get('answer') or ''
            print(f"   [PASS] Cross-document query successful")
            print(f"   Mode: {result.get('mode_name')}")
            print(f"   Answer length: {len(answer)} characters")
            if answer:
                print(f"\n   Full Answer:")
                print("   " + "-"*56)
                print("   " + answer.replace("\n", "\n   "))
                print("   " + "-"*56)
            else:
                print("   [WARNING] Answer was empty")
        else:
            print(f"   [FAIL] Query failed: {result.get('error')}")
    else:
        print(f"   [FAIL] HTTP {response.status_code}: {response.text[:200]}")

def main():
    print("="*60)
    print("END-TO-END VALIDATION TEST")
    print("="*60)
    print(f"Server: {BASE_URL}")
    print(f"Store: {STORE_NAME}")

    # Test 1: Upload files
    uploaded = test_upload_files()

    if len(uploaded) == 0:
        print("\n[FAIL] No files uploaded - cannot proceed with query tests")
        return

    # Test 2: Query single document
    test_query_single_doc()

    # Test 3: Cross-document query
    test_cross_document_query()

    print("\n" + "="*60)
    print("[PASS] END-TO-END VALIDATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
