"""Unit tests for BeneficiaryService."""

import pytest
from datetime import datetime, date
import uuid

from app.services.beneficiary_service import BeneficiaryService
from app.models.beneficiary import Beneficiary, BeneficiaryStatus, EmploymentStatus, EducationLevel
from app.core.exceptions import NotFoundError, ValidationError, PermissionError


class TestBeneficiaryService:
    """Test cases for BeneficiaryService."""

    def test_get_all_basic(self, db_session, admin_user, multiple_beneficiaries):
        """Test basic get_all functionality."""
        service = BeneficiaryService(db_session, admin_user)
        beneficiaries, total = service.get_all()

        assert total == 7  # 5 active + 2 inactive
        assert len(beneficiaries) == 7
        assert all(b.tenant_id == admin_user.tenant_id for b in beneficiaries)

    def test_get_all_with_pagination(self, db_session, admin_user, multiple_beneficiaries):
        """Test get_all with pagination."""
        service = BeneficiaryService(db_session, admin_user)

        # First page
        beneficiaries, total = service.get_all(page=1, per_page=3)
        assert len(beneficiaries) == 3
        assert total == 7

        # Second page
        beneficiaries, total = service.get_all(page=2, per_page=3)
        assert len(beneficiaries) == 3

        # Third page
        beneficiaries, total = service.get_all(page=3, per_page=3)
        assert len(beneficiaries) == 1

    def test_get_all_with_search(self, db_session, admin_user, multiple_beneficiaries):
        """Test get_all with search functionality."""
        service = BeneficiaryService(db_session, admin_user)

        # Search by first name
        beneficiaries, total = service.get_all(search="Test")
        assert total == 5
        assert all("Test" in b.first_name for b in beneficiaries)

        # Search by email
        beneficiaries, total = service.get_all(search="inactive")
        assert total == 2
        assert all("inactive" in b.email for b in beneficiaries)

    def test_get_all_with_status_filter(self, db_session, admin_user, multiple_beneficiaries):
        """Test get_all with status filter."""
        service = BeneficiaryService(db_session, admin_user)

        # Active beneficiaries
        beneficiaries, total = service.get_all(status="active")
        assert total == 5
        assert all(b.status == BeneficiaryStatus.ACTIVE for b in beneficiaries)

        # Inactive beneficiaries
        beneficiaries, total = service.get_all(status="inactive")
        assert total == 2
        assert all(b.status == BeneficiaryStatus.INACTIVE for b in beneficiaries)

        # Invalid status
        with pytest.raises(ValidationError) as exc:
            service.get_all(status="invalid_status")
        assert "Invalid status" in str(exc.value)

    def test_get_all_with_trainer_filter(self, db_session, admin_user, trainer_user, multiple_beneficiaries):
        """Test get_all with trainer filter."""
        service = BeneficiaryService(db_session, admin_user)

        beneficiaries, total = service.get_all(assigned_trainer_id=trainer_user.id)
        assert total == 3  # Based on fixture: i % 2 == 0
        assert all(b.assigned_trainer_id == trainer_user.id for b in beneficiaries)

    def test_get_all_with_tags_filter(self, db_session, admin_user, multiple_beneficiaries):
        """Test get_all with tags filter."""
        service = BeneficiaryService(db_session, admin_user)

        # Filter by single tag
        beneficiaries, total = service.get_all(tags=["tag1"])
        assert total == 2  # Based on fixture: i % 3 == 0

        # Filter by multiple tags
        beneficiaries, total = service.get_all(tags=["tag1", "tag2"])
        assert total == 2
        assert all("tag1" in b.tags and "tag2" in b.tags for b in beneficiaries)

    def test_get_all_trainer_role_restriction(self, db_session, trainer_user, multiple_beneficiaries):
        """Test that trainers only see their assigned beneficiaries."""
        service = BeneficiaryService(db_session, trainer_user)

        beneficiaries, total = service.get_all()
        assert total == 3  # Only assigned beneficiaries
        assert all(b.assigned_trainer_id == trainer_user.id for b in beneficiaries)

    def test_get_all_sorting(self, db_session, admin_user, multiple_beneficiaries):
        """Test get_all with different sorting options."""
        service = BeneficiaryService(db_session, admin_user)

        # Sort by first_name ascending
        beneficiaries, _ = service.get_all(sort_by="first_name", sort_order="asc")
        first_names = [b.first_name for b in beneficiaries]
        assert first_names == sorted(first_names)

        # Sort by created_at descending (default)
        beneficiaries, _ = service.get_all(sort_by="created_at", sort_order="desc")
        created_dates = [b.created_at for b in beneficiaries]
        assert created_dates == sorted(created_dates, reverse=True)

    def test_get_by_id_success(self, db_session, admin_user, test_beneficiary):
        """Test successful get_by_id."""
        service = BeneficiaryService(db_session, admin_user)

        beneficiary = service.get_by_id(test_beneficiary.id)
        assert beneficiary.id == test_beneficiary.id
        assert beneficiary.email == test_beneficiary.email

    def test_get_by_id_not_found(self, db_session, admin_user):
        """Test get_by_id with non-existent ID."""
        service = BeneficiaryService(db_session, admin_user)

        with pytest.raises(NotFoundError) as exc:
            service.get_by_id(999999)
        assert "Beneficiary not found" in str(exc.value)

    def test_get_by_id_trainer_permission(self, db_session, trainer_user, test_beneficiary):
        """Test trainer can't access non-assigned beneficiary."""
        service = BeneficiaryService(db_session, trainer_user)

        # Beneficiary not assigned to this trainer
        with pytest.raises(PermissionError) as exc:
            service.get_by_id(test_beneficiary.id)
        assert "don't have permission" in str(exc.value)

    def test_get_by_uuid_success(self, db_session, admin_user, test_beneficiary):
        """Test successful get_by_uuid."""
        service = BeneficiaryService(db_session, admin_user)

        beneficiary = service.get_by_uuid(str(test_beneficiary.uuid))
        assert beneficiary.id == test_beneficiary.id
        assert beneficiary.uuid == test_beneficiary.uuid

    def test_get_by_uuid_invalid_format(self, db_session, admin_user):
        """Test get_by_uuid with invalid UUID format."""
        service = BeneficiaryService(db_session, admin_user)

        with pytest.raises(ValidationError) as exc:
            service.get_by_uuid("invalid-uuid")
        assert "Invalid UUID format" in str(exc.value)

    def test_create_success(self, db_session, admin_user, test_tenant):
        """Test successful beneficiary creation."""
        service = BeneficiaryService(db_session, admin_user)

        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@test.com",
            "phone": "+33987654321",
            "date_of_birth": "1995-05-15",
            "employment_status": "employed",
            "education_level": "bachelor",
        }

        beneficiary = service.create(data)

        assert beneficiary.id is not None
        assert beneficiary.first_name == "Jane"
        assert beneficiary.last_name == "Smith"
        assert beneficiary.email == "jane.smith@test.com"
        assert beneficiary.tenant_id == test_tenant.id
        assert beneficiary.created_by == admin_user.id
        assert beneficiary.employment_status == EmploymentStatus.EMPLOYED
        assert beneficiary.education_level == EducationLevel.BACHELOR

    def test_create_missing_required_fields(self, db_session, admin_user):
        """Test create with missing required fields."""
        service = BeneficiaryService(db_session, admin_user)

        # Missing first_name
        with pytest.raises(ValidationError) as exc:
            service.create({"last_name": "Smith"})
        assert "first_name is required" in str(exc.value)

        # Missing last_name
        with pytest.raises(ValidationError) as exc:
            service.create({"first_name": "Jane"})
        assert "last_name is required" in str(exc.value)

    def test_create_duplicate_email(self, db_session, admin_user, test_beneficiary):
        """Test create with duplicate email."""
        service = BeneficiaryService(db_session, admin_user)

        data = {"first_name": "Another", "last_name": "User", "email": test_beneficiary.email}  # Duplicate email

        with pytest.raises(ValidationError) as exc:
            service.create(data)
        assert "Email already exists" in str(exc.value)

    def test_create_invalid_enums(self, db_session, admin_user):
        """Test create with invalid enum values."""
        service = BeneficiaryService(db_session, admin_user)

        # Invalid status
        data = {"first_name": "Test", "last_name": "User", "status": "invalid_status"}

        with pytest.raises(ValidationError) as exc:
            service.create(data)
        assert "Invalid status" in str(exc.value)

        # Invalid employment status
        data = {"first_name": "Test", "last_name": "User", "employment_status": "invalid_employment"}

        with pytest.raises(ValidationError) as exc:
            service.create(data)
        assert "Invalid employment status" in str(exc.value)

    def test_update_success(self, db_session, admin_user, test_beneficiary):
        """Test successful beneficiary update."""
        service = BeneficiaryService(db_session, admin_user)

        data = {"first_name": "Updated", "email": "updated.email@test.com", "employment_status": "self_employed"}

        beneficiary = service.update(test_beneficiary.id, data)

        assert beneficiary.first_name == "Updated"
        assert beneficiary.email == "updated.email@test.com"
        assert beneficiary.employment_status == EmploymentStatus.SELF_EMPLOYED
        assert beneficiary.last_name == test_beneficiary.last_name  # Unchanged

    def test_update_trainer_permission(self, db_session, trainer_user, test_beneficiary):
        """Test trainer can't update non-assigned beneficiary."""
        service = BeneficiaryService(db_session, trainer_user)

        with pytest.raises(PermissionError) as exc:
            service.update(test_beneficiary.id, {"first_name": "Updated"})
        assert "don't have permission" in str(exc.value)

    def test_delete_success(self, db_session, admin_user, test_beneficiary):
        """Test successful beneficiary deletion (soft delete)."""
        service = BeneficiaryService(db_session, admin_user)

        result = service.delete(test_beneficiary.id)

        assert result is True
        assert test_beneficiary.status == BeneficiaryStatus.INACTIVE

    def test_delete_permission_denied(self, db_session, trainer_user, test_beneficiary):
        """Test non-admin can't delete beneficiary."""
        service = BeneficiaryService(db_session, trainer_user)

        with pytest.raises(PermissionError) as exc:
            service.delete(test_beneficiary.id)
        assert "Only administrators can delete" in str(exc.value)

    def test_add_note_success(self, db_session, admin_user, test_beneficiary):
        """Test successful note addition."""
        service = BeneficiaryService(db_session, admin_user)

        note_text = "This is a test note"
        beneficiary = service.add_note(test_beneficiary.id, note_text)

        assert len(beneficiary.notes) == 1
        assert beneficiary.notes[0]["text"] == note_text
        assert beneficiary.notes[0]["created_by"] == admin_user.id
        assert "id" in beneficiary.notes[0]
        assert "created_at" in beneficiary.notes[0]

    def test_add_note_student_denied(self, db_session, student_user, test_beneficiary):
        """Test students can't add notes."""
        service = BeneficiaryService(db_session, student_user)

        with pytest.raises(PermissionError) as exc:
            service.add_note(test_beneficiary.id, "Note")
        assert "Students cannot add notes" in str(exc.value)

    def test_add_tag_success(self, db_session, admin_user, test_beneficiary):
        """Test successful tag addition."""
        service = BeneficiaryService(db_session, admin_user)

        beneficiary = service.add_tag(test_beneficiary.id, "new-tag")

        assert "new-tag" in beneficiary.tags

        # Add duplicate tag (should not add again)
        beneficiary = service.add_tag(test_beneficiary.id, "new-tag")
        assert beneficiary.tags.count("new-tag") == 1

    def test_remove_tag_success(self, db_session, admin_user, test_beneficiary):
        """Test successful tag removal."""
        service = BeneficiaryService(db_session, admin_user)

        # First add a tag
        service.add_tag(test_beneficiary.id, "tag-to-remove")

        # Then remove it
        beneficiary = service.remove_tag(test_beneficiary.id, "tag-to-remove")

        assert "tag-to-remove" not in beneficiary.tags

    def test_get_statistics(self, db_session, admin_user, multiple_beneficiaries):
        """Test statistics generation."""
        service = BeneficiaryService(db_session, admin_user)

        stats = service.get_statistics()

        assert stats["total"] == 7
        assert stats["by_status"]["active"] == 5
        assert stats["by_status"]["inactive"] == 2
        assert "by_employment" in stats
        assert "by_education" in stats
        assert "by_age" in stats

    def test_get_statistics_trainer_filtered(self, db_session, trainer_user, multiple_beneficiaries):
        """Test statistics are filtered for trainers."""
        service = BeneficiaryService(db_session, trainer_user)

        stats = service.get_statistics()

        assert stats["total"] == 3  # Only assigned beneficiaries

    def test_assign_trainer_success(self, db_session, admin_user, test_beneficiary, trainer_user):
        """Test successful trainer assignment."""
        service = BeneficiaryService(db_session, admin_user)

        beneficiary = service.assign_trainer(test_beneficiary.id, trainer_user.id)

        assert beneficiary.assigned_trainer_id == trainer_user.id

    def test_assign_trainer_invalid_trainer(self, db_session, admin_user, test_beneficiary):
        """Test assign non-existent or non-trainer user."""
        service = BeneficiaryService(db_session, admin_user)

        with pytest.raises(ValidationError) as exc:
            service.assign_trainer(test_beneficiary.id, 999999)
        assert "Invalid trainer ID" in str(exc.value)

    def test_assign_trainer_permission_denied(self, db_session, trainer_user, test_beneficiary):
        """Test non-admin can't assign trainers."""
        service = BeneficiaryService(db_session, trainer_user)

        with pytest.raises(PermissionError) as exc:
            service.assign_trainer(test_beneficiary.id, trainer_user.id)
        assert "Only administrators can assign trainers" in str(exc.value)
