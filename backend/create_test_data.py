#!/usr/bin/env python3
"""Create test data for API testing."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.beneficiary import Beneficiary, BeneficiaryStatus, EmploymentStatus, EducationLevel
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel
from app.models.evaluation import Evaluation
from datetime import datetime, timedelta

def create_test_data():
    """Create test data for API testing."""
    app = create_app()
    
    with app.app_context():
        # Get admin user
        admin_user = User.query.filter_by(email="admin@bdc.local").first()
        if not admin_user:
            print("Admin user not found. Run simple_seed.py first.")
            return
        
        tenant_id = admin_user.tenant_id
        
        # Check if beneficiary with ID 1 exists
        beneficiary = Beneficiary.query.filter_by(id=1).first()
        if not beneficiary:
            # Create beneficiary with specific ID
            beneficiary = Beneficiary(
                id=1,
                first_name="Test",
                last_name="Beneficiary",
                email="test.beneficiary@example.com",
                phone="+1234567890",
                date_of_birth=datetime(2000, 1, 1).date(),
                address={
                    "street": "123 Test Street",
                    "city": "Test City",
                    "state": "TS",
                    "zip_code": "12345",
                    "country": "Test Country"
                },
                gender="male",
                employment_status=EmploymentStatus.EMPLOYED,
                education_level=EducationLevel.BACHELOR,
                tenant_id=tenant_id,
                created_by=admin_user.id,
                status=BeneficiaryStatus.ACTIVE
            )
            db.session.add(beneficiary)
            db.session.flush()
            print("Created beneficiary with ID 1")
        
        # Check if program with ID 1 exists
        program = Program.query.filter_by(id=1).first()
        if not program:
            # Create program with specific ID
            program = Program(
                id=1,
                code="PROG001",
                title="Test Development Program",
                description="A test program for development",
                objectives=["Learn basics", "Practice skills", "Build projects"],
                program_type=ProgramType.TRAINING,
                status=ProgramStatus.ACTIVE,
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=90)).date(),
                enrollment_start=datetime.now().date(),
                enrollment_end=(datetime.now() + timedelta(days=30)).date(),
                min_participants=5,
                max_participants=20,
                location="Online",
                is_online=True,
                price=0,
                currency="USD",
                tenant_id=tenant_id,
                created_by=admin_user.id
            )
            db.session.add(program)
            db.session.flush()
            print("Created program with ID 1")
        
        # Check if course with ID 1 exists
        course = Course.query.filter_by(id=1).first()
        if not course:
            # Create course with specific ID
            course = Course(
                id=1,
                code="COURSE001",
                title="Introduction to Python",
                subtitle="Learn Python basics",
                description="This course covers Python fundamentals",
                status=CourseStatus.PUBLISHED,
                format=CourseFormat.SELF_PACED,
                difficulty_level=DifficultyLevel.BEGINNER,
                duration_hours=20,
                duration_weeks=4,
                objectives=["Understand Python syntax", "Write basic programs", "Use Python libraries"],
                prerequisites=["Basic computer skills"],
                program_id=program.id,
                instructor_id=admin_user.id,
                min_participants=1,
                max_participants=50,
                passing_score=70,
                tenant_id=tenant_id,
                created_by=admin_user.id
            )
            db.session.add(course)
            db.session.flush()
            print("Created course with ID 1")
        
        # Check if evaluation with ID 1 exists
        evaluation = Evaluation.query.filter_by(id=1).first()
        if not evaluation:
            # Create evaluation with specific ID
            evaluation = Evaluation(
                id=1,
                title="Python Basics Assessment",
                description="Test your Python knowledge",
                course_id=course.id,
                program_id=program.id,
                total_questions=10,
                total_points=100,
                passing_score=70,
                time_limit_minutes=60,
                max_attempts=3,
                available_from=datetime.now(),
                available_until=datetime.now() + timedelta(days=30),
                tenant_id=tenant_id,
                created_by=admin_user.id
            )
            db.session.add(evaluation)
            db.session.flush()
            print("Created evaluation with ID 1")
        
        # Commit all changes
        db.session.commit()
        print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data()