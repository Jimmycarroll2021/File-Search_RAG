"""
Files blueprint - handles file upload and store management
"""
from flask import Blueprint, request, jsonify
from app.services.gemini_service import GeminiService
from app.services.category_service import detect_category_from_path
from app.services.bulk_upload_service import (
    scan_directory,
    upload_batch,
    get_category_distribution
)
from app.models import Store, Document
from app.database import db
import os

files_bp = Blueprint('files', __name__, url_prefix='/api/files')

# Initialize Gemini service
gemini_service = GeminiService()

# Store for file search stores (in production, use a database)
file_search_stores = {}


@files_bp.route('/create_store', methods=['POST'])
def create_store():
    """Create a new file search store"""
    try:
        store_name = request.json.get('store_name', 'my-file-search-store')

        # Create the file search store
        file_search_store = gemini_service.create_file_search_store(store_name)

        # Store it in memory (use database in production)
        file_search_stores[store_name] = file_search_store.name

        return jsonify({
            'success': True,
            'store_name': file_search_store.name,
            'message': f'File search store "{store_name}" created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@files_bp.route('/upload_file', methods=['POST'])
def upload_file():
    """Upload a file to a file search store with category detection"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        store_name = request.form.get('store_name', 'my-file-search-store')
        category_override = request.form.get('category')  # Optional manual category

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Save file temporarily
        temp_path = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(temp_path)

        # Auto-detect category from file path or use override
        if category_override:
            category = category_override
        else:
            category = detect_category_from_path(temp_path)

        # Get or create store
        if store_name not in file_search_stores:
            file_search_store = gemini_service.create_file_search_store(store_name)
            file_search_stores[store_name] = file_search_store.name

        store_id = file_search_stores[store_name]

        # Upload to file search store
        operation = gemini_service.upload_file_to_store(
            file_path=temp_path,
            store_id=store_id,
            display_name=file.filename
        )

        # Get database store record
        db_store = Store.query.filter_by(gemini_store_id=store_id).first()
        if not db_store:
            # Create database record if it doesn't exist
            db_store = Store(
                name=store_name,
                gemini_store_id=store_id,
                display_name=store_name
            )
            db.session.add(db_store)
            db.session.commit()

        # Save document record with category
        document = Document(
            store_id=db_store.id,
            filename=file.filename,
            category=category,
            file_path=temp_path,
            gemini_file_id=operation.name if hasattr(operation, 'name') else None,
            file_size=os.path.getsize(temp_path) if os.path.exists(temp_path) else None
        )
        db.session.add(document)
        db.session.commit()

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'success': True,
            'message': f'File "{file.filename}" uploaded and indexed successfully',
            'store_name': store_name,
            'category': category,
            'document_id': document.id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@files_bp.route('/list_stores', methods=['GET'])
def list_stores():
    """List all file search stores"""
    return jsonify({
        'success': True,
        'stores': list(file_search_stores.keys())
    })


@files_bp.route('/bulk_upload', methods=['POST'])
def bulk_upload():
    """
    Bulk upload documents from directory.

    Request JSON parameters:
        - source_directory: Path to directory containing files
        - store_name: Name of the store to upload to
        - auto_categorize: Whether to auto-detect categories (default: True)
        - scan_only: Only scan directory without uploading (default: False)
        - batch_size: Number of files to process per batch (default: 10)

    Returns:
        JSON response with upload results:
        - success: Boolean indicating overall success
        - total: Total number of files found
        - success_count: Number of successfully uploaded files
        - failed_count: Number of failed uploads
        - skipped_count: Number of skipped duplicates
        - files: List of file results with status
        - category_distribution: Dictionary of categories and counts
    """
    try:
        # Get request parameters
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        source_directory = data.get('source_directory')
        store_name = data.get('store_name')
        auto_categorize = data.get('auto_categorize', True)
        scan_only = data.get('scan_only', False)
        batch_size = data.get('batch_size', 10)

        # Validate required parameters
        if not source_directory:
            return jsonify({
                'success': False,
                'error': 'source_directory is required'
            }), 400

        if not store_name and not scan_only:
            return jsonify({
                'success': False,
                'error': 'store_name is required for upload'
            }), 400

        # Scan directory
        try:
            files = scan_directory(source_directory, auto_categorize=auto_categorize)
        except FileNotFoundError as e:
            return jsonify({
                'success': False,
                'error': f'Directory not found: {source_directory}'
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error scanning directory: {str(e)}'
            }), 500

        # Get category distribution
        category_dist = get_category_distribution(files)

        # If scan only, return file list without uploading
        if scan_only:
            return jsonify({
                'success': True,
                'total': len(files),
                'files': files,
                'category_distribution': category_dist
            })

        # Get store from database
        store = Store.query.filter_by(name=store_name).first()
        if not store:
            return jsonify({
                'success': False,
                'error': f'Store not found: {store_name}'
            }), 404

        # Upload files in batches
        results = upload_batch(files, store.id, batch_size=batch_size)

        # Return results
        return jsonify({
            'success': True,
            'total': results['total'],
            'success_count': results['success'],
            'failed_count': results['failed'],
            'skipped_count': results.get('skipped', 0),
            'files': results['files'],
            'category_distribution': category_dist,
            'message': f'Uploaded {results["success"]} files successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
