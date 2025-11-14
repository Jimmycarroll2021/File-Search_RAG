"""
Stress test for the Google Gemini File Search API
"""
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = 'http://127.0.0.1:5000'

def test_list_stores():
    """Test list stores endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/api/files/list_stores', timeout=5)
        return {'status': response.status_code, 'success': response.status_code == 200}
    except Exception as e:
        return {'status': 'ERROR', 'success': False, 'error': str(e)}

def test_categories():
    """Test categories endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/api/categories/stats', timeout=5)
        return {'status': response.status_code, 'success': response.status_code == 200}
    except Exception as e:
        return {'status': 'ERROR', 'success': False, 'error': str(e)}

def main():
    print("=" * 60)
    print("STRESS TEST: Multiple Rapid Requests")
    print("=" * 60)

    # Sequential test
    print("\n1. Sequential Requests (10x)")
    results = {'success': 0, 'failed': 0}
    start = time.time()

    for i in range(10):
        result = test_list_stores()
        if result['success']:
            results['success'] += 1
        else:
            results['failed'] += 1
        print(f"  Request {i+1}: {result['status']}")
        time.sleep(0.1)

    elapsed = time.time() - start
    print(f"\n  Completed: {results['success']}/{results['success']+results['failed']} successful")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Average response time: {elapsed/(results['success']+results['failed']):.3f}s")

    # Concurrent test
    print("\n2. Concurrent Requests (10x)")
    start = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(test_list_stores) for _ in range(10)]
        concurrent_results = {'success': 0, 'failed': 0}

        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result['success']:
                concurrent_results['success'] += 1
            else:
                concurrent_results['failed'] += 1
            print(f"  Request {i}: {result['status']}")

    elapsed = time.time() - start
    print(f"\n  Completed: {concurrent_results['success']}/{concurrent_results['success']+concurrent_results['failed']} successful")
    print(f"  Total time: {elapsed:.2f}s")

    # Test different endpoints
    print("\n3. Testing Multiple Endpoints")
    endpoints = [
        test_list_stores,
        test_categories,
        test_list_stores,
        test_categories,
    ]

    for i, test_func in enumerate(endpoints, 1):
        result = test_func()
        status = "OK" if result['success'] else "FAILED"
        print(f"  Test {i} ({test_func.__name__}): {status} - {result['status']}")

    print("\n" + "=" * 60)
    print("STRESS TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
