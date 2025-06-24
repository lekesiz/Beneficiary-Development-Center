"""
Adaptive Evaluation Service for intelligent question selection.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy import and_, not_, func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.evaluation import (
    Evaluation, Question, EvaluationAttempt, 
    QuestionResponse, QuestionBank
)
from app.services.base import BaseService
from app.services.ai_service import ai_service
from app.exceptions import NotFoundError, BadRequestError


class AdaptiveEvaluationService(BaseService):
    """Service for adaptive evaluation features."""
    
    def get_next_question(
        self, 
        tenant_id: int,
        evaluation_id: int,
        attempt_id: int,
        user_id: int
    ) -> Optional[Question]:
        """
        Get the next question based on AI-powered adaptive logic.
        
        Args:
            tenant_id: Tenant ID
            evaluation_id: Evaluation ID
            attempt_id: Current attempt ID
            user_id: User taking the evaluation
            
        Returns:
            Next question or None if evaluation is complete
        """
        # Get evaluation and attempt
        evaluation = self.db.query(Evaluation).filter(
            Evaluation.tenant_id == tenant_id,
            Evaluation.id == evaluation_id
        ).first()
        
        if not evaluation:
            raise NotFoundError("Evaluation not found")
        
        attempt = self.db.query(EvaluationAttempt).filter(
            EvaluationAttempt.evaluation_id == evaluation_id,
            EvaluationAttempt.id == attempt_id,
            EvaluationAttempt.user_id == user_id
        ).first()
        
        if not attempt:
            raise NotFoundError("Evaluation attempt not found")
        
        if attempt.completed_at:
            raise BadRequestError("Evaluation attempt already completed")
        
        # Get already answered questions
        answered_question_ids = self.db.query(QuestionResponse.question_id).filter(
            QuestionResponse.evaluation_attempt_id == attempt_id
        ).subquery()
        
        # Get recent responses for AI analysis
        recent_responses = self._get_recent_responses(attempt_id)
        
        # Determine next difficulty level using AI
        current_difficulty = self._get_current_difficulty(recent_responses)
        next_difficulty = self._determine_next_difficulty(
            recent_responses, 
            current_difficulty,
            evaluation
        )
        
        # Select next question based on difficulty
        next_question = self._select_next_question(
            evaluation_id,
            answered_question_ids,
            next_difficulty,
            evaluation
        )
        
        # Log the selection for analytics
        if next_question:
            self._log_question_selection(
                attempt_id,
                next_question.id,
                next_difficulty,
                recent_responses
            )
        
        return next_question
    
    def _get_recent_responses(
        self, 
        attempt_id: int, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent question responses for analysis."""
        responses = self.db.query(
            QuestionResponse,
            Question
        ).join(
            Question,
            QuestionResponse.question_id == Question.id
        ).filter(
            QuestionResponse.evaluation_attempt_id == attempt_id
        ).order_by(
            QuestionResponse.created_at.desc()
        ).limit(limit).all()
        
        response_data = []
        for response, question in responses:
            # Calculate time spent (if we have both created_at and responded_at)
            time_spent = None
            if response.responded_at and response.created_at:
                time_spent = (response.responded_at - response.created_at).total_seconds()
            
            response_data.append({
                'question_id': question.id,
                'question_type': question.question_type,
                'difficulty': question.difficulty_level,
                'is_correct': response.is_correct,
                'points_earned': response.points_earned,
                'max_points': question.points,
                'time_spent_seconds': time_spent,
                'topic': question.question_data.get('topic', 'General')
            })
        
        return response_data
    
    def _get_current_difficulty(self, recent_responses: List[Dict[str, Any]]) -> str:
        """Get the current difficulty level from recent responses."""
        if not recent_responses:
            return 'medium'  # Default starting difficulty
        
        # Get the most recent question's difficulty
        return recent_responses[0].get('difficulty', 'medium')
    
    def _determine_next_difficulty(
        self, 
        recent_responses: List[Dict[str, Any]], 
        current_difficulty: str,
        evaluation: Evaluation
    ) -> str:
        """Determine next difficulty using AI service."""
        evaluation_context = {
            'subject': evaluation.title,
            'description': evaluation.description,
            'total_questions': self.db.query(Question).filter(
                Question.evaluation_id == evaluation.id
            ).count()
        }
        
        # Use AI service to determine next difficulty
        return ai_service.determine_next_difficulty(
            recent_responses,
            current_difficulty,
            evaluation_context
        )
    
    def _select_next_question(
        self,
        evaluation_id: int,
        answered_question_ids,
        difficulty: str,
        evaluation: Evaluation
    ) -> Optional[Question]:
        """Select the next question based on difficulty and other criteria."""
        # Base query for unanswered questions
        query = self.db.query(Question).filter(
            Question.evaluation_id == evaluation_id,
            ~Question.id.in_(answered_question_ids)
        )
        
        # First try to get a question with the target difficulty
        question = query.filter(
            Question.difficulty_level == difficulty
        ).order_by(func.random()).first()
        
        # If no question found with target difficulty, relax criteria
        if not question:
            # Try adjacent difficulties
            if difficulty == 'medium':
                # Try easy or hard
                question = query.filter(
                    Question.difficulty_level.in_(['easy', 'hard'])
                ).order_by(func.random()).first()
            elif difficulty == 'easy':
                # Try medium
                question = query.filter(
                    Question.difficulty_level == 'medium'
                ).order_by(func.random()).first()
            elif difficulty == 'hard':
                # Try medium
                question = query.filter(
                    Question.difficulty_level == 'medium'
                ).order_by(func.random()).first()
        
        # If still no question, get any remaining question
        if not question:
            question = query.order_by(func.random()).first()
        
        return question
    
    def _log_question_selection(
        self,
        attempt_id: int,
        question_id: int,
        selected_difficulty: str,
        recent_responses: List[Dict[str, Any]]
    ):
        """Log question selection for analytics and debugging."""
        # This could be stored in a separate analytics table
        # For now, we'll just log it
        accuracy = 0
        if recent_responses:
            correct = sum(1 for r in recent_responses if r['is_correct'])
            accuracy = correct / len(recent_responses)
        
        self.logger.info(
            f"Adaptive selection - Attempt: {attempt_id}, "
            f"Question: {question_id}, Difficulty: {selected_difficulty}, "
            f"Recent accuracy: {accuracy:.2f}"
        )
    
    def get_learning_insights(
        self,
        tenant_id: int,
        evaluation_id: int,
        attempt_id: int
    ) -> Dict[str, Any]:
        """Get AI-powered learning insights for the attempt."""
        # Get evaluation and attempt details
        evaluation = self.db.query(Evaluation).filter(
            Evaluation.tenant_id == tenant_id,
            Evaluation.id == evaluation_id
        ).first()
        
        if not evaluation:
            raise NotFoundError("Evaluation not found")
        
        attempt = self.db.query(EvaluationAttempt).filter(
            EvaluationAttempt.id == attempt_id,
            EvaluationAttempt.evaluation_id == evaluation_id
        ).first()
        
        if not attempt:
            raise NotFoundError("Evaluation attempt not found")
        
        # Get all responses for the attempt with question details
        responses = self.db.query(
            QuestionResponse,
            Question
        ).join(
            Question,
            QuestionResponse.question_id == Question.id
        ).filter(
            QuestionResponse.evaluation_attempt_id == attempt_id,
            Question.evaluation_id == evaluation_id
        ).order_by(
            QuestionResponse.created_at
        ).all()
        
        if not responses:
            return {
                'strengths': [],
                'weaknesses': [],
                'recommendations': ["Henüz değerlendirilecek veri yok"],
                'performance_metrics': {},
                'visual_indicators': {}
            }
        
        # Format responses for AI analysis
        all_responses = []
        topic_performance = {}
        
        for response, question in responses:
            # Calculate time spent if available
            time_spent = None
            if response.responded_at and response.created_at:
                time_spent = (response.responded_at - response.created_at).total_seconds()
            
            # Extract topic from question data or metadata
            topic = (question.question_data.get('topic') or 
                    question.question_metadata.get('subject') or 
                    'Genel')
            
            # Build response data
            response_data = {
                'question_id': question.id,
                'question_type': question.question_type,
                'difficulty': question.difficulty_level,
                'is_correct': response.is_correct,
                'points_earned': response.points_earned,
                'max_points': question.points,
                'time_spent_seconds': time_spent,
                'expected_time_seconds': question.question_data.get('expected_time', 60),
                'topic': topic,
                'question_text': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text
            }
            
            all_responses.append(response_data)
            
            # Track topic performance
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            
            topic_performance[topic]['total'] += 1
            if response.is_correct:
                topic_performance[topic]['correct'] += 1
        
        # Prepare comprehensive performance data
        performance_data = {
            'responses': all_responses,
            'topic_performance': topic_performance,
            'evaluation_info': {
                'title': evaluation.title,
                'description': evaluation.description,
                'total_questions': evaluation.total_questions,
                'passing_score': evaluation.passing_score
            },
            'attempt_info': {
                'score': attempt.score_earned,
                'total_points': attempt.total_points,
                'percentage_score': attempt.percentage_score,
                'passed': attempt.passed,
                'time_spent_minutes': attempt.time_spent_minutes,
                'questions_answered': attempt.questions_answered
            },
            'accuracy': attempt.percentage_score / 100 if attempt.percentage_score else 0
        }
        
        # Generate AI-powered insights
        insights = ai_service.generate_learning_insights(performance_data)
        
        # Add attempt-specific metrics
        insights['attempt_summary'] = {
            'evaluation_title': evaluation.title,
            'score': f"{attempt.score_earned:.1f} / {attempt.total_points}",
            'percentage': f"{attempt.percentage_score:.1f}%",
            'passed': attempt.passed,
            'duration': f"{attempt.time_spent_minutes or 0} dakika",
            'questions_answered': f"{attempt.questions_answered} / {attempt.total_questions}"
        }
        
        # Log insights generation
        self.logger.info(
            f"Generated learning insights for attempt {attempt_id} "
            f"(Evaluation: {evaluation_id}, Score: {attempt.percentage_score}%)"
        )
        
        return insights


# Create service instance
adaptive_evaluation_service = AdaptiveEvaluationService()