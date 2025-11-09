"""
Tests for bulk upload endpoint
"""
import json
import tempfile
import shutil
import os
import pytest
from app import create_app
from app.database import db
from app.models import Store, Document


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def test_store(app):
    """Create test store"""
    with app.app_context():
        store = Store(
            name="test-store",
            gemini_store_id="stores/test123",
            display_name="Test Store"
        )
        db.session.add(store)
        db.session.commit()
        return store.id


@pytest.fixture
def temp_directory():
    """Create temporary directory with test files"""
    temp_dir = tempfile.mkdtemp()

    # Create category folders
    os.makedirs(os.path.join(temp_dir, "compliance"))
    os.makedirs(os.path.join(temp_dir, "proposals"))

    # Create test files
    test_files = [
        os.path.join(temp_dir, "compliance", "policy1.pdf"),
        os.path.join(temp_dir, "compliance", "policy2.pdf"),
        os.path.join(temp_dir, "proposals", "bid.docx"),
    ]

    for file_path in test_files:
        with open(file_path, 'w') as f:
            f.write("Test content")

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


class TestBulkUploadEndpoint:
    """Test bulk upload endpoint"""

    def test_bulk_upload_missing_parameters(self, client):
        """Should return 400 if required parameters missing"""
        response = client.post(
            '/api/files/bulk_upload',
            json={}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

    def test_bulk_upload_nonexistent_directory(self, client, test_store):
        """Should return error for nonexistent directory"""
        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': r'C:\nonexistent\path',
                'store_name': 'test-store',
                'auto_categorize': True
            }
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error'].lower()

    def test_bulk_upload_nonexistent_store(self, client, temp_directory):
        """Should return error for nonexistent store"""
        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': temp_directory,
                'store_name': 'nonexistent-store',
                'auto_categorize': True
            }
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error'].lower()

    def test_bulk_upload_scan_only(self, client, test_store, temp_directory):
        """Should scan directory without uploading when scan_only=True"""
        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': temp_directory,
                'store_name': 'test-store',
                'auto_categorize': True,
                'scan_only': True
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] == 3
        assert 'files' in data
        assert 'category_distribution' in data

        # Verify categories were detected
        assert data['category_distribution']['compliance'] == 2
        assert data['category_distribution']['proposals'] == 1

    def test_bulk_upload_scan_only_no_auto_categorize(self, client, test_store, temp_directory):
        """Should scan without categories when auto_categorize=False"""
        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': temp_directory,
                'store_name': 'test-store',
                'auto_categorize': False,
                'scan_only': True
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] == 3

        # Check that files have no category
        for file_info in data['files']:
            assert file_info['category'] is None

    def test_bulk_upload_with_mock_gemini(self, client, test_store, temp_directory, mocker):
        """Should successfully upload files with mocked Gemini service"""
        # Mock Gemini service
        mock_gemini = mocker.patch('app.services.bulk_upload_service.GeminiService')
        mock_instance = mock_gemini.return_value
        mock_instance.upload_file_to_store.return_value = type('obj', (object,), {
            'done': True,
            'name': 'operations/test123'
        })()

        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': temp_directory,
                'store_name': 'test-store',
                'auto_categorize': True
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] == 3
        assert data['success_count'] == 3
        assert data['failed_count'] == 0
        assert data['skipped_count'] == 0

        # Verify documents were created in database
        with client.application.app_context():
            docs = Document.query.filter_by(store_id=test_store).all()
            assert len(docs) == 3

    def test_bulk_upload_with_duplicates(self, client, test_store, temp_directory, mocker):
        """Should skip duplicate files"""
        # Add existing document
        with client.application.app_context():
            doc = Document(
                store_id=test_store,
                filename="policy1.pdf",
                category="compliance"
            )
            db.session.add(doc)
            db.session.commit()

        # Mock Gemini service
        mock_gemini = mocker.patch('app.services.bulk_upload_service.GeminiService')
        mock_instance = mock_gemini.return_value
        mock_instance.upload_file_to_store.return_value = type('obj', (object,), {
            'done': True,
            'name': 'operations/test123'
        })()

        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': temp_directory,
                'store_name': 'test-store',
                'auto_categorize': True
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] == 3
        assert data['success_count'] == 2  # Only 2 new files
        assert data['skipped_count'] == 1  # 1 duplicate

        # Check that skipped file is identified
        skipped_files = [f for f in data['files'] if f['status'] == 'skipped']
        assert len(skipped_files) == 1
        assert skipped_files[0]['filename'] == 'policy1.pdf'

    def test_bulk_upload_with_batch_size(self, client, test_store, temp_directory, mocker):
        """Should respect batch_size parameter"""
        # Create more files
        for i in range(5):
            file_path = os.path.join(temp_directory, "compliance", f"extra{i}.pdf")
            with open(file_path, 'w') as f:
                f.write(f"Extra content {i}")

        # Mock Gemini service
        mock_gemini = mocker.patch('app.services.bulk_upload_service.GeminiService')
        mock_instance = mock_gemini.return_value
        mock_instance.upload_file_to_store.return_value = type('obj', (object,), {
            'done': True,
            'name': 'operations/test123'
        })()

        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': temp_directory,
                'store_name': 'test-store',
                'auto_categorize': True,
                'batch_size': 3
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        # 3 original + 5 extra = 8 total
        assert data['total'] == 8

    def test_bulk_upload_category_distribution(self, client, test_store, temp_directory):
        """Should return accurate category distribution"""
        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': temp_directory,
                'store_name': 'test-store',
                'auto_categorize': True,
                'scan_only': True
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'category_distribution' in data
        distribution = data['category_distribution']
        assert distribution['compliance'] == 2
        assert distribution['proposals'] == 1
        assert sum(distribution.values()) == data['total']

    def test_bulk_upload_returns_file_details(self, client, test_store, temp_directory):
        """Should return detailed information for each file"""
        response = client.post(
            '/api/files/bulk_upload',
            json={
                'source_directory': temp_directory,
                'store_name': 'test-store',
                'auto_categorize': True,
                'scan_only': True
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'files' in data
        for file_info in data['files']:
            assert 'filename' in file_info
            assert 'category' in file_info
            assert 'file_size' in file_info
            assert file_info['file_size'] > 0
