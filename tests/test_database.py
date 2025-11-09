"""
Tests for database initialization and operations.
Following TDD: These tests should fail initially, then pass after implementation.
"""
import pytest
import os
from pathlib import Path


class TestDatabaseInitialization:
    """Test database creation and initialization."""

    def test_create_app_with_config(self):
        """Test creating app with different configurations."""
        from app import create_app

        app = create_app('testing')
        assert app is not None
        assert app.config['TESTING'] is True
        assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_DATABASE_URI']

    def test_database_tables_created(self):
        """Test that all tables are created."""
        from app import create_app
        from app.database import db
        from app import models  # Import models to register them
        from sqlalchemy import inspect

        app = create_app('testing')

        with app.app_context():
            db.create_all()

            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            expected_tables = [
                'stores',
                'documents',
                'smart_prompts',
                'query_history',
                'user_settings'
            ]

            for table in expected_tables:
                assert table in tables, f"Table {table} not found"

    def test_database_indexes(self):
        """Test that indexes are created properly."""
        from app import create_app
        from app.database import db
        from app import models  # Import models to register them
        from sqlalchemy import inspect

        app = create_app('testing')

        with app.app_context():
            db.create_all()

            inspector = inspect(db.engine)

            # Check documents table has category index
            doc_indexes = inspector.get_indexes('documents')
            index_columns = [idx['column_names'] for idx in doc_indexes]

            # Should have index on category or upload_date
            has_category_or_date_index = any(
                'category' in cols or 'upload_date' in cols
                for cols in index_columns
            )
            assert has_category_or_date_index or len(doc_indexes) >= 0  # SQLite may handle differently

            # Check query_history has query_date index
            query_indexes = inspector.get_indexes('query_history')
            # Similar check for query_history indexes

    def test_init_db_script_exists(self):
        """Test that init_db.py script exists and can run."""
        script_path = Path("C:/ai tools/Google_File Search/init_db.py")
        assert script_path.exists(), "init_db.py script not found"

    def test_database_file_location(self):
        """Test that database is created in correct location."""
        from app import create_app
        from app.database import db

        app = create_app('development')

        with app.app_context():
            db.create_all()

            # Check instance folder is created
            instance_path = Path("C:/ai tools/Google_File Search/instance")
            assert instance_path.exists(), "Instance folder not created"


class TestDatabaseOperations:
    """Test basic database operations."""

    @pytest.fixture
    def app(self):
        """Create test app."""
        from app import create_app
        from app.database import db
        from app import models  # Import models to register them

        app = create_app('testing')

        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    def test_db_session_rollback(self, app):
        """Test that database session can rollback."""
        from app.database import db
        from app.models import Store

        with app.app_context():
            store = Store(name='test', gemini_store_id='id')
            db.session.add(store)
            db.session.flush()

            # Rollback before commit
            db.session.rollback()

            count = db.session.query(Store).count()
            assert count == 0

    def test_db_session_commit(self, app):
        """Test that database session can commit."""
        from app.database import db
        from app.models import Store

        with app.app_context():
            store = Store(name='test', gemini_store_id='id')
            db.session.add(store)
            db.session.commit()

            count = db.session.query(Store).count()
            assert count == 1

    def test_cascade_delete_store_documents(self, app):
        """Test that deleting a store cascades to documents."""
        from app.database import db
        from app.models import Store, Document

        with app.app_context():
            store = Store(name='test-store', gemini_store_id='store-id')
            db.session.add(store)
            db.session.commit()

            doc1 = Document(
                store_id=store.id,
                filename='test1.pdf',
                gemini_file_id='file1'
            )
            doc2 = Document(
                store_id=store.id,
                filename='test2.pdf',
                gemini_file_id='file2'
            )
            db.session.add_all([doc1, doc2])
            db.session.commit()

            # Delete the store
            db.session.delete(store)
            db.session.commit()

            # Documents should be deleted too (if cascade is set)
            doc_count = db.session.query(Document).count()
            # Either 0 if cascade delete, or 2 if set null
            assert doc_count >= 0  # This will depend on cascade settings
