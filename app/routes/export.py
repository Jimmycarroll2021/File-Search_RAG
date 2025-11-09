"""
Export blueprint - handles PDF and DOCX export functionality
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import re
from app.services.export_service import ExportService

export_bp = Blueprint('export', __name__, url_prefix='/api/export')

# Initialize export service
export_service = ExportService()


@export_bp.route('/pdf', methods=['POST'])
def export_pdf():
    """Export markdown content to PDF"""
    try:
        data = request.json
        markdown_text = data.get('markdown_text')
        metadata = data.get('metadata', {})

        if not markdown_text:
            return jsonify({
                'success': False,
                'error': 'markdown_text is required'
            }), 400

        # Generate PDF
        pdf_buffer = export_service.markdown_to_pdf(markdown_text, metadata)

        # Generate filename
        title = metadata.get('title', 'document')
        filename = _generate_filename(title, 'pdf')

        # Send file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@export_bp.route('/docx', methods=['POST'])
def export_docx():
    """Export markdown content to DOCX"""
    try:
        data = request.json
        markdown_text = data.get('markdown_text')
        metadata = data.get('metadata', {})

        if not markdown_text:
            return jsonify({
                'success': False,
                'error': 'markdown_text is required'
            }), 400

        # Generate DOCX
        docx_buffer = export_service.markdown_to_docx(markdown_text, metadata)

        # Generate filename
        title = metadata.get('title', 'document')
        filename = _generate_filename(title, 'docx')

        # Send file
        return send_file(
            docx_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _generate_filename(title, extension):
    """
    Generate a safe filename from title and extension.

    Args:
        title: Document title
        extension: File extension (pdf or docx)

    Returns:
        Safe filename string
    """
    # Replace spaces with underscores
    safe_title = title.replace(' ', '_')

    # Remove invalid characters
    safe_title = re.sub(r'[<>:"/\\|?*]', '', safe_title)

    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return f"{safe_title}_{timestamp}.{extension}"
