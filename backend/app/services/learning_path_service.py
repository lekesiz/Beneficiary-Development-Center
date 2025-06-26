"""
Learning Path Service for managing personalized learning plans
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.learning_path import LearningPath, LearningMilestone, LearningPathStatus, LearningPathUpdate, MilestoneStatus
from app.models.evaluation import EvaluationAttempt
from app.models.user import User
from app.services.base import BaseService
from app.services.ai_service import ai_service
from app.services.adaptive_evaluation_service import AdaptiveEvaluationService
from app.services.student_profile_service import StudentProfileService
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


class LearningPathService(BaseService):
    """Service for managing learning paths."""

    def create_learning_path(self, tenant_id: int, evaluation_id: int, attempt_id: int, user: User) -> LearningPath:
        """
        Create a new learning path based on evaluation insights.

        Args:
            tenant_id: Tenant ID
            evaluation_id: Evaluation ID
            attempt_id: Evaluation attempt ID
            user: Current user

        Returns:
            Created learning path
        """
        # Get learning insights for the attempt
        adaptive_service = AdaptiveEvaluationService(db_session=self.db)
        insights = adaptive_service.get_learning_insights(tenant_id, evaluation_id, attempt_id)

        # Get evaluation and attempt details
        attempt = (
            self.db.query(EvaluationAttempt)
            .filter(EvaluationAttempt.id == attempt_id, EvaluationAttempt.evaluation_id == evaluation_id)
            .first()
        )

        if not attempt:
            raise NotFoundError("Evaluation attempt not found")

        # Check if user owns the attempt or has permission
        if attempt.user_id != user.id and user.role not in ["admin", "manager", "instructor"]:
            raise ForbiddenError("You don't have permission to create a learning path for this attempt")

        # Check if learning path already exists for this attempt
        existing_path = (
            self.db.query(LearningPath)
            .filter(LearningPath.evaluation_attempt_id == attempt_id, LearningPath.tenant_id == tenant_id)
            .first()
        )

        if existing_path:
            raise BadRequestError("Learning path already exists for this attempt")

        # Prepare user info
        user_info = {
            "learning_style": user.profile.get("learning_style", "mixed") if hasattr(user, "profile") else "mixed",
            "weekly_hours": user.profile.get("weekly_study_hours", "5-10") if hasattr(user, "profile") else "5-10",
            "experience_level": self._determine_experience_level(user.id),
        }

        # Prepare evaluation info
        evaluation_info = {
            "title": attempt.evaluation.title if hasattr(attempt, "evaluation") else "Değerlendirme",
            "description": attempt.evaluation.description if hasattr(attempt, "evaluation") else "",
            "topics": attempt.evaluation.tags if hasattr(attempt, "evaluation") else [],
        }

        # Generate learning path using AI
        path_data = ai_service.generate_learning_path(insights, user_info, evaluation_info)

        # Create learning path record
        learning_path = LearningPath(
            tenant_id=tenant_id,
            user_id=attempt.user_id,
            evaluation_id=evaluation_id,
            evaluation_attempt_id=attempt_id,
            title=path_data["title"],
            description=path_data["description"],
            objective=path_data["objective"],
            status=LearningPathStatus.PROPOSED.value,
            duration_weeks=path_data["duration_weeks"],
            estimated_hours_per_week=path_data["estimated_hours_per_week"],
            learning_style=path_data["learning_style"],
            difficulty_adjustment=path_data["difficulty_adjustment"],
            ai_insights_summary=path_data["ai_insights_summary"],
            weekly_schedule=path_data["weekly_schedule"],
            resources=path_data["resources"],
            prerequisites=path_data.get("prerequisites", []),
            total_milestones=path_data["total_milestones"],
        )

        self.db.add(learning_path)
        self.db.flush()  # Get ID before creating milestones

        # Create milestones
        for milestone_data in path_data["milestones"]:
            milestone = LearningMilestone(
                tenant_id=tenant_id,
                learning_path_id=learning_path.id,
                title=milestone_data["title"],
                description=milestone_data["description"],
                objective=milestone_data["objective"],
                order_index=milestone_data["order_index"],
                week_number=milestone_data["week_number"],
                estimated_hours=milestone_data["estimated_hours"],
                skill_focus=milestone_data.get("skill_focus", ""),
                resources=milestone_data.get("resources", []),
                activities=milestone_data.get("activities", []),
                assessment_criteria=milestone_data.get("assessment_criteria", []),
                related_topics=milestone_data.get("related_topics", []),
            )
            self.db.add(milestone)

        self.db.commit()

        # Load relationships
        self.db.refresh(learning_path)

        self.logger.info(f"Created learning path {learning_path.id} for attempt {attempt_id}")

        return learning_path

    def get_learning_path(self, path_id: int, tenant_id: int, user: User) -> LearningPath:
        """Get learning path by ID."""
        learning_path = (
            self.db.query(LearningPath).filter(LearningPath.id == path_id, LearningPath.tenant_id == tenant_id).first()
        )

        if not learning_path:
            raise NotFoundError("Learning path not found")

        # Check permissions
        if learning_path.user_id != user.id and user.role not in ["admin", "manager", "instructor"]:
            raise ForbiddenError("You don't have permission to view this learning path")

        return learning_path

    def get_user_learning_paths(
        self, user_id: int, tenant_id: int, filters: Dict[str, Any] = None
    ) -> List[LearningPath]:
        """Get all learning paths for a user."""
        query = self.db.query(LearningPath).filter(LearningPath.user_id == user_id, LearningPath.tenant_id == tenant_id)

        if filters:
            if filters.get("status"):
                query = query.filter(LearningPath.status == filters["status"])
            if filters.get("evaluation_id"):
                query = query.filter(LearningPath.evaluation_id == filters["evaluation_id"])

        return query.order_by(LearningPath.created_at.desc()).all()

    def accept_learning_path(
        self, path_id: int, tenant_id: int, user: User, customization_notes: Optional[str] = None
    ) -> LearningPath:
        """Accept a proposed learning path."""
        learning_path = self.get_learning_path(path_id, tenant_id, user)

        if learning_path.user_id != user.id:
            raise ForbiddenError("Only the owner can accept the learning path")

        if learning_path.status != LearningPathStatus.PROPOSED.value:
            raise BadRequestError(f"Cannot accept learning path in {learning_path.status} status")

        # Update status and acceptance
        learning_path.status = LearningPathStatus.ACCEPTED.value
        learning_path.accepted_by_user = True
        learning_path.accepted_at = datetime.utcnow()

        # Set start and end dates
        learning_path.start_date = datetime.utcnow()
        learning_path.end_date = learning_path.start_date + timedelta(weeks=learning_path.duration_weeks)

        # Add customization notes if provided
        if customization_notes:
            learning_path.customization_notes = customization_notes

        self.db.commit()
        self.db.refresh(learning_path)

        self.logger.info(f"Learning path {path_id} accepted by user {user.id}")

        return learning_path

    def update_learning_path(self, path_id: int, tenant_id: int, user: User, updates: Dict[str, Any]) -> LearningPath:
        """Update learning path details."""
        learning_path = self.get_learning_path(path_id, tenant_id, user)

        # Only owner or instructors can update
        if learning_path.user_id != user.id and user.role not in ["admin", "manager", "instructor"]:
            raise ForbiddenError("You don't have permission to update this learning path")

        # Allowed updates
        allowed_fields = [
            "title",
            "description",
            "objective",
            "estimated_hours_per_week",
            "customization_notes",
            "weekly_schedule",
        ]

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(learning_path, field, value)

        self.db.commit()
        self.db.refresh(learning_path)

        return learning_path

    def update_milestone_progress(
        self, path_id: int, milestone_id: int, tenant_id: int, user: User, progress: float, notes: Optional[str] = None
    ) -> LearningMilestone:
        """Update milestone progress."""
        learning_path = self.get_learning_path(path_id, tenant_id, user)

        if learning_path.user_id != user.id:
            raise ForbiddenError("Only the owner can update milestone progress")

        milestone = (
            self.db.query(LearningMilestone)
            .filter(
                LearningMilestone.id == milestone_id,
                LearningMilestone.learning_path_id == path_id,
                LearningMilestone.tenant_id == tenant_id,
            )
            .first()
        )

        if not milestone:
            raise NotFoundError("Milestone not found")

        # Update progress
        milestone.progress = max(0, min(100, progress))  # Ensure 0-100 range

        # Update status based on progress
        if milestone.progress == 0:
            milestone.status = "pending"
        elif milestone.progress < 100:
            milestone.status = "in_progress"
            if not milestone.started_at:
                milestone.started_at = datetime.utcnow()
        else:
            milestone.status = "completed"
            milestone.completed_at = datetime.utcnow()

        # Add notes if provided
        if notes:
            milestone.user_notes = notes

        # Update learning path overall progress
        self._update_overall_progress(learning_path)

        self.db.commit()
        self.db.refresh(milestone)

        return milestone

    def provide_feedback(
        self, path_id: int, tenant_id: int, user: User, feedback: str, rating: Optional[float] = None
    ) -> LearningPath:
        """Provide feedback on a learning path."""
        learning_path = self.get_learning_path(path_id, tenant_id, user)

        if learning_path.user_id != user.id:
            raise ForbiddenError("Only the owner can provide feedback")

        learning_path.feedback = feedback

        if rating is not None:
            learning_path.rating = max(1, min(5, rating))  # Ensure 1-5 range

        self.db.commit()
        self.db.refresh(learning_path)

        return learning_path

    def _determine_experience_level(self, user_id: int) -> str:
        """Determine user's experience level based on completed evaluations."""
        # Count completed evaluations
        completed_count = (
            self.db.query(EvaluationAttempt)
            .filter(EvaluationAttempt.user_id == user_id, EvaluationAttempt.status == "completed")
            .count()
        )

        if completed_count == 0:
            return "beginner"
        elif completed_count < 5:
            return "intermediate"
        else:
            return "advanced"

    def _update_overall_progress(self, learning_path: LearningPath):
        """Update overall progress based on milestone completion."""
        if not learning_path.milestones:
            return

        total_progress = sum(m.progress for m in learning_path.milestones)
        learning_path.overall_progress = total_progress / len(learning_path.milestones)

        completed_count = sum(1 for m in learning_path.milestones if m.status == "completed")
        learning_path.completed_milestones = completed_count

        # Update status if all milestones are completed
        if completed_count == learning_path.total_milestones:
            learning_path.status = LearningPathStatus.COMPLETED.value

    def suggest_learning_path_updates(
        self, student_id: int, tenant_id: int, requesting_user: User
    ) -> List[LearningPathUpdate]:
        """
        Generate learning path update suggestions based on student profile analysis.

        Args:
            student_id: Student user ID
            tenant_id: Tenant ID
            requesting_user: User making the request

        Returns:
            List of learning path update suggestions
        """
        # Check permissions
        if requesting_user.role not in ["admin", "manager", "instructor", "trainer"]:
            raise ForbiddenError("You don't have permission to suggest learning path updates")

        # Get student's active learning paths
        active_paths = (
            self.db.query(LearningPath)
            .filter(
                LearningPath.user_id == student_id,
                LearningPath.tenant_id == tenant_id,
                LearningPath.status.in_(["accepted", "in_progress"]),
            )
            .all()
        )

        if not active_paths:
            return []

        # Get student profile with AI analysis
        profile_service = StudentProfileService()
        profile = profile_service.get_student_profile(student_id, tenant_id, requesting_user)

        suggestions = []

        # Process each active learning path
        for path in active_paths:
            path_suggestions = self._generate_path_suggestions(path, profile)
            suggestions.extend(path_suggestions)

        return suggestions

    def _generate_path_suggestions(
        self, learning_path: LearningPath, profile: Dict[str, Any]
    ) -> List[LearningPathUpdate]:
        """Generate suggestions for a specific learning path based on student profile."""
        suggestions = []

        ai_analysis = profile.get("ai_analysis", {})
        scores = profile.get("development_scores", {})
        recent_activities = profile.get("recent_activities", {})

        # Determine strategy based on multiple factors
        strategy = self._determine_intervention_strategy(profile)

        # 1. Crisis Intervention Strategy
        if strategy == "crisis_intervention":
            suggestions.append(self._create_crisis_intervention_suggestion(learning_path, profile))

        # 2. Performance Recovery Strategy
        elif strategy == "performance_recovery":
            suggestions.append(self._create_performance_recovery_suggestion(learning_path, profile))

        # 3. Accelerated Learning Strategy
        elif strategy == "accelerated_learning":
            suggestions.append(self._create_advanced_acceleration_suggestion(learning_path, profile))

        # 4. Balanced Development Strategy
        elif strategy == "balanced_development":
            suggestions.append(self._create_balanced_development_suggestion(learning_path, profile))

        # 5. Standard interventions for specific issues
        else:
            # High risk support
            if scores.get("risk_score") == "High":
                suggestions.append(self._create_support_milestone_suggestion(learning_path, ai_analysis, scores))

            # Weakness reinforcement
            weaknesses = ai_analysis.get("weaknesses", [])
            if weaknesses:
                suggestions.append(self._create_reinforcement_suggestion(learning_path, weaknesses, ai_analysis))

            # Critical interventions
            interventions = ai_analysis.get("interventions", [])
            critical_interventions = [i for i in interventions if i.get("priority") == "critical"]
            if critical_interventions:
                suggestions.append(self._create_intervention_based_suggestion(learning_path, critical_interventions))

        # Filter out None values and save to database
        valid_suggestions = [s for s in suggestions if s is not None]

        # Add temporal context to suggestions
        for suggestion in valid_suggestions:
            suggestion.ai_analysis_data["strategy"] = strategy
            suggestion.ai_analysis_data["generated_at"] = datetime.utcnow().isoformat()
            self.db.add(suggestion)

        if valid_suggestions:
            self.db.commit()

        return valid_suggestions

    def _determine_intervention_strategy(self, profile: Dict[str, Any]) -> str:
        """Determine the best intervention strategy based on student profile."""
        scores = profile.get("development_scores", {})
        recent_activities = profile.get("recent_activities", {})
        ai_analysis = profile.get("ai_analysis", {})

        # Calculate days since last activity
        last_activity = recent_activities.get("last_activity_date")
        days_inactive = 999
        if last_activity:
            from datetime import datetime

            try:
                activity_date = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
                days_inactive = (datetime.utcnow() - activity_date.replace(tzinfo=None)).days
            except (ValueError, AttributeError):
                pass

        # Crisis intervention needed
        if scores.get("risk_score") == "High" and scores.get("engagement_score", 0) < 30 and days_inactive > 21:
            return "crisis_intervention"

        # Performance recovery needed
        evaluations = recent_activities.get("recent_evaluations", [])
        if len(evaluations) >= 3:
            recent_scores = [e.get("score", 0) for e in evaluations[:3]]
            if all(recent_scores[i] > recent_scores[i + 1] for i in range(len(recent_scores) - 1)):
                return "performance_recovery"

        # Accelerated learning opportunity
        if scores.get("performance_index", 0) >= 95 and scores.get("completion_rate", 0) >= 90:
            return "accelerated_learning"

        # Balanced development needed
        # This would need skill-level analysis - simplified for now
        if ai_analysis.get("weaknesses") and len(ai_analysis.get("strengths", [])) >= 3:
            return "balanced_development"

        return "standard"

    def _create_support_milestone_suggestion(
        self, learning_path: LearningPath, ai_analysis: Dict[str, Any], scores: Dict[str, Any]
    ) -> Optional[LearningPathUpdate]:
        """Create suggestion for additional support milestones."""
        # Check if similar suggestion already exists
        existing = (
            self.db.query(LearningPathUpdate)
            .filter(
                LearningPathUpdate.learning_path_id == learning_path.id,
                LearningPathUpdate.update_type == "add_milestone",
                LearningPathUpdate.status == "pending",
            )
            .first()
        )

        if existing:
            return None

        support_milestones = []

        # Add motivational support milestone
        if scores.get("engagement_score", 0) < 50:
            support_milestones.append(
                {
                    "title": "Motivasyon ve Hedef Belirleme Çalışması",
                    "description": "Öğrenme motivasyonunu artırmak için kişisel hedefler belirleme",
                    "objective": "Öğrenme motivasyonunu yükseltmek ve net hedefler koymak",
                    "week_number": 1,
                    "estimated_hours": 1.5,
                    "skill_focus": "self_motivation",
                    "activities": [
                        {"title": "Kişisel öğrenme hedefleri belirleme", "duration": "30 dakika"},
                        {"title": "Motivasyon kaynakları keşfi", "duration": "30 dakika"},
                        {"title": "Haftalık ilerleme takip planı oluşturma", "duration": "30 dakika"},
                    ],
                    "resources": [{"type": "video", "title": "Etkili Hedef Belirleme Teknikleri", "url": "#"}],
                }
            )

        # Add basic skills reinforcement
        if ai_analysis.get("weaknesses"):
            support_milestones.append(
                {
                    "title": "Temel Beceri Güçlendirme",
                    "description": "Zayıf olunan alanlarda temel becerileri güçlendirme",
                    "objective": "Temel konularda sağlam bir anlayış oluşturmak",
                    "week_number": 1,
                    "estimated_hours": 3.0,
                    "skill_focus": "fundamentals",
                    "activities": [
                        {"title": "Temel kavramları gözden geçirme", "duration": "1 saat"},
                        {"title": "Pratik alıştırmalar", "duration": "1.5 saat"},
                        {"title": "Mini değerlendirme", "duration": "30 dakika"},
                    ],
                }
            )

        if not support_milestones:
            return None

        return LearningPathUpdate(
            tenant_id=learning_path.tenant_id,
            learning_path_id=learning_path.id,
            update_type="add_milestone",
            source="ai",
            suggested_milestones=support_milestones,
            reason=f"Öğrencinin risk skoru '{scores.get('risk_score')}' ve katılım skoru {scores.get('engagement_score')}. Ek destek adımları öneriliyor.",
            expected_impact="Risk seviyesinde azalma ve motivasyonda artış",
            priority="high",
            ai_analysis_data=ai_analysis,
            student_metrics=scores,
        )

    def _create_reinforcement_suggestion(
        self, learning_path: LearningPath, weaknesses: List[str], ai_analysis: Dict[str, Any]
    ) -> Optional[LearningPathUpdate]:
        """Create suggestion for reinforcing weak areas."""
        reinforcement_milestones = []

        # Create a reinforcement milestone for identified weaknesses
        reinforcement_milestones.append(
            {
                "title": "Zayıf Alanları Güçlendirme Programı",
                "description": f"Tespit edilen zayıf alanlar: {', '.join(weaknesses[:2])}",
                "objective": "Zayıf alanlarda yetkinlik kazanmak",
                "week_number": 2,
                "estimated_hours": 4.0,
                "skill_focus": "weakness_improvement",
                "activities": [
                    {"title": "Detaylı konu anlatımı çalışması", "duration": "1.5 saat"},
                    {"title": "Uygulamalı alıştırmalar", "duration": "2 saat"},
                    {"title": "Akran değerlendirmesi", "duration": "30 dakika"},
                ],
                "resources": [
                    {"type": "document", "title": "Konu Özeti ve Örnekler", "url": "#"},
                    {"type": "practice", "title": "İnteraktif Alıştırmalar", "url": "#"},
                ],
                "assessment_criteria": [
                    "Temel kavramları açıklayabilme",
                    "Pratik problemleri çözebilme",
                    "İlerleme testinde %70+ başarı",
                ],
            }
        )

        return LearningPathUpdate(
            tenant_id=learning_path.tenant_id,
            learning_path_id=learning_path.id,
            update_type="add_milestone",
            source="ai",
            suggested_milestones=reinforcement_milestones,
            reason=f"AI analizi şu zayıf alanları tespit etti: {', '.join(weaknesses[:3])}",
            expected_impact="Zayıf alanlarda %30 performans artışı",
            priority="medium",
            ai_analysis_data=ai_analysis,
        )

    def _create_intervention_based_suggestion(
        self, learning_path: LearningPath, interventions: List[Dict[str, Any]]
    ) -> Optional[LearningPathUpdate]:
        """Create suggestion based on critical interventions."""
        milestone_updates = {}
        new_milestones = []

        for intervention in interventions:
            if intervention.get("type") == "immediate":
                # Adjust current milestones to be easier
                for milestone in learning_path.milestones:
                    if milestone.status != "completed":
                        milestone_updates[milestone.id] = {
                            "estimated_hours": milestone.estimated_hours * 0.75,
                            "activities": (
                                milestone.activities[:2] if len(milestone.activities) > 2 else milestone.activities
                            ),
                        }

                # Add a preparation milestone
                new_milestones.append(
                    {
                        "title": "Hazırlık ve Motivasyon Güçlendirme",
                        "description": intervention.get("description", ""),
                        "objective": "Öğrenmeye hazır hale gelmek",
                        "week_number": 0,
                        "estimated_hours": 2.0,
                        "skill_focus": "preparation",
                        "activities": intervention.get("action_items", []),
                    }
                )

        if not milestone_updates and not new_milestones:
            return None

        return LearningPathUpdate(
            tenant_id=learning_path.tenant_id,
            learning_path_id=learning_path.id,
            update_type="modify_milestone" if milestone_updates else "add_milestone",
            source="system",
            suggested_milestones=new_milestones,
            milestone_updates=milestone_updates,
            reason=f"Kritik müdahale önerisi: {interventions[0].get('title', '')}",
            expected_impact=interventions[0].get("expected_impact", "Öğrenme performansında iyileşme"),
            priority="critical",
            ai_analysis_data={"interventions": interventions},
        )

    def _create_acceleration_suggestion(
        self, learning_path: LearningPath, scores: Dict[str, Any]
    ) -> Optional[LearningPathUpdate]:
        """Create suggestion for accelerating high-performing students."""
        # Add advanced milestones
        advanced_milestones = [
            {
                "title": "İleri Seviye Uygulama Projesi",
                "description": "Öğrenilen konuları birleştiren kapsamlı proje",
                "objective": "Derinlemesine uygulama becerisi kazanmak",
                "week_number": learning_path.duration_weeks,
                "estimated_hours": 6.0,
                "skill_focus": "advanced_application",
                "activities": [
                    {"title": "Proje planlama", "duration": "1 saat"},
                    {"title": "Proje geliştirme", "duration": "4 saat"},
                    {"title": "Sunum ve değerlendirme", "duration": "1 saat"},
                ],
                "assessment_criteria": ["Özgün proje fikri", "Teknik uygulama kalitesi", "Sunum ve dokümantasyon"],
            }
        ]

        return LearningPathUpdate(
            tenant_id=learning_path.tenant_id,
            learning_path_id=learning_path.id,
            update_type="add_milestone",
            source="system",
            suggested_milestones=advanced_milestones,
            reason=f"Öğrenci yüksek performans gösteriyor (Performans: {scores.get('performance_index')}%, Tamamlama: {scores.get('completion_rate')}%)",
            expected_impact="İleri seviye beceri kazanımı ve motivasyon artışı",
            priority="low",
            student_metrics=scores,
        )

    def get_pending_updates(self, learning_path_id: int, tenant_id: int, user: User) -> List[LearningPathUpdate]:
        """Get pending update suggestions for a learning path."""
        # Verify access
        learning_path = self.get_learning_path(learning_path_id, tenant_id, user)

        # Get pending updates
        updates = (
            self.db.query(LearningPathUpdate)
            .filter(
                LearningPathUpdate.learning_path_id == learning_path_id,
                LearningPathUpdate.tenant_id == tenant_id,
                LearningPathUpdate.status == "pending",
            )
            .all()
        )

        # Sort by priority manually
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        updates.sort(key=lambda x: (priority_order.get(x.priority, 4), x.created_at), reverse=True)

        return updates

    def apply_learning_path_update(self, update_id: int, tenant_id: int, user: User) -> LearningPath:
        """Apply an approved learning path update."""
        # Check permissions
        if user.role not in ["admin", "manager", "instructor", "trainer"]:
            raise ForbiddenError("You don't have permission to apply updates")

        # Get update
        update = (
            self.db.query(LearningPathUpdate)
            .filter(LearningPathUpdate.id == update_id, LearningPathUpdate.tenant_id == tenant_id)
            .first()
        )

        if not update:
            raise NotFoundError("Update not found")

        if update.status != "approved":
            raise BadRequestError("Update must be approved before applying")

        # Get learning path
        learning_path = self.db.query(LearningPath).filter(LearningPath.id == update.learning_path_id).first()

        # Apply update based on type
        if update.update_type == "add_milestone":
            self._apply_add_milestone_update(learning_path, update)
        elif update.update_type == "modify_milestone":
            self._apply_modify_milestone_update(learning_path, update)
        elif update.update_type == "obsolete_milestone":
            self._apply_obsolete_milestone_update(learning_path, update)
        elif update.update_type == "reorder":
            self._apply_reorder_update(learning_path, update)

        # Mark update as applied
        update.status = "applied"
        update.applied_at = datetime.utcnow()

        # Update learning path total milestones
        learning_path.total_milestones = len([m for m in learning_path.milestones if m.status != "skipped"])

        self.db.commit()
        self.db.refresh(learning_path)

        return learning_path

    def _apply_add_milestone_update(self, learning_path: LearningPath, update: LearningPathUpdate):
        """Apply add milestone update."""
        for milestone_data in update.suggested_milestones:
            milestone = LearningMilestone(
                tenant_id=learning_path.tenant_id,
                learning_path_id=learning_path.id,
                title=milestone_data["title"],
                description=milestone_data.get("description"),
                objective=milestone_data.get("objective"),
                week_number=milestone_data.get("week_number", 1),
                estimated_hours=milestone_data.get("estimated_hours", 2.0),
                skill_focus=milestone_data.get("skill_focus"),
                activities=milestone_data.get("activities", []),
                resources=milestone_data.get("resources", []),
                assessment_criteria=milestone_data.get("assessment_criteria", []),
                order_index=len(learning_path.milestones),
            )
            self.db.add(milestone)

    def _apply_modify_milestone_update(self, learning_path: LearningPath, update: LearningPathUpdate):
        """Apply modify milestone update."""
        for milestone_id, changes in update.milestone_updates.items():
            milestone = (
                self.db.query(LearningMilestone)
                .filter(
                    LearningMilestone.id == int(milestone_id), LearningMilestone.learning_path_id == learning_path.id
                )
                .first()
            )

            if milestone:
                for key, value in changes.items():
                    if hasattr(milestone, key):
                        setattr(milestone, key, value)

    def _apply_obsolete_milestone_update(self, learning_path: LearningPath, update: LearningPathUpdate):
        """Apply obsolete milestone update."""
        for milestone_id in update.obsolete_milestone_ids:
            milestone = (
                self.db.query(LearningMilestone)
                .filter(LearningMilestone.id == milestone_id, LearningMilestone.learning_path_id == learning_path.id)
                .first()
            )

            if milestone:
                milestone.status = MilestoneStatus.SKIPPED.value

    def _apply_reorder_update(self, learning_path: LearningPath, update: LearningPathUpdate):
        """Apply reorder update."""
        for milestone_id, new_order in update.reorder_map.items():
            milestone = (
                self.db.query(LearningMilestone)
                .filter(
                    LearningMilestone.id == int(milestone_id), LearningMilestone.learning_path_id == learning_path.id
                )
                .first()
            )

            if milestone:
                milestone.order_index = new_order

    def _create_crisis_intervention_suggestion(
        self, learning_path: LearningPath, profile: Dict[str, Any]
    ) -> Optional[LearningPathUpdate]:
        """Create crisis intervention for severely disengaged students."""
        scores = profile.get("development_scores", {})

        crisis_milestones = [
            {
                "title": "🆘 Acil Motivasyon Kurtarma - Adım 1",
                "description": "Öğrenciyle güven inşası ve minimal başlangıç",
                "objective": "Öğrenciyi platforma geri kazandırmak",
                "week_number": 0,
                "estimated_hours": 0.5,
                "skill_focus": "engagement_recovery",
                "activities": [
                    {"title": "15 dakikalık hoş geldin görüşmesi", "duration": "15 dakika"},
                    {"title": "Engelleri dinleme ve anlama", "duration": "10 dakika"},
                    {"title": "İlk hafta için tek bir mini hedef belirleme", "duration": "5 dakika"},
                ],
                "resources": [
                    {"type": "checklist", "title": "Koç Görüşme Rehberi", "url": "#"},
                    {"type": "template", "title": "Motivasyon Formu", "url": "#"},
                ],
                "assessment_criteria": [
                    "Öğrenci görüşmeye katıldı",
                    "En az bir engel tanımlandı",
                    "Bir mini hedef belirlendi",
                ],
            },
            {
                "title": "🌱 Mikro Öğrenme Başlangıcı",
                "description": "Günde 5-10 dakikalık minimal aktiviteler",
                "objective": "Düzenli katılım alışkanlığı oluşturmak",
                "week_number": 1,
                "estimated_hours": 1.0,
                "skill_focus": "habit_formation",
                "activities": [
                    {"title": "Günlük 5 dakikalık mini aktivite", "duration": "5 dakika/gün"},
                    {"title": "Anlık başarı geri bildirimi", "duration": "Anında"},
                    {"title": "Haftalık motivasyon mesajı", "duration": "2 dakika"},
                ],
            },
        ]

        return LearningPathUpdate(
            tenant_id=learning_path.tenant_id,
            learning_path_id=learning_path.id,
            update_type="add_milestone",
            source="system",
            suggested_milestones=crisis_milestones,
            reason=f"🚨 KRİTİK: Öğrenci {profile.get('recent_activities', {}).get('last_activity_date', 'bilinmeyen')} tarihinden beri aktif değil. Katılım skoru: {scores.get('engagement_score', 0)}%",
            expected_impact="2 hafta içinde platforma geri dönüş ve %50 aktivite artışı",
            priority="critical",
            ai_analysis_data={
                "strategy": "crisis_intervention",
                "risk_indicators": {
                    "engagement_score": scores.get("engagement_score", 0),
                    "days_inactive": self._calculate_days_inactive(profile),
                    "risk_score": scores.get("risk_score"),
                },
            },
        )

    def _create_performance_recovery_suggestion(
        self, learning_path: LearningPath, profile: Dict[str, Any]
    ) -> Optional[LearningPathUpdate]:
        """Create performance recovery plan for declining students."""
        evaluations = profile.get("recent_activities", {}).get("recent_evaluations", [])
        recent_scores = [e.get("score", 0) for e in evaluations[:3]] if evaluations else []

        recovery_milestones = [
            {
                "title": "📊 Performans Analizi ve Zorluk Ayarlama",
                "description": "Mevcut içeriğin zorluğunu öğrenci seviyesine uyarlama",
                "objective": "Başarı hissini yeniden kazandırmak",
                "week_number": 1,
                "estimated_hours": 2.0,
                "skill_focus": "confidence_building",
                "activities": [
                    {"title": "Zayıf noktaları belirleme", "duration": "30 dakika"},
                    {"title": "Kolay seviye pratik soruları", "duration": "1 saat"},
                    {"title": "Başarı odaklı mini sınav", "duration": "30 dakika"},
                ],
                "resources": [
                    {"type": "practice", "title": "Temel Seviye Alıştırmalar", "url": "#"},
                    {"type": "video", "title": "Konu Anlatım Videoları", "url": "#"},
                ],
            },
            {
                "title": "🔄 Tekrar ve Pekiştirme Programı",
                "description": "Temel kavramları sağlamlaştırma",
                "objective": "Bilgi boşluklarını doldurmak",
                "week_number": 2,
                "estimated_hours": 3.0,
                "skill_focus": "knowledge_consolidation",
                "activities": [
                    {"title": "Temel kavram haritası oluşturma", "duration": "45 dakika"},
                    {"title": "Adım adım çözümlü örnekler", "duration": "1.5 saat"},
                    {"title": "Akran ile çalışma seansı", "duration": "45 dakika"},
                ],
            },
        ]

        # Also modify existing milestones to reduce complexity
        milestone_updates = {}
        for milestone in learning_path.milestones:
            if milestone.status != "completed":
                milestone_updates[str(milestone.id)] = {
                    "estimated_hours": milestone.estimated_hours * 0.75,
                    "assessment_criteria": ["Temel seviyede yeterlilik"] if milestone.assessment_criteria else [],
                }

        return LearningPathUpdate(
            tenant_id=learning_path.tenant_id,
            learning_path_id=learning_path.id,
            update_type="add_milestone",
            source="system",
            suggested_milestones=recovery_milestones,
            milestone_updates=milestone_updates,
            reason=f"📉 Performans düşüşü tespit edildi. Son 3 değerlendirme: {' → '.join([f'%{s}' for s in recent_scores])}",
            expected_impact="4 hafta içinde performans stabilizasyonu ve özgüven artışı",
            priority="high",
            ai_analysis_data={
                "strategy": "performance_recovery",
                "performance_trend": recent_scores,
                "average_drop": (
                    sum(recent_scores[i] - recent_scores[i + 1] for i in range(len(recent_scores) - 1))
                    / (len(recent_scores) - 1)
                    if len(recent_scores) > 1
                    else 0
                ),
            },
        )

    def _create_advanced_acceleration_suggestion(
        self, learning_path: LearningPath, profile: Dict[str, Any]
    ) -> Optional[LearningPathUpdate]:
        """Create advanced learning opportunities for high performers."""
        scores = profile.get("development_scores", {})

        acceleration_milestones = [
            {
                "title": "🚀 Gerçek Dünya Meydan Okuması",
                "description": "Sektörden gerçek bir problemi çözme projesi",
                "objective": "Teorik bilgiyi pratik uygulamaya dönüştürmek",
                "week_number": learning_path.duration_weeks + 1,
                "estimated_hours": 8.0,
                "skill_focus": "real_world_application",
                "activities": [
                    {"title": "Problem araştırması ve seçimi", "duration": "2 saat"},
                    {"title": "Çözüm tasarımı ve planlama", "duration": "2 saat"},
                    {"title": "Prototip geliştirme", "duration": "3 saat"},
                    {"title": "Sunum ve dokümantasyon", "duration": "1 saat"},
                ],
                "resources": [
                    {"type": "case_study", "title": "Sektör Vaka Çalışmaları", "url": "#"},
                    {"type": "mentorship", "title": "Uzman Mentor Desteği", "url": "#"},
                ],
                "assessment_criteria": [
                    "Özgün problem tanımı",
                    "Yaratıcı çözüm yaklaşımı",
                    "Teknik uygulama kalitesi",
                    "Profesyonel sunum",
                ],
            },
            {
                "title": "🎓 Bilgi Paylaşımı ve Liderlik",
                "description": "Öğrendiğini öğretme ve liderlik geliştirme",
                "objective": "Derin anlayış ve liderlik becerileri kazanmak",
                "week_number": learning_path.duration_weeks + 2,
                "estimated_hours": 4.0,
                "skill_focus": "leadership",
                "activities": [
                    {"title": "Mini workshop içeriği hazırlama", "duration": "2 saat"},
                    {"title": "Akranlara sunum yapma", "duration": "1 saat"},
                    {"title": "Mentor olarak destek verme", "duration": "1 saat"},
                ],
            },
        ]

        return LearningPathUpdate(
            tenant_id=learning_path.tenant_id,
            learning_path_id=learning_path.id,
            update_type="add_milestone",
            source="ai",
            suggested_milestones=acceleration_milestones,
            reason=f"🌟 Olağanüstü performans! Performans: {scores.get('performance_index')}%, Tamamlama: {scores.get('completion_rate')}%",
            expected_impact="İleri seviye uzmanlık, liderlik becerileri ve sektörel hazırlık",
            priority="medium",
            ai_analysis_data={
                "strategy": "accelerated_learning",
                "excellence_indicators": {
                    "performance_index": scores.get("performance_index"),
                    "completion_rate": scores.get("completion_rate"),
                    "average_score": scores.get("average_score"),
                },
            },
        )

    def _create_balanced_development_suggestion(
        self, learning_path: LearningPath, profile: Dict[str, Any]
    ) -> Optional[LearningPathUpdate]:
        """Create balanced development plan for uneven skill distribution."""
        ai_analysis = profile.get("ai_analysis", {})
        strengths = ai_analysis.get("strengths", [])
        weaknesses = ai_analysis.get("weaknesses", [])

        balance_milestones = [
            {
                "title": "⚖️ Beceri Dengeleme Atölyesi",
                "description": f"Zayıf alanlar: {', '.join(weaknesses[:2])}",
                "objective": "Zayıf becerileri güçlü becerilerle desteklemek",
                "week_number": 2,
                "estimated_hours": 4.0,
                "skill_focus": "skill_balance",
                "activities": [
                    {"title": "Zayıf alan temel eğitimi", "duration": "1.5 saat"},
                    {"title": "Güçlü-zayıf alan entegrasyonu", "duration": "1.5 saat"},
                    {"title": "Karma beceri uygulaması", "duration": "1 saat"},
                ],
                "resources": [
                    {"type": "interactive", "title": "Beceri Geliştirme Simülasyonu", "url": "#"},
                    {"type": "peer_learning", "title": "Akran Destek Grubu", "url": "#"},
                ],
            },
            {
                "title": "🔗 Entegre Proje Uygulaması",
                "description": "Tüm becerileri birleştiren kapsamlı proje",
                "objective": "Dengeli beceri kullanımını pekiştirmek",
                "week_number": 3,
                "estimated_hours": 5.0,
                "skill_focus": "integrated_application",
                "activities": [
                    {"title": "Çok yönlü proje tasarımı", "duration": "1 saat"},
                    {"title": "Takım çalışması ve iletişim", "duration": "2 saat"},
                    {"title": "Teknik uygulama ve sunum", "duration": "2 saat"},
                ],
            },
        ]

        return LearningPathUpdate(
            tenant_id=learning_path.tenant_id,
            learning_path_id=learning_path.id,
            update_type="add_milestone",
            source="ai",
            suggested_milestones=balance_milestones,
            reason=f"🎯 Dengesiz gelişim tespit edildi. Güçlü: {len(strengths)} alan, Zayıf: {len(weaknesses)} alan",
            expected_impact="Dengeli beceri profili ve bütünsel gelişim",
            priority="medium",
            ai_analysis_data={
                "strategy": "balanced_development",
                "skill_analysis": {
                    "strong_areas": strengths[:3],
                    "weak_areas": weaknesses[:3],
                    "imbalance_ratio": len(weaknesses) / (len(strengths) + 1),
                },
            },
        )

    def _calculate_days_inactive(self, profile: Dict[str, Any]) -> int:
        """Calculate days since last activity."""
        last_activity = profile.get("recent_activities", {}).get("last_activity_date")
        if not last_activity:
            return 999

        from datetime import datetime

        try:
            activity_date = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
            return (datetime.utcnow() - activity_date.replace(tzinfo=None)).days
        except (ValueError, AttributeError):
            return 999


# Initialize service - create when needed with proper context
# learning_path_service = LearningPathService()
