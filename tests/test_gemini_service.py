"""
Tests for Gemini service module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.gemini_service import GeminiService


class TestGeminiService:
    """Test cases for GeminiService"""

    def test_service_initialization(self):
        """Test that GeminiService initializes with a Gemini client"""
        service = GeminiService()
        assert service.client is not None

    def test_create_file_search_store(self):
        """Test creating a file search store"""
        with patch('app.services.gemini_service.genai.Client') as mock_client:
            mock_store = Mock()
            mock_store.name = 'stores/test-store-123'
            mock_client.return_value.file_search_stores.create.return_value = mock_store

            service = GeminiService()
            result = service.create_file_search_store('test-store')

            assert result.name == 'stores/test-store-123'
            mock_client.return_value.file_search_stores.create.assert_called_once()

    def test_upload_file_to_store(self):
        """Test uploading file to file search store"""
        with patch('app.services.gemini_service.genai.Client') as mock_client:
            mock_operation = Mock()
            mock_operation.done = True
            mock_client.return_value.file_search_stores.upload_to_file_search_store.return_value = mock_operation
            mock_client.return_value.operations.get.return_value = mock_operation

            service = GeminiService()
            result = service.upload_file_to_store(
                file_path='test.pdf',
                store_id='stores/test-123',
                display_name='test.pdf'
            )

            assert result.done is True
            mock_client.return_value.file_search_stores.upload_to_file_search_store.assert_called_once()

    def test_query_with_file_search(self):
        """Test querying with file search"""
        with patch('app.services.gemini_service.genai.Client') as mock_client:
            mock_response = Mock()
            mock_response.text = 'This is the answer'
            mock_client.return_value.models.generate_content.return_value = mock_response

            service = GeminiService()
            result = service.query_with_file_search(
                question='What is this about?',
                store_id='stores/test-123'
            )

            assert result == 'This is the answer'
            mock_client.return_value.models.generate_content.assert_called_once()

    def test_query_with_system_prompt(self):
        """Test querying with custom system prompt"""
        with patch('app.services.gemini_service.genai.Client') as mock_client:
            mock_response = Mock()
            mock_response.text = 'Expert analysis result'
            mock_client.return_value.models.generate_content.return_value = mock_response

            service = GeminiService()
            result = service.query_with_file_search(
                question='Analyze this tender',
                store_id='stores/test-123',
                system_prompt='You are an expert tender analyst.'
            )

            assert result == 'Expert analysis result'
            # Verify system_instruction was passed in config
            call_args = mock_client.return_value.models.generate_content.call_args
            config = call_args.kwargs['config']
            assert config.system_instruction == 'You are an expert tender analyst.'

    def test_query_with_temperature(self):
        """Test querying with custom temperature"""
        with patch('app.services.gemini_service.genai.Client') as mock_client:
            mock_response = Mock()
            mock_response.text = 'Creative response'
            mock_client.return_value.models.generate_content.return_value = mock_response

            service = GeminiService()
            result = service.query_with_file_search(
                question='Generate ideas',
                store_id='stores/test-123',
                temperature=0.8
            )

            assert result == 'Creative response'
            # Verify temperature was passed in config
            call_args = mock_client.return_value.models.generate_content.call_args
            config = call_args.kwargs['config']
            assert config.temperature == 0.8

    def test_query_with_system_prompt_and_temperature(self):
        """Test querying with both system prompt and temperature"""
        with patch('app.services.gemini_service.genai.Client') as mock_client:
            mock_response = Mock()
            mock_response.text = 'Formal tender response'
            mock_client.return_value.models.generate_content.return_value = mock_response

            service = GeminiService()
            result = service.query_with_file_search(
                question='What are the requirements?',
                store_id='stores/test-123',
                system_prompt='You are a tender specialist.',
                temperature=0.3
            )

            assert result == 'Formal tender response'
            call_args = mock_client.return_value.models.generate_content.call_args
            config = call_args.kwargs['config']
            assert config.system_instruction == 'You are a tender specialist.'
            assert config.temperature == 0.3
