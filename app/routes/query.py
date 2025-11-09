"""
Query blueprint - handles querying file search stores
"""
from flask import Blueprint, request, jsonify
from app.services.gemini_service import GeminiService
from app.services.response_modes import get_mode_config
from app.services.category_service import validate_categories
from app.models import Document, Store
from app.database import db
from app.routes.files import file_search_stores

query_bp = Blueprint('query', __name__, url_prefix='/api/query')

# Initialize Gemini service
gemini_service = GeminiService()


@query_bp.route('/query', methods=['POST'])
def query():
    """
    Query a file search store with a question.

    Supports category filtering to search only specific document types.

    Request JSON:
        - question: The query text (required)
        - store_name: Name of the store to query (default: 'my-file-search-store')
        - mode: Response mode (default: 'quick')
        - categories: List of category names to filter by (optional)
    """
    try:
        question = request.json.get('question')
        store_name = request.json.get('store_name', 'my-file-search-store')
        mode = request.json.get('mode', 'quick')  # Default to quick mode
        categories = request.json.get('categories', [])

        if not question:
            return jsonify({'success': False, 'error': 'No question provided'}), 400

        if store_name not in file_search_stores:
            return jsonify({
                'success': False,
                'error': f'Store "{store_name}" not found. Please upload files first.'
            }), 404

        store_id = file_search_stores[store_name]

        # Get mode configuration
        mode_config = get_mode_config(mode)

        # Validate and filter categories if provided
        filtered_categories = []
        if categories and isinstance(categories, list):
            filtered_categories = validate_categories(categories)

        # If categories are specified, get filtered document info
        # Note: For now, we query all documents in the store
        # In a full implementation, we would filter Gemini queries by specific file IDs
        category_info = None
        if filtered_categories:
            # Get the database store
            db_store = Store.query.filter_by(gemini_store_id=store_id).first()
            if db_store:
                # Count documents in selected categories
                doc_count = Document.query.filter(
                    Document.store_id == db_store.id,
                    Document.category.in_(filtered_categories)
                ).count()

                category_info = {
                    'filtered_categories': filtered_categories,
                    'document_count': doc_count
                }

        # Query with file search and mode-specific settings
        # TODO: In future, pass specific file IDs to Gemini for category filtering
        answer = gemini_service.query_with_file_search(
            question=question,
            store_id=store_id,
            system_prompt=mode_config['system_prompt'],
            temperature=mode_config['temperature']
        )

        response = {
            'success': True,
            'answer': answer,
            'question': question,
            'mode': 'quick' if mode not in ['tender', 'quick', 'analysis', 'strategy', 'checklist'] else mode,
            'mode_name': mode_config['name'],
            'mode_icon': mode_config['icon']
        }

        # Add category info if filtering was applied
        if category_info:
            response['category_filter'] = category_info

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
