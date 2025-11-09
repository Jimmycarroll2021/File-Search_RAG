"""
Tests for prompt service.

Tests CRUD operations, search/filter logic, and usage tracking
for smart prompts.
"""
import pytest
from datetime import datetime
from app.models import SmartPrompt
from app.services.prompt_service import PromptService
from app.database import db


@pytest.fixture
def prompt_service(app):
    """Create a prompt service instance."""
    with app.app_context():
        yield PromptService()


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


class TestPromptServiceCRUD:
    """Test CRUD operations."""

    def test_get_all_prompts(self, prompt_service, sample_prompts):
        """Test retrieving all prompts."""
        prompts = prompt_service.get_all_prompts()
        assert len(prompts) == 3
        assert all(isinstance(p, SmartPrompt) for p in prompts)

    def test_get_prompt_by_id(self, prompt_service, sample_prompts):
        """Test retrieving a specific prompt by ID."""
        prompt_id = sample_prompts[0].id
        prompt = prompt_service.get_prompt_by_id(prompt_id)
        assert prompt is not None
        assert prompt.title == "Compliance Matrix"
        assert prompt.category == "Tender Response"

    def test_get_prompt_by_id_not_found(self, prompt_service):
        """Test retrieving non-existent prompt."""
        prompt = prompt_service.get_prompt_by_id(99999)
        assert prompt is None

    def test_create_prompt(self, prompt_service):
        """Test creating a new prompt."""
        prompt_data = {
            'title': 'Risk Assessment',
            'prompt_text': 'Identify and analyze risks...',
            'category': 'Tender Response',
            'response_mode': 'comprehensive'
        }

        prompt = prompt_service.create_prompt(prompt_data)
        assert prompt is not None
        assert prompt.id is not None
        assert prompt.title == 'Risk Assessment'
        assert prompt.usage_count == 0
        assert prompt.created_at is not None

    def test_update_prompt(self, prompt_service, sample_prompts):
        """Test updating an existing prompt."""
        prompt_id = sample_prompts[0].id
        update_data = {
            'title': 'Updated Compliance Matrix',
            'prompt_text': 'New compliance text...',
            'category': 'Compliance'
        }

        updated_prompt = prompt_service.update_prompt(prompt_id, update_data)
        assert updated_prompt is not None
        assert updated_prompt.title == 'Updated Compliance Matrix'
        assert updated_prompt.category == 'Compliance'
        assert updated_prompt.response_mode == 'tender'  # Unchanged

    def test_update_prompt_not_found(self, prompt_service):
        """Test updating non-existent prompt."""
        result = prompt_service.update_prompt(99999, {'title': 'Test'})
        assert result is None

    def test_delete_prompt(self, prompt_service, sample_prompts):
        """Test deleting a prompt."""
        prompt_id = sample_prompts[0].id
        result = prompt_service.delete_prompt(prompt_id)
        assert result is True

        # Verify deletion
        deleted_prompt = prompt_service.get_prompt_by_id(prompt_id)
        assert deleted_prompt is None

    def test_delete_prompt_not_found(self, prompt_service):
        """Test deleting non-existent prompt."""
        result = prompt_service.delete_prompt(99999)
        assert result is False


class TestPromptServiceSearch:
    """Test search and filter functionality."""

    def test_search_prompts_by_title(self, prompt_service, sample_prompts):
        """Test searching prompts by title."""
        results = prompt_service.search_prompts(query="Compliance")
        assert len(results) == 1
        assert results[0].title == "Compliance Matrix"

    def test_search_prompts_by_text(self, prompt_service, sample_prompts):
        """Test searching prompts by prompt text."""
        results = prompt_service.search_prompts(query="tender")
        assert len(results) >= 1

    def test_search_prompts_case_insensitive(self, prompt_service, sample_prompts):
        """Test case-insensitive search."""
        results = prompt_service.search_prompts(query="PRICING")
        assert len(results) == 1
        assert results[0].title == "Pricing Benchmarks"

    def test_filter_by_category(self, prompt_service, sample_prompts):
        """Test filtering prompts by category."""
        results = prompt_service.filter_by_category("Strategy")
        assert len(results) == 1
        assert results[0].category == "Strategy"

    def test_filter_by_category_multiple_results(self, prompt_service, sample_prompts):
        """Test filtering with multiple results."""
        # Add another Tender Response prompt
        new_prompt = SmartPrompt(
            title="Executive Summary",
            prompt_text="Create executive summary...",
            category="Tender Response",
            response_mode="comprehensive"
        )
        db.session.add(new_prompt)
        db.session.commit()

        results = prompt_service.filter_by_category("Tender Response")
        assert len(results) == 2

    def test_search_with_category_filter(self, prompt_service, sample_prompts):
        """Test combined search and category filter."""
        results = prompt_service.search_prompts(
            query="Matrix",
            category="Tender Response"
        )
        assert len(results) == 1
        assert results[0].title == "Compliance Matrix"


class TestPromptServiceUsageTracking:
    """Test usage tracking functionality."""

    def test_increment_usage_count(self, prompt_service, sample_prompts):
        """Test incrementing usage count."""
        prompt_id = sample_prompts[0].id
        original_count = sample_prompts[0].usage_count

        prompt = prompt_service.increment_usage(prompt_id)
        assert prompt is not None
        assert prompt.usage_count == original_count + 1

    def test_increment_usage_count_not_found(self, prompt_service):
        """Test incrementing usage for non-existent prompt."""
        result = prompt_service.increment_usage(99999)
        assert result is None

    def test_get_popular_prompts(self, prompt_service, sample_prompts):
        """Test retrieving most-used prompts."""
        popular = prompt_service.get_popular_prompts(limit=2)
        assert len(popular) == 2
        # Should be ordered by usage count descending
        assert popular[0].usage_count >= popular[1].usage_count
        assert popular[0].title == "Compliance Matrix"  # usage_count=10

    def test_get_popular_prompts_default_limit(self, prompt_service, sample_prompts):
        """Test default limit for popular prompts."""
        popular = prompt_service.get_popular_prompts()
        assert len(popular) <= 10

    def test_get_recent_prompts(self, prompt_service, sample_prompts):
        """Test retrieving recently created prompts."""
        recent = prompt_service.get_recent_prompts(limit=2)
        assert len(recent) == 2
        # Should be ordered by created_at descending
        assert recent[0].created_at >= recent[1].created_at


class TestPromptServiceSeeding:
    """Test seeding functionality for default prompts."""

    def test_seed_default_prompts(self, prompt_service):
        """Test seeding default prompts from JSON."""
        default_prompts = [
            {
                "title": "Test Prompt 1",
                "prompt_text": "Test text 1",
                "category": "Test Category",
                "response_mode": "test"
            },
            {
                "title": "Test Prompt 2",
                "prompt_text": "Test text 2",
                "category": "Test Category",
                "response_mode": "test"
            }
        ]

        count = prompt_service.seed_prompts(default_prompts)
        assert count == 2

        # Verify prompts were created
        all_prompts = prompt_service.get_all_prompts()
        assert len(all_prompts) == 2

    def test_seed_prompts_skip_existing(self, prompt_service, sample_prompts):
        """Test that seeding skips existing prompts."""
        initial_count = len(prompt_service.get_all_prompts())

        # Try to seed with overlapping titles
        default_prompts = [
            {
                "title": "Compliance Matrix",  # Already exists
                "prompt_text": "Different text",
                "category": "Different",
                "response_mode": "different"
            },
            {
                "title": "New Prompt",
                "prompt_text": "New text",
                "category": "New",
                "response_mode": "new"
            }
        ]

        count = prompt_service.seed_prompts(default_prompts)
        assert count == 1  # Only one new prompt added

        all_prompts = prompt_service.get_all_prompts()
        assert len(all_prompts) == initial_count + 1


class TestPromptServiceValidation:
    """Test validation and error handling."""

    def test_create_prompt_missing_required_fields(self, prompt_service):
        """Test creating prompt with missing required fields."""
        with pytest.raises((ValueError, KeyError, TypeError)):
            prompt_service.create_prompt({'title': 'Test'})

    def test_create_prompt_empty_title(self, prompt_service):
        """Test creating prompt with empty title."""
        with pytest.raises((ValueError, TypeError)):
            prompt_service.create_prompt({
                'title': '',
                'prompt_text': 'Test',
                'category': 'Test',
                'response_mode': 'test'
            })
