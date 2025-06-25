"""
Program schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class ProgramCreateSchema(Schema):
    """Schema for creating a program"""
    code = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    name = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(allow_none=True)
    category = fields.Str(required=False, validate=validate.OneOf([
        'education', 'vocational', 'health', 'social', 'economic', 'other'
    ]))
    status = fields.Str(required=False, validate=validate.OneOf([
        'draft', 'active', 'completed', 'suspended'
    ]))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    budget = fields.Decimal(required=False, places=2)
    objectives = fields.List(fields.Str(), required=False)
    eligibility_criteria = fields.Dict(required=False)
    metadata = fields.Dict(required=False)
    
    @validates('end_date')
    def validate_dates(self, end_date, **kwargs):
        start_date = self.context.get('start_date') or kwargs.get('start_date')
        if start_date and end_date and end_date <= start_date:
            raise ValidationError('End date must be after start date')


class ProgramUpdateSchema(Schema):
    """Schema for updating a program"""
    name = fields.Str(required=False, validate=validate.Length(min=3, max=200))
    description = fields.Str(allow_none=True)
    category = fields.Str(required=False, validate=validate.OneOf([
        'education', 'vocational', 'health', 'social', 'economic', 'other'
    ]))
    status = fields.Str(required=False, validate=validate.OneOf([
        'draft', 'active', 'completed', 'suspended'
    ]))
    start_date = fields.Date(required=False)
    end_date = fields.Date(required=False)
    budget = fields.Decimal(required=False, places=2)
    objectives = fields.List(fields.Str(), required=False)
    eligibility_criteria = fields.Dict(required=False)
    metadata = fields.Dict(required=False)


class ProgramQuerySchema(Schema):
    """Schema for program query parameters"""
    page = fields.Int(required=False, validate=validate.Range(min=1))
    per_page = fields.Int(required=False, validate=validate.Range(min=1, max=100))
    status = fields.Str(required=False, validate=validate.OneOf([
        'draft', 'active', 'completed', 'suspended'
    ]))
    category = fields.Str(required=False, validate=validate.OneOf([
        'education', 'vocational', 'health', 'social', 'economic', 'other'
    ]))
    search = fields.Str(required=False)
    sort_by = fields.Str(required=False, validate=validate.OneOf([
        'name', 'created_at', 'start_date', 'status'
    ]))
    sort_desc = fields.Bool(required=False)
    created_after = fields.DateTime(required=False)
    created_before = fields.DateTime(required=False)
    min_budget = fields.Decimal(required=False, places=2)
    max_budget = fields.Decimal(required=False, places=2)


class ProgramStatisticsSchema(Schema):
    """Schema for program statistics response"""
    program_id = fields.Int(required=True)
    program_name = fields.Str(required=True)
    status = fields.Str(required=True)
    courses = fields.Dict(required=True)
    beneficiaries = fields.Dict(required=True)
    budget = fields.Dict(required=True)
    performance = fields.Dict(required=True)


class ProgramResponseSchema(Schema):
    """Schema for program response"""
    id = fields.Int(required=True)
    code = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    category = fields.Str(required=True)
    status = fields.Str(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    budget = fields.Decimal(places=2, as_string=True)
    objectives = fields.List(fields.Str())
    eligibility_criteria = fields.Dict()
    metadata = fields.Dict()
    course_count = fields.Int()
    active_beneficiary_count = fields.Int()
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    created_by = fields.Int()
    updated_by = fields.Int()


class ProgramListResponseSchema(Schema):
    """Schema for program list response"""
    programs = fields.List(fields.Nested(ProgramResponseSchema))
    pagination = fields.Dict(required=True, keys=fields.Str(), values=fields.Int())


# Export schemas
program_create_schema = ProgramCreateSchema()
program_update_schema = ProgramUpdateSchema()
program_query_schema = ProgramQuerySchema()
program_response_schema = ProgramResponseSchema()
program_list_response_schema = ProgramListResponseSchema()
program_statistics_schema = ProgramStatisticsSchema()