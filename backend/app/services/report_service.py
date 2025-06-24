"""
Report Generation Service for creating comprehensive development reports
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.evaluation import Evaluation, EvaluationAttempt, QuestionResponse
from app.models.learning_path import LearningPath, LearningMilestone
from app.services.base import BaseService
from app.services.ai_service import ai_service
from app.services.adaptive_evaluation_service import adaptive_evaluation_service
from app.exceptions import NotFoundError, ForbiddenError


class ReportService(BaseService):
    """Service for generating comprehensive development reports."""
    
    def generate_development_report(
        self,
        user_id: int,
        tenant_id: int,
        requesting_user: User,
        date_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive development report for a user.
        
        Args:
            user_id: User ID to generate report for
            tenant_id: Tenant ID
            requesting_user: User requesting the report
            date_range_days: Number of days to include in the report
            
        Returns:
            Development report in JSON format
        """
        # Check permissions
        if user_id != requesting_user.id and requesting_user.role not in ['admin', 'manager', 'instructor']:
            raise ForbiddenError("You don't have permission to view this report")
        
        # Get user data
        user = self.db.query(User).filter(
            User.id == user_id,
            User.tenant_id == tenant_id
        ).first()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=date_range_days)
        
        # Gather all data
        evaluation_data = self._get_evaluation_data(user_id, tenant_id, start_date, end_date)
        learning_path_data = self._get_learning_path_data(user_id, tenant_id, start_date, end_date)
        performance_metrics = self._calculate_performance_metrics(evaluation_data, learning_path_data)
        
        # Prepare data for GPT-4
        report_data = {
            'user_info': {
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'learning_style': getattr(user.profile, 'learning_style', 'mixed') if hasattr(user, 'profile') else 'mixed'
            },
            'evaluation_results': evaluation_data,
            'learning_paths': learning_path_data,
            'performance_metrics': performance_metrics,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': date_range_days
            }
        }
        
        # Generate report using AI
        report = ai_service.generate_development_report(report_data)
        
        # Add metadata
        report['metadata'] = {
            'generated_at': datetime.utcnow().isoformat(),
            'generated_by': f"{requesting_user.first_name} {requesting_user.last_name}",
            'report_period_days': date_range_days,
            'tenant_id': tenant_id
        }
        
        self.logger.info(f"Generated development report for user {user_id}")
        
        return report
    
    def _get_evaluation_data(
        self,
        user_id: int,
        tenant_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get evaluation data for the report period."""
        # Get all evaluation attempts
        attempts = self.db.query(EvaluationAttempt).filter(
            EvaluationAttempt.user_id == user_id,
            EvaluationAttempt.tenant_id == tenant_id,
            EvaluationAttempt.completed_at >= start_date,
            EvaluationAttempt.completed_at <= end_date,
            EvaluationAttempt.status == 'completed'
        ).all()
        
        evaluation_data = {
            'total_attempts': len(attempts),
            'passed_attempts': len([a for a in attempts if a.passed]),
            'average_score': 0,
            'attempts_by_evaluation': {},
            'insights': [],
            'performance_trend': []
        }
        
        if attempts:
            # Calculate average score
            evaluation_data['average_score'] = sum(a.percentage_score for a in attempts) / len(attempts)
            
            # Group by evaluation
            for attempt in attempts:
                eval_id = attempt.evaluation_id
                if eval_id not in evaluation_data['attempts_by_evaluation']:
                    evaluation_data['attempts_by_evaluation'][eval_id] = {
                        'evaluation_title': attempt.evaluation.title if hasattr(attempt, 'evaluation') else f'Evaluation {eval_id}',
                        'attempts': []
                    }
                
                evaluation_data['attempts_by_evaluation'][eval_id]['attempts'].append({
                    'attempt_number': attempt.attempt_number,
                    'score': attempt.percentage_score,
                    'passed': attempt.passed,
                    'completed_at': attempt.completed_at.isoformat(),
                    'duration_minutes': attempt.duration_seconds // 60 if attempt.duration_seconds else 0
                })
            
            # Get insights for recent attempts
            recent_attempts = sorted(attempts, key=lambda a: a.completed_at, reverse=True)[:3]
            for attempt in recent_attempts:
                insights = adaptive_evaluation_service.get_learning_insights(
                    tenant_id,
                    attempt.evaluation_id,
                    attempt.id
                )
                evaluation_data['insights'].append({
                    'evaluation_id': attempt.evaluation_id,
                    'attempt_id': attempt.id,
                    'insights': insights
                })
            
            # Calculate performance trend
            sorted_attempts = sorted(attempts, key=lambda a: a.completed_at)
            for i, attempt in enumerate(sorted_attempts):
                evaluation_data['performance_trend'].append({
                    'date': attempt.completed_at.isoformat(),
                    'score': attempt.percentage_score,
                    'index': i + 1
                })
        
        return evaluation_data
    
    def _get_learning_path_data(
        self,
        user_id: int,
        tenant_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get learning path data for the report period."""
        # Get all learning paths
        learning_paths = self.db.query(LearningPath).filter(
            LearningPath.user_id == user_id,
            LearningPath.tenant_id == tenant_id,
            LearningPath.created_at >= start_date
        ).all()
        
        path_data = {
            'total_paths': len(learning_paths),
            'active_paths': 0,
            'completed_paths': 0,
            'average_progress': 0,
            'milestone_completion_rate': 0,
            'paths': [],
            'feedback_notes': []
        }
        
        if learning_paths:
            total_milestones = 0
            completed_milestones = 0
            
            for path in learning_paths:
                if path.status in ['accepted', 'in_progress']:
                    path_data['active_paths'] += 1
                elif path.status == 'completed':
                    path_data['completed_paths'] += 1
                
                # Milestone data
                path_milestones = path.milestones if hasattr(path, 'milestones') else []
                total_milestones += len(path_milestones)
                completed_milestones += len([m for m in path_milestones if m.status == 'completed'])
                
                path_info = {
                    'id': path.id,
                    'title': path.title,
                    'status': path.status,
                    'progress': path.overall_progress,
                    'duration_weeks': path.duration_weeks,
                    'learning_style': path.learning_style,
                    'difficulty': path.difficulty_adjustment,
                    'milestones': []
                }
                
                # Add milestone details
                for milestone in path_milestones:
                    path_info['milestones'].append({
                        'title': milestone.title,
                        'week': milestone.week_number,
                        'status': milestone.status,
                        'progress': milestone.progress,
                        'skill_focus': milestone.skill_focus,
                        'user_notes': milestone.user_notes
                    })
                
                path_data['paths'].append(path_info)
                
                # Collect feedback
                if path.feedback:
                    path_data['feedback_notes'].append({
                        'path_id': path.id,
                        'feedback': path.feedback,
                        'rating': path.rating
                    })
                if path.customization_notes:
                    path_data['feedback_notes'].append({
                        'path_id': path.id,
                        'notes': path.customization_notes,
                        'type': 'customization'
                    })
            
            # Calculate averages
            path_data['average_progress'] = sum(p.overall_progress for p in learning_paths) / len(learning_paths)
            if total_milestones > 0:
                path_data['milestone_completion_rate'] = (completed_milestones / total_milestones) * 100
        
        return path_data
    
    def _calculate_performance_metrics(
        self,
        evaluation_data: Dict[str, Any],
        learning_path_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        metrics = {
            'completion_rate': 0,
            'performance_index': 0,
            'engagement_score': 0,
            'consistency_score': 0,
            'risk_indicators': []
        }
        
        # Calculate completion rate
        total_started = evaluation_data['total_attempts'] + learning_path_data['total_paths']
        total_completed = evaluation_data['passed_attempts'] + learning_path_data['completed_paths']
        if total_started > 0:
            metrics['completion_rate'] = (total_completed / total_started) * 100
        
        # Calculate performance index (weighted average)
        eval_weight = 0.6
        path_weight = 0.4
        
        eval_score = evaluation_data['average_score'] if evaluation_data['average_score'] else 0
        path_score = learning_path_data['average_progress'] if learning_path_data['average_progress'] else 0
        
        metrics['performance_index'] = (eval_score * eval_weight) + (path_score * path_weight)
        
        # Calculate engagement score
        if evaluation_data['total_attempts'] > 0 or learning_path_data['active_paths'] > 0:
            metrics['engagement_score'] = min(100, 
                (evaluation_data['total_attempts'] * 10) + 
                (learning_path_data['active_paths'] * 20) +
                (learning_path_data['milestone_completion_rate'] * 0.5)
            )
        
        # Calculate consistency score
        if len(evaluation_data['performance_trend']) >= 3:
            scores = [p['score'] for p in evaluation_data['performance_trend']]
            # Check for consistent improvement or stable high performance
            if all(scores[i] <= scores[i+1] for i in range(len(scores)-1)):
                metrics['consistency_score'] = 90  # Consistent improvement
            elif all(s >= 70 for s in scores):
                metrics['consistency_score'] = 80  # Stable high performance
            else:
                # Calculate variance
                avg = sum(scores) / len(scores)
                variance = sum((s - avg) ** 2 for s in scores) / len(scores)
                metrics['consistency_score'] = max(0, min(100, 100 - variance))
        
        # Identify risk indicators
        if evaluation_data['average_score'] < 50:
            metrics['risk_indicators'].append('Low evaluation scores')
        
        if learning_path_data['average_progress'] < 30 and learning_path_data['active_paths'] > 0:
            metrics['risk_indicators'].append('Slow learning path progress')
        
        if metrics['engagement_score'] < 40:
            metrics['risk_indicators'].append('Low engagement level')
        
        if evaluation_data['total_attempts'] == 0 and learning_path_data['total_paths'] == 0:
            metrics['risk_indicators'].append('No recent activity')
        
        # Check for declining performance
        if len(evaluation_data['performance_trend']) >= 3:
            recent_scores = [p['score'] for p in evaluation_data['performance_trend'][-3:]]
            if all(recent_scores[i] > recent_scores[i+1] for i in range(len(recent_scores)-1)):
                metrics['risk_indicators'].append('Declining performance trend')
        
        return metrics
    
    def get_batch_reports(
        self,
        user_ids: List[int],
        tenant_id: int,
        requesting_user: User,
        date_range_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Generate development reports for multiple users.
        
        Args:
            user_ids: List of user IDs
            tenant_id: Tenant ID
            requesting_user: User requesting the reports
            date_range_days: Number of days to include
            
        Returns:
            List of development reports
        """
        # Check permissions
        if requesting_user.role not in ['admin', 'manager', 'instructor']:
            raise ForbiddenError("You don't have permission to generate batch reports")
        
        reports = []
        for user_id in user_ids:
            try:
                report = self.generate_development_report(
                    user_id,
                    tenant_id,
                    requesting_user,
                    date_range_days
                )
                reports.append(report)
            except Exception as e:
                self.logger.error(f"Failed to generate report for user {user_id}: {str(e)}")
                reports.append({
                    'user_id': user_id,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return reports


# Initialize service
report_service = ReportService()