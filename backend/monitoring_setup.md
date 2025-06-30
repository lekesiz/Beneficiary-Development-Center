# BDC Platform Monitoring and Logging Setup

## Overview

This document describes the comprehensive monitoring and logging setup for the BDC platform, including structured logging, metrics collection, and observability features.

## Components

### 1. Structured Logging

The platform uses structured JSON logging for better observability and log analysis.

#### Features:
- JSON formatted logs for easy parsing
- Request ID tracking across all logs
- User and tenant context in logs
- Specialized loggers for different concerns:
  - **Security Logger**: Login attempts, permission denials, suspicious activities
  - **Performance Logger**: Slow queries, slow requests, resource usage
  - **Business Event Logger**: User registrations, enrollments, completions

#### Configuration:
```python
# In your app initialization
from app.core.logging_config import setup_logging
setup_logging(app)
```

#### Log Files:
- `logs/app.log` - General application logs
- `logs/errors.log` - Error logs only
- `logs/access.log` - HTTP access logs
- `logs/security.log` - Security-related events

### 2. Prometheus Metrics

The platform exposes Prometheus-compatible metrics at `/metrics` endpoint.

#### Available Metrics:
- `bdc_http_requests_total` - Total HTTP requests by method, endpoint, and status
- `bdc_http_request_duration_seconds` - Request duration histogram
- `bdc_active_users` - Currently active users gauge
- `bdc_database_connections` - Active database connections
- `bdc_cpu_percent` - CPU usage percentage
- `bdc_memory_percent` - Memory usage percentage

#### Setup:
```bash
# Install prometheus client
pip install prometheus-client
```

### 3. Health Check Endpoints

Multiple health check endpoints for different monitoring needs:

- `/health` - Basic health check
- `/health/detailed` - Detailed health with service checks
- `/health/liveness` - Kubernetes liveness probe
- `/health/readiness` - Kubernetes readiness probe

### 4. Performance Monitoring

#### Request Monitoring:
- Automatic tracking of slow requests (>1 second)
- Request duration headers (`X-Response-Time`)
- Request ID tracking (`X-Request-ID`)

#### Database Query Monitoring:
```python
from app.core.monitoring import log_database_queries
log_database_queries()  # Enable SQL query logging
```

#### Performance Decorators:
```python
from app.core.monitoring import monitor_performance

@monitor_performance(threshold_ms=500)
def slow_function():
    # Function will log warning if takes >500ms
    pass
```

## Integration Examples

### 1. Security Event Logging

```python
from app.core.logging_config import security_logger

# Log login attempt
security_logger.log_login_attempt(
    email="user@example.com",
    success=True,
    ip_address="192.168.1.1",
    tenant_id=1
)

# Log permission denied
security_logger.log_permission_denied(
    user_id=123,
    resource="beneficiaries",
    action="delete",
    required_permission="admin"
)
```

### 2. Business Event Tracking

```python
from app.core.logging_config import business_logger

# Log user registration
business_logger.log_user_registration(
    user_id=456,
    email="newuser@example.com",
    role="student",
    tenant_id=1
)

# Log evaluation completion
business_logger.log_evaluation_completed(
    user_id=456,
    evaluation_id=789,
    score=85.5,
    passed=True
)
```

### 3. Performance Monitoring

```python
from app.core.monitoring import PerformanceMonitor

# Monitor code block performance
with PerformanceMonitor("data_processing", threshold_ms=1000):
    # Code that might be slow
    process_large_dataset()
```

## Deployment Configuration

### Environment Variables

```bash
# Logging level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# OpenTelemetry (if using)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=bdc-backend
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  app:
    image: bdc-backend
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bdc-backend'
    static_configs:
      - targets: ['app:5001']
    metrics_path: '/metrics'
```

## Monitoring Dashboards

### Grafana Dashboard Queries

1. **Request Rate**:
```promql
rate(bdc_http_requests_total[5m])
```

2. **Error Rate**:
```promql
rate(bdc_http_requests_total{status=~"5.."}[5m])
```

3. **Response Time (95th percentile)**:
```promql
histogram_quantile(0.95, rate(bdc_http_request_duration_seconds_bucket[5m]))
```

4. **Active Users**:
```promql
bdc_active_users
```

## Alerting Rules

### Prometheus Alert Examples

```yaml
groups:
  - name: bdc_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(bdc_http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          
      - alert: SlowRequests
        expr: histogram_quantile(0.95, rate(bdc_http_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: Slow request performance
```

## Log Analysis

### Example Log Queries (for ELK/CloudWatch/etc)

1. **Failed Login Attempts**:
```json
{
  "event_type": "login_attempt",
  "success": false
}
```

2. **Slow Queries**:
```json
{
  "event_type": "slow_query",
  "duration": { "$gt": 1.0 }
}
```

3. **Security Events by User**:
```json
{
  "logger": "app.security",
  "user_id": 123
}
```

## Best Practices

1. **Use Request IDs**: Always include request ID in logs for tracing
2. **Log Security Events**: Track all authentication and authorization events
3. **Monitor Performance**: Set up alerts for slow requests and queries
4. **Business Metrics**: Track key business events for analytics
5. **Regular Reviews**: Review logs and metrics regularly
6. **Retention Policy**: Set appropriate log retention (e.g., 30 days)

## Troubleshooting

### Common Issues

1. **Missing Metrics**: Ensure prometheus-client is installed
2. **Log Files Not Created**: Check logs directory permissions
3. **High Memory Usage**: Adjust log rotation settings
4. **Missing Request Context**: Ensure middleware is properly configured

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export FLASK_ENV=development
```

## Future Enhancements

1. **Distributed Tracing**: Integrate OpenTelemetry for full tracing
2. **APM Integration**: Add Application Performance Monitoring
3. **Log Aggregation**: Centralize logs with ELK or similar
4. **Custom Metrics**: Add more business-specific metrics
5. **Real-time Alerts**: Integrate with PagerDuty/Slack