"""
Bulk upload test documents to Google Gemini File Search
"""
import requests
import os
import time
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:5000"
STORE_NAME = "multi-doc-test-store"
TEST_DOCS_DIR = "test_docs"

def upload_file(file_path, store_name):
    """Upload a single file to the file search store"""
    url = f"{BASE_URL}/api/files/upload_file"

    filename = os.path.basename(file_path)
    print(f"\n📄 Uploading: {filename}")

    with open(file_path, 'rb') as f:
        files = {'file': (filename, f)}
        data = {'store_name': store_name}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Success: {result.get('message')}")
                return True
            else:
                print(f"   ❌ Failed: {result.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False

def main():
    print("=" * 60)
    print("🚀 BULK UPLOAD TEST - Multiple Document Types")
    print("=" * 60)

    # Check if test docs directory exists
    if not os.path.exists(TEST_DOCS_DIR):
        print(f"❌ Error: {TEST_DOCS_DIR} directory not found!")
        return

    # Get all files in test_docs directory
    test_files = []
    for file in os.listdir(TEST_DOCS_DIR):
        file_path = os.path.join(TEST_DOCS_DIR, file)
        if os.path.isfile(file_path):
            test_files.append(file_path)

    print(f"\n📁 Found {len(test_files)} files to upload:")
    for f in test_files:
        print(f"   - {os.path.basename(f)}")

    print(f"\n🎯 Target store: {STORE_NAME}")
    print("\n" + "-" * 60)

    # Upload each file
    success_count = 0
    failed_count = 0

    for file_path in test_files:
        if upload_file(file_path, STORE_NAME):
            success_count += 1
        else:
            failed_count += 1

        # Wait a bit between uploads to avoid rate limiting
        time.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("📊 UPLOAD SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{len(test_files)}")
    print(f"❌ Failed:     {failed_count}/{len(test_files)}")
    print(f"📦 Store name: {STORE_NAME}")
    print("\n🎯 You can now query these documents at:")
    print(f"   {BASE_URL}")
    print("\n💡 Try asking questions like:")
    print("   - 'What security certifications do we have?'")
    print("   - 'What are the hourly rates for cloud architects?'")
    print("   - 'How many people are on the security team?'")
    print("   - 'Summarize our PSPF compliance status'")
    print("=" * 60)

if __name__ == "__main__":
    main()
