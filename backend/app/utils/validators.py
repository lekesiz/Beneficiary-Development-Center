"""Validation utilities."""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        min_length: Minimum password length (default: 8)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits and has reasonable length
    if not cleaned.isdigit():
        return False
    
    # Phone number should be between 7 and 15 digits
    return 7 <= len(cleaned) <= 15


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must not exceed 50 characters"
    
    # Username should only contain alphanumeric characters, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    # Username should not start or end with special characters
    if username[0] in '_-' or username[-1] in '_-':
        return False, "Username cannot start or end with underscore or hyphen"
    
    return True, None


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False
    
    # Basic URL regex pattern
    pattern = r'^https?://([\w.-]+)(:[0-9]+)?(/.*)?$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def validate_date_range(start_date, end_date) -> tuple[bool, Optional[str]]:
    """
    Validate that start date is before end date.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not start_date or not end_date:
        return True, None  # Optional dates
    
    if start_date > end_date:
        return False, "Start date must be before end date"
    
    return True, None


def sanitize_html(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    
    # Replace multiple spaces with single space
    clean = re.sub(r'\s+', ' ', clean)
    
    return clean.strip()


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validate file extension.
    
    Args:
        filename: Filename to validate
        allowed_extensions: Set of allowed extensions
        
    Returns:
        True if valid, False otherwise
    """
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions