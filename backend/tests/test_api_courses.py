"""Tests for Course API endpoints."""

import pytest
from datetime import datetime, date, timedelta
from app.models.course import CourseStatus, CourseFormat, DifficultyLevel


class TestCourseAPI:
    """Test course API endpoints."""

    @pytest.fixture
    def sample_program(self, db_session, test_tenant, admin_user):
        """Create a sample program for testing."""
        from app.models.program import Program, ProgramStatus, ProgramType

        program = Program(
            tenant_id=test_tenant.id,
            code="TEST-PRG-001",
            title="Test Program",
            description="Test program for course testing",
            program_type=ProgramType.TRAINING,
            status=ProgramStatus.PUBLISHED,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=90),
            enrollment_start=date.today(),
            enrollment_end=date.today() + timedelta(days=20),
            min_participants=5,
            max_participants=30,
            created_by=admin_user.id,
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        return program

    @pytest.fixture
    def sample_course(self, db_session, test_tenant, sample_program, instructor_user):
        """Create a sample course for testing."""
        from app.models.course import Course

        course = Course(
            tenant_id=test_tenant.id,
            program_id=sample_program.id,
            code="TEST-CRS-001",
            title="Introduction to Python",
            subtitle="Learn Python basics",
            description="A comprehensive introduction to Python programming",
            format=CourseFormat.LECTURE,
            difficulty_level=DifficultyLevel.BEGINNER,
            status=CourseStatus.PUBLISHED,
            duration_hours=40,
            duration_weeks=4,
            objectives=["Learn Python syntax", "Understand data types", "Write basic programs"],
            prerequisites=["Basic computer skills"],
            instructor_id=instructor_user.id,
            created_by=instructor_user.id,
            min_participants=5,
            max_participants=20,
            has_assessment=True,
            assessment_type="quiz",
            passing_score=70.0,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        return course

    @pytest.fixture
    def multiple_courses(self, db_session, test_tenant, sample_program, instructor_user, trainer_user):
        """Create multiple courses for testing."""
        from app.models.course import Course

        courses = []

        # Create 5 courses with different statuses and formats
        course_data = [
            {
                "title": "Advanced Python",
                "format": CourseFormat.WORKSHOP,
                "difficulty_level": DifficultyLevel.ADVANCED,
                "status": CourseStatus.PUBLISHED,
                "instructor_id": instructor_user.id,
            },
            {
                "title": "Web Development Basics",
                "format": CourseFormat.ONLINE,
                "difficulty_level": DifficultyLevel.INTERMEDIATE,
                "status": CourseStatus.DRAFT,
                "instructor_id": trainer_user.id,
            },
            {
                "title": "Database Design",
                "format": CourseFormat.HYBRID,
                "difficulty_level": DifficultyLevel.INTERMEDIATE,
                "status": CourseStatus.PUBLISHED,
                "instructor_id": instructor_user.id,
            },
            {
                "title": "Machine Learning Fundamentals",
                "format": CourseFormat.SELF_PACED,
                "difficulty_level": DifficultyLevel.EXPERT,
                "status": CourseStatus.ARCHIVED,
                "instructor_id": trainer_user.id,
            },
            {
                "title": "Project Management",
                "format": CourseFormat.PRACTICAL,
                "difficulty_level": DifficultyLevel.BEGINNER,
                "status": CourseStatus.PUBLISHED,
                "instructor_id": instructor_user.id,
            },
        ]

        for i, data in enumerate(course_data):
            course = Course(
                tenant_id=test_tenant.id,
                program_id=sample_program.id,
                code=f"TEST-CRS-{i+2:03d}",
                title=data["title"],
                description=f'Description for {data["title"]}',
                format=data["format"],
                difficulty_level=data["difficulty_level"],
                status=data["status"],
                duration_hours=20 + i * 5,
                instructor_id=data["instructor_id"],
                created_by=instructor_user.id,
                order_index=i,
            )
            courses.append(course)
            db_session.add(course)

        db_session.commit()
        for course in courses:
            db_session.refresh(course)

        return courses

    def test_get_courses_empty(self, client, admin_headers, sample_program):
        """Test getting courses when none exist."""
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses", headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["courses"] == []
        assert data["pagination"]["total"] == 0

    def test_get_courses_with_data(self, client, admin_headers, sample_program, sample_course, multiple_courses):
        """Test getting courses with data."""
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses", headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["courses"]) == 6  # sample_course + 5 from multiple_courses
        assert data["pagination"]["total"] == 6

        # Check courses are ordered by order_index
        course_titles = [c["title"] for c in data["courses"]]
        assert course_titles[0] == "Introduction to Python"  # Has default order_index 0

    def test_get_courses_with_filters(self, client, admin_headers, sample_program, multiple_courses):
        """Test getting courses with various filters."""
        # Filter by status
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses?status=published", headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert all(c["status"] == "published" for c in data["courses"])

        # Filter by format
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses?format=online", headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert all(c["format"] == "online" for c in data["courses"])

        # Filter by difficulty
        response = client.get(
            f"/api/v1/programs/{sample_program.id}/courses?difficulty=beginner", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert all(c["difficulty_level"] == "beginner" for c in data["courses"])

    def test_get_courses_search(self, client, admin_headers, sample_program, multiple_courses):
        """Test searching courses."""
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses?search=Python", headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["courses"]) == 1
        assert "Python" in data["courses"][0]["title"]

    def test_get_course_by_id(self, client, admin_headers, sample_program, sample_course):
        """Test getting a specific course."""
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == sample_course.id
        assert data["title"] == "Introduction to Python"
        assert data["program_id"] == sample_program.id
        assert "instructor_name" in data  # Include related data

    def test_get_course_not_found(self, client, admin_headers, sample_program):
        """Test getting non-existent course."""
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses/99999", headers=admin_headers)

        assert response.status_code == 404
        assert "not found" in response.json["error"].lower()

    def test_create_course_success(self, client, admin_headers, sample_program, instructor_user):
        """Test creating a new course."""
        course_data = {
            "title": "New Course",
            "subtitle": "A brand new course",
            "description": "This is a new course",
            "format": "lecture",
            "difficulty_level": "intermediate",
            "duration_hours": 30,
            "duration_weeks": 3,
            "objectives": ["Objective 1", "Objective 2"],
            "prerequisites": ["Basic knowledge"],
            "instructor_id": instructor_user.id,
            "min_participants": 10,
            "max_participants": 25,
            "has_assessment": True,
            "assessment_type": "project",
            "passing_score": 80.0,
            "program_id": sample_program.id,
        }

        response = client.post(f"/api/v1/programs/{sample_program.id}/courses", json=course_data, headers=admin_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "New Course"
        assert data["code"] is not None  # Auto-generated
        assert data["order_index"] == 0  # First course in program

    def test_create_course_instructor_permission(self, client, instructor_headers, sample_program, instructor_user):
        """Test instructor creating course in program they coordinate."""
        # Update program to have instructor as coordinator
        sample_program.coordinator_id = instructor_user.id
        from app.extensions import db

        db.session.commit()

        course_data = {"title": "Instructor Course", "program_id": sample_program.id}

        response = client.post(
            f"/api/v1/programs/{sample_program.id}/courses", json=course_data, headers=instructor_headers
        )

        assert response.status_code == 201
        assert response.json["instructor_id"] == instructor_user.id

    def test_create_course_validation_error(self, client, admin_headers, sample_program):
        """Test creating course with validation errors."""
        course_data = {
            "program_id": sample_program.id
            # Missing required title
        }

        response = client.post(f"/api/v1/programs/{sample_program.id}/courses", json=course_data, headers=admin_headers)

        assert response.status_code == 400
        assert "Validation error" in response.json["error"]

    def test_update_course_success(self, client, admin_headers, sample_program, sample_course):
        """Test updating a course."""
        update_data = {"title": "Updated Python Course", "duration_hours": 50, "max_participants": 30}

        response = client.put(
            f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}", json=update_data, headers=admin_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Updated Python Course"
        assert data["duration_hours"] == 50
        assert data["max_participants"] == 30

    def test_update_course_instructor_permission(self, client, instructor_headers, sample_program, sample_course):
        """Test instructor updating their own course."""
        update_data = {"description": "Updated by instructor"}

        response = client.put(
            f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}",
            json=update_data,
            headers=instructor_headers,
        )

        assert response.status_code == 200
        assert response.json["description"] == "Updated by instructor"

    def test_update_course_status(self, client, admin_headers, sample_program, sample_course):
        """Test updating course status."""
        # First set to draft
        sample_course.status = CourseStatus.DRAFT
        from app.extensions import db

        db.session.commit()

        response = client.put(
            f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}/status",
            json={"status": "published"},
            headers=admin_headers,
        )

        assert response.status_code == 200
        assert response.json["status"] == "published"

    def test_update_course_invalid_status_transition(self, client, admin_headers, sample_program, sample_course):
        """Test invalid status transition."""
        # Try to go from published to draft (invalid)
        response = client.put(
            f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}/status",
            json={"status": "draft"},
            headers=admin_headers,
        )

        assert response.status_code == 400
        assert "Cannot transition" in response.json["error"]

    def test_delete_course_success(self, client, admin_headers, sample_program, sample_course):
        """Test deleting a course."""
        response = client.delete(
            f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}", headers=admin_headers
        )

        assert response.status_code == 204

        # Verify course is soft deleted
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}", headers=admin_headers)
        assert response.status_code == 404

    def test_delete_course_forbidden(self, client, instructor_headers, sample_program, sample_course):
        """Test instructor cannot delete courses."""
        response = client.delete(
            f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}", headers=instructor_headers
        )

        assert response.status_code == 403

    def test_reorder_courses(self, client, admin_headers, sample_program, multiple_courses):
        """Test reordering courses."""
        # Create new order mapping
        course_orders = {multiple_courses[0].id: 2, multiple_courses[1].id: 0, multiple_courses[2].id: 1}

        response = client.put(
            f"/api/v1/programs/{sample_program.id}/courses/reorder",
            json={"course_orders": course_orders},
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.get_json()

        # Verify new order
        reordered = sorted(data["courses"][:3], key=lambda x: x["order_index"])
        assert reordered[0]["id"] == multiple_courses[1].id
        assert reordered[1]["id"] == multiple_courses[2].id
        assert reordered[2]["id"] == multiple_courses[0].id

    def test_duplicate_course(self, client, admin_headers, sample_program, sample_course):
        """Test duplicating a course."""
        response = client.post(
            f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}/duplicate",
            json={"title": "Python Course Copy"},
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "Python Course Copy"
        assert data["id"] != sample_course.id
        assert data["code"] != sample_course.code
        assert data["status"] == "draft"  # New copies start as draft

    def test_duplicate_course_to_different_program(
        self, client, admin_headers, sample_program, sample_course, db_session, test_tenant, admin_user
    ):
        """Test duplicating course to a different program."""
        from app.models.program import Program, ProgramStatus, ProgramType

        # Create another program
        new_program = Program(
            tenant_id=test_tenant.id,
            code="TEST-PRG-002",
            title="Another Program",
            program_type=ProgramType.WORKSHOP,
            status=ProgramStatus.PUBLISHED,
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=120),
            created_by=admin_user.id,
        )
        db_session.add(new_program)
        db_session.commit()

        response = client.post(
            f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}/duplicate",
            json={"program_id": new_program.id},
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["program_id"] == new_program.id

    def test_get_course_statistics(self, client, admin_headers, sample_program, sample_course, multiple_courses):
        """Test getting course statistics."""
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses/statistics", headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["total_courses"] == 6
        assert "status_breakdown" in data
        assert "format_breakdown" in data
        assert "difficulty_breakdown" in data
        assert data["total_duration_hours"] > 0

    def test_pagination(self, client, admin_headers, sample_program, multiple_courses):
        """Test course pagination."""
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses?page=1&per_page=3", headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["courses"]) == 3
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 3
        assert data["pagination"]["pages"] == 2

    def test_instructor_filter(self, client, admin_headers, sample_program, multiple_courses, instructor_user):
        """Test filtering courses by instructor."""
        response = client.get(
            f"/api/v1/programs/{sample_program.id}/courses?instructor_id={instructor_user.id}", headers=admin_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert all(c["instructor_id"] == instructor_user.id for c in data["courses"])

    def test_course_with_assessment(self, client, admin_headers, sample_program, sample_course):
        """Test course with assessment details."""
        response = client.get(f"/api/v1/programs/{sample_program.id}/courses/{sample_course.id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["has_assessment"] is True
        assert data["assessment_type"] == "quiz"
        assert data["passing_score"] == 70.0

    def test_program_not_found(self, client, admin_headers):
        """Test accessing courses for non-existent program."""
        response = client.get("/api/v1/programs/99999/courses", headers=admin_headers)

        assert response.status_code == 404
        assert "Program not found" in response.json["error"]
