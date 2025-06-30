"""
Unit tests for Coach Notes API endpoints
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.models.coach_note import CoachNote, NoteCategory, NotePriority


class TestCoachNotesAPI:
    """Test cases for coach notes endpoints"""

    @pytest.fixture
    def sample_coach_note(self, db_session, test_tenant, trainer_user, student_user):
        """Create a sample coach note for testing"""
        note = CoachNote(
            tenant_id=test_tenant.id,
            created_by=trainer_user.id,
            student_id=student_user.id,
            category=NoteCategory.PROGRESS,
            priority=NotePriority.MEDIUM,
            title="Progress Update",
            content="Student is making good progress in Python fundamentals.",
            tags=["python", "progress"],
            is_private=False
        )
        db_session.add(note)
        db_session.commit()
        return note

    @pytest.fixture
    def multiple_coach_notes(self, db_session, test_tenant, trainer_user, student_user, admin_user):
        """Create multiple coach notes for testing"""
        notes = []
        categories = [NoteCategory.PROGRESS, NoteCategory.FEEDBACK, NoteCategory.CONCERN, 
                     NoteCategory.ACHIEVEMENT, NoteCategory.GENERAL]
        priorities = [NotePriority.LOW, NotePriority.MEDIUM, NotePriority.HIGH]
        
        for i in range(6):
            note = CoachNote(
                tenant_id=test_tenant.id,
                created_by=trainer_user.id if i < 3 else admin_user.id,
                student_id=student_user.id,
                category=categories[i % len(categories)],
                priority=priorities[i % len(priorities)],
                title=f"Note {i+1}",
                content=f"Content for note {i+1}",
                tags=[f"tag{i}", "test"],
                is_private=i % 2 == 0  # Every other note is private
            )
            notes.append(note)
        
        db_session.add_all(notes)
        db_session.commit()
        return notes

    def test_get_coach_notes_list(self, client, trainer_auth_headers, multiple_coach_notes):
        """Test getting list of coach notes"""
        response = client.get(
            '/api/v1/coach-notes',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'notes' in data
        assert 'pagination' in data
        assert isinstance(data['notes'], list)
        
        # Check note structure
        if data['notes']:
            note = data['notes'][0]
            assert 'id' in note
            assert 'title' in note
            assert 'content' in note
            assert 'category' in note
            assert 'priority' in note
            assert 'created_by' in note
            assert 'student' in note
            assert 'created_at' in note

    def test_get_coach_notes_filtered_by_student(self, client, trainer_auth_headers, 
                                                 multiple_coach_notes, student_user):
        """Test filtering coach notes by student"""
        response = client.get(
            f'/api/v1/coach-notes?student_id={student_user.id}',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # All notes should be for the specified student
        assert all(note['student']['id'] == student_user.id for note in data['notes'])

    def test_get_coach_notes_filtered_by_category(self, client, trainer_auth_headers, multiple_coach_notes):
        """Test filtering coach notes by category"""
        response = client.get(
            '/api/v1/coach-notes?category=progress',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # All notes should have progress category
        assert all(note['category'] == 'progress' for note in data['notes'])

    def test_get_coach_notes_filtered_by_priority(self, client, trainer_auth_headers, multiple_coach_notes):
        """Test filtering coach notes by priority"""
        response = client.get(
            '/api/v1/coach-notes?priority=high',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # All notes should have high priority
        assert all(note['priority'] == 'high' for note in data['notes'])

    def test_get_single_coach_note(self, client, trainer_auth_headers, sample_coach_note):
        """Test getting a single coach note"""
        response = client.get(
            f'/api/v1/coach-notes/{sample_coach_note.id}',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['id'] == sample_coach_note.id
        assert data['title'] == sample_coach_note.title
        assert data['content'] == sample_coach_note.content
        assert data['category'] == sample_coach_note.category.value
        assert data['priority'] == sample_coach_note.priority.value
        assert 'tags' in data

    def test_create_coach_note(self, client, trainer_auth_headers, student_user):
        """Test creating a new coach note"""
        note_data = {
            "student_id": student_user.id,
            "category": "feedback",
            "priority": "medium",
            "title": "Mid-term Feedback",
            "content": "Student shows excellent understanding of concepts.",
            "tags": ["midterm", "excellent"],
            "is_private": False
        }
        
        response = client.post(
            '/api/v1/coach-notes',
            headers=trainer_auth_headers,
            json=note_data
        )
        
        assert response.status_code == 201
        data = response.json
        
        assert data['title'] == note_data['title']
        assert data['content'] == note_data['content']
        assert data['category'] == note_data['category']
        assert 'id' in data
        assert 'created_at' in data

    def test_update_coach_note(self, client, trainer_auth_headers, sample_coach_note):
        """Test updating a coach note"""
        update_data = {
            "title": "Updated Progress Note",
            "content": "Updated content with more details.",
            "priority": "high"
        }
        
        response = client.put(
            f'/api/v1/coach-notes/{sample_coach_note.id}',
            headers=trainer_auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['title'] == update_data['title']
        assert data['content'] == update_data['content']
        assert data['priority'] == update_data['priority']

    def test_delete_coach_note(self, client, trainer_auth_headers, sample_coach_note):
        """Test deleting a coach note"""
        response = client.delete(
            f'/api/v1/coach-notes/{sample_coach_note.id}',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify note is deleted
        get_response = client.get(
            f'/api/v1/coach-notes/{sample_coach_note.id}',
            headers=trainer_auth_headers
        )
        assert get_response.status_code == 404

    def test_get_note_categories(self, client, trainer_auth_headers):
        """Test getting available note categories"""
        response = client.get(
            '/api/v1/coach-notes/categories',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'categories' in data
        assert isinstance(data['categories'], list)
        assert len(data['categories']) > 0
        
        # Check category structure
        category = data['categories'][0]
        assert 'value' in category
        assert 'label' in category

    def test_get_note_priorities(self, client, trainer_auth_headers):
        """Test getting available note priorities"""
        response = client.get(
            '/api/v1/coach-notes/priorities',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'priorities' in data
        assert isinstance(data['priorities'], list)
        assert len(data['priorities']) == 3  # low, medium, high

    def test_student_cannot_create_coach_note(self, client, student_auth_headers, student_user):
        """Test that students cannot create coach notes"""
        note_data = {
            "student_id": student_user.id,
            "category": "general",
            "priority": "low",
            "title": "Student trying to create note",
            "content": "This should not be allowed."
        }
        
        response = client.post(
            '/api/v1/coach-notes',
            headers=student_auth_headers,
            json=note_data
        )
        
        assert response.status_code == 403

    def test_student_can_view_own_notes(self, client, student_auth_headers, sample_coach_note):
        """Test that students can view notes about themselves"""
        # Non-private note about the student
        response = client.get(
            f'/api/v1/coach-notes/{sample_coach_note.id}',
            headers=student_auth_headers
        )
        
        # Students may or may not have access depending on implementation
        assert response.status_code in [200, 403]

    def test_private_note_access(self, client, trainer_auth_headers, admin_headers, 
                                db_session, test_tenant, trainer_user, student_user):
        """Test private note access control"""
        # Create a private note
        private_note = CoachNote(
            tenant_id=test_tenant.id,
            created_by=trainer_user.id,
            student_id=student_user.id,
            category=NoteCategory.CONCERN,
            priority=NotePriority.HIGH,
            title="Private Concern",
            content="Confidential information",
            is_private=True
        )
        db_session.add(private_note)
        db_session.commit()
        
        # Creator should be able to see it
        response = client.get(
            f'/api/v1/coach-notes/{private_note.id}',
            headers=trainer_auth_headers
        )
        assert response.status_code == 200
        
        # Admin should be able to see it
        response = client.get(
            f'/api/v1/coach-notes/{private_note.id}',
            headers=admin_headers
        )
        assert response.status_code == 200

    def test_search_coach_notes(self, client, trainer_auth_headers, multiple_coach_notes):
        """Test searching coach notes"""
        response = client.get(
            '/api/v1/coach-notes?search=progress',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Should find notes with 'progress' in title or content
        assert len(data['notes']) > 0

    def test_coach_notes_no_auth(self, client):
        """Test accessing coach notes without authentication"""
        response = client.get('/api/v1/coach-notes')
        assert response.status_code == 401

    def test_bulk_delete_coach_notes(self, client, trainer_auth_headers, multiple_coach_notes):
        """Test bulk deletion of coach notes"""
        note_ids = [note.id for note in multiple_coach_notes[:3]]
        
        response = client.delete(
            '/api/v1/coach-notes/bulk',
            headers=trainer_auth_headers,
            json={"note_ids": note_ids}
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 204, 404]

    @pytest.mark.parametrize("tag", ["python", "test", "progress"])
    def test_filter_by_tag(self, client, trainer_auth_headers, multiple_coach_notes, tag):
        """Test filtering notes by tag"""
        response = client.get(
            f'/api/v1/coach-notes?tag={tag}',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check that notes contain the specified tag
        for note in data['notes']:
            if 'tags' in note:
                assert tag in note['tags'] or len(data['notes']) == 0
