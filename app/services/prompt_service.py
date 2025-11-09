"""
Service layer for smart prompts management.

Provides CRUD operations, search/filter logic, and usage tracking
for reusable query templates.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import or_, desc
from app.models import SmartPrompt
from app.database import db


class PromptService:
    """Service for managing smart prompts."""

    def get_all_prompts(self) -> List[SmartPrompt]:
        """
        Get all prompts.

        Returns:
            List of all SmartPrompt objects.
        """
        return SmartPrompt.query.all()

    def get_prompt_by_id(self, prompt_id: int) -> Optional[SmartPrompt]:
        """
        Get a specific prompt by ID.

        Args:
            prompt_id: The ID of the prompt to retrieve.

        Returns:
            SmartPrompt object or None if not found.
        """
        return SmartPrompt.query.get(prompt_id)

    def create_prompt(self, prompt_data: Dict[str, Any]) -> SmartPrompt:
        """
        Create a new prompt.

        Args:
            prompt_data: Dictionary containing prompt fields:
                - title (required)
                - prompt_text (required)
                - category (optional)
                - response_mode (optional)

        Returns:
            Created SmartPrompt object.

        Raises:
            ValueError: If required fields are missing or invalid.
            KeyError: If required fields are not in prompt_data.
        """
        # Validate required fields
        if not prompt_data.get('title'):
            raise ValueError("Title is required and cannot be empty")
        if not prompt_data.get('prompt_text'):
            raise ValueError("Prompt text is required and cannot be empty")

        # Create new prompt
        prompt = SmartPrompt(
            title=prompt_data['title'],
            prompt_text=prompt_data['prompt_text'],
            category=prompt_data.get('category'),
            response_mode=prompt_data.get('response_mode'),
            usage_count=0
        )

        db.session.add(prompt)
        db.session.commit()
        db.session.refresh(prompt)

        return prompt

    def update_prompt(self, prompt_id: int, update_data: Dict[str, Any]) -> Optional[SmartPrompt]:
        """
        Update an existing prompt.

        Args:
            prompt_id: The ID of the prompt to update.
            update_data: Dictionary containing fields to update.

        Returns:
            Updated SmartPrompt object or None if not found.
        """
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            return None

        # Update fields if provided
        if 'title' in update_data:
            prompt.title = update_data['title']
        if 'prompt_text' in update_data:
            prompt.prompt_text = update_data['prompt_text']
        if 'category' in update_data:
            prompt.category = update_data['category']
        if 'response_mode' in update_data:
            prompt.response_mode = update_data['response_mode']

        db.session.commit()
        db.session.refresh(prompt)

        return prompt

    def delete_prompt(self, prompt_id: int) -> bool:
        """
        Delete a prompt.

        Args:
            prompt_id: The ID of the prompt to delete.

        Returns:
            True if deleted, False if not found.
        """
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            return False

        db.session.delete(prompt)
        db.session.commit()

        return True

    def search_prompts(self, query: str, category: Optional[str] = None) -> List[SmartPrompt]:
        """
        Search prompts by query string.

        Searches in title and prompt_text fields (case-insensitive).

        Args:
            query: Search query string.
            category: Optional category filter.

        Returns:
            List of matching SmartPrompt objects.
        """
        # Build base query with search
        search_query = SmartPrompt.query.filter(
            or_(
                SmartPrompt.title.ilike(f'%{query}%'),
                SmartPrompt.prompt_text.ilike(f'%{query}%')
            )
        )

        # Apply category filter if provided
        if category:
            search_query = search_query.filter(SmartPrompt.category == category)

        return search_query.all()

    def filter_by_category(self, category: str) -> List[SmartPrompt]:
        """
        Filter prompts by category.

        Args:
            category: The category to filter by.

        Returns:
            List of SmartPrompt objects in the category.
        """
        return SmartPrompt.query.filter_by(category=category).all()

    def increment_usage(self, prompt_id: int) -> Optional[SmartPrompt]:
        """
        Increment the usage count for a prompt.

        Args:
            prompt_id: The ID of the prompt.

        Returns:
            Updated SmartPrompt object or None if not found.
        """
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            return None

        prompt.usage_count += 1
        db.session.commit()
        db.session.refresh(prompt)

        return prompt

    def get_popular_prompts(self, limit: int = 10) -> List[SmartPrompt]:
        """
        Get most-used prompts ordered by usage count.

        Args:
            limit: Maximum number of prompts to return.

        Returns:
            List of SmartPrompt objects ordered by usage count (descending).
        """
        return SmartPrompt.query.order_by(desc(SmartPrompt.usage_count)).limit(limit).all()

    def get_recent_prompts(self, limit: int = 10) -> List[SmartPrompt]:
        """
        Get recently created prompts.

        Args:
            limit: Maximum number of prompts to return.

        Returns:
            List of SmartPrompt objects ordered by created_at (descending).
        """
        return SmartPrompt.query.order_by(desc(SmartPrompt.created_at)).limit(limit).all()

    def seed_prompts(self, prompts_data: List[Dict[str, Any]]) -> int:
        """
        Seed default prompts from a list.

        Skips prompts that already exist (by title).

        Args:
            prompts_data: List of dictionaries containing prompt data.

        Returns:
            Number of prompts created.
        """
        created_count = 0

        for prompt_data in prompts_data:
            # Check if prompt with this title already exists
            existing = SmartPrompt.query.filter_by(title=prompt_data['title']).first()
            if existing:
                continue

            # Create new prompt
            prompt = SmartPrompt(
                title=prompt_data['title'],
                prompt_text=prompt_data['prompt_text'],
                category=prompt_data.get('category'),
                response_mode=prompt_data.get('response_mode'),
                usage_count=0
            )
            db.session.add(prompt)
            created_count += 1

        if created_count > 0:
            db.session.commit()

        return created_count

    def get_categories(self) -> List[str]:
        """
        Get all unique categories.

        Returns:
            List of unique category names.
        """
        categories = db.session.query(SmartPrompt.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]
