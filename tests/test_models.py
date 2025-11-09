"""
Tests for SQLAlchemy database models.
Following TDD: These tests should fail initially, then pass after implementation.
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import json


@pytest.fixture(scope='function')
def test_app():
    """Create and configure a test app instance."""
    from app import create_app
    from app.database import db

    # Import models before creating tables
    from app import models

    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def db_session(test_app):
    """Provide a database session for tests."""
    from app.database import db

    with test_app.app_context():
        yield db.session
        db.session.rollback()


class TestStoreModel:
    """Test the Store model for file search store metadata."""

    def test_create_store(self, db_session):
        """Test creating a basic store."""
        from app.models import Store

        store = Store(
            name='test-store',
            gemini_store_id='stores/test-store-123',
            display_name='Test Store'
        )
        db_session.add(store)
        db_session.commit()

        assert store.id is not None
        assert store.name == 'test-store'
        assert store.gemini_store_id == 'stores/test-store-123'
        assert store.display_name == 'Test Store'
        assert isinstance(store.created_at, datetime)

    def test_store_name_unique(self, db_session):
        """Test that store name must be unique."""
        from app.models import Store

        store1 = Store(name='duplicate', gemini_store_id='id1')
        db_session.add(store1)
        db_session.commit()

        store2 = Store(name='duplicate', gemini_store_id='id2')
        db_session.add(store2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_store_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        from app.models import Store

        # Missing gemini_store_id
        store = Store(name='test')
        db_session.add(store)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_store_documents_relationship(self, db_session):
        """Test the relationship between store and documents."""
        from app.models import Store, Document

        store = Store(name='test-store', gemini_store_id='store-id')
        db_session.add(store)
        db_session.commit()

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
        db_session.add_all([doc1, doc2])
        db_session.commit()

        assert store.documents.count() == 2
        assert doc1 in store.documents.all()
        assert doc2 in store.documents.all()


class TestDocumentModel:
    """Test the Document model for uploaded document tracking."""

    def test_create_document(self, db_session):
        """Test creating a basic document."""
        from app.models import Store, Document

        store = Store(name='test-store', gemini_store_id='store-id')
        db_session.add(store)
        db_session.commit()

        doc = Document(
            store_id=store.id,
            filename='test.pdf',
            category='research',
            file_path='/uploads/test.pdf',
            gemini_file_id='file-123',
            file_size=1024000
        )
        db_session.add(doc)
        db_session.commit()

        assert doc.id is not None
        assert doc.filename == 'test.pdf'
        assert doc.category == 'research'
        assert doc.file_size == 1024000
        assert isinstance(doc.upload_date, datetime)

    def test_document_required_fields(self, db_session):
        """Test that filename is required."""
        from app.models import Document

        doc = Document(store_id=1, gemini_file_id='file-id')
        db_session.add(doc)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_document_metadata_json(self, db_session):
        """Test storing JSON metadata."""
        from app.models import Store, Document

        store = Store(name='test-store', gemini_store_id='store-id')
        db_session.add(store)
        db_session.commit()

        metadata = {
            'author': 'John Doe',
            'tags': ['ai', 'ml'],
            'version': 1
        }

        doc = Document(
            store_id=store.id,
            filename='test.pdf',
            gemini_file_id='file-id',
            file_metadata=json.dumps(metadata)
        )
        db_session.add(doc)
        db_session.commit()

        retrieved_doc = db_session.query(Document).filter_by(id=doc.id).first()
        assert json.loads(retrieved_doc.file_metadata) == metadata

    def test_document_category_filtering(self, db_session):
        """Test filtering documents by category (index test)."""
        from app.models import Store, Document

        store = Store(name='test-store', gemini_store_id='store-id')
        db_session.add(store)
        db_session.commit()

        doc1 = Document(
            store_id=store.id,
            filename='research1.pdf',
            gemini_file_id='file1',
            category='research'
        )
        doc2 = Document(
            store_id=store.id,
            filename='policy1.pdf',
            gemini_file_id='file2',
            category='policy'
        )
        doc3 = Document(
            store_id=store.id,
            filename='research2.pdf',
            gemini_file_id='file3',
            category='research'
        )
        db_session.add_all([doc1, doc2, doc3])
        db_session.commit()

        research_docs = db_session.query(Document).filter_by(category='research').all()
        assert len(research_docs) == 2


class TestSmartPromptModel:
    """Test the SmartPrompt model for reusable query templates."""

    def test_create_smart_prompt(self, db_session):
        """Test creating a smart prompt."""
        from app.models import SmartPrompt

        prompt = SmartPrompt(
            title='Summary Template',
            prompt_text='Summarize the key findings from {category} documents',
            category='research',
            response_mode='precise'
        )
        db_session.add(prompt)
        db_session.commit()

        assert prompt.id is not None
        assert prompt.title == 'Summary Template'
        assert prompt.usage_count == 0
        assert isinstance(prompt.created_at, datetime)

    def test_smart_prompt_required_fields(self, db_session):
        """Test that title and prompt_text are required."""
        from app.models import SmartPrompt

        prompt = SmartPrompt(title='Test')
        db_session.add(prompt)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_increment_usage_count(self, db_session):
        """Test incrementing usage count."""
        from app.models import SmartPrompt

        prompt = SmartPrompt(
            title='Test',
            prompt_text='Test prompt'
        )
        db_session.add(prompt)
        db_session.commit()

        assert prompt.usage_count == 0

        prompt.usage_count += 1
        db_session.commit()

        assert prompt.usage_count == 1


class TestQueryHistoryModel:
    """Test the QueryHistory model for analytics and history."""

    def test_create_query_history(self, db_session):
        """Test creating a query history entry."""
        from app.models import Store, QueryHistory

        store = Store(name='test-store', gemini_store_id='store-id')
        db_session.add(store)
        db_session.commit()

        query = QueryHistory(
            question='What are the key findings?',
            response='Here are the key findings...',
            response_mode='comprehensive',
            category_filter='research',
            store_id=store.id,
            response_time=1.25
        )
        db_session.add(query)
        db_session.commit()

        assert query.id is not None
        assert query.question == 'What are the key findings?'
        assert query.response_time == 1.25
        assert isinstance(query.query_date, datetime)

    def test_query_history_required_fields(self, db_session):
        """Test that question is required."""
        from app.models import QueryHistory

        query = QueryHistory(response='Answer')
        db_session.add(query)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_query_history_date_filtering(self, db_session):
        """Test filtering by date (index test)."""
        from app.models import QueryHistory
        from datetime import datetime, timedelta

        old_query = QueryHistory(
            question='Old question',
            response='Old answer'
        )
        db_session.add(old_query)
        db_session.commit()

        # Manually set old date
        old_query.query_date = datetime.utcnow() - timedelta(days=30)
        db_session.commit()

        new_query = QueryHistory(
            question='New question',
            response='New answer'
        )
        db_session.add(new_query)
        db_session.commit()

        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_queries = db_session.query(QueryHistory).filter(
            QueryHistory.query_date >= cutoff_date
        ).all()

        assert len(recent_queries) == 1
        assert recent_queries[0].question == 'New question'


class TestUserSettingsModel:
    """Test the UserSettings model for application settings."""

    def test_create_user_setting(self, db_session):
        """Test creating a user setting."""
        from app.models import UserSetting

        setting = UserSetting(
            setting_key='default_response_mode',
            setting_value='comprehensive'
        )
        db_session.add(setting)
        db_session.commit()

        assert setting.id is not None
        assert setting.setting_key == 'default_response_mode'
        assert setting.setting_value == 'comprehensive'

    def test_setting_key_unique(self, db_session):
        """Test that setting_key must be unique."""
        from app.models import UserSetting

        setting1 = UserSetting(
            setting_key='theme',
            setting_value='dark'
        )
        db_session.add(setting1)
        db_session.commit()

        setting2 = UserSetting(
            setting_key='theme',
            setting_value='light'
        )
        db_session.add(setting2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_setting_required_fields(self, db_session):
        """Test that setting_key is required."""
        from app.models import UserSetting

        setting = UserSetting(setting_value='value')
        db_session.add(setting)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_update_setting(self, db_session):
        """Test updating an existing setting."""
        from app.models import UserSetting

        setting = UserSetting(
            setting_key='max_results',
            setting_value='10'
        )
        db_session.add(setting)
        db_session.commit()

        setting.setting_value = '20'
        db_session.commit()

        retrieved = db_session.query(UserSetting).filter_by(
            setting_key='max_results'
        ).first()
        assert retrieved.setting_value == '20'
