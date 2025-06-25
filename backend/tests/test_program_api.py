"""Tests for Program API endpoints."""
import pytest
from datetime import datetime, timedelta
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.user import User


class TestProgramAPI:
    """Test cases for Program API endpoints."""
    
    def test_get_programs_success(self, client, auth_headers, db_session):
        """Test successful retrieval of programs."""
        # Create test programs
        program1 = Program(
            tenant_id=1,
            code="PROG001",
            title="Test Program 1",
            description="Description 1",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.ACTIVE,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=90),
            created_by=1
        )
        program2 = Program(
            tenant_id=1,
            code="PROG002",
            title="Test Program 2",
            description="Description 2",
            program_type=ProgramType.ACADEMIC,
            status=ProgramStatus.DRAFT,
            start_date=datetime.now().date() + timedelta(days=60),
            end_date=datetime.now().date() + timedelta(days=120),
            created_by=1
        )
        db_session.add_all([program1, program2])
        db_session.commit()
        
        response = client.get('/api/v1/programs', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'programs' in data
        assert 'pagination' in data
        assert len(data['programs']) == 2
        assert data['pagination']['total'] == 2
    
    def test_get_programs_with_filters(self, client, auth_headers, db_session):
        """Test retrieving programs with filters."""
        # Create test programs
        program1 = Program(
            tenant_id=1,
            code="PROG001",
            title="Vocational Program",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.ACTIVE,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=90),
            created_by=1
        )
        program2 = Program(
            tenant_id=1,
            code="PROG002",
            title="Academic Program",
            program_type=ProgramType.ACADEMIC,
            status=ProgramStatus.DRAFT,
            start_date=datetime.now().date() + timedelta(days=60),
            end_date=datetime.now().date() + timedelta(days=120),
            created_by=1
        )
        db_session.add_all([program1, program2])
        db_session.commit()
        
        # Test status filter
        response = client.get('/api/v1/programs?status=active', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['programs']) == 1
        assert data['programs'][0]['status'] == 'active'
        
        # Test type filter
        response = client.get('/api/v1/programs?type=academic', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['programs']) == 1
        assert data['programs'][0]['program_type'] == 'academic'
        
        # Test search filter
        response = client.get('/api/v1/programs?search=vocational', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['programs']) == 1
        assert 'Vocational' in data['programs'][0]['title']
    
    def test_get_program_by_id_success(self, client, auth_headers, db_session):
        """Test successful retrieval of a specific program."""
        program = Program(
            tenant_id=1,
            code="PROG001",
            title="Test Program",
            description="Test Description",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.ACTIVE,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=90),
            created_by=1
        )
        db_session.add(program)
        db_session.commit()
        
        response = client.get(f'/api/v1/programs/{program.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == program.id
        assert data['code'] == 'PROG001'
        assert data['title'] == 'Test Program'
    
    def test_get_program_not_found(self, client, auth_headers):
        """Test retrieving non-existent program."""
        response = client.get('/api/v1/programs/9999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_create_program_success(self, client, admin_headers, db_session):
        """Test successful program creation."""
        program_data = {
            'code': 'NEWPROG001',
            'title': 'New Program',
            'description': 'New program description',
            'program_type': 'vocational',
            'start_date': (datetime.now() + timedelta(days=30)).date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=90)).date().isoformat(),
            'min_participants': 10,
            'max_participants': 50,
            'is_online': False,
            'is_hybrid': True
        }
        
        response = client.post('/api/v1/programs', json=program_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['code'] == 'NEWPROG001'
        assert data['title'] == 'New Program'
        assert data['status'] == 'draft'  # Default status
        
        # Verify in database
        program = db_session.query(Program).filter_by(code='NEWPROG001').first()
        assert program is not None
        assert program.title == 'New Program'
    
    def test_create_program_validation_error(self, client, admin_headers):
        """Test program creation with invalid data."""
        # Missing required field
        program_data = {
            'code': 'NEWPROG001',
            'description': 'Missing title',
            'start_date': datetime.now().date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=90)).date().isoformat()
        }
        
        response = client.post('/api/v1/programs', json=program_data, headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Validation error' in data['error']
    
    def test_create_program_permission_denied(self, client, auth_headers):
        """Test program creation without proper permissions."""
        program_data = {
            'code': 'NEWPROG001',
            'title': 'New Program',
            'start_date': datetime.now().date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=90)).date().isoformat()
        }
        
        response = client.post('/api/v1/programs', json=program_data, headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_update_program_success(self, client, admin_headers, db_session):
        """Test successful program update."""
        program = Program(
            tenant_id=1,
            code="PROG001",
            title="Original Title",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.DRAFT,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=90),
            created_by=1
        )
        db_session.add(program)
        db_session.commit()
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'max_participants': 100
        }
        
        response = client.put(f'/api/v1/programs/{program.id}', json=update_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Updated Title'
        assert data['description'] == 'Updated description'
        assert data['max_participants'] == 100
        
        # Verify in database
        db_session.refresh(program)
        assert program.title == 'Updated Title'
    
    def test_update_program_invalid_dates(self, client, admin_headers, db_session):
        """Test program update with invalid dates."""
        program = Program(
            tenant_id=1,
            code="PROG001",
            title="Test Program",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.DRAFT,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=90),
            created_by=1
        )
        db_session.add(program)
        db_session.commit()
        
        # End date before start date
        update_data = {
            'start_date': (datetime.now() + timedelta(days=90)).date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=30)).date().isoformat()
        }
        
        response = client.put(f'/api/v1/programs/{program.id}', json=update_data, headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Start date must be before end date' in data['error']
    
    def test_delete_program_success(self, client, admin_headers, db_session):
        """Test successful program deletion."""
        program = Program(
            tenant_id=1,
            code="PROG001",
            title="To Delete",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.DRAFT,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=90),
            created_by=1
        )
        db_session.add(program)
        db_session.commit()
        
        response = client.delete(f'/api/v1/programs/{program.id}', headers=admin_headers)
        
        assert response.status_code == 204
        
        # Verify soft delete
        db_session.refresh(program)
        assert program.deleted_at is not None
    
    def test_delete_program_with_enrollments(self, client, admin_headers, db_session):
        """Test deleting program with active enrollments."""
        # This would require creating enrollments
        # For now, we'll test the basic structure
        program = Program(
            tenant_id=1,
            code="PROG001",
            title="Active Program",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.ACTIVE,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=90),
            created_by=1
        )
        db_session.add(program)
        db_session.commit()
        
        # In a real scenario with enrollments, this should fail
        response = client.delete(f'/api/v1/programs/{program.id}', headers=admin_headers)
        
        # For now it should succeed since no enrollments exist
        assert response.status_code == 204
    
    def test_update_program_status_success(self, client, admin_headers, db_session):
        """Test successful program status update."""
        program = Program(
            tenant_id=1,
            code="PROG001",
            title="Test Program",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.DRAFT,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=90),
            created_by=1
        )
        db_session.add(program)
        db_session.commit()
        
        response = client.put(
            f'/api/v1/programs/{program.id}/status',
            json={'status': 'published'},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'published'
        
        # Verify in database
        db_session.refresh(program)
        assert program.status == ProgramStatus.PUBLISHED
    
    def test_update_program_status_invalid_transition(self, client, admin_headers, db_session):
        """Test invalid program status transition."""
        program = Program(
            tenant_id=1,
            code="PROG001",
            title="Test Program",
            program_type=ProgramType.VOCATIONAL,
            status=ProgramStatus.COMPLETED,
            start_date=datetime.now().date() - timedelta(days=90),
            end_date=datetime.now().date() - timedelta(days=30),
            created_by=1
        )
        db_session.add(program)
        db_session.commit()
        
        # Try to move completed program back to draft
        response = client.put(
            f'/api/v1/programs/{program.id}/status',
            json={'status': 'draft'},
            headers=admin_headers
        )
        
        assert response.status_code == 400
    
    def test_get_program_statistics_success(self, client, admin_headers, db_session):
        """Test retrieving program statistics."""
        # Create multiple programs with different statuses
        programs = [
            Program(
                tenant_id=1,
                code=f"PROG00{i}",
                title=f"Program {i}",
                program_type=ProgramType.VOCATIONAL if i % 2 == 0 else ProgramType.ACADEMIC,
                status=ProgramStatus.ACTIVE if i < 3 else ProgramStatus.DRAFT,
                start_date=datetime.now().date() + timedelta(days=30),
                end_date=datetime.now().date() + timedelta(days=90),
                created_by=1
            )
            for i in range(5)
        ]
        db_session.add_all(programs)
        db_session.commit()
        
        response = client.get('/api/v1/programs/statistics', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_programs' in data
        assert 'status_breakdown' in data
        assert 'type_breakdown' in data
        assert data['total_programs'] == 5
    
    def test_get_program_statistics_permission_denied(self, client, auth_headers):
        """Test retrieving statistics without proper permissions."""
        response = client.get('/api/v1/programs/statistics', headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_pagination(self, client, auth_headers, db_session):
        """Test program list pagination."""
        # Create multiple programs
        programs = [
            Program(
                tenant_id=1,
                code=f"PROG{i:03d}",
                title=f"Program {i}",
                program_type=ProgramType.VOCATIONAL,
                status=ProgramStatus.ACTIVE,
                start_date=datetime.now().date() + timedelta(days=30),
                end_date=datetime.now().date() + timedelta(days=90),
                created_by=1
            )
            for i in range(25)
        ]
        db_session.add_all(programs)
        db_session.commit()
        
        # Test first page
        response = client.get('/api/v1/programs?page=1&per_page=10', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['programs']) == 10
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 10
        assert data['pagination']['total'] == 25
        assert data['pagination']['pages'] == 3
        
        # Test second page
        response = client.get('/api/v1/programs?page=2&per_page=10', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['programs']) == 10
        assert data['pagination']['page'] == 2
        
        # Test last page
        response = client.get('/api/v1/programs?page=3&per_page=10', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['programs']) == 5
        assert data['pagination']['page'] == 3