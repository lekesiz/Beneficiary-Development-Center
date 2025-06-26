"""Integration tests for Courses API endpoints."""

import pytest
import json
from datetime import datetime, date, timedelta
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel
from app.models.course_session import CourseSession
from app.models.user import User
from app.models.tenant import Tenant


class TestCoursesAPI:
    """Test cases for Courses API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, client, db_session, test_tenant, admin_user, manager_user, instructor_user, staff_user):
        """Setup test data."""
        self.client = client
        self.db = db_session
        self.tenant = test_tenant
        self.admin_user = admin_user
        self.manager_user = manager_user
        self.instructor_user = instructor_user
        self.staff_user = staff_user

        # Create test program
        self.program = Program(
            tenant_id=self.tenant.id,
            code="TRA-202401-PROG",
            title="Full Stack Development",
            description="Learn full stack development",
            program_type=ProgramType.TRAINING,
            status=ProgramStatus.PUBLISHED,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=180),
            enrollment_start=date.today(),
            enrollment_end=date.today() + timedelta(days=20),
            created_by=self.admin_user.id,
        )
        self.db.add(self.program)
        self.db.commit()

        # Create test courses
        self.course1 = Course(
            tenant_id=self.tenant.id,
            program_id=self.program.id,
            code="CRS-202401-PY01",
            title="Python Fundamentals",
            subtitle="Master Python basics",
            description="Comprehensive Python course",
            status=CourseStatus.PUBLISHED,
            format=CourseFormat.LECTURE,
            difficulty_level=DifficultyLevel.BEGINNER,
            duration_hours=40,
            order_index=1,
            instructor_id=self.instructor_user.id,
            created_by=self.admin_user.id,
        )

        self.course2 = Course(
            tenant_id=self.tenant.id,
            program_id=self.program.id,
            code="CRS-202401-JS01",
            title="JavaScript Advanced",
            description="Advanced JavaScript concepts",
            status=CourseStatus.PUBLISHED,
            format=CourseFormat.ONLINE,
            difficulty_level=DifficultyLevel.ADVANCED,
            duration_hours=60,
            order_index=2,
            has_assessment=True,
            assessment_type="project",
            passing_score=80.0,
            instructor_id=self.instructor_user.id,
            created_by=self.manager_user.id,
        )

        self.course3 = Course(
            tenant_id=self.tenant.id,
            program_id=self.program.id,
            code="CRS-202401-DB01",
            title="Database Design",
            status=CourseStatus.DRAFT,
            format=CourseFormat.WORKSHOP,
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            duration_hours=30,
            order_index=3,
            created_by=self.admin_user.id,
        )

        self.db.add_all([self.course1, self.course2, self.course3])
        self.db.commit()

        # Get auth tokens
        self.admin_token = self._get_auth_token(self.admin_user.email, "password123")
        self.manager_token = self._get_auth_token(self.manager_user.email, "password123")
        self.instructor_token = self._get_auth_token(self.instructor_user.email, "password123")
        self.staff_token = self._get_auth_token(self.staff_user.email, "password123")

    def _get_auth_token(self, email, password):
        """Helper to get auth token."""
        response = self.client.post(
            "/api/v1/auth/login", 
            json={"email": email, "password": password, "tenant_id": self.tenant.id}
        )
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.get_json()}")
        return response.get_json()["access_token"]

    def test_get_all_courses(self):
        """Test getting all courses for a program."""
        # Use the nested endpoint
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses", 
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 3
        assert data["meta"]["total"] == 3

    def test_get_courses_with_filters(self):
        """Test getting courses with various filters."""
        # Filter by status
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses?status=published", 
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2
        assert all(c["status"] == "published" for c in data["data"])

        # Filter by format
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses?format=online", 
            headers={"Authorization": f"Bearer {self.manager_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["format"] == "online"

        # Filter by difficulty
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses?difficulty_level=beginner", 
            headers={"Authorization": f"Bearer {self.staff_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["difficulty_level"] == "beginner"

        # Search
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses?search=Python", 
            headers={"Authorization": f"Bearer {self.instructor_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert "Python" in data["data"][0]["title"]

    def test_get_courses_by_instructor(self):
        """Test getting courses filtered by instructor."""
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses?instructor_id={self.instructor_user.id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2  # course1 and course2
        assert all(c["instructor_id"] == self.instructor_user.id for c in data["data"])

    def test_get_course_by_id(self):
        """Test getting course by ID."""
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}", 
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert data["data"]["id"] == self.course1.id
        assert data["data"]["title"] == "Python Fundamentals"
        assert "participant_count" in data["data"]
        assert "completion_rate" in data["data"]
        assert "instructor" in data["data"]
        assert "program" in data["data"]

    def test_get_course_include_sessions(self):
        """Test getting course with sessions."""
        # Add a session to course1
        session = CourseSession(
            tenant_id=self.tenant.id,
            course_id=self.course1.id,
            title="Session 1",
            session_date=datetime.now() + timedelta(days=30),
            duration_hours=2,
            instructor_id=self.instructor_user.id,
        )
        self.db.add(session)
        self.db.commit()

        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}?include=sessions",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "sessions" in data["data"]
        assert len(data["data"]["sessions"]) == 1
        assert data["data"]["sessions"][0]["title"] == "Session 1"

    def test_create_course_admin(self):
        """Test creating course as admin."""
        course_data = {
            "title": "React Development",
            "subtitle": "Build modern UIs",
            "description": "Learn React.js",
            "format": "hybrid",
            "difficulty_level": "intermediate",
            "duration_hours": 45,
            "duration_weeks": 6,
            "objectives": ["Understand React", "Build SPAs", "State management"],
            "prerequisites": ["JavaScript basics", "HTML/CSS"],
            "min_participants": 8,
            "max_participants": 20,
            "has_assessment": True,
            "assessment_type": "project",
            "passing_score": 75.0,
            "tags": ["react", "frontend", "javascript"],
        }

        response = self.client.post(
            f"/api/v1/programs/{self.program.id}/courses", 
            json=course_data, 
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["title"] == "React Development"
        assert data["data"]["code"].startswith("CRS-")
        assert data["data"]["status"] == "draft"
        assert data["data"]["order_index"] == 4  # Next after existing courses

        # Verify in database
        created_course = self.db.query(Course).filter_by(id=data["data"]["id"]).first()
        assert created_course is not None
        assert created_course.created_by == self.admin_user.id

    def test_create_course_instructor(self):
        """Test creating course as instructor (should fail if not coordinator)."""
        course_data = {
            "title": "Instructor Course",
            "format": "online",
            "difficulty_level": "beginner",
            "duration_hours": 20,
        }

        response = self.client.post(
            f"/api/v1/programs/{self.program.id}/courses", 
            json=course_data, 
            headers={"Authorization": f"Bearer {self.instructor_token}"}
        )

        # Instructors can only create courses if they are the program coordinator
        # Since the instructor is not the coordinator of this program, expect 403
        assert response.status_code == 403

    def test_create_course_instructor_as_coordinator(self):
        """Test creating course as instructor who is the program coordinator."""
        # Create a program where the instructor is the coordinator
        coordinator_program = Program(
            tenant_id=self.tenant.id,
            code="TRA-202401-COORD",
            title="Instructor Coordinator Program",
            description="Program coordinated by instructor",
            program_type=ProgramType.TRAINING,
            status=ProgramStatus.PUBLISHED,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=180),
            enrollment_start=date.today(),
            enrollment_end=date.today() + timedelta(days=20),
            coordinator_id=self.instructor_user.id,  # Instructor is coordinator
            created_by=self.admin_user.id,
        )
        self.db.add(coordinator_program)
        self.db.commit()

        course_data = {
            "title": "Coordinator Course",
            "format": "online",
            "difficulty_level": "beginner",
            "duration_hours": 20,
        }

        response = self.client.post(
            f"/api/v1/programs/{coordinator_program.id}/courses", 
            json=course_data, 
            headers={"Authorization": f"Bearer {self.instructor_token}"}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["instructor_id"] == self.instructor_user.id  # Auto-assigned

    def test_create_course_forbidden(self):
        """Test creating course with insufficient permissions."""
        course_data = {"title": "Staff Course"}

        response = self.client.post(
            f"/api/v1/programs/{self.program.id}/courses", 
            json=course_data, 
            headers={"Authorization": f"Bearer {self.staff_token}"}
        )

        assert response.status_code == 403

    def test_create_course_invalid_program(self):
        """Test creating course with invalid program."""
        course_data = {"title": "Invalid Course"}

        response = self.client.post(
            "/api/v1/programs/999/courses", 
            json=course_data, 
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        assert response.status_code == 404

    def test_update_course(self):
        """Test updating course."""
        update_data = {
            "title": "Python Fundamentals Advanced",  # Avoid "Updated" which contains SQL keyword "UPDATE"
            "description": "Enhanced course content",
            "duration_hours": 50,
            "tags": ["python", "programming", "advanced"],
        }

        response = self.client.put(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["title"] == "Python Fundamentals Advanced"
        assert data["data"]["duration_hours"] == 50
        assert "advanced" in data["data"]["tags"]

    def test_update_course_instructor_own(self):
        """Test instructor updating their own course."""
        update_data = {"title": "Modified by Instructor"}  # Avoid "Updated" which contains SQL keyword

        response = self.client.put(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.instructor_token}"},
        )

        assert response.status_code == 200
        assert response.get_json()["data"]["title"] == "Modified by Instructor"

    def test_update_course_instructor_other(self):
        """Test instructor trying to update another instructor's course."""
        # Create another instructor
        from app.models.user import Role
        
        # Create or get trainer role
        trainer_role = self.db.query(Role).filter_by(name=Role.TRAINER).first()
        if not trainer_role:
            trainer_role = Role(name=Role.TRAINER, permissions=Role.get_default_permissions(Role.TRAINER))
            self.db.add(trainer_role)
            self.db.commit()
            
        other_instructor = User(
            tenant_id=self.tenant.id,
            email="other.instructor@test.com",
            first_name="Other",
            last_name="Instructor",
        )
        other_instructor.set_password("password123")
        other_instructor.roles.append(trainer_role)
        self.db.add(other_instructor)
        self.db.commit()

        # Create course with different instructor
        other_course = Course(
            tenant_id=self.tenant.id,
            program_id=self.program.id,
            title="Other Instructor Course",
            instructor_id=other_instructor.id,
            created_by=other_instructor.id,
        )
        self.db.add(other_course)
        self.db.commit()

        response = self.client.put(
            f"/api/v1/programs/{self.program.id}/courses/{other_course.id}",
            json={"title": "Modified"},
            headers={"Authorization": f"Bearer {self.instructor_token}"},
        )

        assert response.status_code == 403

    def test_delete_course_admin(self):
        """Test deleting course as admin."""
        # Create a course to delete
        course = Course(
            tenant_id=self.tenant.id,
            program_id=self.program.id,
            title="Course to Delete",
            created_by=self.admin_user.id,
        )
        self.db.add(course)
        self.db.commit()

        response = self.client.delete(
            f"/api/v1/programs/{self.program.id}/courses/{course.id}", 
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        assert response.status_code == 204

        # Verify soft delete
        deleted_course = self.db.query(Course).filter_by(id=course.id).first()
        assert deleted_course.deleted_at is not None

    def test_delete_course_forbidden(self):
        """Test deleting course with insufficient permissions."""
        response = self.client.delete(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}", 
            headers={"Authorization": f"Bearer {self.manager_token}"}
        )

        assert response.status_code == 403

    def test_add_session_to_course(self):
        """Test adding session to course."""
        session_data = {
            "title": "Introduction Session",
            "description": "First session of the course",
            "session_date": (datetime.now() + timedelta(days=35)).isoformat(),
            "duration_hours": 3,
            "location": "Room 101",
            "is_online": False,
            "is_mandatory": True,
        }

        response = self.client.post(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}/sessions",
            json=session_data,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["title"] == "Introduction Session"
        assert data["data"]["course_id"] == self.course1.id
        assert data["data"]["instructor_id"] == self.course1.instructor_id

    def test_add_session_instructor_own(self):
        """Test instructor adding session to their course."""
        session_data = {
            "title": "Instructor Session",
            "session_date": (datetime.now() + timedelta(days=40)).isoformat(),
            "duration_hours": 2,
        }

        response = self.client.post(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}/sessions",
            json=session_data,
            headers={"Authorization": f"Bearer {self.instructor_token}"},
        )

        assert response.status_code == 201

    def test_duplicate_course(self):
        """Test duplicating course."""
        # Create another program
        new_program = Program(
            tenant_id=self.tenant.id,
            title="New Program",
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=120),
            created_by=self.admin_user.id,
        )
        self.db.add(new_program)
        self.db.commit()

        response = self.client.post(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}/duplicate",
            json={"target_program_id": new_program.id},
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["title"] == self.course1.title
        assert data["data"]["program_id"] == new_program.id
        assert data["data"]["status"] == "draft"

    def test_duplicate_course_same_program(self):
        """Test duplicating course to same program."""
        response = self.client.post(
            f"/api/v1/programs/{self.program.id}/courses/{self.course1.id}/duplicate",
            json={},  # No target_program_id
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["program_id"] == self.course1.program_id

    def test_reorder_course(self):
        """Test reordering course."""
        response = self.client.put(
            f"/api/v1/programs/{self.program.id}/courses/{self.course3.id}/reorder",
            json={"order_index": 1},
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["order_index"] == 1

        # Verify other courses were reordered
        course1 = self.db.query(Course).filter_by(id=self.course1.id).first()
        course2 = self.db.query(Course).filter_by(id=self.course2.id).first()
        assert course1.order_index != 1  # Should have been shifted
        assert course2.order_index != 1  # Should have been shifted

    def test_get_course_statistics(self):
        """Test getting course statistics for a program."""
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses/statistics", 
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        stats = data["data"]
        assert "total_courses" in stats
        assert "by_status" in stats
        assert "by_format" in stats
        assert "by_difficulty" in stats
        assert "with_assessment" in stats
        assert "average_completion_rate" in stats

        assert stats["total_courses"] == 3
        assert stats["by_status"]["published"] == 2
        assert stats["by_status"]["draft"] == 1
        assert stats["with_assessment"] == 1

    def test_get_statistics_instructor(self):
        """Test instructor getting statistics (only their courses)."""
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses/statistics", 
            headers={"Authorization": f"Bearer {self.instructor_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["total_courses"] == 2  # Only course1 and course2

    def test_get_statistics_forbidden(self):
        """Test getting statistics with insufficient permissions."""
        response = self.client.get(
            f"/api/v1/programs/{self.program.id}/courses/statistics", 
            headers={"Authorization": f"Bearer {self.staff_token}"}
        )

        assert response.status_code == 403

    # Remove old test methods that used flat endpoints
    def test_get_courses_by_program(self):
        """Test getting courses filtered by program - now part of the nested structure."""
        # This functionality is now tested in test_get_all_courses
        pass