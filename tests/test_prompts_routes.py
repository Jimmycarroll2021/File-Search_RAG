"""
Tests for prompts routes/endpoints.

Tests all CRUD endpoints, usage tracking, and popular prompts.
"""
import pytest
import json
from app.models import SmartPrompt
from app.database import db


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def sample_prompts(app):
    """Create sample prompts for testing."""
    with app.app_context():
        prompts = [
            SmartPrompt(
                title="Compliance Matrix",
                prompt_text="Generate a detailed compliance matrix...",
                category="Tender Response",
                response_mode="tender",
                usage_count=10
            ),
            SmartPrompt(
                title="Win Themes",
                prompt_text="Analyze tender requirements...",
                category="Strategy",
                response_mode="strategy",
                usage_count=5
            ),
            SmartPrompt(
                title="Pricing Benchmarks",
                prompt_text="Find pricing benchmarks...",
                category="Pricing & Commercial",
                response_mode="precise",
                usage_count=8
            ),
        ]
        for prompt in prompts:
            db.session.add(prompt)
        db.session.commit()

        # Refresh to get IDs
        for prompt in prompts:
            db.session.refresh(prompt)

        yield prompts

        # Cleanup
        SmartPrompt.query.delete()
        db.session.commit()


class TestGetAllPromptsEndpoint:
    """Test GET /api/prompts endpoint."""

    def test_get_all_prompts_empty(self, client):
        """Test getting prompts when none exist."""
        response = client.get('/api/prompts')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['prompts'] == []
        assert data['count'] == 0

    def test_get_all_prompts(self, client, sample_prompts):
        """Test getting all prompts."""
        response = client.get('/api/prompts')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['prompts']) == 3
        assert data['count'] == 3

        # Verify structure of returned prompts
        prompt = data['prompts'][0]
        assert 'id' in prompt
        assert 'title' in prompt
        assert 'prompt_text' in prompt
        assert 'category' in prompt
        assert 'response_mode' in prompt
        assert 'usage_count' in prompt
        assert 'created_at' in prompt

    def test_search_prompts(self, client, sample_prompts):
        """Test searching prompts with query parameter."""
        response = client.get('/api/prompts?query=Compliance')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['prompts']) == 1
        assert data['prompts'][0]['title'] == 'Compliance Matrix'

    def test_filter_by_category(self, client, sample_prompts):
        """Test filtering prompts by category."""
        response = client.get('/api/prompts?category=Strategy')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['prompts']) == 1
        assert data['prompts'][0]['category'] == 'Strategy'

    def test_search_with_category(self, client, sample_prompts):
        """Test combined search and category filter."""
        response = client.get('/api/prompts?query=Matrix&category=Tender Response')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['prompts']) == 1


class TestCreatePromptEndpoint:
    """Test POST /api/prompts endpoint."""

    def test_create_prompt_success(self, client):
        """Test creating a new prompt."""
        prompt_data = {
            'title': 'Risk Assessment',
            'prompt_text': 'Identify and analyze risks...',
            'category': 'Tender Response',
            'response_mode': 'comprehensive'
        }

        response = client.post(
            '/api/prompts',
            data=json.dumps(prompt_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['prompt']['title'] == 'Risk Assessment'
        assert data['prompt']['usage_count'] == 0
        assert 'id' in data['prompt']

    def test_create_prompt_missing_title(self, client):
        """Test creating prompt without title."""
        prompt_data = {
            'prompt_text': 'Some text...',
            'category': 'Test'
        }

        response = client.post(
            '/api/prompts',
            data=json.dumps(prompt_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data

    def test_create_prompt_missing_text(self, client):
        """Test creating prompt without prompt_text."""
        prompt_data = {
            'title': 'Test Title',
            'category': 'Test'
        }

        response = client.post(
            '/api/prompts',
            data=json.dumps(prompt_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data

    def test_create_prompt_no_json(self, client):
        """Test creating prompt without JSON body."""
        response = client.post('/api/prompts')
        assert response.status_code == 400


class TestUpdatePromptEndpoint:
    """Test PUT /api/prompts/<id> endpoint."""

    def test_update_prompt_success(self, client, sample_prompts):
        """Test updating an existing prompt."""
        prompt_id = sample_prompts[0].id
        update_data = {
            'title': 'Updated Compliance Matrix',
            'category': 'Compliance'
        }

        response = client.put(
            f'/api/prompts/{prompt_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['prompt']['title'] == 'Updated Compliance Matrix'
        assert data['prompt']['category'] == 'Compliance'

    def test_update_prompt_not_found(self, client):
        """Test updating non-existent prompt."""
        update_data = {'title': 'Test'}

        response = client.put(
            '/api/prompts/99999',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False

    def test_update_prompt_no_json(self, client, sample_prompts):
        """Test updating without JSON body."""
        prompt_id = sample_prompts[0].id
        response = client.put(f'/api/prompts/{prompt_id}')
        assert response.status_code == 400


class TestDeletePromptEndpoint:
    """Test DELETE /api/prompts/<id> endpoint."""

    def test_delete_prompt_success(self, client, sample_prompts):
        """Test deleting a prompt."""
        prompt_id = sample_prompts[0].id

        response = client.delete(f'/api/prompts/{prompt_id}')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True

        # Verify deletion
        get_response = client.get(f'/api/prompts')
        prompts = get_response.get_json()['prompts']
        assert len(prompts) == 2

    def test_delete_prompt_not_found(self, client):
        """Test deleting non-existent prompt."""
        response = client.delete('/api/prompts/99999')
        assert response.status_code == 404

        data = response.get_json()
        assert data['success'] is False


class TestIncrementUsageEndpoint:
    """Test POST /api/prompts/<id>/use endpoint."""

    def test_increment_usage_success(self, client, sample_prompts):
        """Test incrementing usage count."""
        prompt_id = sample_prompts[0].id
        original_count = sample_prompts[0].usage_count

        response = client.post(f'/api/prompts/{prompt_id}/use')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['prompt']['usage_count'] == original_count + 1

    def test_increment_usage_not_found(self, client):
        """Test incrementing usage for non-existent prompt."""
        response = client.post('/api/prompts/99999/use')
        assert response.status_code == 404

        data = response.get_json()
        assert data['success'] is False


class TestGetPopularPromptsEndpoint:
    """Test GET /api/prompts/popular endpoint."""

    def test_get_popular_prompts(self, client, sample_prompts):
        """Test getting most-used prompts."""
        response = client.get('/api/prompts/popular')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['prompts']) == 3

        # Verify ordering by usage count
        prompts = data['prompts']
        assert prompts[0]['usage_count'] >= prompts[1]['usage_count']
        assert prompts[1]['usage_count'] >= prompts[2]['usage_count']
        assert prompts[0]['title'] == 'Compliance Matrix'  # usage_count=10

    def test_get_popular_prompts_with_limit(self, client, sample_prompts):
        """Test getting popular prompts with limit."""
        response = client.get('/api/prompts/popular?limit=2')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['prompts']) == 2

    def test_get_popular_prompts_empty(self, client):
        """Test getting popular prompts when none exist."""
        response = client.get('/api/prompts/popular')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['prompts'] == []


class TestGetCategoriesEndpoint:
    """Test GET /api/prompts/categories endpoint."""

    def test_get_categories(self, client, sample_prompts):
        """Test getting unique categories."""
        response = client.get('/api/prompts/categories')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['categories']) == 3
        assert 'Tender Response' in data['categories']
        assert 'Strategy' in data['categories']
        assert 'Pricing & Commercial' in data['categories']

    def test_get_categories_empty(self, client):
        """Test getting categories when no prompts exist."""
        response = client.get('/api/prompts/categories')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['categories'] == []


class TestErrorHandling:
    """Test error handling in routes."""

    def test_invalid_prompt_id_format(self, client):
        """Test with invalid ID format."""
        response = client.get('/api/prompts/invalid')
        # Should return 404 or 400 depending on implementation
        assert response.status_code in [400, 404]

    def test_malformed_json(self, client):
        """Test with malformed JSON."""
        response = client.post(
            '/api/prompts',
            data='{"invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400
