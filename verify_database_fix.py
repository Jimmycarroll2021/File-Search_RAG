"""
Database Fix Verification Script

This script verifies that all database issues have been resolved:
1. Database file exists
2. All required tables exist
3. Tables can be queried without errors
4. Auto-initialization works
5. API endpoints are functional
"""
import sys
import os
import sqlite3

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_file():
    """Check if database file exists."""
    print("\n" + "=" * 60)
    print("1. CHECKING DATABASE FILE")
    print("=" * 60)

    db_path = os.path.join('instance', 'app.db')
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ Database file exists: {db_path}")
        print(f"   Size: {size:,} bytes")
        return True
    else:
        print(f"❌ Database file NOT found: {db_path}")
        return False


def check_tables():
    """Check if all required tables exist."""
    print("\n" + "=" * 60)
    print("2. CHECKING DATABASE TABLES")
    print("=" * 60)

    required_tables = ['stores', 'documents', 'smart_prompts', 'query_history', 'user_settings']

    try:
        db_path = os.path.join('instance', 'app.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  ✅ {table}")

        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"\n❌ Missing required tables: {', '.join(missing)}")
            conn.close()
            return False

        print(f"\n✅ All {len(required_tables)} required tables exist")
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")
        return False


def check_table_queries():
    """Test querying each table."""
    print("\n" + "=" * 60)
    print("3. TESTING TABLE QUERIES")
    print("=" * 60)

    tables = ['stores', 'documents', 'smart_prompts', 'query_history', 'user_settings']

    try:
        db_path = os.path.join('instance', 'app.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        all_passed = True
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} records")
            except Exception as e:
                print(f"❌ {table}: Query failed - {str(e)}")
                all_passed = False

        conn.close()
        return all_passed

    except Exception as e:
        print(f"❌ Error querying tables: {str(e)}")
        return False


def check_app_initialization():
    """Test application initialization."""
    print("\n" + "=" * 60)
    print("4. TESTING APP INITIALIZATION")
    print("=" * 60)

    try:
        from app import create_app
        from app.database import db

        app = create_app('development')
        print("✅ App created successfully")

        with app.app_context():
            # Test database connection
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Database connection established ({len(tables)} tables)")

            # Test models import
            from app import models
            print("✅ Models imported successfully")

            # Test auto-initialization worked
            if 'stores' in tables:
                print("✅ Auto-initialization working (tables exist)")
            else:
                print("❌ Auto-initialization may have issues")
                return False

        return True

    except Exception as e:
        print(f"❌ App initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_api_availability():
    """Check if API endpoints are available."""
    print("\n" + "=" * 60)
    print("5. CHECKING API ENDPOINTS")
    print("=" * 60)

    try:
        import requests

        # Check if server is running
        try:
            response = requests.get('http://127.0.0.1:5000/list_stores', timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server is running at http://127.0.0.1:5000")
                print(f"✅ /list_stores endpoint working")
                print(f"   Stores in database: {len(data.get('stores', []))}")
                return True
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("ℹ️  Server is not currently running")
            print("   To start: python wsgi.py")
            return None  # Not a failure, just not running

    except ImportError:
        print("⚠️  requests library not available, skipping API check")
        return None


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("DATABASE FIX VERIFICATION")
    print("=" * 70)
    print("\nThis script verifies the database initialization fix...")

    results = {
        'Database File': check_database_file(),
        'Tables Exist': check_tables(),
        'Table Queries': check_table_queries(),
        'App Initialization': check_app_initialization(),
        'API Endpoints': check_api_availability()
    }

    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "ℹ️  SKIP"
        print(f"{status:12} {test_name}")

    # Overall result
    print("\n" + "=" * 70)
    failed = [name for name, result in results.items() if result is False]

    if not failed:
        print("✅ ALL CRITICAL CHECKS PASSED!")
        print("\nThe database is properly initialized and ready to use.")
        print("\nNext steps:")
        print("1. Start the server: python wsgi.py")
        print("2. Upload files via the web interface at http://127.0.0.1:5000")
        print("3. Query your documents")
        print("=" * 70)
        return 0
    else:
        print(f"❌ {len(failed)} CHECK(S) FAILED:")
        for name in failed:
            print(f"   - {name}")
        print("\nPlease review the errors above.")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
