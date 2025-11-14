"""
Test script to verify database functionality.
Tests database initialization, file upload tracking, and query operations.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import Store, Document, SmartPrompt, QueryHistory, UserSetting


def test_database():
    """Test database operations."""
    app = create_app('development')

    with app.app_context():
        print("=" * 60)
        print("DATABASE CONNECTIVITY TEST")
        print("=" * 60)

        # Test 1: Verify tables exist
        print("\n1. Verifying database tables...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"   Found tables: {', '.join(tables)}")

        expected_tables = ['stores', 'documents', 'smart_prompts', 'query_history', 'user_settings']
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            print(f"   ERROR: Missing tables: {', '.join(missing_tables)}")
            return False
        else:
            print("   SUCCESS: All required tables exist")

        # Test 2: Test Store creation
        print("\n2. Testing Store creation...")
        try:
            test_store = Store(
                name='test_store',
                gemini_store_id='corpora/test-store-123',
                display_name='Test Store'
            )
            db.session.add(test_store)
            db.session.commit()
            print(f"   SUCCESS: Created store with ID: {test_store.id}")
        except Exception as e:
            print(f"   ERROR: Failed to create store: {str(e)}")
            db.session.rollback()
            return False

        # Test 3: Test Document creation
        print("\n3. Testing Document creation...")
        try:
            test_doc = Document(
                store_id=test_store.id,
                filename='test.pdf',
                category='test',
                file_path='/uploads/test.pdf',
                gemini_file_id='files/test-file-123',
                file_size=1024
            )
            db.session.add(test_doc)
            db.session.commit()
            print(f"   SUCCESS: Created document with ID: {test_doc.id}")
        except Exception as e:
            print(f"   ERROR: Failed to create document: {str(e)}")
            db.session.rollback()
            return False

        # Test 4: Test Query
        print("\n4. Testing database queries...")
        try:
            store_count = Store.query.count()
            doc_count = Document.query.count()
            print(f"   SUCCESS: Found {store_count} store(s) and {doc_count} document(s)")
        except Exception as e:
            print(f"   ERROR: Failed to query database: {str(e)}")
            return False

        # Test 5: Test QueryHistory
        print("\n5. Testing QueryHistory...")
        try:
            query_record = QueryHistory(
                question='Test question',
                response='Test response',
                response_mode='comprehensive',
                store_id=test_store.id
            )
            db.session.add(query_record)
            db.session.commit()
            print(f"   SUCCESS: Created query history with ID: {query_record.id}")
        except Exception as e:
            print(f"   ERROR: Failed to create query history: {str(e)}")
            db.session.rollback()
            return False

        # Test 6: Test UserSetting
        print("\n6. Testing UserSetting...")
        try:
            UserSetting.set_setting('test_key', 'test_value')
            value = UserSetting.get_setting('test_key')
            if value == 'test_value':
                print(f"   SUCCESS: Set and retrieved setting: {value}")
            else:
                print(f"   ERROR: Setting value mismatch: {value}")
                return False
        except Exception as e:
            print(f"   ERROR: Failed to set/get setting: {str(e)}")
            return False

        # Cleanup test data
        print("\n7. Cleaning up test data...")
        try:
            db.session.delete(query_record)
            db.session.delete(test_doc)
            db.session.delete(test_store)
            UserSetting.query.filter_by(setting_key='test_key').delete()
            db.session.commit()
            print("   SUCCESS: Test data cleaned up")
        except Exception as e:
            print(f"   ERROR: Failed to cleanup: {str(e)}")
            db.session.rollback()
            return False

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        return True


if __name__ == '__main__':
    success = test_database()
    sys.exit(0 if success else 1)
