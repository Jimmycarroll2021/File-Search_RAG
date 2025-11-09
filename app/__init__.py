"""
Flask application factory with SQLAlchemy database support.
"""
from flask import Flask, render_template
from dotenv import load_dotenv
import os
from config import config
from app.database import db


def create_app(config_name='default'):
    """
    Application factory function.

    Args:
        config_name: Configuration to use ('development', 'testing', 'production')

    Returns:
        Configured Flask application instance
    """
    # Load environment variables
    load_dotenv()

    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static',
                instance_relative_config=True)

    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize database
    db.init_app(app)

    # Create instance folder if it doesn't exist
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Register blueprints
    try:
        from app.routes.files import files_bp
        from app.routes.query import query_bp
        from app.routes.categories import categories_bp
        from app.routes.prompts import prompts_bp
        from app.routes.export import export_bp
        app.register_blueprint(files_bp)
        app.register_blueprint(query_bp)
        app.register_blueprint(categories_bp)
        app.register_blueprint(prompts_bp)
        app.register_blueprint(export_bp)
    except ImportError:
        # Blueprints not yet created, skip for now
        pass

    # Main route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Test route for markdown rendering
    @app.route('/test-markdown')
    def test_markdown():
        return render_template('test-markdown.html')

    # Backward compatibility routes (without /api prefix)
    # These allow old clients to continue using the original routes
    try:
        from app.routes.files import create_store, upload_file, list_stores
        from app.routes.query import query

        @app.route('/create_store', methods=['POST'])
        def create_store_compat():
            """Backward compatible route for /create_store"""
            return create_store()

        @app.route('/upload_file', methods=['POST'])
        def upload_file_compat():
            """Backward compatible route for /upload_file"""
            return upload_file()

        @app.route('/list_stores', methods=['GET'])
        def list_stores_compat():
            """Backward compatible route for /list_stores"""
            return list_stores()

        @app.route('/query', methods=['POST'])
        def query_compat():
            """Backward compatible route for /query"""
            return query()
    except ImportError:
        # Routes not yet created, skip for now
        pass

    return app
