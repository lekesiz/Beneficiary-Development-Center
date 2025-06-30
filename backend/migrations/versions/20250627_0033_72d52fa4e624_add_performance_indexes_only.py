"""Add performance indexes only

Revision ID: 72d52fa4e624
Revises: 3c0dd0961f70
Create Date: 2025-06-27 00:33:28.279611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72d52fa4e624'
down_revision: Union[str, None] = 'f9a0a95ea042'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add performance indexes for frequently queried columns
    
    # User indexes - skip email_tenant as it may conflict with existing unique constraint
    op.create_index('idx_users_role_active', 'users', ['is_active', 'tenant_id'])
    op.create_index('idx_users_last_login', 'users', ['last_login_at'])
    
    # Beneficiary indexes
    op.create_index('idx_beneficiaries_status_tenant', 'beneficiaries', ['status', 'tenant_id'])
    op.create_index('idx_beneficiaries_trainer', 'beneficiaries', ['assigned_trainer_id'])
    op.create_index('idx_beneficiaries_created_by', 'beneficiaries', ['created_by'])
    
    # Program indexes
    op.create_index('idx_programs_status_dates', 'programs', ['status', 'start_date', 'end_date'])
    op.create_index('idx_programs_enrollment_dates', 'programs', ['enrollment_start', 'enrollment_end'])
    op.create_index('idx_programs_coordinator', 'programs', ['coordinator_id'])
    
    # Course indexes  
    op.create_index('idx_courses_program_order', 'courses', ['program_id', 'order_index'])
    op.create_index('idx_courses_instructor', 'courses', ['instructor_id'])
    op.create_index('idx_courses_status', 'courses', ['status'])
    
    # Enrollment indexes
    op.create_index('idx_enrollments_beneficiary_status', 'enrollments', ['beneficiary_id', 'status'])
    op.create_index('idx_enrollments_program_status', 'enrollments', ['program_id', 'status'])
    op.create_index('idx_enrollments_dates', 'enrollments', ['enrolled_date', 'completion_date'])
    
    # Course Progress indexes
    op.create_index('idx_course_progress_enrollment', 'course_progress', ['enrollment_id'])
    op.create_index('idx_course_progress_beneficiary_course', 'course_progress', ['beneficiary_id', 'course_id'])
    op.create_index('idx_course_progress_completed', 'course_progress', ['is_completed', 'completed_at'])
    
    # Evaluation indexes
    op.create_index('idx_evaluations_status_dates', 'evaluations', ['status', 'available_from', 'available_until'])
    op.create_index('idx_evaluations_course', 'evaluations', ['course_id'])
    op.create_index('idx_evaluations_program', 'evaluations', ['program_id'])
    
    # Evaluation Attempt indexes
    op.create_index('idx_evaluation_attempts_user_eval', 'evaluation_attempts', ['user_id', 'evaluation_id'])
    op.create_index('idx_evaluation_attempts_status', 'evaluation_attempts', ['status', 'started_at'])
    op.create_index('idx_evaluation_attempts_completed', 'evaluation_attempts', ['completed_at'])
    
    # Learning Path indexes
    op.create_index('idx_learning_paths_user_status', 'learning_paths', ['user_id', 'status'])
    op.create_index('idx_learning_paths_evaluation', 'learning_paths', ['evaluation_id'])
    op.create_index('idx_learning_paths_dates', 'learning_paths', ['start_date', 'end_date'])
    
    # Milestone Progress indexes
    op.create_index('idx_milestone_progress_user_status', 'milestone_progress', ['user_id', 'status'])
    op.create_index('idx_milestone_progress_milestone', 'milestone_progress', ['milestone_id'])
    
    # Course Session indexes
    op.create_index('idx_course_sessions_course_date', 'course_sessions', ['course_id', 'session_date'])
    op.create_index('idx_course_sessions_instructor', 'course_sessions', ['instructor_id'])


def downgrade() -> None:
    # Drop performance indexes in reverse order
    op.drop_index('idx_course_sessions_instructor')
    op.drop_index('idx_course_sessions_course_date')
    op.drop_index('idx_milestone_progress_milestone')
    op.drop_index('idx_milestone_progress_user_status')
    op.drop_index('idx_learning_paths_dates')
    op.drop_index('idx_learning_paths_evaluation')
    op.drop_index('idx_learning_paths_user_status')
    op.drop_index('idx_evaluation_attempts_completed')
    op.drop_index('idx_evaluation_attempts_status')
    op.drop_index('idx_evaluation_attempts_user_eval')
    op.drop_index('idx_evaluations_program')
    op.drop_index('idx_evaluations_course')
    op.drop_index('idx_evaluations_status_dates')
    op.drop_index('idx_course_progress_completed')
    op.drop_index('idx_course_progress_beneficiary_course')
    op.drop_index('idx_course_progress_enrollment')
    op.drop_index('idx_enrollments_dates')
    op.drop_index('idx_enrollments_program_status')
    op.drop_index('idx_enrollments_beneficiary_status')
    op.drop_index('idx_courses_status')
    op.drop_index('idx_courses_instructor')
    op.drop_index('idx_courses_program_order')
    op.drop_index('idx_programs_coordinator')
    op.drop_index('idx_programs_enrollment_dates')
    op.drop_index('idx_programs_status_dates')
    op.drop_index('idx_beneficiaries_created_by')
    op.drop_index('idx_beneficiaries_trainer')
    op.drop_index('idx_beneficiaries_status_tenant')
    op.drop_index('idx_users_last_login')
    op.drop_index('idx_users_role_active')
