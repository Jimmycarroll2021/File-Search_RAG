"""
Bulk upload service for processing multiple files from directories.

Handles directory scanning, category auto-detection, batch processing,
and duplicate detection for efficient bulk uploads.
"""
import os
from typing import List, Dict, Optional
from app.services.gemini_service import GeminiService
from app.models import Document, Store
from app.database import db


# Supported file extensions for document upload
SUPPORTED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.txt', '.md',
    '.json', '.csv', '.xls', '.xlsx', '.ppt', '.pptx'
}

# Category mapping from folder names
CATEGORY_MAPPING = {
    'compliance': 'compliance',
    'proposals': 'proposals',
    'contracts': 'contracts',
    'technical': 'technical',
    'pricing': 'pricing',
    'policies': 'policies',
    'requirements': 'requirements',
    'cvs_resumes': 'cvs_resumes',
    'other': 'other'
}


def detect_category(file_path: str) -> str:
    """
    Auto-detect category from parent folder name.

    Examines the file path and identifies the category based on
    the parent folder name. Supports nested paths.

    Args:
        file_path: Full path to the file

    Returns:
        Category name (lowercase) or 'uncategorized' if not found
    """
    # Normalize path separators
    normalized_path = file_path.replace('\\', '/').lower()
    path_parts = normalized_path.split('/')

    # Check each path component for known categories
    for part in reversed(path_parts):
        if part in CATEGORY_MAPPING:
            return CATEGORY_MAPPING[part]

    return 'uncategorized'


def scan_directory(source_dir: str, auto_categorize: bool = True) -> List[Dict]:
    """
    Scan directory and return file list with detected categories.

    Recursively walks through directory tree and collects all supported
    document files with their metadata.

    Args:
        source_dir: Path to the directory to scan
        auto_categorize: Whether to auto-detect categories from folder structure

    Returns:
        List of file dictionaries with keys:
            - file_path: Absolute path to file
            - filename: Base filename
            - category: Detected category (or None if auto_categorize=False)
            - file_size: File size in bytes

    Raises:
        FileNotFoundError: If source directory does not exist
    """
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Directory not found: {source_dir}")

    files = []

    # Walk through directory tree
    for root, dirs, filenames in os.walk(source_dir):
        for filename in filenames:
            # Get file extension
            _, ext = os.path.splitext(filename)

            # Filter for supported file types
            if ext.lower() not in SUPPORTED_EXTENSIONS:
                continue

            # Build full file path
            file_path = os.path.join(root, filename)

            # Detect category if enabled
            category = detect_category(file_path) if auto_categorize else None

            # Get file size
            try:
                file_size = os.path.getsize(file_path)
            except OSError:
                continue  # Skip files we can't access

            files.append({
                'file_path': file_path,
                'filename': filename,
                'category': category,
                'file_size': file_size
            })

    return files


def check_duplicate(filename: str, store_id: int) -> bool:
    """
    Check if file already exists in the store.

    Args:
        filename: Name of the file to check
        store_id: Database ID of the store

    Returns:
        True if file already exists, False otherwise
    """
    existing = Document.query.filter_by(
        store_id=store_id,
        filename=filename
    ).first()

    return existing is not None


def upload_batch(
    files: List[Dict],
    store_id: int,
    batch_size: int = 10
) -> Dict:
    """
    Upload files in batches, return results.

    Processes files in batches to avoid timeouts and memory issues.
    Handles duplicates, errors, and tracks progress.

    Args:
        files: List of file dictionaries from scan_directory
        store_id: Database ID of the store to upload to
        batch_size: Number of files to process in each batch

    Returns:
        Dictionary with keys:
            - total: Total number of files processed
            - success: Number of successful uploads
            - failed: Number of failed uploads
            - skipped: Number of skipped duplicates
            - files: List of file results with status and error info
    """
    gemini_service = GeminiService()

    # Get store
    store = Store.query.get(store_id)
    if not store:
        raise ValueError(f"Store not found: {store_id}")

    results = {
        'total': len(files),
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'files': []
    }

    # Process files in batches
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]

        for file_info in batch:
            file_result = {
                'filename': file_info['filename'],
                'category': file_info['category'],
                'status': 'pending',
                'error': None
            }

            try:
                # Check for duplicate
                if check_duplicate(file_info['filename'], store_id):
                    file_result['status'] = 'skipped'
                    file_result['error'] = 'File already exists'
                    results['skipped'] += 1
                    results['files'].append(file_result)
                    continue

                # Upload to Gemini
                operation = gemini_service.upload_file_to_store(
                    file_path=file_info['file_path'],
                    store_id=store.gemini_store_id,
                    display_name=file_info['filename']
                )

                # Create document record
                document = Document(
                    store_id=store_id,
                    filename=file_info['filename'],
                    category=file_info['category'],
                    file_path=file_info['file_path'],
                    gemini_file_id=operation.name if hasattr(operation, 'name') else None,
                    file_size=file_info['file_size']
                )
                db.session.add(document)

                file_result['status'] = 'success'
                results['success'] += 1

            except Exception as e:
                file_result['status'] = 'failed'
                file_result['error'] = str(e)
                results['failed'] += 1

            results['files'].append(file_result)

        # Commit batch to database
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Mark batch as failed
            for file_result in results['files'][-len(batch):]:
                if file_result['status'] == 'success':
                    file_result['status'] = 'failed'
                    file_result['error'] = f'Database error: {str(e)}'
                    results['success'] -= 1
                    results['failed'] += 1

    return results


def get_category_distribution(files: List[Dict]) -> Dict[str, int]:
    """
    Get category distribution from scanned files.

    Args:
        files: List of file dictionaries from scan_directory

    Returns:
        Dictionary mapping category names to file counts
    """
    distribution = {}

    for file_info in files:
        category = file_info.get('category', 'uncategorized')
        distribution[category] = distribution.get(category, 0) + 1

    return distribution
