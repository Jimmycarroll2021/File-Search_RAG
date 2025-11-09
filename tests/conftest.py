"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='function')
def app():
    """Create and configure a test app instance."""
    from app import create_app
    from app.database import db

    # Import models before creating tables
    from app import models

    test_app = create_app('testing')

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def db_session(app):
    """Provide a database session for tests."""
    from app.database import db

    with app.app_context():
        yield db.session
        db.session.rollback()
