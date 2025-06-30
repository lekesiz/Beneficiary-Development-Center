"""
Audit logging system for BDC Platform
Provides decorators and utilities for comprehensive audit trail
"""

import time
import json
from functools import wraps
from flask import request, g, current_app
from datetime import datetime
from typing import Optional, Dict, Any, Callable

from app.models.audit_log import AuditLog
from app.extensions import db
from app.core.jwt_utils import get_current_user_id
from app.core.security import get_real_ip

import logging
logger = logging.getLogger(__name__)


def audit_log(action: str, resource_type: str, get_resource_id: Optional[Callable] = None,
              capture_request_data: bool = False, capture_response_data: bool = False,
              risk_factors: Optional[Dict[str, Any]] = None):
    """
    Decorator for automatic audit logging of API endpoints
    
    Args:
        action: Action being performed (e.g., 'create', 'update', 'delete')
        resource_type: Type of resource (e.g., 'user', 'course', 'coach_note')
        get_resource_id: Function to extract resource ID from request/response
        capture_request_data: Whether to capture request payload
        capture_response_data: Whether to capture response data
        risk_factors: Additional risk assessment factors
        
    Usage:
        @audit_log('create', 'coach_note', get_resource_id=lambda: request.json.get('student_id'))
        def create_note():
            # endpoint implementation
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Record start time
            start_time = time.time()
            
            # Initialize audit data
            audit_data = {
                'action': action,
                'resource_type': resource_type,
                'endpoint': request.endpoint,
                'http_method': request.method,
                'ip_address': get_real_ip(),
                'user_agent': request.headers.get('User-Agent'),
                'tenant_id': request.headers.get('X-Tenant-ID'),
                'user_id': None,
                'resource_id': None,
                'details': {},
                'old_values': None,
                'new_values': None,
                'status': 'success',
                'error_message': None,
                'session_id': getattr(g, 'session_id', None),
                'risk_score': 0
            }
            
            # Get current user
            try:
                audit_data['user_id'] = get_current_user_id()
            except:
                pass  # Anonymous request
            
            # Capture request data if requested
            if capture_request_data and request.is_json:
                audit_data['new_values'] = request.get_json()
            
            # Get resource ID if function provided
            if get_resource_id:
                try:
                    audit_data['resource_id'] = str(get_resource_id())
                except:
                    pass
            
            # Capture additional details
            if risk_factors:
                audit_data['details'].update(risk_factors)
            
            # Add query parameters if relevant
            if request.args:
                audit_data['details']['query_params'] = dict(request.args)
            
            try:
                # Execute the original function
                response = f(*args, **kwargs)
                
                # Capture response data if requested and successful
                if capture_response_data and hasattr(response, 'get_json'):
                    try:
                        response_data = response.get_json()
                        if response_data:
                            audit_data['new_values'] = response_data
                    except:
                        pass
                
                # Extract resource ID from response if not already set
                if not audit_data['resource_id'] and hasattr(response, 'get_json'):
                    try:
                        response_data = response.get_json()
                        if response_data and isinstance(response_data, dict):
                            # Try common ID fields
                            for id_field in ['id', 'resource_id', f'{resource_type}_id']:
                                if id_field in response_data:
                                    audit_data['resource_id'] = str(response_data[id_field])
                                    break
                    except:
                        pass
                
                return response
                
            except Exception as e:
                # Log failed operation
                audit_data['status'] = 'failure'
                audit_data['error_message'] = str(e)
                audit_data['details']['exception_type'] = type(e).__name__
                raise
                
            finally:
                # Calculate duration
                end_time = time.time()
                audit_data['duration_ms'] = int((end_time - start_time) * 1000)
                
                # Calculate risk score
                audit_data['risk_score'] = calculate_risk_score(audit_data)
                
                # Create audit log entry
                try:
                    log_entry = AuditLog.create_log(**audit_data)
                    db.session.add(log_entry)
                    db.session.commit()
                except Exception as e:
                    # Don't fail the request if audit logging fails
                    logger.error(f"Failed to create audit log: {str(e)}")
                    try:
                        db.session.rollback()
                    except:
                        pass
        
        return decorated_function
    return decorator


def log_security_event(event_type: str, details: Dict[str, Any], 
                      user_id: Optional[int] = None, risk_score: int = 50):
    """
    Log security-related events
    
    Args:
        event_type: Type of security event (e.g., 'failed_login', 'privilege_escalation')
        details: Event details and context
        user_id: User ID if applicable
        risk_score: Risk assessment score (0-100)
    """
    try:
        audit_data = {
            'action': event_type,
            'resource_type': 'security',
            'user_id': user_id,
            'tenant_id': request.headers.get('X-Tenant-ID') if request else None,
            'endpoint': request.endpoint if request else None,
            'http_method': request.method if request else None,
            'ip_address': get_real_ip() if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'details': details,
            'status': 'success',
            'risk_score': risk_score,
            'timestamp': datetime.utcnow()
        }
        
        log_entry = AuditLog.create_log(**audit_data)
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Failed to log security event: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass


def log_data_access(resource_type: str, resource_id: str, action: str = 'read',
                   user_id: Optional[int] = None, additional_details: Optional[Dict] = None):
    """
    Log data access events for sensitive resources
    
    Args:
        resource_type: Type of resource accessed
        resource_id: ID of the resource
        action: Action performed (read, export, etc.)
        user_id: User performing the action
        additional_details: Additional context
    """
    details = additional_details or {}
    details['data_access'] = True
    
    try:
        audit_data = {
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'user_id': user_id or get_current_user_id(),
            'tenant_id': request.headers.get('X-Tenant-ID') if request else None,
            'endpoint': request.endpoint if request else None,
            'http_method': request.method if request else None,
            'ip_address': get_real_ip() if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'details': details,
            'status': 'success',
            'risk_score': 15,  # Data access has moderate risk
            'timestamp': datetime.utcnow()
        }
        
        log_entry = AuditLog.create_log(**audit_data)
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Failed to log data access: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass


def calculate_risk_score(audit_data: Dict[str, Any]) -> int:
    """
    Calculate risk score for an audit event
    
    Args:
        audit_data: Audit event data
        
    Returns:
        Risk score (0-100)
    """
    try:
        # Get user role
        user_role = getattr(g, 'current_user_role', 'unknown')
        
        # Check for IP changes (simplified - would need session tracking)
        ip_change = False
        
        # Check for time anomalies (simplified - would need user behavior analysis)
        time_anomaly = False
        
        # Check for bulk operations
        bulk_operation = audit_data.get('details', {}).get('bulk_operation', False)
        
        # Use the model's risk calculation
        return AuditLog.calculate_risk_score(
            action=audit_data['action'],
            resource_type=audit_data['resource_type'],
            user_role=user_role,
            ip_change=ip_change,
            time_anomaly=time_anomaly,
            bulk_operation=bulk_operation
        )
    except Exception as e:
        logger.warning(f"Failed to calculate risk score: {str(e)}")
        return 25  # Default moderate risk


def get_resource_id_from_url(param_name: str = 'id'):
    """
    Helper function to extract resource ID from URL parameters
    
    Args:
        param_name: Name of the URL parameter containing the ID
        
    Returns:
        Function that extracts the resource ID
    """
    def extractor():
        from flask import request
        return request.view_args.get(param_name)
    
    return extractor


def get_resource_id_from_json(field_name: str = 'id'):
    """
    Helper function to extract resource ID from JSON payload
    
    Args:
        field_name: Name of the JSON field containing the ID
        
    Returns:
        Function that extracts the resource ID
    """
    def extractor():
        if request.is_json:
            data = request.get_json()
            return data.get(field_name) if data else None
        return None
    
    return extractor


# Pre-configured decorators for common operations
def audit_create(resource_type: str, get_resource_id: Optional[Callable] = None):
    """Audit decorator for create operations"""
    return audit_log('create', resource_type, get_resource_id, 
                    capture_request_data=True, capture_response_data=True)


def audit_read(resource_type: str, get_resource_id: Optional[Callable] = None):
    """Audit decorator for read operations"""
    return audit_log('read', resource_type, get_resource_id)


def audit_update(resource_type: str, get_resource_id: Optional[Callable] = None):
    """Audit decorator for update operations"""
    return audit_log('update', resource_type, get_resource_id,
                    capture_request_data=True, capture_response_data=True)


def audit_delete(resource_type: str, get_resource_id: Optional[Callable] = None):
    """Audit decorator for delete operations"""
    return audit_log('delete', resource_type, get_resource_id,
                    risk_factors={'high_risk_operation': True})


# Sensitive operation decorators
def audit_auth(action: str):
    """Audit decorator for authentication operations"""
    return audit_log(action, 'auth', capture_request_data=True,
                    risk_factors={'authentication_event': True})


def audit_admin(action: str, resource_type: str):
    """Audit decorator for admin operations"""
    return audit_log(action, resource_type, capture_request_data=True,
                    risk_factors={'admin_operation': True})


def audit_export(resource_type: str):
    """Audit decorator for data export operations"""
    return audit_log('export', resource_type, capture_request_data=True,
                    risk_factors={'data_export': True, 'high_risk_operation': True})