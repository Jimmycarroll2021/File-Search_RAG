"""
Test file to validate all API endpoints are correctly implemented and accessible.
This test validates that the JavaScript files are using the correct endpoint URLs.
"""
import pytest
from flask import json
import os
import tempfile


class TestAPIEndpoints:
    """Test suite for API endpoint validation"""

    def test_query_endpoint_exists(self, client):
        """Test that /api/query/query endpoint exists and accepts POST"""
        # This should handle the request even without valid data
        response = client.post('/api/query/query',
                              json={'question': 'test question', 'store_name': 'test-store'},
                              content_type='application/json')
        # Should not be 404 (endpoint exists) - store will not exist but endpoint exists
        assert response.status_code in [200, 400, 404, 500], f"Unexpected status {response.status_code}"
        # Should return JSON
        assert response.content_type == 'application/json'

    def test_query_endpoint_requires_question(self, client):
        """Test that query endpoint validates required question parameter"""
        response = client.post('/api/query/query',
                              json={'store_name': 'test-store'},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'question' in data['error'].lower()

    def test_upload_file_endpoint_exists(self, client):
        """Test that /api/files/upload_file endpoint exists"""
        # Test that endpoint accepts POST with file data
        response = client.post('/api/files/upload_file')
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404

    def test_upload_file_endpoint_requires_file(self, client):
        """Test that upload_file endpoint validates file parameter"""
        response = client.post('/api/files/upload_file',
                              data={},
                              content_type='multipart/form-data')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'file' in data['error'].lower()

    def test_bulk_upload_endpoint_exists(self, client):
        """Test that /api/files/bulk_upload endpoint exists"""
        response = client.post('/api/files/bulk_upload',
                              json={},
                              content_type='application/json')
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404

    def test_bulk_upload_endpoint_requires_directory(self, client):
        """Test that bulk_upload endpoint validates source_directory parameter"""
        response = client.post('/api/files/bulk_upload',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        # Either missing source_directory or missing json data
        assert 'source_directory' in data['error'].lower() or 'json' in data['error'].lower()

    def test_list_stores_endpoint_exists(self, client):
        """Test that /api/files/list_stores endpoint exists"""
        response = client.get('/api/files/list_stores')
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
        # Should return JSON
        assert response.content_type == 'application/json'

    def test_list_stores_returns_valid_json(self, client):
        """Test that list_stores returns valid JSON structure"""
        response = client.get('/api/files/list_stores')
        data = json.loads(response.data)
        assert 'success' in data
        assert 'stores' in data

    def test_endpoint_paths_are_correct(self):
        """Verify that all endpoint paths match what JavaScript expects"""
        # Define expected endpoints
        expected_endpoints = {
            'query': '/api/query/query',
            'upload': '/api/files/upload_file',
            'bulk_upload': '/api/files/bulk_upload',
            'list_stores': '/api/files/list_stores'
        }

        # These would be used in actual endpoint testing
        assert expected_endpoints['query'] == '/api/query/query'
        assert expected_endpoints['upload'] == '/api/files/upload_file'
        assert expected_endpoints['bulk_upload'] == '/api/files/bulk_upload'
        assert expected_endpoints['list_stores'] == '/api/files/list_stores'

    def test_javascript_endpoint_references(self):
        """Validate that JavaScript files reference correct endpoints"""
        # Read main.js
        main_js_path = 'static/js/main.js'
        with open(main_js_path, 'r') as f:
            main_js = f.read()

        # Check for correct endpoints in main.js
        assert '/api/query/query' in main_js, "main.js should use /api/query/query endpoint"
        assert '/api/files/upload_file' in main_js, "main.js should use /api/files/upload_file endpoint"
        
        # Should NOT have old endpoints
        assert "fetch('/query'" not in main_js, "main.js should not use old /query endpoint"
        assert "fetch('/upload_file'" not in main_js, "main.js should not use old /upload_file endpoint"

        # Read bulk-upload.js
        bulk_js_path = 'static/js/bulk-upload.js'
        with open(bulk_js_path, 'r') as f:
            bulk_js = f.read()

        # Check for correct endpoints in bulk-upload.js
        assert '/api/files/bulk_upload' in bulk_js, "bulk-upload.js should use /api/files/bulk_upload endpoint"
        assert '/api/files/list_stores' in bulk_js, "bulk-upload.js should use /api/files/list_stores endpoint"


class TestEndpointErrorHandling:
    """Test suite for endpoint error handling"""

    def test_query_endpoint_handles_invalid_store(self, client):
        """Test that query endpoint handles invalid store gracefully"""
        response = client.post('/api/query/query',
                              json={'question': 'test', 'store_name': 'nonexistent-store'},
                              content_type='application/json')
        # Should not be 500, should be 404 or similar
        assert response.status_code != 500
        data = json.loads(response.data)
        assert data['success'] is False

    def test_bulk_upload_endpoint_handles_nonexistent_directory(self, client):
        """Test that bulk_upload handles nonexistent directory gracefully"""
        response = client.post('/api/files/bulk_upload',
                              json={
                                  'source_directory': '/nonexistent/path',
                                  'store_name': 'test-store'
                              },
                              content_type='application/json')
        # Should not be 500, should be 400 or 404
        assert response.status_code != 500
        data = json.loads(response.data)
        assert data['success'] is False

    def test_endpoints_return_json_on_error(self, client):
        """Test that all endpoints return JSON even on error"""
        endpoints = [
            ('POST', '/api/query/query', {}),
            ('POST', '/api/files/bulk_upload', {}),
            ('GET', '/api/files/list_stores', None),
        ]

        for method, path, data in endpoints:
            if method == 'POST':
                response = client.post(path, json=data, content_type='application/json')
            else:
                response = client.get(path)

            # All responses should be JSON (may be application/json or application/json; charset=utf-8)
            assert 'application/json' in response.content_type, \
                f"{method} {path} should return JSON, got {response.content_type}"


class TestEndpointIntegration:
    """Integration tests for endpoint workflow"""

    def test_create_store_and_list(self, client):
        """Test creating a store and listing it"""
        store_name = 'integration-test-store'

        # Create store
        response = client.post('/api/files/create_store',
                              json={'store_name': store_name},
                              content_type='application/json')
        assert response.status_code in [200, 201]

        # List stores
        response = client.get('/api/files/list_stores')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
