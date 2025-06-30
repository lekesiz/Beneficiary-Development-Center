"""
Notifications management API endpoints
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.user import User
from app.models.notification import Notification
from app.core.jwt_utils import get_current_user_id
from app.core.decorators import require_permission
from app.core.audit import audit_create, audit_update, audit_delete, audit_read
from app.core.rate_limiting import api_rate_limit
from app.utils.response import success_response, error_response
from app.services.notification_service import NotificationService
from sqlalchemy import desc, and_

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/v1/notifications")


@notifications_bp.route("", methods=["GET"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_read('notifications_list')
def get_notifications():
    """Get user's notifications with pagination and filtering"""
    try:
        user_id = get_current_user_id()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        category = request.args.get('category')
        priority = request.args.get('priority')
        
        # Build query
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        if category:
            query = query.filter_by(category=category)
            
        if priority:
            query = query.filter_by(priority=priority)
        
        # Order by creation date (newest first)
        query = query.order_by(desc(Notification.created_at))
        
        # Paginate
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        notifications = [notification.to_dict() for notification in paginated.items]
        
        # Get unread count
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return success_response({
            'notifications': notifications,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_prev': paginated.has_prev,
                'has_next': paginated.has_next
            },
            'unread_count': unread_count
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch notifications: {str(e)}', 500)


@notifications_bp.route("/unread-count", methods=["GET"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_read('notifications_unread_count')
def get_unread_count():
    """Get unread notification count for the current user"""
    try:
        user_id = get_current_user_id()
        
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return success_response({
            'unread_count': unread_count
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch unread count: {str(e)}', 500)


@notifications_bp.route("/<int:notification_id>/read", methods=["PUT"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_update('notification_read', lambda: request.view_args.get('notification_id'))
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    try:
        user_id = get_current_user_id()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if not notification:
            return error_response('Notification not found', 404)
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
        
        return success_response({
            'message': 'Notification marked as read',
            'notification': notification.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to mark notification as read: {str(e)}', 500)


@notifications_bp.route("/mark-all-read", methods=["PUT"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_update('notifications_mark_all_read')
def mark_all_notifications_read():
    """Mark all user's notifications as read"""
    try:
        user_id = get_current_user_id()
        
        # Update all unread notifications for the user
        updated_count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        
        db.session.commit()
        
        return success_response({
            'message': f'{updated_count} notifications marked as read',
            'updated_count': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to mark all notifications as read: {str(e)}', 500)


@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_delete('notification', lambda: request.view_args.get('notification_id'))
def delete_notification(notification_id):
    """Delete a specific notification"""
    try:
        user_id = get_current_user_id()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if not notification:
            return error_response('Notification not found', 404)
        
        db.session.delete(notification)
        db.session.commit()
        
        return success_response({
            'message': 'Notification deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete notification: {str(e)}', 500)


@notifications_bp.route("/batch-delete", methods=["POST"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_delete('notifications_batch')
def batch_delete_notifications():
    """Delete multiple notifications"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        if not data or 'notification_ids' not in data:
            return error_response('notification_ids is required', 400)
        
        notification_ids = data['notification_ids']
        if not isinstance(notification_ids, list):
            return error_response('notification_ids must be a list', 400)
        
        # Delete notifications belonging to the user
        deleted_count = Notification.query.filter(
            and_(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id
            )
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        return success_response({
            'message': f'{deleted_count} notifications deleted',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete notifications: {str(e)}', 500)


@notifications_bp.route("/settings", methods=["GET"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_read('notification_settings')
def get_notification_settings():
    """Get user's notification settings"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        # Get notification preferences (this would extend the user model)
        # For now, return default settings
        settings = {
            'email_notifications': True,
            'push_notifications': True,
            'categories': {
                'program_updates': True,
                'evaluation_reminders': True,
                'achievement_notifications': True,
                'coach_messages': True,
                'system_alerts': True
            },
            'frequency': {
                'immediate': True,
                'daily_digest': False,
                'weekly_digest': False
            },
            'quiet_hours': {
                'enabled': False,
                'start_time': '22:00',
                'end_time': '08:00'
            }
        }
        
        return success_response({'settings': settings})
        
    except Exception as e:
        return error_response(f'Failed to fetch notification settings: {str(e)}', 500)


@notifications_bp.route("/settings", methods=["PUT"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_update('notification_settings')
def update_notification_settings():
    """Update user's notification settings"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return error_response('Settings data is required', 400)
        
        # In a real implementation, this would update the user's notification preferences
        # For now, just return success
        
        return success_response({
            'message': 'Notification settings updated successfully',
            'settings': data
        })
        
    except Exception as e:
        return error_response(f'Failed to update notification settings: {str(e)}', 500)


@notifications_bp.route("/test", methods=["POST"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit("5 per hour")
@audit_create('test_notification')
def send_test_notification():
    """Send a test notification to verify the system is working"""
    try:
        user_id = get_current_user_id()
        data = request.get_json() or {}
        
        # Create test notification
        notification = Notification(
            user_id=user_id,
            title="Test Notification",
            message=data.get('message', 'This is a test notification to verify the system is working correctly.'),
            category='system',
            priority='normal',
            tenant_id=request.headers.get('X-Tenant-ID')
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Also send real-time notification if available
        try:
            NotificationService.send_notification(
                user_id=user_id,
                title="Test Notification",
                message=notification.message,
                category='system'
            )
        except Exception as realtime_error:
            # Real-time notification failed, but persist notification succeeded
            pass
        
        return success_response({
            'message': 'Test notification sent successfully',
            'notification': notification.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to send test notification: {str(e)}', 500)


@notifications_bp.route("/summary", methods=["GET"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_read('notifications_summary')
def get_notifications_summary():
    """Get summary of user's notifications"""
    try:
        user_id = get_current_user_id()
        
        # Get counts by category and status
        total_count = Notification.query.filter_by(user_id=user_id).count()
        unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        
        # Count by priority
        priority_counts = {}
        for priority in ['low', 'normal', 'high', 'urgent']:
            count = Notification.query.filter_by(
                user_id=user_id,
                priority=priority,
                is_read=False
            ).count()
            if count > 0:
                priority_counts[priority] = count
        
        # Count by category  
        category_counts = {}
        categories = db.session.query(Notification.category).filter_by(
            user_id=user_id,
            is_read=False
        ).distinct().all()
        
        for (category,) in categories:
            count = Notification.query.filter_by(
                user_id=user_id,
                category=category,
                is_read=False
            ).count()
            category_counts[category] = count
        
        # Recent notifications (last 5)
        recent_notifications = Notification.query.filter_by(
            user_id=user_id
        ).order_by(desc(Notification.created_at)).limit(5).all()
        
        return success_response({
            'summary': {
                'total_notifications': total_count,
                'unread_notifications': unread_count,
                'priority_breakdown': priority_counts,
                'category_breakdown': category_counts
            },
            'recent_notifications': [n.to_dict() for n in recent_notifications]
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch notifications summary: {str(e)}', 500)