"""
Tests for bulk upload service
"""
import os
import pytest
import tempfile
import shutil
from app.services.bulk_upload_service import (
    scan_directory,
    detect_category,
    upload_batch,
    check_duplicate
)
from app.models import Document, Store
from app.database import db


class TestCategoryDetection:
    """Test category auto-detection from folder structure"""

    def test_detect_category_from_compliance_folder(self):
        """Should detect 'compliance' category from path"""
        file_path = r"C:\documents\compliance\policy.pdf"
        category = detect_category(file_path)
        assert category == "compliance"

    def test_detect_category_from_proposals_folder(self):
        """Should detect 'proposals' category from path"""
        file_path = r"C:\documents\proposals\bid_2024.docx"
        category = detect_category(file_path)
        assert category == "proposals"

    def test_detect_category_from_contracts_folder(self):
        """Should detect 'contracts' category from path"""
        file_path = r"C:\documents\contracts\agreement.pdf"
        category = detect_category(file_path)
        assert category == "contracts"

    def test_detect_category_from_technical_folder(self):
        """Should detect 'technical' category from path"""
        file_path = r"C:\documents\technical\spec.pdf"
        category = detect_category(file_path)
        assert category == "technical"

    def test_detect_category_from_pricing_folder(self):
        """Should detect 'pricing' category from path"""
        file_path = r"C:\documents\pricing\quote.xlsx"
        category = detect_category(file_path)
        assert category == "pricing"

    def test_detect_category_from_policies_folder(self):
        """Should detect 'policies' category from path"""
        file_path = r"C:\documents\policies\handbook.pdf"
        category = detect_category(file_path)
        assert category == "policies"

    def test_detect_category_from_requirements_folder(self):
        """Should detect 'requirements' category from path"""
        file_path = r"C:\documents\requirements\spec.docx"
        category = detect_category(file_path)
        assert category == "requirements"

    def test_detect_category_from_cvs_resumes_folder(self):
        """Should detect 'cvs_resumes' category from path"""
        file_path = r"C:\documents\cvs_resumes\resume.pdf"
        category = detect_category(file_path)
        assert category == "cvs_resumes"

    def test_detect_category_from_other_folder(self):
        """Should detect 'other' category from unknown folder"""
        file_path = r"C:\documents\other\misc.pdf"
        category = detect_category(file_path)
        assert category == "other"

    def test_detect_category_from_nested_path(self):
        """Should detect category from deeply nested path"""
        file_path = r"C:\users\docs\sales\compliance\subfolder\file.pdf"
        category = detect_category(file_path)
        assert category == "compliance"

    def test_detect_category_case_insensitive(self):
        """Should detect category case-insensitively"""
        file_path = r"C:\documents\COMPLIANCE\policy.pdf"
        category = detect_category(file_path)
        assert category == "compliance"

    def test_detect_category_unknown_folder(self):
        """Should return 'uncategorized' for unknown folders"""
        file_path = r"C:\documents\random_folder\file.pdf"
        category = detect_category(file_path)
        assert category == "uncategorized"


class TestDirectoryScanning:
    """Test directory scanning functionality"""

    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory structure for testing"""
        temp_dir = tempfile.mkdtemp()

        # Create category folders
        os.makedirs(os.path.join(temp_dir, "compliance"))
        os.makedirs(os.path.join(temp_dir, "proposals"))
        os.makedirs(os.path.join(temp_dir, "contracts"))

        # Create test files
        test_files = [
            os.path.join(temp_dir, "compliance", "policy1.pdf"),
            os.path.join(temp_dir, "compliance", "policy2.pdf"),
            os.path.join(temp_dir, "proposals", "bid.docx"),
            os.path.join(temp_dir, "contracts", "agreement.pdf"),
        ]

        for file_path in test_files:
            with open(file_path, 'w') as f:
                f.write("Test content")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_scan_directory_returns_all_files(self, temp_directory):
        """Should return all files in directory tree"""
        result = scan_directory(temp_directory, auto_categorize=True)

        assert len(result) == 4
        assert all('file_path' in item for item in result)
        assert all('category' in item for item in result)
        assert all('filename' in item for item in result)

    def test_scan_directory_auto_categorize_enabled(self, temp_directory):
        """Should auto-detect categories when enabled"""
        result = scan_directory(temp_directory, auto_categorize=True)

        # Group by category
        categories = [item['category'] for item in result]
        assert 'compliance' in categories
        assert 'proposals' in categories
        assert 'contracts' in categories

        # Check specific files have correct categories
        compliance_files = [r for r in result if r['category'] == 'compliance']
        assert len(compliance_files) == 2

    def test_scan_directory_auto_categorize_disabled(self, temp_directory):
        """Should not categorize when disabled"""
        result = scan_directory(temp_directory, auto_categorize=False)

        assert len(result) == 4
        assert all(item['category'] is None for item in result)

    def test_scan_directory_filters_supported_files(self, temp_directory):
        """Should only include supported file types"""
        # Add unsupported file
        unsupported_file = os.path.join(temp_directory, "compliance", "image.jpg")
        with open(unsupported_file, 'w') as f:
            f.write("Image")

        result = scan_directory(temp_directory, auto_categorize=True)

        # Should still have 4 files (jpg not supported for document upload)
        filenames = [item['filename'] for item in result]
        assert 'image.jpg' not in filenames

    def test_scan_directory_includes_file_size(self, temp_directory):
        """Should include file size in results"""
        result = scan_directory(temp_directory, auto_categorize=True)

        assert all('file_size' in item for item in result)
        assert all(item['file_size'] > 0 for item in result)

    def test_scan_empty_directory(self):
        """Should return empty list for empty directory"""
        temp_dir = tempfile.mkdtemp()
        result = scan_directory(temp_dir, auto_categorize=True)
        assert result == []
        shutil.rmtree(temp_dir)

    def test_scan_nonexistent_directory(self):
        """Should raise error for nonexistent directory"""
        with pytest.raises(FileNotFoundError):
            scan_directory(r"C:\nonexistent\path", auto_categorize=True)


class TestDuplicateDetection:
    """Test duplicate detection functionality"""

    def test_check_duplicate_exists(self, app):
        """Should detect when file already exists in store"""
        with app.app_context():
            # Create store
            store = Store(
                name="test-duplicate-store-1",
                gemini_store_id="stores/duplicate-test-123",
                display_name="Test Duplicate Store 1"
            )
            db.session.add(store)
            db.session.commit()

            # Add existing document
            doc = Document(
                store_id=store.id,
                filename="existing.pdf",
                category="compliance"
            )
            db.session.add(doc)
            db.session.commit()

            # Check duplicate
            is_duplicate = check_duplicate("existing.pdf", store.id)
            assert is_duplicate is True

    def test_check_duplicate_not_exists(self, app):
        """Should return False when file does not exist"""
        with app.app_context():
            # Create store
            store = Store(
                name="test-duplicate-store-2",
                gemini_store_id="stores/duplicate-test-456",
                display_name="Test Duplicate Store 2"
            )
            db.session.add(store)
            db.session.commit()

            # Check non-existent file
            is_duplicate = check_duplicate("new_file.pdf", store.id)
            assert is_duplicate is False

    def test_check_duplicate_different_store(self, app):
        """Should not detect duplicate in different store"""
        with app.app_context():
            # Create two stores
            store1 = Store(
                name="test-duplicate-store-3",
                gemini_store_id="stores/duplicate-test-789",
                display_name="Test Duplicate Store 3"
            )
            store2 = Store(
                name="test-duplicate-store-4",
                gemini_store_id="stores/duplicate-test-012",
                display_name="Test Duplicate Store 4"
            )
            db.session.add(store1)
            db.session.add(store2)
            db.session.commit()

            # Add document to store1
            doc = Document(
                store_id=store1.id,
                filename="file.pdf",
                category="compliance"
            )
            db.session.add(doc)
            db.session.commit()

            # Check in store2 - should not be duplicate
            is_duplicate = check_duplicate("file.pdf", store2.id)
            assert is_duplicate is False


class TestBatchUpload:
    """Test batch upload functionality"""

    @pytest.fixture
    def mock_gemini_service(self, mocker):
        """Mock Gemini service for testing"""
        mock = mocker.patch('app.services.bulk_upload_service.GeminiService')
        mock_instance = mock.return_value
        mock_instance.upload_file_to_store.return_value = type('obj', (object,), {
            'done': True,
            'name': 'operations/test123'
        })()
        return mock_instance

    def test_upload_batch_success(self, app, mock_gemini_service):
        """Should successfully upload batch of files"""
        with app.app_context():
            # Create store
            store = Store(
                name="test-store",
                gemini_store_id="stores/test123",
                display_name="Test Store"
            )
            db.session.add(store)
            db.session.commit()

            # Create temp files
            temp_dir = tempfile.mkdtemp()
            files = []
            for i in range(3):
                file_path = os.path.join(temp_dir, f"file{i}.pdf")
                with open(file_path, 'w') as f:
                    f.write(f"Content {i}")
                files.append({
                    'file_path': file_path,
                    'filename': f"file{i}.pdf",
                    'category': 'compliance',
                    'file_size': os.path.getsize(file_path)
                })

            # Upload batch
            results = upload_batch(files, store.id, batch_size=10)

            assert results['total'] == 3
            assert results['success'] == 3
            assert results['failed'] == 0
            assert len(results['files']) == 3

            # Verify documents in database
            docs = Document.query.filter_by(store_id=store.id).all()
            assert len(docs) == 3

            # Cleanup
            shutil.rmtree(temp_dir)

    def test_upload_batch_with_duplicates(self, app, mock_gemini_service):
        """Should skip duplicate files"""
        with app.app_context():
            # Create store
            store = Store(
                name="test-store",
                gemini_store_id="stores/test123",
                display_name="Test Store"
            )
            db.session.add(store)
            db.session.commit()

            # Add existing document
            existing_doc = Document(
                store_id=store.id,
                filename="file0.pdf",
                category="compliance"
            )
            db.session.add(existing_doc)
            db.session.commit()

            # Create temp files
            temp_dir = tempfile.mkdtemp()
            files = []
            for i in range(3):
                file_path = os.path.join(temp_dir, f"file{i}.pdf")
                with open(file_path, 'w') as f:
                    f.write(f"Content {i}")
                files.append({
                    'file_path': file_path,
                    'filename': f"file{i}.pdf",
                    'category': 'compliance',
                    'file_size': os.path.getsize(file_path)
                })

            # Upload batch
            results = upload_batch(files, store.id, batch_size=10)

            assert results['total'] == 3
            assert results['success'] == 2  # file1 and file2
            assert results['skipped'] == 1  # file0 already exists

            # Cleanup
            shutil.rmtree(temp_dir)

    def test_upload_batch_handles_errors(self, app, mocker):
        """Should continue on upload errors and collect error info"""
        with app.app_context():
            # Create store
            store = Store(
                name="test-store",
                gemini_store_id="stores/test123",
                display_name="Test Store"
            )
            db.session.add(store)
            db.session.commit()

            # Mock Gemini service to fail on second file
            mock_service = mocker.patch('app.services.bulk_upload_service.GeminiService')
            mock_instance = mock_service.return_value

            def upload_side_effect(file_path, *args, **kwargs):
                if 'file1.pdf' in file_path:
                    raise Exception("Upload failed")
                return type('obj', (object,), {
                    'done': True,
                    'name': 'operations/test123'
                })()

            mock_instance.upload_file_to_store.side_effect = upload_side_effect

            # Create temp files
            temp_dir = tempfile.mkdtemp()
            files = []
            for i in range(3):
                file_path = os.path.join(temp_dir, f"file{i}.pdf")
                with open(file_path, 'w') as f:
                    f.write(f"Content {i}")
                files.append({
                    'file_path': file_path,
                    'filename': f"file{i}.pdf",
                    'category': 'compliance',
                    'file_size': os.path.getsize(file_path)
                })

            # Upload batch
            results = upload_batch(files, store.id, batch_size=10)

            assert results['total'] == 3
            assert results['success'] == 2
            assert results['failed'] == 1

            # Check error info
            failed_file = [f for f in results['files'] if f['status'] == 'failed'][0]
            assert failed_file['filename'] == 'file1.pdf'
            assert 'error' in failed_file

            # Cleanup
            shutil.rmtree(temp_dir)

    def test_upload_batch_processes_in_batches(self, app, mock_gemini_service):
        """Should process files in specified batch size"""
        with app.app_context():
            # Create store
            store = Store(
                name="test-store",
                gemini_store_id="stores/test123",
                display_name="Test Store"
            )
            db.session.add(store)
            db.session.commit()

            # Create temp files
            temp_dir = tempfile.mkdtemp()
            files = []
            for i in range(25):
                file_path = os.path.join(temp_dir, f"file{i}.pdf")
                with open(file_path, 'w') as f:
                    f.write(f"Content {i}")
                files.append({
                    'file_path': file_path,
                    'filename': f"file{i}.pdf",
                    'category': 'compliance',
                    'file_size': os.path.getsize(file_path)
                })

            # Upload with batch size of 10
            results = upload_batch(files, store.id, batch_size=10)

            assert results['total'] == 25
            assert results['success'] == 25

            # Verify all documents in database
            docs = Document.query.filter_by(store_id=store.id).all()
            assert len(docs) == 25

            # Cleanup
            shutil.rmtree(temp_dir)


@pytest.fixture
def app():
    """Create Flask app for testing"""
    from app import create_app

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
