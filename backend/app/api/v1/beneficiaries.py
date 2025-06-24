"""Beneficiary API endpoints."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.database import get_db
from app.models.user import User
from app.services.beneficiary_service import BeneficiaryService
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.core.decorators import requires_role
from app.core.validators import validate_request
from app.schemas.beneficiary import (
    BeneficiaryCreateSchema,
    BeneficiaryUpdateSchema,
    BeneficiaryListSchema,
    BeneficiaryDetailSchema
)

bp = Blueprint('beneficiaries', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_beneficiaries():
    """Get all beneficiaries with pagination and filters."""
    # Get current user
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search')
    status = request.args.get('status')
    assigned_trainer_id = request.args.get('assigned_trainer_id', type=int)
    tags = request.args.getlist('tags')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Validate pagination
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiaries, total = service.get_all(
            page=page,
            per_page=per_page,
            search=search,
            status=status,
            assigned_trainer_id=assigned_trainer_id,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return jsonify({
            'beneficiaries': [b.to_dict(include_related=True) for b in beneficiaries],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
def get_beneficiary(beneficiary_id):
    """Get beneficiary by ID."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiary = service.get_by_id(beneficiary_id)
        
        return jsonify({
            'beneficiary': beneficiary.to_dict(include_related=True)
        }), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/uuid/<uuid>', methods=['GET'])
@jwt_required()
def get_beneficiary_by_uuid(uuid):
    """Get beneficiary by UUID."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiary = service.get_by_uuid(uuid)
        
        return jsonify({
            'beneficiary': beneficiary.to_dict(include_related=True)
        }), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('', methods=['POST'])
@jwt_required()
@requires_role(['super_admin', 'admin', 'trainer'])
def create_beneficiary():
    """Create a new beneficiary."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    # Validate request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiary = service.create(data)
        
        return jsonify({
            'message': 'Beneficiary created successfully',
            'beneficiary': beneficiary.to_dict(include_related=True)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiary_id>', methods=['PUT'])
@jwt_required()
@requires_role(['super_admin', 'admin', 'trainer'])
def update_beneficiary(beneficiary_id):
    """Update beneficiary."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    # Validate request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiary = service.update(beneficiary_id, data)
        
        return jsonify({
            'message': 'Beneficiary updated successfully',
            'beneficiary': beneficiary.to_dict(include_related=True)
        }), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiary_id>', methods=['DELETE'])
@jwt_required()
@requires_role(['super_admin', 'admin'])
def delete_beneficiary(beneficiary_id):
    """Delete beneficiary (soft delete)."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    try:
        service = BeneficiaryService(db, current_user)
        service.delete(beneficiary_id)
        
        return jsonify({
            'message': 'Beneficiary deleted successfully'
        }), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiary_id>/notes', methods=['POST'])
@jwt_required()
@requires_role(['super_admin', 'admin', 'trainer'])
def add_note(beneficiary_id):
    """Add note to beneficiary."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    # Validate request data
    data = request.get_json()
    if not data or 'note' not in data:
        return jsonify({'error': 'Note text is required'}), 400
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiary = service.add_note(beneficiary_id, data['note'])
        
        return jsonify({
            'message': 'Note added successfully',
            'beneficiary': beneficiary.to_dict(include_related=True)
        }), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiary_id>/tags', methods=['POST'])
@jwt_required()
@requires_role(['super_admin', 'admin', 'trainer'])
def add_tag(beneficiary_id):
    """Add tag to beneficiary."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    # Validate request data
    data = request.get_json()
    if not data or 'tag' not in data:
        return jsonify({'error': 'Tag is required'}), 400
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiary = service.add_tag(beneficiary_id, data['tag'])
        
        return jsonify({
            'message': 'Tag added successfully',
            'beneficiary': beneficiary.to_dict(include_related=True)
        }), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiary_id>/tags/<tag>', methods=['DELETE'])
@jwt_required()
@requires_role(['super_admin', 'admin', 'trainer'])
def remove_tag(beneficiary_id, tag):
    """Remove tag from beneficiary."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiary = service.remove_tag(beneficiary_id, tag)
        
        return jsonify({
            'message': 'Tag removed successfully',
            'beneficiary': beneficiary.to_dict(include_related=True)
        }), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get beneficiary statistics."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    try:
        service = BeneficiaryService(db, current_user)
        statistics = service.get_statistics()
        
        return jsonify({
            'statistics': statistics
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiary_id>/assign-trainer', methods=['POST'])
@jwt_required()
@requires_role(['super_admin', 'admin'])
def assign_trainer(beneficiary_id):
    """Assign trainer to beneficiary."""
    current_user_id = get_jwt_identity()
    db = next(get_db())
    current_user = db.query(User).get(current_user_id)
    
    # Validate request data
    data = request.get_json()
    if not data or 'trainer_id' not in data:
        return jsonify({'error': 'Trainer ID is required'}), 400
    
    try:
        service = BeneficiaryService(db, current_user)
        beneficiary = service.assign_trainer(beneficiary_id, data['trainer_id'])
        
        return jsonify({
            'message': 'Trainer assigned successfully',
            'beneficiary': beneficiary.to_dict(include_related=True)
        }), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()