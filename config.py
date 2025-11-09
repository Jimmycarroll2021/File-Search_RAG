"""
Application configuration management.
Supports multiple environments: development, testing, production.
"""
import os
from pathlib import Path


class Config:
    """Base configuration class."""

    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Application paths
    BASE_DIR = Path(__file__).parent.absolute()
    INSTANCE_DIR = BASE_DIR / 'instance'
    UPLOAD_DIR = BASE_DIR / 'uploads'

    # Gemini API
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

    @staticmethod
    def init_app(app):
        """Initialize application with this config."""
        # Create necessary directories
        os.makedirs(Config.INSTANCE_DIR, exist_ok=True)
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False

    # SQLite database in instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'sqlite:///{Config.INSTANCE_DIR / "app.db"}'

    # Enable SQL query logging in development
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing environment configuration."""

    DEBUG = False
    TESTING = True

    # Use in-memory SQLite database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Production database (can be PostgreSQL, MySQL, etc.)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{Config.INSTANCE_DIR / "app.db"}'

    # Disable SQL query logging in production
    SQLALCHEMY_ECHO = False

    @classmethod
    def init_app(cls, app):
        """Production-specific initialization."""
        Config.init_app(app)

        # Log to syslog or other production logging
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug:
            log_dir = cls.BASE_DIR / 'logs'
            os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_dir / 'app.log',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('Application startup')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
