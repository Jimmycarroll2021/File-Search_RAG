"""
Category service for document categorization and filtering.

Provides category configuration, auto-detection from file paths,
and statistics about document distribution across categories.
"""
import os
from typing import Dict, List
from sqlalchemy import func
from app.models import Document
from app.database import db


# Category configuration with visual styling
CATEGORIES = {
    "compliance": {
        "color": "#ff6b6b",
        "icon": "🛡️",
        "description": "Security, PSPF, E8"
    },
    "contracts": {
        "color": "#4ecdc4",
        "icon": "📄",
        "description": "Legal agreements"
    },
    "proposals": {
        "color": "#45b7d1",
        "icon": "📊",
        "description": "Tender responses"
    },
    "pricing": {
        "color": "#96ceb4",
        "icon": "💰",
        "description": "Quotes, budgets"
    },
    "requirements": {
        "color": "#ffeaa7",
        "icon": "📋",
        "description": "RFPs, SOWs"
    },
    "technical": {
        "color": "#a29bfe",
        "icon": "⚙️",
        "description": "Technical docs"
    },
    "cvs_resumes": {
        "color": "#fd79a8",
        "icon": "👤",
        "description": "Team capabilities"
    },
    "policies": {
        "color": "#74b9ff",
        "icon": "📚",
        "description": "Internal policies"
    },
    "other": {
        "color": "#dfe6e9",
        "icon": "📁",
        "description": "Miscellaneous"
    }
}


def detect_category_from_path(file_path: str) -> str:
    """
    Auto-detect category from file path.

    Searches the file path for category keywords and returns
    the matching category. Case-insensitive matching.

    Args:
        file_path: Full or relative path to the file

    Returns:
        Category name (one of the keys in CATEGORIES dict)
        Defaults to 'other' if no match found
    """
    if not file_path:
        return "other"

    # Normalize path separators and convert to lowercase for matching
    normalized_path = file_path.replace('\\', '/').lower()

    # Check for each category keyword in the path
    # Order matters - check more specific patterns first

    # Check for CVs/resumes (multiple keywords)
    if any(keyword in normalized_path for keyword in ['cvs_resumes', 'cv/', 'cvs/', 'resumes/', 'resume/']):
        return "cvs_resumes"

    # Check for proposals (including singular form)
    if 'proposal' in normalized_path:
        return "proposals"

    # Check for other categories
    category_keywords = {
        'compliance': 'compliance',
        'contracts': 'contracts',
        'pricing': 'pricing',
        'requirements': 'requirements',
        'technical': 'technical',
        'policies': 'policies'
    }

    for category, keyword in category_keywords.items():
        if keyword in normalized_path:
            return category

    # Default to 'other' if no match found
    return "other"


def get_all_categories() -> List[Dict[str, str]]:
    """
    Get all categories with their configuration.

    Returns:
        List of category dictionaries with name, color, icon, and description
    """
    return [
        {
            "name": category,
            "color": config["color"],
            "icon": config["icon"],
            "description": config["description"]
        }
        for category, config in CATEGORIES.items()
    ]


def get_category_stats() -> Dict[str, int]:
    """
    Get document counts per category from database.

    Returns:
        Dictionary mapping category names to document counts
        All categories are included, even if count is 0
    """
    # Initialize all categories with 0 count
    stats = {category: 0 for category in CATEGORIES.keys()}

    # Query database for actual counts
    # Group by category and count, filtering out null/empty categories
    try:
        results = db.session.query(
            Document.category,
            func.count(Document.id)
        ).filter(
            Document.category.isnot(None),
            Document.category != ''
        ).group_by(
            Document.category
        ).all()

        # Update stats with actual counts
        for category, count in results:
            if category in stats:
                stats[category] = count

    except Exception as e:
        # If database query fails, return empty stats
        # This handles cases where database isn't initialized yet
        print(f"Error getting category stats: {e}")

    return stats


def validate_categories(categories: List[str]) -> List[str]:
    """
    Validate a list of category names.

    Args:
        categories: List of category names to validate

    Returns:
        List of valid category names (invalid ones filtered out)
    """
    if not categories:
        return []

    valid_categories = set(CATEGORIES.keys())
    return [cat for cat in categories if cat in valid_categories]
