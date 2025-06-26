"""
Tests for evaluation API endpoints
"""

import pytest
from flask import json
from datetime import datetime, timedelta

from app.models.evaluation import (
    Evaluation,
    Question,
    EvaluationAttempt,
    QuestionResponse,
    EvaluationStatus,
    QuestionType,
    DifficultyLevel,
    AttemptStatus,
)
from app.models.user import User
from app.models.program import Program
from app.models.course import Course


class TestEvaluationAPI:
    """Test evaluation API endpoints"""

    def test_create_evaluation(self, client, auth_headers_admin, test_program, test_course):
        """Test creating a new evaluation"""
        data = {
            "title": "Test Evaluation",
            "description": "Test evaluation description",
            "course_id": test_course.id,
            "program_id": test_program.id,
            "instructions": "Follow the instructions carefully",
            "time_limit_minutes": 60,
            "passing_score": 70,
            "max_attempts": 2,
            "shuffle_questions": True,
            "show_results_immediately": True,
            "allow_review": True,
        }

        response = client.post(
            "/api/v1/evaluations", data=json.dumps(data), headers=auth_headers_admin, content_type="application/json"
        )

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result["title"] == data["title"]
        assert result["status"] == "draft"
        assert result["total_questions"] == 0
        assert result["total_points"] == 0.0

    def test_list_evaluations(self, client, auth_headers_admin, test_evaluations):
        """Test listing evaluations with filtering"""
        # Test basic listing
        response = client.get("/api/v1/evaluations", headers=auth_headers_admin)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert "evaluations" in result
        assert "pagination" in result
        assert len(result["evaluations"]) > 0

        # Test filtering by status
        response = client.get("/api/v1/evaluations?status=active", headers=auth_headers_admin)
        assert response.status_code == 200
        result = json.loads(response.data)
        for evaluation in result["evaluations"]:
            assert evaluation["status"] == "active"

        # Test search
        response = client.get("/api/v1/evaluations?search=Test", headers=auth_headers_admin)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert len(result["evaluations"]) > 0

    def test_get_evaluation(self, client, auth_headers_admin, test_evaluation):
        """Test getting a single evaluation"""
        response = client.get(f"/api/v1/evaluations/{test_evaluation.id}", headers=auth_headers_admin)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["id"] == test_evaluation.id
        assert result["title"] == test_evaluation.title

        # Test with include_questions
        response = client.get(
            f"/api/v1/evaluations/{test_evaluation.id}?include_questions=true", headers=auth_headers_admin
        )
        assert response.status_code == 200
        result = json.loads(response.data)
        assert "questions" in result

    def test_update_evaluation(self, client, auth_headers_admin, test_evaluation):
        """Test updating an evaluation"""
        data = {"title": "Updated Evaluation Title", "description": "Updated description", "passing_score": 80}

        response = client.put(
            f"/api/v1/evaluations/{test_evaluation.id}",
            data=json.dumps(data),
            headers=auth_headers_admin,
            content_type="application/json",
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["title"] == data["title"]
        assert result["description"] == data["description"]
        assert result["passing_score"] == data["passing_score"]

    def test_delete_evaluation(self, client, auth_headers_admin, test_evaluation):
        """Test deleting an evaluation"""
        response = client.delete(f"/api/v1/evaluations/{test_evaluation.id}", headers=auth_headers_admin)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["message"] == "Evaluation deleted successfully"

    def test_activate_evaluation(self, client, auth_headers_admin, test_evaluation_with_questions):
        """Test activating an evaluation"""
        response = client.put(
            f"/api/v1/evaluations/{test_evaluation_with_questions.id}/activate", headers=auth_headers_admin
        )
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["status"] == "active"

    def test_archive_evaluation(self, client, auth_headers_admin, test_evaluation):
        """Test archiving an evaluation"""
        response = client.put(f"/api/v1/evaluations/{test_evaluation.id}/archive", headers=auth_headers_admin)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["status"] == "archived"

    def test_add_question(self, client, auth_headers_admin, test_evaluation):
        """Test adding a question to an evaluation"""
        data = {
            "question_text": "What is the capital of France?",
            "question_type": "multiple_choice",
            "points": 10,
            "difficulty_level": "medium",
            "question_data": {"options": ["London", "Paris", "Berlin", "Madrid"], "correct_answer": "Paris"},
            "explanation": "Paris is the capital and largest city of France.",
        }

        response = client.post(
            f"/api/v1/evaluations/{test_evaluation.id}/questions",
            data=json.dumps(data),
            headers=auth_headers_admin,
            content_type="application/json",
        )

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result["question_text"] == data["question_text"]
        assert result["question_type"] == data["question_type"]
        assert result["points"] == data["points"]

    def test_update_question(self, client, auth_headers_admin, test_question):
        """Test updating a question"""
        data = {"question_text": "Updated question text", "points": 15}

        response = client.put(
            f"/api/v1/evaluations/questions/{test_question.id}",
            data=json.dumps(data),
            headers=auth_headers_admin,
            content_type="application/json",
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["question_text"] == data["question_text"]
        assert result["points"] == data["points"]

    def test_delete_question(self, client, auth_headers_admin, test_question):
        """Test deleting a question"""
        response = client.delete(f"/api/v1/evaluations/questions/{test_question.id}", headers=auth_headers_admin)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["message"] == "Question deleted successfully"

    def test_start_attempt(self, client, auth_headers_student, test_active_evaluation):
        """Test starting an evaluation attempt"""
        response = client.post(f"/api/v1/evaluations/{test_active_evaluation.id}/start", headers=auth_headers_student)

        assert response.status_code == 201
        result = json.loads(response.data)
        assert result["evaluation_id"] == test_active_evaluation.id
        assert result["status"] == "in_progress"
        assert result["attempt_number"] == 1

    def test_save_response(self, client, auth_headers_student, test_attempt, test_question):
        """Test saving a question response"""
        data = {"question_id": test_question.id, "response_data": {"selected_option": "Paris"}}

        response = client.post(
            f"/api/v1/evaluations/attempts/{test_attempt.id}/responses",
            data=json.dumps(data),
            headers=auth_headers_student,
            content_type="application/json",
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["message"] == "Response saved successfully"
        assert "is_correct" in result
        assert "points_earned" in result

    def test_submit_attempt(self, client, auth_headers_student, test_attempt_with_responses):
        """Test submitting an evaluation attempt"""
        response = client.post(
            f"/api/v1/evaluations/attempts/{test_attempt_with_responses.id}/submit", headers=auth_headers_student
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["status"] == "completed"
        assert "percentage_score" in result
        assert "passed" in result

    def test_get_attempt_results(self, client, auth_headers_student, test_completed_attempt):
        """Test getting attempt results"""
        response = client.get(
            f"/api/v1/evaluations/attempts/{test_completed_attempt.id}/results", headers=auth_headers_student
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["attempt_id"] == test_completed_attempt.id
        assert result["status"] == "completed"
        assert "score_earned" in result
        assert "percentage_score" in result
        assert "passed" in result
        assert "responses" in result

    def test_get_user_attempts(self, client, auth_headers_student, test_evaluation_with_attempts):
        """Test getting user's attempts for an evaluation"""
        response = client.get(
            f"/api/v1/evaluations/{test_evaluation_with_attempts.id}/attempts", headers=auth_headers_student
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_evaluation_statistics(self, client, auth_headers_admin, test_evaluation_with_attempts):
        """Test getting evaluation statistics"""
        response = client.get(
            f"/api/v1/evaluations/{test_evaluation_with_attempts.id}/statistics", headers=auth_headers_admin
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["evaluation_id"] == test_evaluation_with_attempts.id
        assert "total_attempts" in result
        assert "completed_attempts" in result
        assert "passed_attempts" in result
        assert "pass_rate" in result
        assert "average_score" in result
        assert "question_statistics" in result

    def test_permissions(self, client, auth_headers_student, test_evaluation):
        """Test role-based permissions"""
        # Student should not be able to create evaluation
        data = {"title": "Test"}
        response = client.post(
            "/api/v1/evaluations", data=json.dumps(data), headers=auth_headers_student, content_type="application/json"
        )
        assert response.status_code == 403

        # Student should not be able to delete evaluation
        response = client.delete(f"/api/v1/evaluations/{test_evaluation.id}", headers=auth_headers_student)
        assert response.status_code == 403

        # Student should not be able to view statistics
        response = client.get(f"/api/v1/evaluations/{test_evaluation.id}/statistics", headers=auth_headers_student)
        assert response.status_code == 403
