"""Utility functions for API responses."""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    """Create a standardized success response."""
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response["data"] = data
    
    return jsonify(response), status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    """Create a standardized error response."""
    response = {
        "success": False,
        "message": message
    }
    
    if errors:
        response["errors"] = errors
    
    return jsonify(response), status_code


def paginated_response(items, pagination, message="Success"):
    """Create a standardized paginated response."""
    return success_response({
        "items": items,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_prev": pagination.has_prev,
            "has_next": pagination.has_next,
            "prev_num": pagination.prev_num,
            "next_num": pagination.next_num
        }
    }, message)


def created_response(data=None, message="Created successfully"):
    """Create a standardized response for created resources."""
    return success_response(data, message, 201)


def updated_response(data=None, message="Updated successfully"):
    """Create a standardized response for updated resources."""
    return success_response(data, message, 200)


def deleted_response(message="Deleted successfully"):
    """Create a standardized response for deleted resources."""
    return success_response(None, message, 200)


def validation_error_response(errors, message="Validation error"):
    """Create a standardized validation error response."""
    return error_response(message, 400, errors)


def not_found_response(message="Resource not found"):
    """Create a standardized 404 response."""
    return error_response(message, 404)


def unauthorized_response(message="Unauthorized"):
    """Create a standardized 401 response."""
    return error_response(message, 401)


def forbidden_response(message="Forbidden"):
    """Create a standardized 403 response."""
    return error_response(message, 403)


def internal_error_response(message="Internal server error"):
    """Create a standardized 500 response."""
    return error_response(message, 500)