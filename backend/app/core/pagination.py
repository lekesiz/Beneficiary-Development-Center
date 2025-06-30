"""Pagination utility for API responses."""
from flask import request, jsonify


def paginate(query, model_class=None):
    """
    Paginate a SQLAlchemy query and return JSON response.
    
    Args:
        query: SQLAlchemy query object
        model_class: Optional model class for serialization
    
    Returns:
        JSON response with paginated data
    """
    # Get pagination parameters from request
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Execute pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Serialize items
    if hasattr(paginated.items[0] if paginated.items else None, 'to_dict'):
        items = [item.to_dict() for item in paginated.items]
    else:
        # Basic serialization for models without to_dict
        items = []
        for item in paginated.items:
            item_dict = {}
            for column in item.__table__.columns:
                value = getattr(item, column.name)
                # Handle datetime and date objects
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                # Handle enum values
                elif hasattr(value, 'value'):
                    value = value.value
                item_dict[column.name] = value
            items.append(item_dict)
    
    # Return paginated response
    return jsonify({
        'items': items,
        'pagination': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_prev': paginated.has_prev,
            'has_next': paginated.has_next,
            'prev_num': paginated.prev_num,
            'next_num': paginated.next_num
        }
    })