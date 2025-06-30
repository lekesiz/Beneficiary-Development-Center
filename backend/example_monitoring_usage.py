"""
Example usage of monitoring and logging features in BDC platform
"""

from flask import Flask, request
from app.core.monitoring import monitor_performance, PerformanceMonitor, track_business_event
from app.core.logging_config import security_logger, performance_logger, business_logger
import time


def example_security_logging():
    """Examples of security event logging"""
    
    # Log successful login
    security_logger.log_login_attempt(
        email="user@example.com",
        success=True,
        ip_address="192.168.1.100",
        tenant_id=1
    )
    
    # Log failed login
    security_logger.log_login_attempt(
        email="hacker@evil.com",
        success=False,
        ip_address="10.0.0.1",
        tenant_id=1,
        reason="Invalid credentials"
    )
    
    # Log permission denied
    security_logger.log_permission_denied(
        user_id=123,
        resource="financial_reports",
        action="delete",
        required_permission="admin"
    )
    
    # Log suspicious activity
    security_logger.log_suspicious_activity(
        user_id=456,
        activity_type="rapid_api_calls",
        details={"requests_per_minute": 500, "endpoints": ["/api/v1/users", "/api/v1/beneficiaries"]},
        ip_address="192.168.1.50"
    )
    
    # Log sensitive data access
    security_logger.log_data_access(
        user_id=789,
        resource_type="beneficiary",
        resource_id=1001,
        action="export"
    )


def example_performance_logging():
    """Examples of performance monitoring"""
    
    # Log slow database query
    performance_logger.log_slow_query(
        query="SELECT * FROM beneficiaries WHERE status = ? AND created_at > ?",
        duration=2.5,
        params={"status": "active", "created_at": "2024-01-01"}
    )
    
    # Log slow HTTP request
    performance_logger.log_slow_request(
        method="GET",
        path="/api/v1/reports/generate",
        duration=5.2,
        status_code=200
    )
    
    # Log resource usage
    performance_logger.log_resource_usage(
        cpu_percent=75.5,
        memory_percent=82.3,
        disk_percent=45.0
    )


def example_business_logging():
    """Examples of business event logging"""
    
    # Log user registration
    business_logger.log_user_registration(
        user_id=1234,
        email="newuser@example.com",
        role="student",
        tenant_id=1
    )
    
    # Log enrollment
    business_logger.log_enrollment(
        user_id=1234,
        program_id=10,
        course_id=25
    )
    
    # Log evaluation completion
    business_logger.log_evaluation_completed(
        user_id=1234,
        evaluation_id=50,
        score=85.5,
        passed=True
    )
    
    # Log milestone completion
    business_logger.log_milestone_completed(
        user_id=1234,
        milestone_id=100,
        learning_path_id=15
    )


# Example using performance monitoring decorator
@monitor_performance(threshold_ms=100)
def process_large_dataset(data):
    """Example function with performance monitoring"""
    # Simulate processing
    time.sleep(0.2)  # This will trigger a warning
    return len(data)


# Example using performance context manager
def batch_processing_example():
    """Example of monitoring code blocks"""
    
    with PerformanceMonitor("data_import", threshold_ms=1000):
        # Simulate data import
        for i in range(100):
            time.sleep(0.01)
    
    with PerformanceMonitor("data_validation", threshold_ms=500):
        # Simulate validation
        time.sleep(0.3)


# Example tracking business events
def track_user_journey():
    """Example of tracking business events"""
    
    # Track enrollment
    track_business_event(
        "user_enrolled",
        user_id=1234,
        program_id=10,
        enrollment_type="self_service"
    )
    
    # Track progress
    track_business_event(
        "milestone_started",
        user_id=1234,
        milestone_id=100,
        learning_path_id=15
    )
    
    # Track achievement
    track_business_event(
        "certification_earned",
        user_id=1234,
        certification_id=500,
        score=92.5
    )


# Example API endpoint with comprehensive monitoring
def monitored_api_endpoint():
    """Example of a fully monitored API endpoint"""
    
    # This would be in your Flask route
    @monitor_performance(threshold_ms=200)
    def create_beneficiary():
        # Log the API call
        business_logger.logger.info(
            "Creating new beneficiary",
            extra={
                "endpoint": "/api/v1/beneficiaries",
                "method": "POST",
                "user_id": 123,  # from JWT
                "tenant_id": 1
            }
        )
        
        # Check permissions
        if not user_has_permission("create_beneficiary"):
            security_logger.log_permission_denied(
                user_id=123,
                resource="beneficiaries",
                action="create",
                required_permission="create_beneficiary"
            )
            return {"error": "Permission denied"}, 403
        
        # Process request with monitoring
        with PerformanceMonitor("beneficiary_creation", threshold_ms=500):
            # Create beneficiary
            beneficiary = create_beneficiary_in_db()
            
            # Track business event
            track_business_event(
                "beneficiary_created",
                beneficiary_id=beneficiary.id,
                created_by=123,
                tenant_id=1
            )
            
            # Log successful creation
            business_logger.logger.info(
                "Beneficiary created successfully",
                extra={
                    "beneficiary_id": beneficiary.id,
                    "user_id": 123,
                    "duration_ms": 450
                }
            )
        
        return {"id": beneficiary.id}, 201


# Example scheduled monitoring task
def system_health_check():
    """Example of a scheduled health monitoring task"""
    import psutil
    
    # Get system metrics
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Log system health
    performance_logger.log_resource_usage(
        cpu_percent=cpu,
        memory_percent=memory.percent,
        disk_percent=disk.percent
    )
    
    # Check thresholds and alert if needed
    if cpu > 90:
        performance_logger.logger.critical(
            "CPU usage critical",
            extra={
                "cpu_percent": cpu,
                "threshold": 90,
                "action": "scale_up_required"
            }
        )
    
    if memory.percent > 85:
        performance_logger.logger.warning(
            "Memory usage high",
            extra={
                "memory_percent": memory.percent,
                "available_mb": memory.available / 1024 / 1024,
                "threshold": 85
            }
        )


if __name__ == "__main__":
    print("Running monitoring examples...")
    
    # Run examples
    example_security_logging()
    example_performance_logging()
    example_business_logging()
    
    # Test performance monitoring
    process_large_dataset([1, 2, 3, 4, 5])
    batch_processing_example()
    
    # Track business events
    track_user_journey()
    
    # System health check
    system_health_check()
    
    print("Monitoring examples completed!")
    print("Check the logs directory for output")