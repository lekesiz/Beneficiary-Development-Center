"""
Notification service for real-time notifications via WebSocket
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from sqlalchemy.orm import Session
import logging
import json
from enum import Enum

from app.models.user import User
from app.models.base import db
from app.core.socketio import emit_to_user, emit_to_role, emit_to_tenant, socketio
from app.core.database import get_db

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationCategory(Enum):
    """Notification categories"""

    SYSTEM = "system"
    PROGRAM = "program"
    COURSE = "course"
    ENROLLMENT = "enrollment"
    EVALUATION = "evaluation"
    ANNOUNCEMENT = "announcement"
    ACHIEVEMENT = "achievement"
    REMINDER = "reminder"


class NotificationService:
    """Service for managing real-time notifications"""

    def __init__(self, db_session: Session = None):
        self.db = db_session or db.session

    def send_notification_to_user(
        self,
        user_id: int,
        event: str,
        data: Dict[str, Any],
        category: Union[NotificationCategory, str] = NotificationCategory.SYSTEM,
        priority: Union[NotificationPriority, str] = NotificationPriority.NORMAL,
    ) -> bool:
        """
        Send a notification to a specific user via WebSocket

        Args:
            user_id: ID of the user to notify
            event: Name of the event/notification type
            data: Notification data payload
            category: Notification category
            priority: Notification priority level

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Verify user exists
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found for notification")
                return False

            # Convert enums to strings if needed
            if isinstance(category, NotificationCategory):
                category = category.value
            if isinstance(priority, NotificationPriority):
                priority = priority.value

            # Add metadata to notification
            notification_data = {
                "id": f"{datetime.utcnow().timestamp()}_{user_id}_{event}",
                "event": event,
                "category": category,
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
                "user_id": user_id,
                "read": False,
            }

            # Send via WebSocket
            emit_to_user(user_id, "notification", notification_data)

            logger.info(f"Notification sent to user {user_id}: {event} (category: {category}, priority: {priority})")
            return True

        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {str(e)}")
            return False

    def send_notification_to_users(self, user_ids: List[int], event_name: str, data: Dict[str, Any]) -> Dict[int, bool]:
        """
        Send notifications to multiple users

        Args:
            user_ids: List of user IDs to notify
            event_name: Name of the event/notification type
            data: Notification data payload

        Returns:
            dict: Dictionary mapping user_id to success status
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = self.send_notification_to_user(user_id, event_name, data)
        return results

    def send_notification_to_role(self, tenant_id: int, role: str, event_name: str, data: Dict[str, Any]) -> bool:
        """
        Send a notification to all users with a specific role in a tenant

        Args:
            tenant_id: Tenant ID
            role: User role
            event_name: Name of the event/notification type
            data: Notification data payload

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Add metadata to notification
            notification_data = {
                "event": event_name,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
                "role": role,
                "tenant_id": tenant_id,
            }

            # Send via WebSocket
            emit_to_role(tenant_id, role, "notification", notification_data)

            logger.info(f"Notification sent to role {role} in tenant {tenant_id}: {event_name}")
            return True

        except Exception as e:
            logger.error(f"Error sending notification to role {role}: {str(e)}")
            return False

    def send_notification_to_tenant(
        self,
        tenant_id: int,
        event: str,
        data: Dict[str, Any],
        category: Union[NotificationCategory, str] = NotificationCategory.SYSTEM,
        priority: Union[NotificationPriority, str] = NotificationPriority.NORMAL,
    ) -> bool:
        """
        Send a notification to all users in a tenant

        Args:
            tenant_id: Tenant ID
            event: Name of the event/notification type
            data: Notification data payload
            category: Notification category
            priority: Notification priority level

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Convert enums to strings if needed
            if isinstance(category, NotificationCategory):
                category = category.value
            if isinstance(priority, NotificationPriority):
                priority = priority.value

            # Add metadata to notification
            notification_data = {
                "id": f"{datetime.utcnow().timestamp()}_tenant_{tenant_id}_{event}",
                "event": event,
                "category": category,
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
                "tenant_id": tenant_id,
                "read": False,
            }

            # Send via WebSocket
            emit_to_tenant(tenant_id, "notification", notification_data)

            logger.info(
                f"Notification sent to tenant {tenant_id}: {event} (category: {category}, priority: {priority})"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending notification to tenant {tenant_id}: {str(e)}")
            return False

    def notify_program_created(self, program_id: int, program_title: str, created_by_id: int, tenant_id: int):
        """Notify relevant users about a new program"""
        # Notify the creator
        self.send_notification_to_user(
            created_by_id,
            "program_created",
            {
                "program_id": program_id,
                "program_title": program_title,
                "message": f"Yeni bir program oluşturdunuz: {program_title}",
                "action_url": f"/programs/{program_id}",
            },
            category=NotificationCategory.PROGRAM,
            priority=NotificationPriority.NORMAL,
        )

        # Notify managers and admins (except the creator)
        try:
            db_session = next(get_db())
            managers_admins = (
                db_session.query(User)
                .filter(
                    User.tenant_id == tenant_id,
                    User.role.in_(["manager", "admin"]),
                    User.id != created_by_id,
                    User.is_active.is_(True),
                )
                .all()
            )

            for user in managers_admins:
                self.send_notification_to_user(
                    user.id,
                    "program_created",
                    {
                        "program_id": program_id,
                        "program_title": program_title,
                        "created_by": created_by_id,
                        "message": f"Yeni program oluşturuldu: {program_title}",
                        "action_url": f"/programs/{program_id}",
                    },
                    category=NotificationCategory.PROGRAM,
                    priority=NotificationPriority.NORMAL,
                )
            db_session.close()
        except Exception as e:
            logger.error(f"Error notifying managers/admins about program creation: {str(e)}")

    def notify_enrollment_created(
        self,
        enrollment_id: int,
        beneficiary_name: str,
        program_title: str,
        beneficiary_id: int,
        instructor_ids: List[int],
        tenant_id: int,
    ):
        """Notify relevant users about a new enrollment"""
        # Notify the beneficiary
        self.send_notification_to_user(
            beneficiary_id,
            "enrollment_created",
            {
                "enrollment_id": enrollment_id,
                "program_title": program_title,
                "message": f"{program_title} programına kaydınız oluşturuldu",
            },
        )

        # Notify instructors
        for instructor_id in instructor_ids:
            self.send_notification_to_user(
                instructor_id,
                "new_student_enrolled",
                {
                    "enrollment_id": enrollment_id,
                    "beneficiary_name": beneficiary_name,
                    "program_title": program_title,
                    "message": f"{beneficiary_name} {program_title} programına kaydoldu",
                },
            )

    def notify_evaluation_completed(
        self,
        attempt_id: int,
        evaluation_title: str,
        user_id: int,
        passed: bool,
        score: float,
        instructor_ids: List[int],
    ):
        """Notify about evaluation completion"""
        # Notify the student
        status = "geçtiniz" if passed else "kaldınız"
        self.send_notification_to_user(
            user_id,
            "evaluation_completed",
            {
                "attempt_id": attempt_id,
                "evaluation_title": evaluation_title,
                "passed": passed,
                "score": score,
                "message": f"{evaluation_title} değerlendirmesini tamamladınız. Puan: {score:.1f}% - {status}",
            },
        )

        # Notify instructors
        for instructor_id in instructor_ids:
            self.send_notification_to_user(
                instructor_id,
                "student_evaluation_completed",
                {
                    "attempt_id": attempt_id,
                    "evaluation_title": evaluation_title,
                    "student_id": user_id,
                    "passed": passed,
                    "score": score,
                    "message": f"Bir öğrenci {evaluation_title} değerlendirmesini tamamladı",
                },
            )

    def broadcast_announcement(
        self, tenant_id: int, title: str, message: str, priority: str = "normal", roles: Optional[List[str]] = None
    ):
        """
        Broadcast an announcement to tenant or specific roles

        Args:
            tenant_id: Tenant ID
            title: Announcement title
            message: Announcement message
            priority: Priority level (low, normal, high, urgent)
            roles: Optional list of roles to target
        """
        announcement_data = {"title": title, "message": message, "priority": priority, "type": "announcement"}

        if roles:
            # Send to specific roles
            for role in roles:
                self.send_notification_to_role(tenant_id, role, "announcement", announcement_data)
        else:
            # Send to entire tenant
            self.send_notification_to_tenant(tenant_id, "announcement", announcement_data)


# Create a singleton instance
# notification_service = NotificationService()  # Should be instantiated in request context


# Helper functions for common notifications
def notify_user(user_id: int, event: str, message: str, **kwargs):
    """Simple helper to send a notification to a user"""
    data = {"message": message, **kwargs}
    notification_service = NotificationService()
    return notification_service.send_notification_to_user(user_id, event, data)


def notify_tenant(tenant_id: int, event: str, message: str, **kwargs):
    """Simple helper to send a notification to a tenant"""
    data = {"message": message, **kwargs}
    notification_service = NotificationService()
    return notification_service.send_notification_to_tenant(tenant_id, event, data)
