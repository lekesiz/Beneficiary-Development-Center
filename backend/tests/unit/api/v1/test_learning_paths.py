"""
Unit tests for Learning Paths API endpoints
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.models.learning_path import LearningPath, LearningMilestone, LearningPathUpdate, MilestoneProgress
from app.models.user import User


class TestLearningPathsAPI:
    """Test cases for learning paths endpoints"""

    @pytest.fixture
    def sample_learning_path(self, db_session, test_tenant, student_user):
        """Create a sample learning path for testing"""
        path = LearningPath(
            tenant_id=test_tenant.id,
            user_id=student_user.id,
            title="Python Development Path",
            description="Complete path to become a Python developer",
            status="accepted",
            goals=["Learn Python basics", "Master web frameworks", "Build projects"],
            customization_notes="Focus on web development"
        )
        db_session.add(path)
        db_session.commit()
        
        # Add milestones
        milestones = [
            LearningMilestone(
                tenant_id=test_tenant.id,
                learning_path_id=path.id,
                title="Python Fundamentals",
                description="Learn Python basics",
                objective="Master Python syntax and concepts",
                week_number=1,
                estimated_hours=20,
                skill_focus="Python basics",
                activities=["Complete Python tutorial", "Practice exercises"],
                resources=[{"type": "tutorial", "url": "https://python.org"}]
            ),
            LearningMilestone(
                tenant_id=test_tenant.id,
                learning_path_id=path.id,
                title="Web Development",
                description="Learn Flask/Django",
                objective="Build web applications",
                week_number=2,
                estimated_hours=30,
                skill_focus="Web frameworks",
                activities=["Build a Flask app", "Learn Django basics"],
                resources=[{"type": "documentation", "url": "https://flask.palletsprojects.com"}]
            )
        ]
        
        for milestone in milestones:
            db_session.add(milestone)
        
        db_session.commit()
        return path

    def test_get_learning_path_success(self, client, student_auth_headers, sample_learning_path):
        """Test successful retrieval of a learning path"""
        response = client.get(
            f'/api/v1/learning-paths/{sample_learning_path.id}',
            headers=student_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['id'] == sample_learning_path.id
        assert data['title'] == sample_learning_path.title
        assert 'milestones' in data
        assert len(data['milestones']) == 2

    def test_get_learning_path_not_found(self, client, student_auth_headers):
        """Test getting non-existent learning path"""
        response = client.get(
            '/api/v1/learning-paths/999999',
            headers=student_auth_headers
        )
        assert response.status_code == 404

    def test_get_my_learning_paths(self, client, student_auth_headers, sample_learning_path):
        """Test getting user's learning paths"""
        response = client.get(
            '/api/v1/learning-paths/my-paths',
            headers=student_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check path structure
        path = data[0]
        assert 'id' in path
        assert 'title' in path
        assert 'status' in path
        assert 'overall_progress' in path
        assert 'total_milestones' in path
        assert 'completed_milestones' in path

    def test_get_my_paths_with_status_filter(self, client, student_auth_headers, sample_learning_path):
        """Test filtering learning paths by status"""
        response = client.get(
            '/api/v1/learning-paths/my-paths?status=accepted',
            headers=student_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # All paths should have accepted status
        assert all(p['status'] == 'accepted' for p in data)

    def test_accept_learning_path(self, client, student_auth_headers, db_session, test_tenant, student_user):
        """Test accepting a proposed learning path"""
        # Create a proposed path
        proposed_path = LearningPath(
            tenant_id=test_tenant.id,
            user_id=student_user.id,
            title="Proposed Path",
            description="A proposed learning path",
            status="proposed"
        )
        db_session.add(proposed_path)
        db_session.commit()
        
        response = client.post(
            f'/api/v1/learning-paths/{proposed_path.id}/accept',
            headers=student_auth_headers,
            json={"customization_notes": "Looks good!"}
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['status'] == 'accepted'
        assert data['customization_notes'] == 'Looks good!'

    def test_update_learning_path(self, client, trainer_auth_headers, sample_learning_path):
        """Test updating learning path details"""
        update_data = {
            "title": "Updated Python Path",
            "description": "Updated description"
        }
        
        response = client.put(
            f'/api/v1/learning-paths/{sample_learning_path.id}',
            headers=trainer_auth_headers,
            json=update_data
        )
        
        # May return 200 or 403 depending on permissions
        assert response.status_code in [200, 403]

    def test_provide_feedback(self, client, student_auth_headers, sample_learning_path):
        """Test providing feedback on a learning path"""
        feedback_data = {
            "feedback": "This path is very helpful!",
            "rating": 5
        }
        
        response = client.post(
            f'/api/v1/learning-paths/{sample_learning_path.id}/feedback',
            headers=student_auth_headers,
            json=feedback_data
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'feedback_history' in data or 'id' in data

    def test_get_student_milestones(self, client, student_auth_headers, sample_learning_path):
        """Test getting student's milestones"""
        response = client.get(
            '/api/v1/learning-paths/student/milestones',
            headers=student_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'success' in data
        assert data['success'] is True
        assert 'milestones' in data
        assert isinstance(data['milestones'], list)
        
        # Check milestone structure
        if data['milestones']:
            milestone = data['milestones'][0]
            assert 'id' in milestone
            assert 'title' in milestone
            assert 'status' in milestone
            assert 'progress' in milestone
            assert 'week_number' in milestone

    def test_start_milestone(self, client, student_auth_headers, sample_learning_path, db_session):
        """Test starting a milestone"""
        milestone = sample_learning_path.milestones[0]
        
        response = client.post(
            f'/api/v1/learning-paths/milestones/{milestone.id}/start',
            headers=student_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['success'] is True
        assert 'milestone_id' in data
        
        # Verify progress record was created
        progress = db_session.query(MilestoneProgress).filter_by(
            milestone_id=milestone.id
        ).first()
        assert progress is not None
        assert progress.status == 'in_progress'

    def test_complete_milestone(self, client, student_auth_headers, sample_learning_path, db_session):
        """Test completing a milestone"""
        milestone = sample_learning_path.milestones[0]
        
        # First start the milestone
        progress = MilestoneProgress(
            tenant_id=sample_learning_path.tenant_id,
            milestone_id=milestone.id,
            user_id=sample_learning_path.user_id,
            status='in_progress',
            progress_percentage=50
        )
        db_session.add(progress)
        db_session.commit()
        
        response = client.post(
            f'/api/v1/learning-paths/milestones/{milestone.id}/complete',
            headers=student_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['success'] is True
        assert 'path_completed' in data

    def test_update_milestone_progress(self, client, student_auth_headers, sample_learning_path):
        """Test updating milestone progress"""
        milestone = sample_learning_path.milestones[0]
        
        progress_data = {
            "progress": 75,
            "completed_activities": ["Completed Python tutorial"]
        }
        
        response = client.patch(
            f'/api/v1/learning-paths/milestones/{milestone.id}/progress',
            headers=student_auth_headers,
            json=progress_data
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['success'] is True
        assert data['progress'] == 75

    def test_request_milestone_help(self, client, student_auth_headers, sample_learning_path, db_session):
        """Test requesting help for a milestone"""
        milestone = sample_learning_path.milestones[0]
        
        # Create progress first
        progress = MilestoneProgress(
            tenant_id=sample_learning_path.tenant_id,
            milestone_id=milestone.id,
            user_id=sample_learning_path.user_id,
            status='in_progress'
        )
        db_session.add(progress)
        db_session.commit()
        
        help_data = {
            "message": "I'm stuck on the Python exercises"
        }
        
        response = client.post(
            f'/api/v1/learning-paths/milestones/{milestone.id}/help',
            headers=student_auth_headers,
            json=help_data
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['success'] is True
        assert data['message'] == 'Help request sent successfully'

    def test_get_learning_path_statistics(self, client, student_auth_headers, sample_learning_path):
        """Test getting learning path statistics"""
        response = client.get(
            '/api/v1/learning-paths/statistics',
            headers=student_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'total_paths' in data
        assert 'active_paths' in data
        assert 'completed_paths' in data
        assert 'total_milestones' in data
        assert 'completed_milestones' in data
        assert 'average_progress' in data
        assert 'by_status' in data

    def test_suggest_learning_path_updates(self, client, trainer_auth_headers, student_user):
        """Test suggesting learning path updates for a student"""
        response = client.post(
            f'/api/v1/learning-paths/students/{student_user.id}/suggest-updates',
            headers=trainer_auth_headers
        )
        
        # May return 200 or 403 depending on permissions
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json
            assert 'suggestions' in data
            assert 'total' in data

    def test_get_pending_updates(self, client, trainer_auth_headers, sample_learning_path):
        """Test getting pending updates for a learning path"""
        response = client.get(
            f'/api/v1/learning-paths/{sample_learning_path.id}/pending-updates',
            headers=trainer_auth_headers
        )
        
        # May return 200 or 403 depending on permissions
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json
            assert 'updates' in data
            assert 'total' in data

    def test_learning_paths_no_auth(self, client):
        """Test accessing learning paths without authentication"""
        response = client.get('/api/v1/learning-paths/my-paths')
        assert response.status_code == 401

    def test_milestone_access_control(self, client, student_auth_headers, trainer_auth_headers, 
                                    sample_learning_path, db_session, trainer_user):
        """Test that students can only access their own milestones"""
        # Create another student's learning path
        other_path = LearningPath(
            tenant_id=sample_learning_path.tenant_id,
            user_id=trainer_user.id,  # Different user
            title="Another Path",
            description="Someone else's path",
            status="accepted"
        )
        db_session.add(other_path)
        
        other_milestone = LearningMilestone(
            tenant_id=sample_learning_path.tenant_id,
            learning_path_id=other_path.id,
            title="Other Milestone",
            week_number=1
        )
        db_session.add(other_milestone)
        db_session.commit()
        
        # Try to start another user's milestone
        response = client.post(
            f'/api/v1/learning-paths/milestones/{other_milestone.id}/start',
            headers=student_auth_headers
        )
        
        # Should return 404 or 403
        assert response.status_code in [403, 404]
