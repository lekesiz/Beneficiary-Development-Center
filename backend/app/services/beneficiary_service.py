"""Beneficiary service for business logic."""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime
import uuid

from app.models.beneficiary import Beneficiary, BeneficiaryStatus, EmploymentStatus, EducationLevel
from app.models.user import User
from app.core.exceptions import NotFoundError, ValidationError, PermissionError


class BeneficiaryService:
    """Service class for beneficiary operations."""

    def __init__(self, db: Session, current_user: User):
        """Initialize service with database session and current user."""
        self.db = db
        self.current_user = current_user

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        assigned_trainer_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Beneficiary], int]:
        """Get all beneficiaries with pagination and filters."""
        query = self.db.query(Beneficiary).filter(Beneficiary.tenant_id == self.current_user.tenant_id)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Beneficiary.first_name.ilike(search_term),
                    Beneficiary.last_name.ilike(search_term),
                    Beneficiary.email.ilike(search_term),
                    Beneficiary.phone.ilike(search_term),
                    Beneficiary.mobile_phone.ilike(search_term),
                    Beneficiary.external_id.ilike(search_term),
                )
            )

        # Apply status filter
        if status:
            try:
                status_enum = BeneficiaryStatus(status)
                query = query.filter(Beneficiary.status == status_enum)
            except ValueError:
                raise ValidationError(f"Invalid status: {status}")

        # Apply trainer filter
        if assigned_trainer_id:
            query = query.filter(Beneficiary.assigned_trainer_id == assigned_trainer_id)

        # Apply tags filter
        if tags:
            for tag in tags:
                query = query.filter(Beneficiary.tags.contains([tag]))

        # Apply role-based filtering
        if self.current_user.role == "trainer":
            # Trainers can only see beneficiaries assigned to them
            query = query.filter(Beneficiary.assigned_trainer_id == self.current_user.id)

        # Get total count
        total = query.count()

        # Apply sorting
        sort_column = getattr(Beneficiary, sort_by, Beneficiary.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * per_page
        beneficiaries = query.offset(offset).limit(per_page).all()

        return beneficiaries, total

    def get_by_id(self, beneficiary_id: int) -> Beneficiary:
        """Get beneficiary by ID."""
        beneficiary = (
            self.db.query(Beneficiary)
            .filter(Beneficiary.id == beneficiary_id, Beneficiary.tenant_id == self.current_user.tenant_id)
            .first()
        )

        if not beneficiary:
            raise NotFoundError("Beneficiary not found")

        # Check permissions
        if self.current_user.role == "trainer" and beneficiary.assigned_trainer_id != self.current_user.id:
            raise PermissionError("You don't have permission to view this beneficiary")

        return beneficiary

    def get_by_uuid(self, uuid_str: str) -> Beneficiary:
        """Get beneficiary by UUID."""
        try:
            beneficiary_uuid = uuid.UUID(uuid_str)
        except ValueError:
            raise ValidationError("Invalid UUID format")

        beneficiary = (
            self.db.query(Beneficiary)
            .filter(Beneficiary.uuid == beneficiary_uuid, Beneficiary.tenant_id == self.current_user.tenant_id)
            .first()
        )

        if not beneficiary:
            raise NotFoundError("Beneficiary not found")

        # Check permissions
        if self.current_user.role == "trainer" and beneficiary.assigned_trainer_id != self.current_user.id:
            raise PermissionError("You don't have permission to view this beneficiary")

        return beneficiary

    def create(self, data: Dict[str, Any]) -> Beneficiary:
        """Create a new beneficiary."""
        # Validate required fields
        required_fields = ["first_name", "last_name"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"{field} is required")

        # Validate email uniqueness within tenant
        if data.get("email"):
            existing = (
                self.db.query(Beneficiary)
                .filter(Beneficiary.email == data["email"], Beneficiary.tenant_id == self.current_user.tenant_id)
                .first()
            )
            if existing:
                raise ValidationError("Email already exists")

        # Validate enums
        if "status" in data and data["status"]:
            try:
                data["status"] = BeneficiaryStatus(data["status"])
            except ValueError:
                raise ValidationError(f"Invalid status: {data['status']}")

        if "employment_status" in data and data["employment_status"]:
            try:
                data["employment_status"] = EmploymentStatus(data["employment_status"])
            except ValueError:
                raise ValidationError(f"Invalid employment status: {data['employment_status']}")

        if "education_level" in data and data["education_level"]:
            try:
                data["education_level"] = EducationLevel(data["education_level"])
            except ValueError:
                raise ValidationError(f"Invalid education level: {data['education_level']}")

        # Set tenant and creator
        data["tenant_id"] = self.current_user.tenant_id
        data["created_by"] = self.current_user.id

        # Create beneficiary
        beneficiary = Beneficiary(**data)
        self.db.add(beneficiary)
        self.db.commit()
        self.db.refresh(beneficiary)

        return beneficiary

    def update(self, beneficiary_id: int, data: Dict[str, Any]) -> Beneficiary:
        """Update beneficiary."""
        beneficiary = self.get_by_id(beneficiary_id)

        # Check permissions
        if self.current_user.role == "trainer" and beneficiary.assigned_trainer_id != self.current_user.id:
            raise PermissionError("You don't have permission to update this beneficiary")

        # Validate email uniqueness if changed
        if "email" in data and data["email"] != beneficiary.email:
            existing = (
                self.db.query(Beneficiary)
                .filter(
                    Beneficiary.email == data["email"],
                    Beneficiary.tenant_id == self.current_user.tenant_id,
                    Beneficiary.id != beneficiary_id,
                )
                .first()
            )
            if existing:
                raise ValidationError("Email already exists")

        # Validate enums
        if "status" in data and data["status"]:
            try:
                data["status"] = BeneficiaryStatus(data["status"])
            except ValueError:
                raise ValidationError(f"Invalid status: {data['status']}")

        if "employment_status" in data and data["employment_status"]:
            try:
                data["employment_status"] = EmploymentStatus(data["employment_status"])
            except ValueError:
                raise ValidationError(f"Invalid employment status: {data['employment_status']}")

        if "education_level" in data and data["education_level"]:
            try:
                data["education_level"] = EducationLevel(data["education_level"])
            except ValueError:
                raise ValidationError(f"Invalid education level: {data['education_level']}")

        # Update fields
        for key, value in data.items():
            if hasattr(beneficiary, key):
                setattr(beneficiary, key, value)

        beneficiary.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(beneficiary)

        return beneficiary

    def delete(self, beneficiary_id: int) -> bool:
        """Delete beneficiary (soft delete by changing status)."""
        beneficiary = self.get_by_id(beneficiary_id)

        # Check permissions (only admins can delete)
        if self.current_user.role not in ["super_admin", "admin"]:
            raise PermissionError("Only administrators can delete beneficiaries")

        # Soft delete by changing status
        beneficiary.status = BeneficiaryStatus.INACTIVE
        beneficiary.updated_at = datetime.utcnow()
        self.db.commit()

        return True

    def add_note(self, beneficiary_id: int, note_text: str) -> Beneficiary:
        """Add note to beneficiary."""
        beneficiary = self.get_by_id(beneficiary_id)

        # Check permissions
        if self.current_user.role == "student":
            raise PermissionError("Students cannot add notes")

        beneficiary.add_note(note_text, self.current_user.id)
        self.db.commit()
        self.db.refresh(beneficiary)

        return beneficiary

    def add_tag(self, beneficiary_id: int, tag: str) -> Beneficiary:
        """Add tag to beneficiary."""
        beneficiary = self.get_by_id(beneficiary_id)

        # Check permissions
        if self.current_user.role == "student":
            raise PermissionError("Students cannot add tags")

        beneficiary.add_tag(tag)
        self.db.commit()
        self.db.refresh(beneficiary)

        return beneficiary

    def remove_tag(self, beneficiary_id: int, tag: str) -> Beneficiary:
        """Remove tag from beneficiary."""
        beneficiary = self.get_by_id(beneficiary_id)

        # Check permissions
        if self.current_user.role == "student":
            raise PermissionError("Students cannot remove tags")

        beneficiary.remove_tag(tag)
        self.db.commit()
        self.db.refresh(beneficiary)

        return beneficiary

    def get_statistics(self) -> Dict[str, Any]:
        """Get beneficiary statistics."""
        query = self.db.query(Beneficiary).filter(Beneficiary.tenant_id == self.current_user.tenant_id)

        # Apply role-based filtering
        if self.current_user.role == "trainer":
            query = query.filter(Beneficiary.assigned_trainer_id == self.current_user.id)

        # Get counts by status
        status_counts = {}
        for status in BeneficiaryStatus:
            count = query.filter(Beneficiary.status == status).count()
            status_counts[status.value] = count

        # Get counts by employment status
        employment_counts = {}
        for emp_status in EmploymentStatus:
            count = query.filter(Beneficiary.employment_status == emp_status).count()
            employment_counts[emp_status.value] = count

        # Get counts by education level
        education_counts = {}
        for edu_level in EducationLevel:
            count = query.filter(Beneficiary.education_level == edu_level).count()
            education_counts[edu_level.value] = count

        # Get age distribution
        age_distribution = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56+": 0}

        beneficiaries = query.all()
        for beneficiary in beneficiaries:
            age = beneficiary.age
            if age:
                if age <= 25:
                    age_distribution["18-25"] += 1
                elif age <= 35:
                    age_distribution["26-35"] += 1
                elif age <= 45:
                    age_distribution["36-45"] += 1
                elif age <= 55:
                    age_distribution["46-55"] += 1
                else:
                    age_distribution["56+"] += 1

        return {
            "total": query.count(),
            "by_status": status_counts,
            "by_employment": employment_counts,
            "by_education": education_counts,
            "by_age": age_distribution,
        }

    def assign_trainer(self, beneficiary_id: int, trainer_id: int) -> Beneficiary:
        """Assign trainer to beneficiary."""
        # Check permissions (only admins can assign trainers)
        if self.current_user.role not in ["super_admin", "admin"]:
            raise PermissionError("Only administrators can assign trainers")

        beneficiary = self.get_by_id(beneficiary_id)

        # Verify trainer exists and has correct role
        trainer = (
            self.db.query(User)
            .filter(User.id == trainer_id, User.tenant_id == self.current_user.tenant_id, User.role == "trainer")
            .first()
        )

        if not trainer:
            raise ValidationError("Invalid trainer ID")

        beneficiary.assigned_trainer_id = trainer_id
        beneficiary.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(beneficiary)

        return beneficiary
