"""Beneficiary schemas for validation."""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class BeneficiaryCreateSchema(Schema):
    """Schema for creating a beneficiary."""
    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile_phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    
    # Personal information
    date_of_birth = fields.Date(required=False, allow_none=True)
    gender = fields.Str(required=False, validate=validate.OneOf(['male', 'female', 'other']))
    nationality = fields.Str(required=False, validate=validate.Length(max=50))
    birthplace = fields.Str(required=False, validate=validate.Length(max=100))
    
    # Address
    address = fields.Dict(required=False, default=dict)
    
    # Professional information
    employment_status = fields.Str(
        required=False,
        validate=validate.OneOf(['employed', 'unemployed', 'student', 'self_employed', 'retired', 'other'])
    )
    job_title = fields.Str(required=False, validate=validate.Length(max=100))
    company = fields.Str(required=False, validate=validate.Length(max=100))
    industry = fields.Str(required=False, validate=validate.Length(max=100))
    years_of_experience = fields.Int(required=False, validate=validate.Range(min=0, max=70))
    
    # Education
    education_level = fields.Str(
        required=False,
        validate=validate.OneOf(['no_diploma', 'primary', 'secondary', 'high_school', 'bachelor', 'master', 'doctorate', 'other'])
    )
    field_of_study = fields.Str(required=False, validate=validate.Length(max=100))
    certifications = fields.List(fields.Str(), required=False, default=list)
    
    # Profile data
    profile_data = fields.Dict(required=False, default=dict)
    skills = fields.List(fields.Str(), required=False, default=list)
    interests = fields.List(fields.Str(), required=False, default=list)
    goals = fields.List(fields.Str(), required=False, default=list)
    
    # Status and management
    status = fields.Str(
        required=False,
        default='active',
        validate=validate.OneOf(['active', 'inactive', 'completed', 'suspended'])
    )
    external_id = fields.Str(required=False, validate=validate.Length(max=100))
    assigned_trainer_id = fields.Int(required=False, allow_none=True)
    tags = fields.List(fields.Str(), required=False, default=list)
    
    @validates('date_of_birth')
    def validate_date_of_birth(self, value):
        """Validate date of birth is not in the future."""
        if value and value > datetime.now().date():
            raise ValidationError("Date of birth cannot be in the future")
    
    @validates('email')
    def validate_email_uniqueness(self, value):
        """Additional email validation if needed."""
        # This will be handled in the service layer
        pass


class BeneficiaryUpdateSchema(BeneficiaryCreateSchema):
    """Schema for updating a beneficiary."""
    # All fields are optional for updates
    first_name = fields.Str(required=False, validate=validate.Length(min=2, max=50))
    last_name = fields.Str(required=False, validate=validate.Length(min=2, max=50))


class BeneficiaryListSchema(Schema):
    """Schema for listing beneficiaries."""
    page = fields.Int(required=False, default=1, validate=validate.Range(min=1))
    per_page = fields.Int(required=False, default=20, validate=validate.Range(min=1, max=100))
    search = fields.Str(required=False)
    status = fields.Str(
        required=False,
        validate=validate.OneOf(['active', 'inactive', 'completed', 'suspended'])
    )
    assigned_trainer_id = fields.Int(required=False)
    tags = fields.List(fields.Str(), required=False)
    sort_by = fields.Str(
        required=False,
        default='created_at',
        validate=validate.OneOf(['created_at', 'updated_at', 'first_name', 'last_name', 'email'])
    )
    sort_order = fields.Str(
        required=False,
        default='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )


class BeneficiaryDetailSchema(Schema):
    """Schema for beneficiary details response."""
    id = fields.Int(required=True)
    uuid = fields.Str(required=True)
    external_id = fields.Str(allow_none=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    full_name = fields.Str(required=True)
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True)
    mobile_phone = fields.Str(allow_none=True)
    
    # Personal information
    date_of_birth = fields.Date(allow_none=True)
    age = fields.Int(allow_none=True)
    gender = fields.Str(allow_none=True)
    nationality = fields.Str(allow_none=True)
    birthplace = fields.Str(allow_none=True)
    
    # Address
    address = fields.Dict()
    
    # Professional information
    employment_status = fields.Str(allow_none=True)
    job_title = fields.Str(allow_none=True)
    company = fields.Str(allow_none=True)
    industry = fields.Str(allow_none=True)
    years_of_experience = fields.Int(allow_none=True)
    
    # Education
    education_level = fields.Str(allow_none=True)
    field_of_study = fields.Str(allow_none=True)
    certifications = fields.List(fields.Str())
    
    # Profile data
    profile_data = fields.Dict()
    skills = fields.List(fields.Str())
    interests = fields.List(fields.Str())
    goals = fields.List(fields.Str())
    
    # Status and management
    status = fields.Str(required=True)
    notes = fields.List(fields.Dict())
    tags = fields.List(fields.Str())
    
    # Relationships
    created_by = fields.Int()
    assigned_trainer_id = fields.Int(allow_none=True)
    assigned_trainer_name = fields.Str(allow_none=True)
    
    # Related data
    progress_summary = fields.Dict()
    active_enrollments = fields.Int()
    completed_programs = fields.Int()
    
    # Timestamps
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class NoteSchema(Schema):
    """Schema for adding a note."""
    note = fields.Str(required=True, validate=validate.Length(min=1, max=1000))


class TagSchema(Schema):
    """Schema for adding a tag."""
    tag = fields.Str(required=True, validate=validate.Length(min=1, max=50))


class AssignTrainerSchema(Schema):
    """Schema for assigning a trainer."""
    trainer_id = fields.Int(required=True, validate=validate.Range(min=1))