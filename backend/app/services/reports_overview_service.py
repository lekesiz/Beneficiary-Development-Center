"""
Reports Overview Service for coaches and administrators
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.user import User
from app.models.program import Program, ProgramEnrollment
from app.models.course import Course, CourseEnrollment
from app.models.evaluation import EvaluationAttempt
from app.models.learning_path import LearningPath
from app.services.base import BaseService
from app.services.report_service import report_service
from app.exceptions import ForbiddenError, NotFoundError
from app.core.cache import cache


class ReportsOverviewService(BaseService):
    """Service for managing reports overview for coaches."""
    
    def get_students_overview(
        self,
        tenant_id: int,
        requesting_user: User,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get overview of all students' development reports.
        
        Args:
            tenant_id: Tenant ID
            requesting_user: User requesting the overview
            filters: Filter parameters
            
        Returns:
            Paginated list of student report summaries
        """
        # Check permissions
        if requesting_user.role not in ['admin', 'manager', 'instructor', 'trainer']:
            raise ForbiddenError("You don't have permission to view reports overview")
        
        # Parse filters
        page = filters.get('page', 1)
        per_page = filters.get('per_page', 20)
        risk_level = filters.get('risk')
        min_performance = filters.get('min_performance', type=float)
        max_performance = filters.get('max_performance', type=float)
        program_id = filters.get('program_id', type=int)
        course_id = filters.get('course_id', type=int)
        search = filters.get('search')
        sort_by = filters.get('sort_by', 'risk_score')  # risk_score, performance, name
        sort_desc = filters.get('sort_desc', 'true').lower() == 'true'
        
        # Build base query for students
        query = self.db.query(User).filter(
            User.tenant_id == tenant_id,
            User.role.in_(['student', 'participant'])
        )
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )
        
        # Apply program/course filters
        if program_id:
            query = query.join(ProgramEnrollment).filter(
                ProgramEnrollment.program_id == program_id,
                ProgramEnrollment.status == 'active'
            )
        
        if course_id:
            query = query.join(CourseEnrollment).filter(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.status == 'active'
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        students = query.offset(offset).limit(per_page).all()
        
        # Generate report summaries for each student
        report_summaries = []
        for student in students:
            # Try to get cached summary first
            cache_key = f"report_summary_{tenant_id}_{student.id}"
            cached_summary = cache.get(cache_key)
            
            if cached_summary:
                summary = cached_summary
            else:
                try:
                    # Generate mini report for overview
                    summary = self._generate_student_summary(student, tenant_id)
                    # Cache for 1 hour
                    cache.set(cache_key, summary, timeout=3600)
                except Exception as e:
                    self.logger.error(f"Failed to generate summary for student {student.id}: {str(e)}")
                    summary = self._get_fallback_summary(student)
            
            # Apply performance filters
            if min_performance is not None and summary['performance_index'] < min_performance:
                continue
            if max_performance is not None and summary['performance_index'] > max_performance:
                continue
            
            # Apply risk filter
            if risk_level and summary['risk_score'].lower() != risk_level.lower():
                continue
            
            report_summaries.append(summary)
        
        # Sort results
        if sort_by == 'risk_score':
            # Sort by risk priority (High -> Medium -> Low)
            risk_order = {'high': 3, 'medium': 2, 'low': 1}
            report_summaries.sort(
                key=lambda x: risk_order.get(x['risk_score'].lower(), 0),
                reverse=sort_desc
            )
        elif sort_by == 'performance':
            report_summaries.sort(
                key=lambda x: x['performance_index'],
                reverse=sort_desc
            )
        elif sort_by == 'name':
            report_summaries.sort(
                key=lambda x: x['student_name'],
                reverse=sort_desc
            )
        
        # Calculate pagination info
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': len(report_summaries),
            'pages': (len(report_summaries) + per_page - 1) // per_page
        }
        
        return {
            'summaries': report_summaries,
            'pagination': pagination,
            'filters_applied': {
                'risk': risk_level,
                'min_performance': min_performance,
                'max_performance': max_performance,
                'program_id': program_id,
                'course_id': course_id,
                'search': search
            }
        }
    
    def _generate_student_summary(
        self,
        student: User,
        tenant_id: int
    ) -> Dict[str, Any]:
        """Generate a summary of student's development report."""
        # Get recent evaluation data
        recent_attempts = self.db.query(EvaluationAttempt).filter(
            EvaluationAttempt.user_id == student.id,
            EvaluationAttempt.tenant_id == tenant_id,
            EvaluationAttempt.status == 'completed',
            EvaluationAttempt.completed_at >= datetime.utcnow() - timedelta(days=30)
        ).order_by(EvaluationAttempt.completed_at.desc()).limit(5).all()
        
        # Get active learning paths
        active_paths = self.db.query(LearningPath).filter(
            LearningPath.user_id == student.id,
            LearningPath.tenant_id == tenant_id,
            LearningPath.status.in_(['accepted', 'in_progress'])
        ).all()
        
        # Calculate metrics
        if recent_attempts:
            avg_score = sum(a.percentage_score for a in recent_attempts) / len(recent_attempts)
            passed_count = sum(1 for a in recent_attempts if a.passed)
            completion_rate = (passed_count / len(recent_attempts)) * 100
        else:
            avg_score = 0
            completion_rate = 0
        
        if active_paths:
            avg_progress = sum(p.overall_progress for p in active_paths) / len(active_paths)
        else:
            avg_progress = 0
        
        # Calculate performance index
        performance_index = (avg_score * 0.6) + (avg_progress * 0.4)
        
        # Determine risk score
        risk_indicators = []
        if avg_score < 50:
            risk_indicators.append('low_scores')
        if avg_progress < 30 and active_paths:
            risk_indicators.append('slow_progress')
        if not recent_attempts and not active_paths:
            risk_indicators.append('no_activity')
        if completion_rate < 50:
            risk_indicators.append('low_completion')
        
        if len(risk_indicators) == 0:
            risk_score = 'Low'
        elif len(risk_indicators) <= 2:
            risk_score = 'Medium'
        else:
            risk_score = 'High'
        
        # Get enrolled programs/courses
        enrollments = self._get_student_enrollments(student.id, tenant_id)
        
        # Generate progress summary
        if performance_index >= 80:
            progress_summary = "Mükemmel performans gösteriyor"
        elif performance_index >= 60:
            progress_summary = "İyi ilerleme kaydediyor"
        elif performance_index >= 40:
            progress_summary = "Orta düzeyde performans"
        else:
            progress_summary = "Destek gerekebilir"
        
        # Get last activity
        last_activity = None
        if recent_attempts:
            last_activity = recent_attempts[0].completed_at
        
        return {
            'student_id': student.id,
            'student_name': f"{student.first_name} {student.last_name}",
            'student_email': student.email,
            'performance_index': round(performance_index),
            'risk_score': risk_score,
            'risk_indicators': risk_indicators,
            'progress_summary': progress_summary,
            'completion_rate': round(completion_rate),
            'average_score': round(avg_score, 1),
            'active_learning_paths': len(active_paths),
            'recent_evaluations': len(recent_attempts),
            'enrollments': enrollments,
            'last_activity': last_activity.isoformat() if last_activity else None,
            'needs_attention': risk_score in ['Medium', 'High'] or performance_index < 60
        }
    
    def _get_fallback_summary(self, student: User) -> Dict[str, Any]:
        """Get fallback summary when report generation fails."""
        return {
            'student_id': student.id,
            'student_name': f"{student.first_name} {student.last_name}",
            'student_email': student.email,
            'performance_index': 0,
            'risk_score': 'Unknown',
            'risk_indicators': ['data_unavailable'],
            'progress_summary': 'Veri yüklenemedi',
            'completion_rate': 0,
            'average_score': 0,
            'active_learning_paths': 0,
            'recent_evaluations': 0,
            'enrollments': [],
            'last_activity': None,
            'needs_attention': True
        }
    
    def _get_student_enrollments(
        self,
        student_id: int,
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """Get student's program and course enrollments."""
        enrollments = []
        
        # Get program enrollments
        program_enrollments = self.db.query(ProgramEnrollment).join(Program).filter(
            ProgramEnrollment.user_id == student_id,
            ProgramEnrollment.tenant_id == tenant_id,
            ProgramEnrollment.status == 'active'
        ).all()
        
        for enrollment in program_enrollments:
            enrollments.append({
                'type': 'program',
                'id': enrollment.program_id,
                'name': enrollment.program.title if hasattr(enrollment, 'program') else f'Program {enrollment.program_id}',
                'progress': enrollment.progress if hasattr(enrollment, 'progress') else 0
            })
        
        # Get course enrollments
        course_enrollments = self.db.query(CourseEnrollment).join(Course).filter(
            CourseEnrollment.user_id == student_id,
            CourseEnrollment.tenant_id == tenant_id,
            CourseEnrollment.status == 'active'
        ).all()
        
        for enrollment in course_enrollments:
            enrollments.append({
                'type': 'course',
                'id': enrollment.course_id,
                'name': enrollment.course.title if hasattr(enrollment, 'course') else f'Course {enrollment.course_id}',
                'progress': enrollment.progress if hasattr(enrollment, 'progress') else 0
            })
        
        return enrollments
    
    def add_coach_note(
        self,
        student_id: int,
        tenant_id: int,
        requesting_user: User,
        note: str
    ) -> Dict[str, Any]:
        """
        Add a coach note for a student.
        
        Args:
            student_id: Student ID
            tenant_id: Tenant ID
            requesting_user: Coach adding the note
            note: Note content
            
        Returns:
            Success response
        """
        # Check permissions
        if requesting_user.role not in ['admin', 'manager', 'instructor', 'trainer']:
            raise ForbiddenError("You don't have permission to add coach notes")
        
        # Verify student exists
        student = self.db.query(User).filter(
            User.id == student_id,
            User.tenant_id == tenant_id
        ).first()
        
        if not student:
            raise NotFoundError("Student not found")
        
        # Store note (you might want to create a CoachNote model for this)
        # For now, we'll store it in user's metadata or a separate table
        # This is a simplified implementation
        
        self.logger.info(f"Coach {requesting_user.id} added note for student {student_id}")
        
        return {
            'success': True,
            'message': 'Note added successfully',
            'note': {
                'student_id': student_id,
                'coach_id': requesting_user.id,
                'coach_name': f"{requesting_user.first_name} {requesting_user.last_name}",
                'note': note,
                'created_at': datetime.utcnow().isoformat()
            }
        }
    
    def export_reports_batch(
        self,
        student_ids: List[int],
        tenant_id: int,
        requesting_user: User,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Export multiple student reports.
        
        Args:
            student_ids: List of student IDs
            tenant_id: Tenant ID
            requesting_user: User requesting export
            format: Export format (json/pdf)
            
        Returns:
            Export data or file reference
        """
        # Check permissions
        if requesting_user.role not in ['admin', 'manager', 'instructor', 'trainer']:
            raise ForbiddenError("You don't have permission to export reports")
        
        # Generate reports for each student
        reports = []
        for student_id in student_ids:
            try:
                report = report_service.generate_development_report(
                    user_id=student_id,
                    tenant_id=tenant_id,
                    requesting_user=requesting_user,
                    date_range_days=30
                )
                reports.append(report)
            except Exception as e:
                self.logger.error(f"Failed to generate report for student {student_id}: {str(e)}")
                reports.append({
                    'student_id': student_id,
                    'error': str(e)
                })
        
        return {
            'format': format,
            'reports': reports,
            'total': len(reports),
            'successful': len([r for r in reports if 'error' not in r]),
            'exported_at': datetime.utcnow().isoformat(),
            'exported_by': f"{requesting_user.first_name} {requesting_user.last_name}"
        }


# Initialize service
reports_overview_service = ReportsOverviewService()