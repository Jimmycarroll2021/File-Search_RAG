"""
Tests for query blueprint routes
"""
import pytest
import json
from unittest.mock import Mock, patch


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


class TestQueryBlueprint:
    """Test cases for query blueprint routes"""

    def test_query_success(self, client):
        """Test successful query"""
        # First create a store
        with patch('app.routes.files.gemini_service') as mock_files_service:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_files_service.create_file_search_store.return_value = mock_store

            client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

        # Now query
        with patch('app.routes.query.gemini_service') as mock_query_service:
            mock_query_service.query_with_file_search.return_value = 'This is the answer to your question'

            response = client.post(
                '/api/query/query',
                data=json.dumps({
                    'question': 'What is this about?',
                    'store_name': 'test-store'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['answer'] == 'This is the answer to your question'
            assert data['question'] == 'What is this about?'

    def test_query_no_question(self, client):
        """Test query without question"""
        response = client.post(
            '/api/query/query',
            data=json.dumps({'store_name': 'test-store'}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No question provided' in data['error']

    def test_query_store_not_found(self, client):
        """Test query with non-existent store"""
        response = client.post(
            '/api/query/query',
            data=json.dumps({
                'question': 'What is this?',
                'store_name': 'non-existent-store'
            }),
            content_type='application/json'
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error']

    def test_query_error(self, client):
        """Test query error handling"""
        # First create a store
        with patch('app.routes.files.gemini_service') as mock_files_service:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_files_service.create_file_search_store.return_value = mock_store

            client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

        # Now query with error
        with patch('app.routes.query.gemini_service') as mock_query_service:
            mock_query_service.query_with_file_search.side_effect = Exception('API Error')

            response = client.post(
                '/api/query/query',
                data=json.dumps({
                    'question': 'What is this?',
                    'store_name': 'test-store'
                }),
                content_type='application/json'
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'API Error' in data['error']

    def test_query_with_tender_mode(self, client):
        """Test query with tender response mode"""
        # First create a store
        with patch('app.routes.files.gemini_service') as mock_files_service:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_files_service.create_file_search_store.return_value = mock_store
            client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

        # Query with tender mode
        with patch('app.routes.query.gemini_service') as mock_query_service:
            mock_query_service.query_with_file_search.return_value = 'Formal tender response'

            response = client.post(
                '/api/query/query',
                data=json.dumps({
                    'question': 'What are the compliance requirements?',
                    'store_name': 'test-store',
                    'mode': 'tender'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['answer'] == 'Formal tender response'
            assert data['mode'] == 'tender'
            assert data['mode_name'] == 'Tender Response'

            # Verify system prompt and temperature were passed
            call_args = mock_query_service.query_with_file_search.call_args
            assert call_args.kwargs['temperature'] == 0.3
            assert 'tender response specialist' in call_args.kwargs['system_prompt'].lower()

    def test_query_with_quick_mode(self, client):
        """Test query with quick answer mode"""
        with patch('app.routes.files.gemini_service') as mock_files_service:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_files_service.create_file_search_store.return_value = mock_store
            client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

        with patch('app.routes.query.gemini_service') as mock_query_service:
            mock_query_service.query_with_file_search.return_value = 'Quick answer'

            response = client.post(
                '/api/query/query',
                data=json.dumps({
                    'question': 'Brief overview?',
                    'store_name': 'test-store',
                    'mode': 'quick'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['mode'] == 'quick'
            call_args = mock_query_service.query_with_file_search.call_args
            assert call_args.kwargs['temperature'] == 0.5

    def test_query_with_invalid_mode_defaults_to_quick(self, client):
        """Test query with invalid mode defaults to quick mode"""
        with patch('app.routes.files.gemini_service') as mock_files_service:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_files_service.create_file_search_store.return_value = mock_store
            client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

        with patch('app.routes.query.gemini_service') as mock_query_service:
            mock_query_service.query_with_file_search.return_value = 'Answer'

            response = client.post(
                '/api/query/query',
                data=json.dumps({
                    'question': 'Test question',
                    'store_name': 'test-store',
                    'mode': 'invalid_mode'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['mode'] == 'quick'  # Should default to quick
            assert data['mode_name'] == 'Quick Answer'

    def test_query_without_mode_defaults_to_quick(self, client):
        """Test query without mode parameter defaults to quick mode"""
        with patch('app.routes.files.gemini_service') as mock_files_service:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_files_service.create_file_search_store.return_value = mock_store
            client.post(
                '/api/files/create_store',
                data=json.dumps({'store_name': 'test-store'}),
                content_type='application/json'
            )

        with patch('app.routes.query.gemini_service') as mock_query_service:
            mock_query_service.query_with_file_search.return_value = 'Answer'

            response = client.post(
                '/api/query/query',
                data=json.dumps({
                    'question': 'Test question',
                    'store_name': 'test-store'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['mode'] == 'quick'
