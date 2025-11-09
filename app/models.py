"""
SQLAlchemy database models for Google Gemini File Search application.

Models:
- Store: File search store metadata
- Document: Uploaded document tracking with categories
- SmartPrompt: Reusable query templates
- QueryHistory: Analytics and query history
- UserSetting: Application settings
"""
from datetime import datetime
from app.database import db


class Store(db.Model):
    """
    File search store metadata.

    Represents a Gemini file search store where documents are uploaded.
    Each store can contain multiple documents.
    """
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    gemini_store_id = db.Column(db.String(500), nullable=False)
    display_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    documents = db.relationship('Document', backref='store', lazy='dynamic', cascade='all, delete-orphan')
    queries = db.relationship('QueryHistory', backref='store', lazy='dynamic')

    def __repr__(self):
        return f'<Store {self.name}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'gemini_store_id': self.gemini_store_id,
            'display_name': self.display_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'document_count': self.documents.count()
        }


class Document(db.Model):
    """
    Uploaded document tracking with categories.

    Tracks all documents uploaded to file search stores,
    including metadata, categories for filtering, and file information.
    """
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=True)
    filename = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), index=True)
    file_path = db.Column(db.String(1000))
    gemini_file_id = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    file_metadata = db.Column(db.Text)  # JSON string (renamed from 'metadata' which is reserved)

    # Indexes for efficient querying
    __table_args__ = (
        db.Index('idx_document_category_date', 'category', 'upload_date'),
    )

    def __repr__(self):
        return f'<Document {self.filename}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'filename': self.filename,
            'category': self.category,
            'file_path': self.file_path,
            'gemini_file_id': self.gemini_file_id,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'file_metadata': self.file_metadata
        }


class SmartPrompt(db.Model):
    """
    Reusable query templates.

    Stores pre-configured prompts that users can reuse
    with different documents or categories.
    """
    __tablename__ = 'smart_prompts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    response_mode = db.Column(db.String(50))  # e.g., 'precise', 'comprehensive', 'creative'
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<SmartPrompt {self.title}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'prompt_text': self.prompt_text,
            'category': self.category,
            'response_mode': self.response_mode,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def increment_usage(self):
        """Increment the usage count."""
        self.usage_count += 1
        db.session.commit()


class QueryHistory(db.Model):
    """
    Analytics and query history.

    Tracks all queries made to the system for analytics,
    debugging, and improving responses.
    """
    __tablename__ = 'query_history'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    response_mode = db.Column(db.String(50))
    category_filter = db.Column(db.String(100))
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=True)
    query_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    response_time = db.Column(db.Float)  # in seconds

    def __repr__(self):
        return f'<QueryHistory {self.id}: {self.question[:50]}...>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'question': self.question,
            'response': self.response,
            'response_mode': self.response_mode,
            'category_filter': self.category_filter,
            'store_id': self.store_id,
            'query_date': self.query_date.isoformat() if self.query_date else None,
            'response_time': self.response_time
        }


class UserSetting(db.Model):
    """
    Application settings.

    Stores user preferences and application configuration
    in a key-value format.
    """
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    setting_value = db.Column(db.Text)

    def __repr__(self):
        return f'<UserSetting {self.setting_key}={self.setting_value}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value
        }

    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value by key."""
        setting = UserSetting.query.filter_by(setting_key=key).first()
        return setting.setting_value if setting else default

    @staticmethod
    def set_setting(key, value):
        """Set a setting value by key."""
        setting = UserSetting.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = value
        else:
            setting = UserSetting(setting_key=key, setting_value=value)
            db.session.add(setting)
        db.session.commit()
        return setting
