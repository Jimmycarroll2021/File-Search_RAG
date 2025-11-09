"""
Tests for files blueprint routes
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO


@pytest.fixture
def app():
    """Create test Flask app"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestFilesBlueprint:
    """Test cases for files blueprint routes"""

    def test_create_store_success(self, client):
        """Test successful store creation"""
        with patch('app.routes.files.gemini_service') as mock_service:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_service.create_file_search_store.return_value = mock_store

            response = client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['store_name'] == 'stores/test-store-123'
            assert 'created successfully' in data['message']

    def test_create_store_error(self, client):
        """Test store creation error handling"""
        with patch('app.routes.files.gemini_service') as mock_service:
            mock_service.create_file_search_store.side_effect = Exception('API Error')

            response = client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'API Error' in data['error']

    def test_upload_file_success(self, client):
        """Test successful file upload"""
        with patch('app.routes.files.gemini_service') as mock_service, \
             patch('app.routes.files.os.makedirs'), \
             patch('app.routes.files.os.remove'):

            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_service.create_file_search_store.return_value = mock_store

            mock_operation = Mock()
            mock_operation.done = True
            mock_service.upload_file_to_store.return_value = mock_operation

            data = {
                'file': (BytesIO(b'test content'), 'test.pdf'),
                'store_name': 'test-store'
            }

            response = client.post(
                '/api/files/upload_file',
                data=data,
                content_type='multipart/form-data'
            )

            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert 'uploaded and indexed successfully' in response_data['message']

    def test_upload_file_no_file(self, client):
        """Test upload without file"""
        response = client.post(
            '/api/files/upload_file',
            data={},
            content_type='multipart/form-data'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No file provided' in data['error']

    def test_list_stores(self, client):
        """Test listing all stores"""
        # First create a store
        with patch('app.routes.files.gemini_service') as mock_service:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_service.create_file_search_store.return_value = mock_store

            client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

            # Now list stores
            response = client.get('/api/files/list_stores')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'test-store' in data['stores']
