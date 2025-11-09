"""
Prompts blueprint - handles smart prompts CRUD operations.

Endpoints:
- GET /api/prompts - List all prompts (with search/filter)
- POST /api/prompts - Create new prompt
- PUT /api/prompts/<id> - Update prompt
- DELETE /api/prompts/<id> - Delete prompt
- POST /api/prompts/<id>/use - Increment usage count
- GET /api/prompts/popular - Most-used prompts
- GET /api/prompts/categories - Get unique categories
"""
from flask import Blueprint, request, jsonify
from app.services.prompt_service import PromptService
from app.database import db

prompts_bp = Blueprint('prompts', __name__, url_prefix='/api/prompts')

# Initialize prompt service
prompt_service = PromptService()


@prompts_bp.route('', methods=['GET'])
def get_prompts():
    """
    Get all prompts with optional search/filter.

    Query Parameters:
        query (str): Search query for title/text
        category (str): Filter by category

    Returns:
        JSON response with prompts list
    """
    try:
        query = request.args.get('query')
        category = request.args.get('category')

        if query:
            prompts = prompt_service.search_prompts(query, category)
        elif category:
            prompts = prompt_service.filter_by_category(category)
        else:
            prompts = prompt_service.get_all_prompts()

        return jsonify({
            'success': True,
            'prompts': [p.to_dict() for p in prompts],
            'count': len(prompts)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompts_bp.route('', methods=['POST'])
def create_prompt():
    """
    Create a new prompt.

    Request Body (JSON):
        title (str): Prompt title
        prompt_text (str): Prompt text
        category (str): Optional category
        response_mode (str): Optional response mode

    Returns:
        JSON response with created prompt
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400

        try:
            data = request.get_json()
        except Exception:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON format'
            }), 400

        # Create prompt
        prompt = prompt_service.create_prompt(data)

        return jsonify({
            'success': True,
            'prompt': prompt.to_dict()
        }), 201

    except (ValueError, KeyError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompts_bp.route('/<int:prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """
    Update an existing prompt.

    URL Parameters:
        prompt_id (int): ID of prompt to update

    Request Body (JSON):
        Any prompt fields to update

    Returns:
        JSON response with updated prompt
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400

        data = request.get_json()

        # Update prompt
        prompt = prompt_service.update_prompt(prompt_id, data)

        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt not found'
            }), 404

        return jsonify({
            'success': True,
            'prompt': prompt.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompts_bp.route('/<int:prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """
    Delete a prompt.

    URL Parameters:
        prompt_id (int): ID of prompt to delete

    Returns:
        JSON response indicating success
    """
    try:
        result = prompt_service.delete_prompt(prompt_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Prompt not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Prompt deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompts_bp.route('/<int:prompt_id>/use', methods=['POST'])
def increment_usage(prompt_id):
    """
    Increment usage count for a prompt.

    URL Parameters:
        prompt_id (int): ID of prompt

    Returns:
        JSON response with updated prompt
    """
    try:
        prompt = prompt_service.increment_usage(prompt_id)

        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt not found'
            }), 404

        return jsonify({
            'success': True,
            'prompt': prompt.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompts_bp.route('/popular', methods=['GET'])
def get_popular_prompts():
    """
    Get most-used prompts.

    Query Parameters:
        limit (int): Maximum number of prompts (default 10)

    Returns:
        JSON response with popular prompts
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        prompts = prompt_service.get_popular_prompts(limit=limit)

        return jsonify({
            'success': True,
            'prompts': [p.to_dict() for p in prompts]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompts_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all unique categories.

    Returns:
        JSON response with category list
    """
    try:
        categories = prompt_service.get_categories()

        return jsonify({
            'success': True,
            'categories': categories
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
