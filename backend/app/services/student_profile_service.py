"""
Student Profile Service for detailed student development analysis
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.user import User
from app.models.program import Program
from app.models.course import Course
from app.models.course_session import CourseSession
from app.models.enrollment import Enrollment
from app.models.evaluation import Evaluation, EvaluationAttempt, QuestionResponse
from app.models.learning_path import LearningPath, LearningMilestone
from app.services.base import BaseService
from app.services.ai_service import ai_service
from app.core.exceptions import NotFoundError, ForbiddenError


class StudentProfileService(BaseService):
    """Service for comprehensive student profile analysis."""

    def get_student_profile(self, student_id: int, tenant_id: int, requesting_user: User) -> Dict[str, Any]:
        """
        Get comprehensive profile data for a student.

        Args:
            student_id: Student user ID
            tenant_id: Tenant ID
            requesting_user: User requesting the profile

        Returns:
            Comprehensive student profile data
        """
        # Check permissions
        if requesting_user.role not in ["admin", "manager", "instructor", "trainer"]:
            if requesting_user.id != student_id:
                raise ForbiddenError("You don't have permission to view this profile")

        # Get student data
        student = self.db.query(User).filter(User.id == student_id, User.tenant_id == tenant_id).first()

        if not student:
            raise NotFoundError("Student not found")

        # Gather all profile sections
        profile = {
            "student_info": self._get_student_info(student),
            "development_scores": self._get_development_scores(student_id, tenant_id),
            "recent_activities": self._get_recent_activities(student_id, tenant_id),
            "enrollments": self._get_enrollments(student_id, tenant_id),
            "ai_analysis": self._get_ai_analysis(student_id, tenant_id),
            "visualization_data": self._get_visualization_data(student_id, tenant_id),
            "coach_notes": self._get_coach_notes(student_id, tenant_id),
            "next_recommendations": self._get_next_recommendations(student_id, tenant_id),
        }

        self.logger.info(f"Generated profile for student {student_id}")

        return profile

    def _get_student_info(self, student: User) -> Dict[str, Any]:
        """Get basic student information."""
        return {
            "id": student.id,
            "name": f"{student.first_name} {student.last_name}",
            "email": student.email,
            "registration_date": student.created_at.isoformat() if student.created_at else None,
            "last_login": (
                student.last_login.isoformat() if hasattr(student, "last_login") and student.last_login else None
            ),
            "status": "active" if student.is_active else "inactive",
            "profile_picture": getattr(student, "profile_picture", None),
            "learning_style": (
                getattr(student.profile, "learning_style", "mixed") if hasattr(student, "profile") else "mixed"
            ),
        }

    def _get_development_scores(self, student_id: int, tenant_id: int) -> Dict[str, Any]:
        """Calculate development scores for the student."""
        # Get evaluation data (last 90 days)
        recent_attempts = (
            self.db.query(EvaluationAttempt)
            .filter(
                EvaluationAttempt.user_id == student_id,
                EvaluationAttempt.tenant_id == tenant_id,
                EvaluationAttempt.status == "completed",
                EvaluationAttempt.completed_at >= datetime.utcnow() - timedelta(days=90),
            )
            .all()
        )

        # Get learning paths
        learning_paths = (
            self.db.query(LearningPath)
            .filter(LearningPath.user_id == student_id, LearningPath.tenant_id == tenant_id)
            .all()
        )

        # Calculate Performance Index
        if recent_attempts:
            avg_score = sum(a.percentage_score for a in recent_attempts) / len(recent_attempts)
            passed_rate = sum(1 for a in recent_attempts if a.passed) / len(recent_attempts) * 100
        else:
            avg_score = 0
            passed_rate = 0

        # Calculate Engagement Score
        active_paths = [p for p in learning_paths if p.status in ["accepted", "in_progress"]]
        completed_paths = [p for p in learning_paths if p.status == "completed"]

        if learning_paths:
            path_engagement = (len(active_paths) + len(completed_paths) * 2) / len(learning_paths) * 50
        else:
            path_engagement = 0

        # Recent activity frequency
        recent_activity_count = len(recent_attempts)
        activity_score = min(50, recent_activity_count * 10)

        engagement_score = path_engagement + activity_score

        # Calculate Completion Rate
        total_milestones = sum(p.total_milestones for p in learning_paths)
        completed_milestones = sum(p.completed_milestones for p in learning_paths)

        if total_milestones > 0:
            completion_rate = (completed_milestones / total_milestones) * 100
        else:
            completion_rate = 0

        # Calculate Risk Score
        risk_factors = []
        if avg_score < 50:
            risk_factors.append("low_performance")
        if engagement_score < 40:
            risk_factors.append("low_engagement")
        if completion_rate < 30:
            risk_factors.append("low_completion")
        if recent_activity_count == 0:
            risk_factors.append("no_recent_activity")

        if len(risk_factors) == 0:
            risk_score = "Low"
            risk_level = 1
        elif len(risk_factors) <= 2:
            risk_score = "Medium"
            risk_level = 2
        else:
            risk_score = "High"
            risk_level = 3

        # Performance Index (weighted average)
        performance_index = avg_score * 0.4 + engagement_score * 0.3 + completion_rate * 0.2 + passed_rate * 0.1

        return {
            "performance_index": round(performance_index, 1),
            "engagement_score": round(engagement_score, 1),
            "completion_rate": round(completion_rate, 1),
            "average_score": round(avg_score, 1),
            "passed_rate": round(passed_rate, 1),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "total_evaluations": len(recent_attempts),
            "active_learning_paths": len(active_paths),
            "completed_learning_paths": len(completed_paths),
        }

    def _get_recent_activities(self, student_id: int, tenant_id: int) -> Dict[str, Any]:
        """Get recent learning activities."""
        # Get last 5 evaluations
        recent_evaluations = (
            self.db.query(EvaluationAttempt)
            .join(Evaluation)
            .filter(
                EvaluationAttempt.user_id == student_id,
                EvaluationAttempt.tenant_id == tenant_id,
                EvaluationAttempt.status == "completed",
            )
            .order_by(desc(EvaluationAttempt.completed_at))
            .limit(5)
            .all()
        )

        evaluations_data = []
        for attempt in recent_evaluations:
            evaluations_data.append(
                {
                    "id": attempt.id,
                    "evaluation_id": attempt.evaluation_id,
                    "evaluation_title": attempt.evaluation.title if hasattr(attempt, "evaluation") else "Değerlendirme",
                    "score": attempt.percentage_score,
                    "passed": attempt.passed,
                    "completed_at": attempt.completed_at.isoformat(),
                    "duration_minutes": attempt.duration_seconds // 60 if attempt.duration_seconds else 0,
                    "attempt_number": attempt.attempt_number,
                }
            )

        # Get last 5 learning sessions (milestone updates)
        recent_milestones = (
            self.db.query(LearningMilestone)
            .join(LearningPath)
            .filter(
                LearningPath.user_id == student_id,
                LearningPath.tenant_id == tenant_id,
                LearningMilestone.updated_at.isnot(None),
            )
            .order_by(desc(LearningMilestone.updated_at))
            .limit(5)
            .all()
        )

        sessions_data = []
        for milestone in recent_milestones:
            sessions_data.append(
                {
                    "id": milestone.id,
                    "path_id": milestone.learning_path_id,
                    "path_title": (
                        milestone.learning_path.title if hasattr(milestone, "learning_path") else "Öğrenme Yolu"
                    ),
                    "milestone_title": milestone.title,
                    "progress": milestone.progress,
                    "status": milestone.status,
                    "updated_at": milestone.updated_at.isoformat() if milestone.updated_at else None,
                    "week_number": milestone.week_number,
                }
            )

        return {
            "recent_evaluations": evaluations_data,
            "recent_sessions": sessions_data,
            "last_activity_date": self._get_last_activity_date(student_id, tenant_id),
        }

    def _get_enrollments(self, student_id: int, tenant_id: int) -> Dict[str, Any]:
        """Get student's program and course enrollments."""
        # Get program enrollments
        program_enrollments = (
            self.db.query(Enrollment)
            .join(Program)
            .filter(Enrollment.beneficiary_id == student_id, Enrollment.tenant_id == tenant_id)
            .all()
        )

        programs_data = []
        for enrollment in program_enrollments:
            programs_data.append(
                {
                    "id": enrollment.program_id,
                    "title": (
                        enrollment.program.title
                        if hasattr(enrollment, "program")
                        else f"Program {enrollment.program_id}"
                    ),
                    "status": enrollment.status,
                    "progress": getattr(enrollment, "progress", 0),
                    "enrolled_at": enrollment.enrolled_at.isoformat() if hasattr(enrollment, "enrolled_at") else None,
                    "completed_at": (
                        enrollment.completed_at.isoformat() if hasattr(enrollment, "completed_at") else None
                    ),
                }
            )

        # Get course enrollments
        course_enrollments = (
            self.db.query(Enrollment)
            .join(Course)
            .filter(Enrollment.beneficiary_id == student_id, Enrollment.tenant_id == tenant_id)
            .all()
        )

        courses_data = []
        for enrollment in course_enrollments:
            courses_data.append(
                {
                    "id": enrollment.course_id,
                    "title": (
                        enrollment.course.title if hasattr(enrollment, "course") else f"Course {enrollment.course_id}"
                    ),
                    "status": enrollment.status,
                    "progress": getattr(enrollment, "progress", 0),
                    "enrolled_at": enrollment.enrolled_at.isoformat() if hasattr(enrollment, "enrolled_at") else None,
                    "completed_at": (
                        enrollment.completed_at.isoformat() if hasattr(enrollment, "completed_at") else None
                    ),
                }
            )

        return {
            "programs": programs_data,
            "courses": courses_data,
            "total_enrollments": len(programs_data) + len(courses_data),
            "active_enrollments": len([p for p in programs_data if p["status"] == "active"])
            + len([c for c in courses_data if c["status"] == "active"]),
        }

    def _get_ai_analysis(self, student_id: int, tenant_id: int) -> Dict[str, Any]:
        """Get AI-powered analysis of student development."""
        # Gather data for AI analysis
        scores = self._get_development_scores(student_id, tenant_id)
        activities = self._get_recent_activities(student_id, tenant_id)

        # Get recent evaluation responses for detailed analysis
        recent_responses = (
            self.db.query(QuestionResponse)
            .join(EvaluationAttempt)
            .filter(
                EvaluationAttempt.user_id == student_id,
                EvaluationAttempt.tenant_id == tenant_id,
                EvaluationAttempt.completed_at >= datetime.utcnow() - timedelta(days=30),
            )
            .limit(50)
            .all()
        )

        # Prepare data for AI
        analysis_data = {
            "scores": scores,
            "recent_evaluations": activities["recent_evaluations"],
            "response_patterns": self._analyze_response_patterns(recent_responses),
            "learning_progress": activities["recent_sessions"],
            "recent_activities": activities,
        }

        # Get AI analysis
        try:
            ai_analysis = ai_service.generate_student_profile_analysis(analysis_data)
        except Exception as e:
            self.logger.error(f"AI analysis failed for student {student_id}: {str(e)}")
            ai_analysis = self._get_fallback_analysis(scores, activities)

        return ai_analysis

    def _get_visualization_data(self, student_id: int, tenant_id: int) -> Dict[str, Any]:
        """Get data for visualizations."""
        # Performance trend (last 12 weeks)
        performance_trend = []

        for week_offset in range(11, -1, -1):
            week_start = datetime.utcnow() - timedelta(weeks=week_offset, days=datetime.utcnow().weekday())
            week_end = week_start + timedelta(days=7)

            week_attempts = (
                self.db.query(EvaluationAttempt)
                .filter(
                    EvaluationAttempt.user_id == student_id,
                    EvaluationAttempt.tenant_id == tenant_id,
                    EvaluationAttempt.status == "completed",
                    EvaluationAttempt.completed_at >= week_start,
                    EvaluationAttempt.completed_at < week_end,
                )
                .all()
            )

            if week_attempts:
                avg_score = sum(a.percentage_score for a in week_attempts) / len(week_attempts)
            else:
                avg_score = None

            performance_trend.append(
                {"week": week_start.strftime("%d/%m"), "score": avg_score, "attempts": len(week_attempts)}
            )

        # Milestone completion data
        learning_paths = (
            self.db.query(LearningPath)
            .filter(
                LearningPath.user_id == student_id,
                LearningPath.tenant_id == tenant_id,
                LearningPath.status.in_(["accepted", "in_progress", "completed"]),
            )
            .all()
        )

        milestone_data = []
        for path in learning_paths:
            milestone_data.append(
                {
                    "path_title": path.title,
                    "total_milestones": path.total_milestones,
                    "completed_milestones": path.completed_milestones,
                    "progress": path.overall_progress,
                }
            )

        # Skill distribution
        skill_distribution = self._calculate_skill_distribution(student_id, tenant_id)

        return {
            "performance_trend": performance_trend,
            "milestone_completion": milestone_data,
            "skill_distribution": skill_distribution,
        }

    def _get_coach_notes(self, student_id: int, tenant_id: int) -> List[Dict[str, Any]]:
        """Get coach notes for the student."""
        # This is a placeholder - in production, you'd have a CoachNote model
        # For now, return empty list
        return []

    def _get_next_recommendations(self, student_id: int, tenant_id: int) -> Dict[str, Any]:
        """Get recommendations for next steps."""
        scores = self._get_development_scores(student_id, tenant_id)

        recommendations = {
            "next_evaluation": None,
            "suggested_courses": [],
            "improvement_areas": [],
            "action_items": [],
        }

        # Suggest next evaluation based on performance
        if scores["average_score"] < 70:
            recommendations["next_evaluation"] = {
                "type": "remedial",
                "focus": "Temel konuların pekiştirilmesi",
                "suggested_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            }
        else:
            recommendations["next_evaluation"] = {
                "type": "advanced",
                "focus": "İleri seviye konular",
                "suggested_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            }

        # Action items based on risk
        if scores["risk_score"] == "High":
            recommendations["action_items"] = [
                "Acil olarak birebir görüşme planlanmalı",
                "Öğrenme planı yeniden değerlendirilmeli",
                "Ek destek kaynakları sağlanmalı",
            ]
        elif scores["risk_score"] == "Medium":
            recommendations["action_items"] = ["Haftalık ilerleme takibi yapılmalı", "Motivasyon desteği sağlanmalı"]
        else:
            recommendations["action_items"] = [
                "Mevcut ilerleme devam ettirilmeli",
                "İleri seviye konulara yönlendirilmeli",
            ]

        return recommendations

    def _get_last_activity_date(self, student_id: int, tenant_id: int) -> Optional[str]:
        """Get the date of last activity."""
        last_attempt = (
            self.db.query(EvaluationAttempt)
            .filter(EvaluationAttempt.user_id == student_id, EvaluationAttempt.tenant_id == tenant_id)
            .order_by(desc(EvaluationAttempt.updated_at))
            .first()
        )

        if last_attempt and last_attempt.updated_at:
            return last_attempt.updated_at.isoformat()

        return None

    def _analyze_response_patterns(self, responses: List[QuestionResponse]) -> Dict[str, Any]:
        """Analyze patterns in question responses."""
        if not responses:
            return {"total_responses": 0, "correct_rate": 0, "avg_time_per_question": 0, "difficulty_performance": {}}

        total = len(responses)
        correct = sum(1 for r in responses if r.is_correct)
        total_time = sum(r.time_spent_seconds for r in responses if r.time_spent_seconds)

        # Group by difficulty
        difficulty_stats = {}
        for diff in ["easy", "medium", "hard"]:
            diff_responses = [r for r in responses if getattr(r, "difficulty", "") == diff]
            if diff_responses:
                difficulty_stats[diff] = {
                    "count": len(diff_responses),
                    "correct_rate": sum(1 for r in diff_responses if r.is_correct) / len(diff_responses) * 100,
                }

        return {
            "total_responses": total,
            "correct_rate": (correct / total * 100) if total > 0 else 0,
            "avg_time_per_question": (total_time / total) if total > 0 else 0,
            "difficulty_performance": difficulty_stats,
        }

    def _calculate_skill_distribution(self, student_id: int, tenant_id: int) -> List[Dict[str, Any]]:
        """Calculate skill distribution from learning paths and evaluations."""
        # Get all milestones for the student
        milestones = (
            self.db.query(LearningMilestone)
            .join(LearningPath)
            .filter(LearningPath.user_id == student_id, LearningPath.tenant_id == tenant_id)
            .all()
        )

        skill_data = {}
        for milestone in milestones:
            skill = milestone.skill_focus or "Genel"
            if skill not in skill_data:
                skill_data[skill] = {"total": 0, "completed": 0, "in_progress": 0, "total_progress": 0}

            skill_data[skill]["total"] += 1
            skill_data[skill]["total_progress"] += milestone.progress

            if milestone.status == "completed":
                skill_data[skill]["completed"] += 1
            elif milestone.status == "in_progress":
                skill_data[skill]["in_progress"] += 1

        # Convert to list format
        distribution = []
        for skill, data in skill_data.items():
            avg_progress = data["total_progress"] / data["total"] if data["total"] > 0 else 0
            distribution.append(
                {
                    "skill": skill,
                    "total_focus": data["total"],
                    "completed": data["completed"],
                    "in_progress": data["in_progress"],
                    "average_progress": round(avg_progress, 1),
                    "mastery_level": self._calculate_mastery_level(avg_progress, data["completed"], data["total"]),
                }
            )

        return sorted(distribution, key=lambda x: x["total_focus"], reverse=True)

    def _calculate_mastery_level(self, avg_progress: float, completed: int, total: int) -> str:
        """Calculate mastery level for a skill."""
        completion_rate = (completed / total * 100) if total > 0 else 0

        if completion_rate >= 80 and avg_progress >= 90:
            return "Expert"
        elif completion_rate >= 60 and avg_progress >= 70:
            return "Proficient"
        elif completion_rate >= 40 and avg_progress >= 50:
            return "Intermediate"
        elif avg_progress >= 30:
            return "Beginner"
        else:
            return "Novice"

    def _get_fallback_analysis(self, scores: Dict[str, Any], activities: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI is not available."""
        strengths = []
        weaknesses = []
        recommendations = []

        # Analyze strengths
        if scores["average_score"] >= 80:
            strengths.append("Değerlendirmelerde yüksek başarı gösteriyor")
        if scores["engagement_score"] >= 70:
            strengths.append("Yüksek katılım ve motivasyon sergiliyor")
        if scores["completion_rate"] >= 80:
            strengths.append("Öğrenme hedeflerini düzenli tamamlıyor")

        # Analyze weaknesses
        if scores["average_score"] < 60:
            weaknesses.append("Değerlendirme puanları geliştirilmeli")
        if scores["engagement_score"] < 50:
            weaknesses.append("Katılım düzeyi artırılmalı")
        if scores["completion_rate"] < 50:
            weaknesses.append("Öğrenme planı tamamlama oranı düşük")

        # Generate recommendations
        if scores["risk_score"] == "High":
            recommendations.extend(
                [
                    "Acil müdahale gerekiyor - birebir görüşme planlanmalı",
                    "Öğrenme hızı ve yöntemi gözden geçirilmeli",
                    "Ek destek kaynakları sağlanmalı",
                ]
            )
        else:
            recommendations.extend(
                ["Mevcut ilerleme takip edilmeli", "Güçlü yönler üzerine odaklanılmalı", "Yeni zorluklar sunulmalı"]
            )

        return {
            "strengths": strengths[:3] if strengths else ["Gelişim potansiyeli yüksek"],
            "weaknesses": weaknesses[:3] if weaknesses else ["Sürekli gelişim gösteriyor"],
            "recommendations": recommendations[:3],
            "learning_pattern": "Standart öğrenme modeli takip ediliyor",
            "motivation_level": "Orta" if scores["engagement_score"] >= 50 else "Düşük",
        }

    def add_coach_note(
        self, student_id: int, tenant_id: int, coach_id: int, note: str, category: str = "general"
    ) -> Dict[str, Any]:
        """Add a coach note for a student."""
        # This is a placeholder implementation
        # In production, you'd save this to a CoachNote table

        note_data = {
            "id": None,  # Would be generated by DB
            "student_id": student_id,
            "coach_id": coach_id,
            "note": note,
            "category": category,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.logger.info(f"Coach {coach_id} added note for student {student_id}")

        return {"success": True, "note": note_data}


# Initialize service - create when needed with proper context
# student_profile_service = StudentProfileService()
