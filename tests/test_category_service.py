"""
Tests for category service functionality.

Tests category detection, configuration, and statistics.
"""
import pytest
from app.services.category_service import (
    CATEGORIES,
    detect_category_from_path,
    get_category_stats,
    get_all_categories
)
from app.models import Document, Store
from app.database import db


class TestCategoryConfiguration:
    """Test category configuration and structure."""

    def test_categories_structure(self):
        """Test that CATEGORIES dict has correct structure."""
        required_keys = {'color', 'icon', 'description'}
        expected_categories = {
            'compliance', 'contracts', 'proposals', 'pricing',
            'requirements', 'technical', 'cvs_resumes', 'policies', 'other'
        }

        assert set(CATEGORIES.keys()) == expected_categories

        for category, config in CATEGORIES.items():
            assert set(config.keys()) == required_keys
            assert isinstance(config['color'], str)
            assert config['color'].startswith('#')
            assert isinstance(config['icon'], str)
            assert isinstance(config['description'], str)

    def test_get_all_categories(self):
        """Test getting all categories with configuration."""
        categories = get_all_categories()

        assert len(categories) == 9
        assert all('name' in cat for cat in categories)
        assert all('color' in cat for cat in categories)
        assert all('icon' in cat for cat in categories)
        assert all('description' in cat for cat in categories)


class TestCategoryDetection:
    """Test category auto-detection from file paths."""

    def test_detect_compliance_category(self):
        """Test detection of compliance documents."""
        paths = [
            r"C:\users\j_car\Downloads\Sales Pipeline Rag\documents\cleaned_organized_docs\compliance\security.pdf",
            r"C:\docs\compliance\PSPF_requirements.docx",
            "/docs/compliance/E8_certification.pdf"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "compliance"

    def test_detect_contracts_category(self):
        """Test detection of contract documents."""
        paths = [
            r"C:\users\j_car\Downloads\Sales Pipeline Rag\documents\cleaned_organized_docs\contracts\agreement.pdf",
            "/docs/contracts/legal_contract_2024.pdf"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "contracts"

    def test_detect_proposals_category(self):
        """Test detection of proposal documents."""
        paths = [
            r"C:\docs\proposals\tender_response.pdf",
            "/docs/proposal/RFP_response.docx",
            r"C:\users\j_car\Downloads\Sales Pipeline Rag\documents\cleaned_organized_docs\proposals\project_proposal.pdf"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "proposals"

    def test_detect_pricing_category(self):
        """Test detection of pricing documents."""
        paths = [
            r"C:\docs\pricing\quote_2024.pdf",
            "/docs/pricing/budget_estimate.xlsx"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "pricing"

    def test_detect_requirements_category(self):
        """Test detection of requirements documents."""
        paths = [
            r"C:\docs\requirements\RFP_specs.pdf",
            "/docs/requirements/SOW_document.docx"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "requirements"

    def test_detect_technical_category(self):
        """Test detection of technical documents."""
        paths = [
            r"C:\docs\technical\architecture.pdf",
            "/docs/technical/specifications.docx"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "technical"

    def test_detect_cvs_resumes_category(self):
        """Test detection of CV/resume documents."""
        paths = [
            r"C:\docs\cvs_resumes\john_doe_cv.pdf",
            "/docs/cvs_resumes/team_resumes.pdf",
            r"C:\docs\cv\developer_resume.pdf",
            "/docs/resumes/engineer_cv.docx"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "cvs_resumes"

    def test_detect_policies_category(self):
        """Test detection of policy documents."""
        paths = [
            r"C:\docs\policies\company_policy.pdf",
            "/docs/policies/internal_guidelines.pdf"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "policies"

    def test_detect_other_category(self):
        """Test detection defaults to 'other' for unknown paths."""
        paths = [
            r"C:\docs\miscellaneous\random.pdf",
            "/docs/unknown/file.pdf",
            r"C:\random_folder\document.docx"
        ]

        for path in paths:
            assert detect_category_from_path(path) == "other"

    def test_case_insensitive_detection(self):
        """Test that category detection is case-insensitive."""
        paths = [
            r"C:\docs\COMPLIANCE\file.pdf",
            r"C:\docs\Proposals\file.pdf",
            r"C:\docs\TeChnIcal\file.pdf"
        ]

        assert detect_category_from_path(paths[0]) == "compliance"
        assert detect_category_from_path(paths[1]) == "proposals"
        assert detect_category_from_path(paths[2]) == "technical"


class TestCategoryStats:
    """Test category statistics functionality."""

    def test_get_category_stats_empty_database(self, app):
        """Test getting stats when database is empty."""
        with app.app_context():
            stats = get_category_stats()

            assert isinstance(stats, dict)
            assert len(stats) == 9
            # All categories should have 0 count
            for category in CATEGORIES.keys():
                assert stats[category] == 0

    def test_get_category_stats_with_documents(self, app):
        """Test getting stats with documents in database."""
        with app.app_context():
            # Create a test store
            store = Store(
                name='test-store',
                gemini_store_id='test-gemini-store-123',
                display_name='Test Store'
            )
            db.session.add(store)
            db.session.commit()

            # Add documents with different categories
            documents = [
                Document(store_id=store.id, filename='doc1.pdf', category='compliance'),
                Document(store_id=store.id, filename='doc2.pdf', category='compliance'),
                Document(store_id=store.id, filename='doc3.pdf', category='proposals'),
                Document(store_id=store.id, filename='doc4.pdf', category='technical'),
                Document(store_id=store.id, filename='doc5.pdf', category='technical'),
                Document(store_id=store.id, filename='doc6.pdf', category='technical'),
                Document(store_id=store.id, filename='doc7.pdf', category='other'),
            ]

            for doc in documents:
                db.session.add(doc)
            db.session.commit()

            # Get stats
            stats = get_category_stats()

            # Verify counts
            assert stats['compliance'] == 2
            assert stats['proposals'] == 1
            assert stats['technical'] == 3
            assert stats['other'] == 1
            assert stats['contracts'] == 0
            assert stats['pricing'] == 0

            # Cleanup
            for doc in documents:
                db.session.delete(doc)
            db.session.delete(store)
            db.session.commit()

    def test_get_category_stats_ignores_null_categories(self, app):
        """Test that stats ignore documents with null categories."""
        with app.app_context():
            store = Store(
                name='test-store-2',
                gemini_store_id='test-gemini-store-456',
                display_name='Test Store 2'
            )
            db.session.add(store)
            db.session.commit()

            # Add documents with null/None categories
            documents = [
                Document(store_id=store.id, filename='doc1.pdf', category='compliance'),
                Document(store_id=store.id, filename='doc2.pdf', category=None),
                Document(store_id=store.id, filename='doc3.pdf', category=''),
            ]

            for doc in documents:
                db.session.add(doc)
            db.session.commit()

            stats = get_category_stats()

            # Only the compliance document should be counted
            assert stats['compliance'] == 1
            assert sum(stats.values()) == 1

            # Cleanup
            for doc in documents:
                db.session.delete(doc)
            db.session.delete(store)
            db.session.commit()
