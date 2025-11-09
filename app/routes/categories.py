"""
Categories blueprint - handles category listing and statistics.

Provides endpoints for:
- Listing all available categories with configuration
- Getting document count statistics per category
"""
from flask import Blueprint, jsonify
from app.services.category_service import get_all_categories, get_category_stats

categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


@categories_bp.route('', methods=['GET'])
@categories_bp.route('/', methods=['GET'])
def list_categories():
    """
    List all available categories with their configuration.

    Returns:
        JSON response with success status and list of categories.
        Each category includes: name, color, icon, description.
    """
    try:
        categories = get_all_categories()

        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@categories_bp.route('/stats', methods=['GET'])
def category_statistics():
    """
    Get document count statistics for all categories.

    Returns:
        JSON response with success status, stats dict (category -> count),
        and total_count of all categorized documents.
    """
    try:
        stats = get_category_stats()
        total_count = sum(stats.values())

        return jsonify({
            'success': True,
            'stats': stats,
            'total_count': total_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
