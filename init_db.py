"""
Database initialization script.

This script initializes the database by creating all tables
defined in the models. Can also be used to reset the database.

Usage:
    python init_db.py              - Initialize database
    python init_db.py --reset      - Drop and recreate all tables
    python init_db.py --seed       - Initialize with sample data
"""
import sys
import os

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db, reset_db
from app.models import Store, Document, SmartPrompt, QueryHistory, UserSetting


def init_database(app):
    """Initialize the database with tables."""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nCreated tables: {', '.join(tables)}")


def seed_database(app):
    """Seed the database with sample data for testing."""
    with app.app_context():
        print("\nSeeding database with sample data...")

        # Add default settings
        default_settings = [
            ('default_response_mode', 'comprehensive'),
            ('max_file_size_mb', '100'),
            ('default_category', 'general'),
            ('enable_query_logging', 'true'),
        ]

        for key, value in default_settings:
            setting = UserSetting.query.filter_by(setting_key=key).first()
            if not setting:
                UserSetting.set_setting(key, value)
                print(f"  - Added setting: {key} = {value}")

        # Add sample smart prompts
        sample_prompts = [
            {
                'title': 'Document Summary',
                'prompt_text': 'Provide a comprehensive summary of the key points from the documents.',
                'category': 'general',
                'response_mode': 'comprehensive'
            },
            {
                'title': 'Find Specific Information',
                'prompt_text': 'Search for specific information about: {topic}',
                'category': 'search',
                'response_mode': 'precise'
            },
            {
                'title': 'Compare Documents',
                'prompt_text': 'Compare and contrast the main arguments in these documents.',
                'category': 'analysis',
                'response_mode': 'comprehensive'
            },
        ]

        for prompt_data in sample_prompts:
            existing = SmartPrompt.query.filter_by(title=prompt_data['title']).first()
            if not existing:
                prompt = SmartPrompt(**prompt_data)
                db.session.add(prompt)
                print(f"  - Added smart prompt: {prompt_data['title']}")

        db.session.commit()
        print("\nDatabase seeded successfully!")


def reset_database(app):
    """Reset the database by dropping and recreating all tables."""
    print("WARNING: This will delete all data in the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")

    if confirm.lower() == 'yes':
        with app.app_context():
            print("Dropping all tables...")
            db.drop_all()
            print("Creating new tables...")
            db.create_all()
            print("Database reset completed successfully!")
    else:
        print("Reset cancelled.")


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(description='Initialize the database')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Drop and recreate all tables (WARNING: deletes all data)'
    )
    parser.add_argument(
        '--seed',
        action='store_true',
        help='Seed the database with sample data'
    )
    parser.add_argument(
        '--env',
        default='development',
        choices=['development', 'testing', 'production'],
        help='Environment to use (default: development)'
    )

    args = parser.parse_args()

    # Create app with specified environment
    app = create_app(args.env)

    print(f"Initializing database for '{args.env}' environment...")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print()

    if args.reset:
        reset_database(app)
        if args.seed:
            seed_database(app)
    else:
        init_database(app)
        if args.seed:
            seed_database(app)


if __name__ == '__main__':
    main()
