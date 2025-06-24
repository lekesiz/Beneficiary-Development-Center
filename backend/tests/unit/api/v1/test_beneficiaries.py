"""Unit tests for Beneficiary API endpoints."""
import pytest
import json
from datetime import datetime


class TestBeneficiaryEndpoints:
    """Test cases for Beneficiary API endpoints."""
    
    def test_get_beneficiaries_success(self, client, auth_headers, multiple_beneficiaries):
        """Test successful GET /api/v1/beneficiaries."""
        response = client.get('/api/v1/beneficiaries', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'beneficiaries' in data
        assert 'pagination' in data
        assert data['pagination']['total'] == 7
        assert len(data['beneficiaries']) == 7
    
    def test_get_beneficiaries_pagination(self, client, auth_headers, multiple_beneficiaries):
        """Test pagination in GET /api/v1/beneficiaries."""
        # First page
        response = client.get('/api/v1/beneficiaries?page=1&per_page=3', headers=auth_headers)
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert len(data['beneficiaries']) == 3
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 3
        assert data['pagination']['pages'] == 3
        
        # Second page
        response = client.get('/api/v1/beneficiaries?page=2&per_page=3', headers=auth_headers)
        data = json.loads(response.data)
        
        assert len(data['beneficiaries']) == 3
        assert data['pagination']['page'] == 2
    
    def test_get_beneficiaries_search(self, client, auth_headers, multiple_beneficiaries):
        """Test search functionality."""
        response = client.get('/api/v1/beneficiaries?search=Test', headers=auth_headers)
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['pagination']['total'] == 5
        assert all('Test' in b['first_name'] for b in data['beneficiaries'])
    
    def test_get_beneficiaries_filter_status(self, client, auth_headers, multiple_beneficiaries):
        """Test status filter."""
        response = client.get('/api/v1/beneficiaries?status=inactive', headers=auth_headers)
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['pagination']['total'] == 2
        assert all(b['status'] == 'inactive' for b in data['beneficiaries'])
    
    def test_get_beneficiaries_invalid_status(self, client, auth_headers, multiple_beneficiaries):
        """Test invalid status filter."""
        response = client.get('/api/v1/beneficiaries?status=invalid', headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid status' in data['error']
    
    def test_get_beneficiaries_filter_tags(self, client, auth_headers, multiple_beneficiaries):
        """Test tags filter."""
        response = client.get('/api/v1/beneficiaries?tags=tag1&tags=tag2', headers=auth_headers)
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['pagination']['total'] == 2
    
    def test_get_beneficiaries_sorting(self, client, auth_headers, multiple_beneficiaries):
        """Test sorting functionality."""
        response = client.get(
            '/api/v1/beneficiaries?sort_by=first_name&sort_order=asc', 
            headers=auth_headers
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        first_names = [b['first_name'] for b in data['beneficiaries']]
        assert first_names == sorted(first_names)
    
    def test_get_beneficiaries_trainer_restricted(self, client, trainer_auth_headers, multiple_beneficiaries):
        """Test trainer only sees assigned beneficiaries."""
        response = client.get('/api/v1/beneficiaries', headers=trainer_auth_headers)
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['pagination']['total'] == 3  # Only assigned beneficiaries
    
    def test_get_beneficiaries_unauthorized(self, client):
        """Test unauthorized access."""
        response = client.get('/api/v1/beneficiaries')
        
        assert response.status_code == 401
    
    def test_get_beneficiary_by_id_success(self, client, auth_headers, test_beneficiary):
        """Test successful GET /api/v1/beneficiaries/{id}."""
        response = client.get(f'/api/v1/beneficiaries/{test_beneficiary.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'beneficiary' in data
        assert data['beneficiary']['id'] == test_beneficiary.id
        assert data['beneficiary']['email'] == test_beneficiary.email
        assert 'full_name' in data['beneficiary']
        assert 'age' in data['beneficiary']
    
    def test_get_beneficiary_by_id_not_found(self, client, auth_headers):
        """Test GET non-existent beneficiary."""
        response = client.get('/api/v1/beneficiaries/999999', headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Beneficiary not found' in data['error']
    
    def test_get_beneficiary_by_uuid_success(self, client, auth_headers, test_beneficiary):
        """Test successful GET /api/v1/beneficiaries/uuid/{uuid}."""
        response = client.get(
            f'/api/v1/beneficiaries/uuid/{test_beneficiary.uuid}', 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['beneficiary']['id'] == test_beneficiary.id
    
    def test_get_beneficiary_by_uuid_invalid(self, client, auth_headers):
        """Test GET with invalid UUID format."""
        response = client.get('/api/v1/beneficiaries/uuid/invalid-uuid', headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid UUID format' in data['error']
    
    def test_create_beneficiary_success(self, client, auth_headers):
        """Test successful POST /api/v1/beneficiaries."""
        payload = {
            'first_name': 'New',
            'last_name': 'Beneficiary',
            'email': 'new.beneficiary@test.com',
            'phone': '+33123456789',
            'date_of_birth': '1990-01-01',
            'employment_status': 'employed',
            'education_level': 'master'
        }
        
        response = client.post(
            '/api/v1/beneficiaries',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert 'beneficiary' in data
        assert data['beneficiary']['first_name'] == 'New'
        assert data['beneficiary']['email'] == 'new.beneficiary@test.com'
        assert data['beneficiary']['employment_status'] == 'employed'
    
    def test_create_beneficiary_missing_required(self, client, auth_headers):
        """Test create with missing required fields."""
        payload = {
            'email': 'missing.name@test.com'
        }
        
        response = client.post(
            '/api/v1/beneficiaries',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'first_name is required' in data['error']
    
    def test_create_beneficiary_duplicate_email(self, client, auth_headers, test_beneficiary):
        """Test create with duplicate email."""
        payload = {
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': test_beneficiary.email
        }
        
        response = client.post(
            '/api/v1/beneficiaries',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Email already exists' in data['error']
    
    def test_create_beneficiary_invalid_enum(self, client, auth_headers):
        """Test create with invalid enum value."""
        payload = {
            'first_name': 'Test',
            'last_name': 'User',
            'employment_status': 'invalid_status'
        }
        
        response = client.post(
            '/api/v1/beneficiaries',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid employment status' in data['error']
    
    def test_create_beneficiary_student_denied(self, client, student_auth_headers):
        """Test student can't create beneficiary."""
        payload = {
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = client.post(
            '/api/v1/beneficiaries',
            headers=student_auth_headers,
            json=payload
        )
        
        assert response.status_code == 403
    
    def test_update_beneficiary_success(self, client, auth_headers, test_beneficiary):
        """Test successful PUT /api/v1/beneficiaries/{id}."""
        payload = {
            'first_name': 'Updated',
            'email': 'updated@test.com',
            'employment_status': 'self_employed'
        }
        
        response = client.put(
            f'/api/v1/beneficiaries/{test_beneficiary.id}',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['beneficiary']['first_name'] == 'Updated'
        assert data['beneficiary']['email'] == 'updated@test.com'
        assert data['beneficiary']['employment_status'] == 'self_employed'
    
    def test_update_beneficiary_not_found(self, client, auth_headers):
        """Test update non-existent beneficiary."""
        payload = {'first_name': 'Updated'}
        
        response = client.put(
            '/api/v1/beneficiaries/999999',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 404
    
    def test_delete_beneficiary_success(self, client, auth_headers, test_beneficiary):
        """Test successful DELETE /api/v1/beneficiaries/{id}."""
        response = client.delete(
            f'/api/v1/beneficiaries/{test_beneficiary.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message']
    
    def test_delete_beneficiary_trainer_denied(self, client, trainer_auth_headers, test_beneficiary):
        """Test trainer can't delete beneficiary."""
        response = client.delete(
            f'/api/v1/beneficiaries/{test_beneficiary.id}',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 403
    
    def test_add_note_success(self, client, auth_headers, test_beneficiary):
        """Test successful POST /api/v1/beneficiaries/{id}/notes."""
        payload = {'note': 'This is a test note'}
        
        response = client.post(
            f'/api/v1/beneficiaries/{test_beneficiary.id}/notes',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['beneficiary']['notes']) > 0
        assert any(n['text'] == 'This is a test note' for n in data['beneficiary']['notes'])
    
    def test_add_note_missing_text(self, client, auth_headers, test_beneficiary):
        """Test add note without text."""
        response = client.post(
            f'/api/v1/beneficiaries/{test_beneficiary.id}/notes',
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Note text is required' in data['error']
    
    def test_add_tag_success(self, client, auth_headers, test_beneficiary):
        """Test successful POST /api/v1/beneficiaries/{id}/tags."""
        payload = {'tag': 'new-tag'}
        
        response = client.post(
            f'/api/v1/beneficiaries/{test_beneficiary.id}/tags',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'new-tag' in data['beneficiary']['tags']
    
    def test_remove_tag_success(self, client, auth_headers, test_beneficiary):
        """Test successful DELETE /api/v1/beneficiaries/{id}/tags/{tag}."""
        # First add a tag
        client.post(
            f'/api/v1/beneficiaries/{test_beneficiary.id}/tags',
            headers=auth_headers,
            json={'tag': 'tag-to-remove'}
        )
        
        # Then remove it
        response = client.delete(
            f'/api/v1/beneficiaries/{test_beneficiary.id}/tags/tag-to-remove',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tag-to-remove' not in data['beneficiary']['tags']
    
    def test_get_statistics_success(self, client, auth_headers, multiple_beneficiaries):
        """Test successful GET /api/v1/beneficiaries/statistics."""
        response = client.get('/api/v1/beneficiaries/statistics', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'statistics' in data
        stats = data['statistics']
        
        assert stats['total'] == 7
        assert 'by_status' in stats
        assert 'by_employment' in stats
        assert 'by_education' in stats
        assert 'by_age' in stats
    
    def test_assign_trainer_success(self, client, auth_headers, test_beneficiary, trainer_user):
        """Test successful POST /api/v1/beneficiaries/{id}/assign-trainer."""
        payload = {'trainer_id': trainer_user.id}
        
        response = client.post(
            f'/api/v1/beneficiaries/{test_beneficiary.id}/assign-trainer',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['beneficiary']['assigned_trainer_id'] == trainer_user.id
        assert 'assigned_trainer_name' in data['beneficiary']
    
    def test_assign_trainer_invalid_id(self, client, auth_headers, test_beneficiary):
        """Test assign non-existent trainer."""
        payload = {'trainer_id': 999999}
        
        response = client.post(
            f'/api/v1/beneficiaries/{test_beneficiary.id}/assign-trainer',
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid trainer ID' in data['error']
    
    def test_assign_trainer_trainer_denied(self, client, trainer_auth_headers, test_beneficiary):
        """Test trainer can't assign trainers."""
        payload = {'trainer_id': 1}
        
        response = client.post(
            f'/api/v1/beneficiaries/{test_beneficiary.id}/assign-trainer',
            headers=trainer_auth_headers,
            json=payload
        )
        
        assert response.status_code == 403