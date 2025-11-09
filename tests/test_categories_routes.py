"""
Tests for category routes API.

Tests the /api/categories endpoints for listing categories and getting statistics.
"""
import pytest
import json
from app.models import Document, Store
from app.database import db


class TestCategoriesRoutes:
    """Test category listing and configuration endpoints."""

    def test_get_categories_list(self, app):
        """Test GET /api/categories returns all categories."""
        with app.test_client() as client:
            response = client.get('/api/categories')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] is True
            assert 'categories' in data
            assert len(data['categories']) == 9

            # Verify each category has required fields
            for category in data['categories']:
                assert 'name' in category
                assert 'color' in category
                assert 'icon' in category
                assert 'description' in category

    def test_categories_include_all_expected(self, app):
        """Test that all expected categories are present."""
        with app.test_client() as client:
            response = client.get('/api/categories')
            data = json.loads(response.data)

            category_names = {cat['name'] for cat in data['categories']}
            expected_categories = {
                'compliance', 'contracts', 'proposals', 'pricing',
                'requirements', 'technical', 'cvs_resumes', 'policies', 'other'
            }

            assert category_names == expected_categories

    def test_get_category_stats_empty(self, app):
        """Test GET /api/categories/stats with no documents."""
        with app.test_client() as client:
            response = client.get('/api/categories/stats')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] is True
            assert 'stats' in data
            assert len(data['stats']) == 9

            # All categories should have 0 count
            for category, count in data['stats'].items():
                assert count == 0

    def test_get_category_stats_with_documents(self, app):
        """Test GET /api/categories/stats with actual documents."""
        with app.app_context():
            # Create test store
            store = Store(
                name='test-store',
                gemini_store_id='test-gemini-store-123',
                display_name='Test Store'
            )
            db.session.add(store)
            db.session.commit()

            # Add documents with different categories
            documents = [
                Document(store_id=store.id, filename='doc1.pdf', category='compliance'),
                Document(store_id=store.id, filename='doc2.pdf', category='compliance'),
                Document(store_id=store.id, filename='doc3.pdf', category='proposals'),
                Document(store_id=store.id, filename='doc4.pdf', category='technical'),
                Document(store_id=store.id, filename='doc5.pdf', category='technical'),
                Document(store_id=store.id, filename='doc6.pdf', category='technical'),
            ]

            for doc in documents:
                db.session.add(doc)
            db.session.commit()

        # Make request
        with app.test_client() as client:
            response = client.get('/api/categories/stats')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] is True
            assert data['stats']['compliance'] == 2
            assert data['stats']['proposals'] == 1
            assert data['stats']['technical'] == 3
            assert data['stats']['contracts'] == 0

        # Cleanup
        with app.app_context():
            for doc in documents:
                db.session.delete(doc)
            db.session.delete(store)
            db.session.commit()

    def test_category_stats_total_count(self, app):
        """Test that stats include total_count field."""
        with app.app_context():
            store = Store(
                name='test-store-2',
                gemini_store_id='test-gemini-store-456',
                display_name='Test Store 2'
            )
            db.session.add(store)
            db.session.commit()

            documents = [
                Document(store_id=store.id, filename='doc1.pdf', category='compliance'),
                Document(store_id=store.id, filename='doc2.pdf', category='proposals'),
                Document(store_id=store.id, filename='doc3.pdf', category='technical'),
            ]

            for doc in documents:
                db.session.add(doc)
            db.session.commit()

        with app.test_client() as client:
            response = client.get('/api/categories/stats')
            data = json.loads(response.data)

            assert 'total_count' in data
            assert data['total_count'] == 3

        # Cleanup
        with app.app_context():
            for doc in documents:
                db.session.delete(doc)
            db.session.delete(store)
            db.session.commit()
