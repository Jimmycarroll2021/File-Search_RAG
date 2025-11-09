"""
Database initialization and configuration.
Provides the SQLAlchemy database instance.
"""
from flask_sqlalchemy import SQLAlchemy
import json
import os

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the Flask app.

    Args:
        app: Flask application instance

    This function:
    1. Binds the database to the Flask app
    2. Creates all tables if they don't exist
    3. Sets up the database session
    4. Seeds default prompts if database is empty
    """
    db.init_app(app)

    with app.app_context():
        # Import models to ensure they're registered
        from app import models

        # Create all tables
        db.create_all()

        # Seed default prompts if none exist
        seed_default_prompts(app)

        # Log database initialization
        app.logger.info(f'Database initialized: {app.config["SQLALCHEMY_DATABASE_URI"]}')


def drop_db(app):
    """
    Drop all database tables.

    Args:
        app: Flask application instance

    WARNING: This will delete all data. Use only for testing or reset.
    """
    with app.app_context():
        db.drop_all()
        app.logger.warning('All database tables dropped')


def reset_db(app):
    """
    Reset the database by dropping and recreating all tables.

    Args:
        app: Flask application instance

    WARNING: This will delete all data.
    """
    drop_db(app)
    init_db(app)
    app.logger.info('Database reset completed')


def seed_default_prompts(app):
    """
    Seed default prompts from JSON file if database is empty.

    Args:
        app: Flask application instance
    """
    try:
        from app.models import SmartPrompt
        from app.services.prompt_service import PromptService

        # Check if prompts already exist
        existing_count = SmartPrompt.query.count()
        if existing_count > 0:
            app.logger.info(f'Skipping prompt seeding - {existing_count} prompts already exist')
            return

        # Load default prompts from JSON file
        json_path = os.path.join(os.path.dirname(__file__), 'data', 'default_prompts.json')

        if not os.path.exists(json_path):
            app.logger.warning(f'Default prompts file not found: {json_path}')
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)

        # Seed prompts using service
        prompt_service = PromptService()
        created_count = prompt_service.seed_prompts(prompts_data)

        app.logger.info(f'Seeded {created_count} default prompts successfully')

    except Exception as e:
        app.logger.error(f'Error seeding default prompts: {str(e)}')
