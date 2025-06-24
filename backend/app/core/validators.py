"""Request validation utilities."""
from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from app.core.exceptions import ValidationError


class Validator:
    """Base validator class."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        # Remove spaces, dashes, and parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        # Check if it's a valid phone number (10-15 digits)
        return bool(re.match(r'^\+?\d{10,15}$', cleaned))
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD)."""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """Validate password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, None
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        # Username must be 3-30 characters, alphanumeric with underscores
        return bool(re.match(r'^[a-zA-Z0-9_]{3,30}$', username))
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format."""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        return bool(re.match(pattern, uuid_str.lower()))


def validate_request(schema: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate request data against a schema.
    
    Schema format:
    {
        'field_name': {
            'type': str/int/float/bool/list/dict,
            'required': True/False,
            'min_length': int (for strings),
            'max_length': int (for strings),
            'min_value': number (for numbers),
            'max_value': number (for numbers),
            'pattern': regex (for strings),
            'validator': callable (custom validator),
            'choices': list (allowed values)
        }
    }
    """
    validated_data = {}
    errors = {}
    
    # Check required fields
    for field_name, rules in schema.items():
        if rules.get('required', False) and field_name not in data:
            errors[field_name] = f"{field_name} is required"
    
    # Validate provided fields
    for field_name, value in data.items():
        if field_name not in schema:
            continue  # Skip fields not in schema
        
        rules = schema[field_name]
        field_errors = []
        
        # Type validation
        expected_type = rules.get('type')
        if expected_type and not isinstance(value, expected_type):
            field_errors.append(f"Must be of type {expected_type.__name__}")
        
        # String validations
        if isinstance(value, str):
            if 'min_length' in rules and len(value) < rules['min_length']:
                field_errors.append(f"Must be at least {rules['min_length']} characters")
            
            if 'max_length' in rules and len(value) > rules['max_length']:
                field_errors.append(f"Must be at most {rules['max_length']} characters")
            
            if 'pattern' in rules and not re.match(rules['pattern'], value):
                field_errors.append("Invalid format")
        
        # Number validations
        if isinstance(value, (int, float)):
            if 'min_value' in rules and value < rules['min_value']:
                field_errors.append(f"Must be at least {rules['min_value']}")
            
            if 'max_value' in rules and value > rules['max_value']:
                field_errors.append(f"Must be at most {rules['max_value']}")
        
        # Choices validation
        if 'choices' in rules and value not in rules['choices']:
            field_errors.append(f"Must be one of: {', '.join(map(str, rules['choices']))}")
        
        # Custom validator
        if 'validator' in rules:
            try:
                is_valid = rules['validator'](value)
                if not is_valid:
                    field_errors.append("Invalid value")
            except Exception as e:
                field_errors.append(str(e))
        
        if field_errors:
            errors[field_name] = '; '.join(field_errors)
        else:
            validated_data[field_name] = value
    
    if errors:
        raise ValidationError(f"Validation failed: {errors}")
    
    return validated_data


# Common validation schemas
class ValidationSchemas:
    """Common validation schemas."""
    
    LOGIN_SCHEMA = {
        'email': {
            'type': str,
            'required': True,
            'validator': Validator.validate_email
        },
        'password': {
            'type': str,
            'required': True,
            'min_length': 8
        },
        'tenant_id': {
            'type': int,
            'required': True,
            'min_value': 1
        }
    }
    
    REGISTER_SCHEMA = {
        'email': {
            'type': str,
            'required': True,
            'validator': Validator.validate_email
        },
        'password': {
            'type': str,
            'required': True,
            'validator': lambda p: Validator.validate_password(p)[0]
        },
        'first_name': {
            'type': str,
            'required': True,
            'min_length': 2,
            'max_length': 50
        },
        'last_name': {
            'type': str,
            'required': True,
            'min_length': 2,
            'max_length': 50
        },
        'tenant_id': {
            'type': int,
            'required': True,
            'min_value': 1
        }
    }
    
    BENEFICIARY_CREATE_SCHEMA = {
        'first_name': {
            'type': str,
            'required': True,
            'min_length': 2,
            'max_length': 50
        },
        'last_name': {
            'type': str,
            'required': True,
            'min_length': 2,
            'max_length': 50
        },
        'email': {
            'type': str,
            'required': False,
            'validator': Validator.validate_email
        },
        'phone': {
            'type': str,
            'required': False,
            'validator': Validator.validate_phone
        },
        'date_of_birth': {
            'type': str,
            'required': False,
            'validator': Validator.validate_date
        },
        'status': {
            'type': str,
            'required': False,
            'choices': ['active', 'inactive', 'completed', 'suspended']
        },
        'employment_status': {
            'type': str,
            'required': False,
            'choices': ['employed', 'unemployed', 'student', 'self_employed', 'retired', 'other']
        },
        'education_level': {
            'type': str,
            'required': False,
            'choices': ['no_diploma', 'primary', 'secondary', 'high_school', 'bachelor', 'master', 'doctorate', 'other']
        }
    }