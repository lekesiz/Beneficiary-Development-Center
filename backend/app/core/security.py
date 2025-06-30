"""
Enhanced security middleware for BDC Platform
Implements comprehensive security headers, rate limiting, and request validation
"""

from flask import Flask, request, g, current_app, jsonify, abort
from functools import wraps
from typing import Optional, Dict, Any, Callable
import logging
import hashlib
import hmac
import time
import re
from datetime import datetime, timedelta
import ipaddress

logger = logging.getLogger(__name__)


def init_security_middleware(app: Flask):
    """Initialize comprehensive security middleware."""
    
    @app.before_request
    def security_checks():
        """Perform security checks before processing requests."""
        # Generate request ID if not present
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            request_id = generate_request_id()
        g.request_id = request_id
        
        # Log security-relevant request information
        log_security_event('request_received', {
            'request_id': request_id,
            'content_length': request.content_length
        })
        
        # Validate request size
        if not validate_request_size():
            abort(413, description="Request entity too large")
        
        # Check for SQL injection attempts
        if detect_sql_injection():
            log_security_event('sql_injection_attempt', {
                'query_string': request.query_string.decode('utf-8'),
                'path': request.path
            })
            abort(400, description="Invalid request")
        
        # Check for XSS attempts
        if detect_xss_attempt():
            log_security_event('xss_attempt', {
                'data': str(request.get_data())[:200]
            })
            abort(400, description="Invalid request")
        
        # Validate content type for POST/PUT requests
        if request.method in ['POST', 'PUT'] and request.content_length:
            if not validate_content_type():
                abort(415, description="Unsupported media type")
    
    @app.after_request
    def apply_security_headers(response):
        """Apply comprehensive security headers."""
        # Get configured headers
        headers = app.config.get('SECURITY_HEADERS', {})
        
        # Apply configured headers
        for header, value in headers.items():
            response.headers[header] = value
        
        # Additional security headers
        response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
        
        # Add security headers based on response type
        if response.content_type and 'html' in response.content_type:
            # Additional HTML-specific headers
            if 'Content-Security-Policy' not in response.headers:
                response.headers['Content-Security-Policy'] = get_default_csp()
        
        # Remove server header
        response.headers.pop('Server', None)
        
        # Add cache control for sensitive endpoints
        if request.endpoint and 'auth' in request.endpoint:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
        
        return response
    
    @app.before_request
    def validate_tenant():
        """Validate tenant ID from header."""
        tenant_header = app.config.get("TENANT_HEADER", "X-Tenant-ID")
        tenant_id = request.headers.get(tenant_header)
        
        if tenant_id:
            try:
                g.tenant_id = int(tenant_id)
            except ValueError:
                logger.warning(f"Invalid tenant ID format: {tenant_id}")
                g.tenant_id = app.config.get("DEFAULT_TENANT_ID", 1)
        else:
            g.tenant_id = app.config.get("DEFAULT_TENANT_ID", 1)
        
        # Store for logging
        g.tenant_id_header = tenant_id


def require_security_headers(f):
    """Decorator to ensure critical security headers are present."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Ensure critical headers are present
        critical_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }
        
        for header, value in critical_headers.items():
            if not response.headers.get(header):
                response.headers[header] = value
        
        return response
    
    return decorated_function


def validate_request_size():
    """Validate request content length."""
    max_length = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    content_length = request.content_length
    
    if content_length and content_length > max_length:
        logger.warning(f"Request too large: {content_length} bytes (max: {max_length})")
        return False
    
    return True


def log_security_event(event_type: str, details: dict = None):
    """Log security-related events with enhanced context."""
    security_logger = logging.getLogger('security')
    
    log_data = {
        'event_type': event_type,
        'ip_address': get_real_ip(),
        'user_agent': request.headers.get('User-Agent'),
        'path': request.path,
        'method': request.method,
        'tenant_id': getattr(g, 'tenant_id', None),
        'user_id': getattr(g, 'current_user_id', None),
        'request_id': getattr(g, 'request_id', None),
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    security_logger.info(f"Security event: {event_type}", extra=log_data)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    timestamp = str(time.time()).encode('utf-8')
    random_data = str(request.remote_addr).encode('utf-8')
    return hashlib.sha256(timestamp + random_data).hexdigest()[:16]


def get_real_ip() -> str:
    """Get the real IP address considering proxies."""
    # Check for App Engine headers
    if 'X-Appengine-User-IP' in request.headers:
        return request.headers['X-Appengine-User-IP']
    
    # Check for standard proxy headers
    for header in ['X-Forwarded-For', 'X-Real-IP']:
        if header in request.headers:
            # Get the first IP in the chain
            ips = request.headers[header].split(',')
            return ips[0].strip()
    
    return request.remote_addr


def validate_content_type() -> bool:
    """Validate that content type is acceptable."""
    content_type = request.content_type
    
    # Allow these content types
    allowed_types = [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data',
        'text/plain'
    ]
    
    if not content_type:
        return False
    
    # Check if content type (without charset) is allowed
    base_type = content_type.split(';')[0].strip()
    return any(allowed in base_type for allowed in allowed_types)


def detect_sql_injection() -> bool:
    """Detect potential SQL injection attempts."""
    # SQL injection patterns
    sql_patterns = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(from|into|where|table)\b)',
        r'(--|#|\/\*|\*\/)',
        r'(\b(or|and)\b\s*[\'"\d]?\s*=\s*[\'"\d]?)',
        r'(\bsleep\s*\(\s*\d+\s*\))',
        r'(\bbenchmark\s*\()',
        r'(;.*?(drop|alter|create|delete)\s+)',
        r'(\'\s*(or|and)\s*\'?\d)',
        r'(xp_cmdshell)',
        r'(sysobjects|syscolumns|systables)'
    ]
    
    # Check query string
    query_string = request.query_string.decode('utf-8', errors='ignore').lower()
    for pattern in sql_patterns:
        if re.search(pattern, query_string, re.IGNORECASE):
            return True
    
    # Check form data if present
    if request.form:
        form_data = ' '.join(request.form.values()).lower()
        for pattern in sql_patterns:
            if re.search(pattern, form_data, re.IGNORECASE):
                return True
    
    # Check JSON data if present
    if request.is_json:
        try:
            json_data = request.get_json()
            if json_data:
                json_str = str(json_data).lower()
                for pattern in sql_patterns:
                    if re.search(pattern, json_str, re.IGNORECASE):
                        return True
        except Exception:
            # If JSON parsing fails, skip the check
            pass
    
    return False


def detect_xss_attempt() -> bool:
    """Detect potential XSS attempts."""
    xss_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        r'<svg.*?onload',
        r'eval\s*\(',
        r'expression\s*\(',
        r'vbscript:',
        r'data:text/html',
        r'<img.*?src.*?=.*?(javascript|data:)',
        r'<link.*?href.*?=.*?javascript'
    ]
    
    # Check all input sources
    data_to_check = []
    
    if request.args:
        data_to_check.extend(request.args.values())
    
    if request.form:
        data_to_check.extend(request.form.values())
    
    if request.is_json:
        try:
            json_data = request.get_json()
            if json_data:
                data_to_check.append(str(json_data))
        except Exception:
            # If JSON parsing fails, skip the check
            pass
    
    # Check each input
    for data in data_to_check:
        data_lower = str(data).lower()
        for pattern in xss_patterns:
            if re.search(pattern, data_lower, re.IGNORECASE):
                return True
    
    return False


def get_default_csp() -> str:
    """Get default Content Security Policy."""
    return (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://www.googletagmanager.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https:; "
        "connect-src 'self' wss: https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )


def require_https(f: Callable) -> Callable:
    """Decorator to require HTTPS in production."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.debug and not request.is_secure:
            return jsonify({'error': 'HTTPS required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def validate_api_key(f: Callable) -> Callable:
    """Decorator to validate API key for external access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key (implement your logic)
        valid_keys = current_app.config.get('VALID_API_KEYS', [])
        if api_key not in valid_keys:
            log_security_event('invalid_api_key', {'api_key': api_key[:8] + '...'})
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit_by_ip(max_requests: int = 100, window: int = 3600) -> Callable:
    """Decorator for IP-based rate limiting."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config.get('RATELIMIT_ENABLED', True):
                return f(*args, **kwargs)
            
            # Get IP address
            ip = get_real_ip()
            
            # Use cache for rate limiting
            cache_key = f"rate_limit:{f.__name__}:{ip}"
            
            try:
                # Get current count
                current = current_app.extensions.get('cache').get(cache_key) or 0
                
                if current >= max_requests:
                    log_security_event('rate_limit_exceeded', {
                        'ip': ip,
                        'endpoint': f.__name__,
                        'limit': max_requests
                    })
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'retry_after': window
                    }), 429
                
                # Increment counter
                current_app.extensions.get('cache').set(
                    cache_key, 
                    current + 1, 
                    timeout=window
                )
                
            except Exception as e:
                logger.warning(f"Rate limiting error: {str(e)}")
                # Continue without rate limiting on error
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_ip_whitelist(whitelist: list) -> Callable:
    """Decorator to restrict access to whitelisted IPs."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = get_real_ip()
            
            # Check if IP is in whitelist
            allowed = False
            for allowed_ip in whitelist:
                try:
                    # Support CIDR notation
                    if '/' in allowed_ip:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if ipaddress.ip_address(client_ip) in network:
                            allowed = True
                            break
                    else:
                        if client_ip == allowed_ip:
                            allowed = True
                            break
                except Exception as e:
                    logger.error(f"IP validation error: {str(e)}")
            
            if not allowed:
                log_security_event('ip_whitelist_denied', {
                    'ip': client_ip,
                    'endpoint': request.endpoint
                })
                abort(403, description="Access denied")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sanitize_input(data: Any) -> Any:
    """Sanitize user input to prevent injection attacks."""
    if isinstance(data, str):
        # Remove null bytes
        data = data.replace('\x00', '')
        
        # Escape HTML entities
        data = data.replace('&', '&amp;')
        data = data.replace('<', '&lt;')
        data = data.replace('>', '&gt;')
        data = data.replace('"', '&quot;')
        data = data.replace("'", '&#x27;')
        
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    
    return data


def verify_webhook_signature(secret: str) -> Callable:
    """Decorator to verify webhook signatures."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get signature from header
            signature = request.headers.get('X-Webhook-Signature')
            
            if not signature:
                return jsonify({'error': 'Missing signature'}), 401
            
            # Calculate expected signature
            payload = request.get_data()
            expected = hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            if not hmac.compare_digest(signature, expected):
                log_security_event('invalid_webhook_signature', {
                    'endpoint': request.endpoint
                })
                return jsonify({'error': 'Invalid signature'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator