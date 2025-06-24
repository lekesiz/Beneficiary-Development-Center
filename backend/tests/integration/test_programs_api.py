"""Integration tests for Programs API endpoints."""
import pytest
import json
from datetime import date, timedelta
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.user import User
from app.models.tenant import Tenant


class TestProgramsAPI:
    """Test cases for Programs API endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, db_session, test_tenant, admin_user, manager_user, staff_user):
        """Setup test data."""
        self.client = client
        self.db = db_session
        self.tenant = test_tenant
        self.admin_user = admin_user
        self.manager_user = manager_user
        self.staff_user = staff_user
        
        # Create test programs
        self.program1 = Program(
            tenant_id=self.tenant.id,
            code='TRA-202401-TEST1',
            title='Python Programming',
            description='Learn Python programming',
            program_type=ProgramType.TRAINING,
            status=ProgramStatus.PUBLISHED,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=90),
            enrollment_start=date.today(),
            enrollment_end=date.today() + timedelta(days=20),
            min_participants=5,
            max_participants=20,
            created_by=self.admin_user.id
        )
        
        self.program2 = Program(
            tenant_id=self.tenant.id,
            code='WOR-202401-TEST2',
            title='Data Science Workshop',
            description='Hands-on data science workshop',
            program_type=ProgramType.WORKSHOP,
            status=ProgramStatus.ACTIVE,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=20),
            min_participants=10,
            max_participants=30,
            created_by=self.manager_user.id
        )
        
        self.program3 = Program(
            tenant_id=self.tenant.id,
            code='CER-202401-TEST3',
            title='AWS Certification',
            description='Prepare for AWS certification',
            program_type=ProgramType.CERTIFICATION,
            status=ProgramStatus.DRAFT,
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=120),
            created_by=self.admin_user.id
        )
        
        self.db.add_all([self.program1, self.program2, self.program3])
        self.db.commit()
        
        # Get auth tokens
        self.admin_token = self._get_auth_token(self.admin_user.email, 'password123')
        self.manager_token = self._get_auth_token(self.manager_user.email, 'password123')
        self.staff_token = self._get_auth_token(self.staff_user.email, 'password123')
    
    def _get_auth_token(self, email, password):
        """Helper to get auth token."""
        response = self.client.post(
            '/api/v1/auth/login',
            json={'email': email, 'password': password}
        )
        return response.json['access_token']
    
    def test_get_all_programs(self):
        """Test getting all programs."""
        response = self.client.get(
            '/api/v1/programs',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'programs' in data
        assert 'pagination' in data
        assert len(data['programs']) == 3
        assert data['pagination']['total'] == 3
    
    def test_get_programs_with_filters(self):
        """Test getting programs with filters."""
        # Filter by status
        response = self.client.get(
            '/api/v1/programs?status=published',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert len(data['programs']) == 1
        assert data['programs'][0]['status'] == 'published'
        
        # Filter by type
        response = self.client.get(
            '/api/v1/programs?type=workshop',
            headers={'Authorization': f'Bearer {self.manager_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert len(data['programs']) == 1
        assert data['programs'][0]['program_type'] == 'workshop'
        
        # Search
        response = self.client.get(
            '/api/v1/programs?search=Python',
            headers={'Authorization': f'Bearer {self.staff_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert len(data['programs']) == 1
        assert 'Python' in data['programs'][0]['title']
    
    def test_get_programs_pagination(self):
        """Test programs pagination."""
        response = self.client.get(
            '/api/v1/programs?page=1&per_page=2',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert len(data['programs']) == 2
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 2
        assert data['pagination']['total'] == 3
        assert data['pagination']['pages'] == 2
    
    def test_get_program_by_id(self):
        """Test getting program by ID."""
        response = self.client.get(
            f'/api/v1/programs/{self.program1.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == self.program1.id
        assert data['title'] == 'Python Programming'
        assert 'enrollment_count' in data
        assert 'available_spots' in data
    
    def test_get_program_include_courses(self):
        """Test getting program with courses."""
        response = self.client.get(
            f'/api/v1/programs/{self.program1.id}?include_courses=true',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'courses' in data
        assert isinstance(data['courses'], list)
    
    def test_get_program_not_found(self):
        """Test getting non-existent program."""
        response = self.client.get(
            '/api/v1/programs/999',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 404
        assert 'error' in response.json
    
    def test_create_program_admin(self):
        """Test creating program as admin."""
        program_data = {
            'title': 'New Training Program',
            'description': 'A new program',
            'program_type': 'training',
            'start_date': (date.today() + timedelta(days=45)).isoformat(),
            'end_date': (date.today() + timedelta(days=105)).isoformat(),
            'enrollment_start': date.today().isoformat(),
            'enrollment_end': (date.today() + timedelta(days=30)).isoformat(),
            'min_participants': 8,
            'max_participants': 25,
            'location': 'Online',
            'is_online': True,
            'price': 50000,  # 500.00 EUR
            'currency': 'EUR',
            'tags': ['python', 'programming', 'beginner']
        }
        
        response = self.client.post(
            '/api/v1/programs',
            json=program_data,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['title'] == 'New Training Program'
        assert data['code'].startswith('TRA-')
        assert data['status'] == 'draft'
        assert data['is_enrollment_open'] is False  # Draft status
        
        # Verify in database
        created_program = self.db.query(Program).filter_by(id=data['id']).first()
        assert created_program is not None
        assert created_program.created_by == self.admin_user.id
    
    def test_create_program_manager(self):
        """Test creating program as manager."""
        program_data = {
            'title': 'Manager Workshop',
            'program_type': 'workshop',
            'start_date': (date.today() + timedelta(days=30)).isoformat(),
            'end_date': (date.today() + timedelta(days=35)).isoformat()
        }
        
        response = self.client.post(
            '/api/v1/programs',
            json=program_data,
            headers={'Authorization': f'Bearer {self.manager_token}'}
        )
        
        assert response.status_code == 201
        assert response.json['title'] == 'Manager Workshop'
    
    def test_create_program_forbidden(self):
        """Test creating program with insufficient permissions."""
        program_data = {
            'title': 'Staff Program',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()
        }
        
        response = self.client.post(
            '/api/v1/programs',
            json=program_data,
            headers={'Authorization': f'Bearer {self.staff_token}'}
        )
        
        assert response.status_code == 403
    
    def test_create_program_invalid_dates(self):
        """Test creating program with invalid dates."""
        program_data = {
            'title': 'Invalid Program',
            'start_date': (date.today() + timedelta(days=90)).isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()  # End before start
        }
        
        response = self.client.post(
            '/api/v1/programs',
            json=program_data,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 400
        assert 'Start date must be before end date' in response.json['error']
    
    def test_update_program(self):
        """Test updating program."""
        update_data = {
            'title': 'Updated Python Programming',
            'description': 'Updated description',
            'max_participants': 25,
            'tags': ['python', 'advanced']
        }
        
        response = self.client.put(
            f'/api/v1/programs/{self.program1.id}',
            json=update_data,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['title'] == 'Updated Python Programming'
        assert data['description'] == 'Updated description'
        assert data['max_participants'] == 25
        assert 'python' in data['tags']
        assert 'advanced' in data['tags']
    
    def test_update_program_forbidden(self):
        """Test updating program with insufficient permissions."""
        response = self.client.put(
            f'/api/v1/programs/{self.program1.id}',
            json={'title': 'New Title'},
            headers={'Authorization': f'Bearer {self.staff_token}'}
        )
        
        assert response.status_code == 403
    
    def test_delete_program_admin(self):
        """Test deleting program as admin."""
        # Create a program to delete
        program = Program(
            tenant_id=self.tenant.id,
            title='Program to Delete',
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            created_by=self.admin_user.id
        )
        self.db.add(program)
        self.db.commit()
        
        response = self.client.delete(
            f'/api/v1/programs/{program.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 204
        
        # Verify soft delete
        deleted_program = self.db.query(Program).filter_by(id=program.id).first()
        assert deleted_program.deleted_at is not None
    
    def test_delete_program_forbidden(self):
        """Test deleting program with insufficient permissions."""
        response = self.client.delete(
            f'/api/v1/programs/{self.program1.id}',
            headers={'Authorization': f'Bearer {self.manager_token}'}
        )
        
        assert response.status_code == 403
    
    def test_update_program_status(self):
        """Test updating program status."""
        # Update draft to published
        response = self.client.put(
            f'/api/v1/programs/{self.program3.id}/status',
            json={'status': 'published'},
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'published'
        
        # Invalid transition
        response = self.client.put(
            f'/api/v1/programs/{self.program3.id}/status',
            json={'status': 'completed'},
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 400
        assert 'Cannot transition' in response.json['error']
    
    def test_add_course_to_program(self):
        """Test adding course to program."""
        course_data = {
            'title': 'Introduction to Python',
            'subtitle': 'Learn Python basics',
            'description': 'A comprehensive introduction',
            'format': 'lecture',
            'difficulty_level': 'beginner',
            'duration_hours': 20,
            'objectives': ['Understand Python syntax', 'Write basic programs']
        }
        
        response = self.client.post(
            f'/api/v1/programs/{self.program1.id}/courses',
            json=course_data,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['title'] == 'Introduction to Python'
        assert data['program_id'] == self.program1.id
        assert data['code'].startswith('CRS-')
    
    def test_add_course_forbidden(self):
        """Test adding course with insufficient permissions."""
        response = self.client.post(
            f'/api/v1/programs/{self.program1.id}/courses',
            json={'title': 'New Course'},
            headers={'Authorization': f'Bearer {self.staff_token}'}
        )
        
        assert response.status_code == 403
    
    def test_get_program_statistics(self):
        """Test getting program statistics."""
        response = self.client.get(
            '/api/v1/programs/statistics',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'total_programs' in data
        assert 'status_breakdown' in data
        assert 'type_breakdown' in data
        assert 'upcoming_programs' in data
        assert 'active_programs' in data
        assert 'total_active_enrollments' in data
        
        assert data['total_programs'] == 3
        assert data['status_breakdown']['draft'] == 1
        assert data['status_breakdown']['published'] == 1
        assert data['status_breakdown']['active'] == 1
        assert data['type_breakdown']['training'] == 1
        assert data['type_breakdown']['workshop'] == 1
        assert data['type_breakdown']['certification'] == 1
    
    def test_get_statistics_forbidden(self):
        """Test getting statistics with insufficient permissions."""
        response = self.client.get(
            '/api/v1/programs/statistics',
            headers={'Authorization': f'Bearer {self.staff_token}'}
        )
        
        assert response.status_code == 403