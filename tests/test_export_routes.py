"""
Tests for export routes - PDF and DOCX generation endpoints
"""
import pytest
import json
from app import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


class TestExportPDFRoute:
    """Tests for PDF export route"""

    def test_export_pdf_success(self, client):
        """Test successful PDF generation"""
        data = {
            "markdown_text": "# Test Document\n\nThis is a test.",
            "metadata": {
                "title": "Test PDF",
                "question": "What is this?",
                "date": "2025-11-09"
            }
        }

        response = client.post(
            '/api/export/pdf',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        assert response.headers['Content-Disposition'].startswith('attachment; filename=')
        assert b'%PDF' in response.data[:10]

    def test_export_pdf_missing_content(self, client):
        """Test PDF generation with missing markdown_text"""
        data = {
            "metadata": {"title": "Test"}
        }

        response = client.post(
            '/api/export/pdf',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert json_data['success'] is False
        assert 'markdown_text' in json_data['error'].lower()

    def test_export_pdf_with_minimal_metadata(self, client):
        """Test PDF generation with minimal metadata"""
        data = {
            "markdown_text": "# Simple Test",
            "metadata": {
                "title": "Minimal PDF"
            }
        }

        response = client.post(
            '/api/export/pdf',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.content_type == 'application/pdf'


class TestExportDOCXRoute:
    """Tests for DOCX export route"""

    def test_export_docx_success(self, client):
        """Test successful DOCX generation"""
        data = {
            "markdown_text": "# Test Document\n\nThis is a test.",
            "metadata": {
                "title": "Test DOCX",
                "question": "What is this?",
                "date": "2025-11-09",
                "response_mode": "Tender Response",
                "company": "Test Company"
            }
        }

        response = client.post(
            '/api/export/docx',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        assert response.headers['Content-Disposition'].startswith('attachment; filename=')
        # Check for DOCX file signature (PK zip format)
        assert response.data[:2] == b'PK'

    def test_export_docx_missing_content(self, client):
        """Test DOCX generation with missing markdown_text"""
        data = {
            "metadata": {"title": "Test"}
        }

        response = client.post(
            '/api/export/docx',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert json_data['success'] is False
        assert 'markdown_text' in json_data['error'].lower()

    def test_export_docx_with_code_blocks(self, client):
        """Test DOCX generation with code blocks"""
        data = {
            "markdown_text": """# Code Example

```python
def hello():
    print("Hello, World!")
```
""",
            "metadata": {
                "title": "Code Document"
            }
        }

        response = client.post(
            '/api/export/docx',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    def test_export_docx_with_tables(self, client):
        """Test DOCX generation with tables"""
        data = {
            "markdown_text": """# Table Test

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
""",
            "metadata": {
                "title": "Table Document"
            }
        }

        response = client.post(
            '/api/export/docx',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


class TestExportFilenames:
    """Tests for export filename generation"""

    def test_pdf_filename_with_title(self, client):
        """Test PDF filename includes title"""
        data = {
            "markdown_text": "# Test",
            "metadata": {
                "title": "My Custom Title"
            }
        }

        response = client.post(
            '/api/export/pdf',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        disposition = response.headers['Content-Disposition']
        assert 'My_Custom_Title' in disposition or 'My Custom Title' in disposition

    def test_docx_filename_with_title(self, client):
        """Test DOCX filename includes title"""
        data = {
            "markdown_text": "# Test",
            "metadata": {
                "title": "My Custom Title"
            }
        }

        response = client.post(
            '/api/export/docx',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        disposition = response.headers['Content-Disposition']
        assert 'My_Custom_Title' in disposition or 'My Custom Title' in disposition
