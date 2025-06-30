"""
File management API endpoints
Handles file uploads, downloads, and management using Cloud Storage
"""

import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, NotFound
from io import BytesIO

from app.core.cloud_storage import get_storage_manager
from app.core.jwt_utils import get_current_user_id
from app.models import User
from app.utils.decorators import require_tenant
from app.utils.validators import validate_file_size

# Create blueprint
files_bp = Blueprint('files', __name__, url_prefix='/api/v1/files')


@files_bp.route('/upload', methods=['POST'])
@jwt_required()
@require_tenant
def upload_file(tenant_id):
    """Upload a file to Cloud Storage"""
    # Get current user
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid user'}), 401
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file size
    if not validate_file_size(file):
        max_size_mb = current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024 * 1024)
        return jsonify({'error': f'File too large. Maximum size is {max_size_mb}MB'}), 413
    
    # Get optional parameters
    path = request.form.get('path', 'uploads/')
    metadata = {}
    
    # Add custom metadata if provided
    for key in request.form:
        if key.startswith('meta_'):
            metadata[key[5:]] = request.form[key]
    
    try:
        # Upload file
        storage = get_storage_manager()
        result = storage.upload_file(
            file=file,
            path=path,
            tenant_id=tenant_id,
            user_id=user_id,
            metadata=metadata,
            public=request.form.get('public', 'false').lower() == 'true'
        )
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': result
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'Failed to upload file'}), 500


@files_bp.route('/upload-url', methods=['POST'])
@jwt_required()
@require_tenant
def get_upload_url(tenant_id):
    """Get a signed URL for direct file upload"""
    # Get current user
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid user'}), 401
    
    # Get parameters
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Filename is required'}), 400
    
    filename = data['filename']
    path = data.get('path', 'uploads/')
    content_type = data.get('content_type', 'application/octet-stream')
    expires_in = min(data.get('expires_in', 3600), 86400)  # Max 24 hours
    
    try:
        # Generate upload URL
        storage = get_storage_manager()
        result = storage.get_upload_url(
            path=os.path.join(path, filename),
            tenant_id=tenant_id,
            user_id=user_id,
            content_type=content_type,
            expires_in=expires_in
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Upload URL generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate upload URL'}), 500


@files_bp.route('/<path:file_path>', methods=['GET'])
@jwt_required()
@require_tenant
def download_file(tenant_id, file_path):
    """Download a file from Cloud Storage"""
    # Get current user
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid user'}), 401
    
    # Get query parameters
    version = request.args.get('version')
    as_attachment = request.args.get('download', 'false').lower() == 'true'
    
    try:
        # Download file
        storage = get_storage_manager()
        file_data, metadata = storage.download_file(
            path=file_path,
            tenant_id=tenant_id,
            user_id=user_id,
            version=version
        )
        
        # Create response
        file_obj = BytesIO(file_data)
        filename = os.path.basename(file_path)
        
        return send_file(
            file_obj,
            mimetype=metadata.get('content_type', 'application/octet-stream'),
            as_attachment=as_attachment,
            download_name=filename
        )
        
    except NotFound:
        return jsonify({'error': 'File not found'}), 404
    except PermissionError:
        return jsonify({'error': 'Access denied'}), 403
    except Exception as e:
        current_app.logger.error(f"File download error: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500


@files_bp.route('/<path:file_path>/url', methods=['GET'])
@jwt_required()
@require_tenant
def get_file_url(tenant_id, file_path):
    """Get a signed URL for file access"""
    # Get current user
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid user'}), 401
    
    # Get parameters
    expires_in = min(int(request.args.get('expires_in', 3600)), 86400)
    download = request.args.get('download', 'false').lower() == 'true'
    
    try:
        # Generate signed URL
        storage = get_storage_manager()
        
        # Verify file exists and user has access
        full_path = storage._generate_path(tenant_id, file_path)
        url = storage.get_file_url(
            path=full_path,
            expires_in=expires_in,
            download=download
        )
        
        return jsonify({
            'url': url,
            'expires_in': expires_in
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"URL generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate file URL'}), 500


@files_bp.route('/<path:file_path>', methods=['DELETE'])
@jwt_required()
@require_tenant
def delete_file(tenant_id, file_path):
    """Delete a file (soft delete by default)"""
    # Get current user
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid user'}), 401
    
    # Check permissions (admin only for permanent delete)
    user = User.query.get(user_id)
    permanent = request.args.get('permanent', 'false').lower() == 'true'
    
    if permanent and user.role != 'admin':
        return jsonify({'error': 'Only admins can permanently delete files'}), 403
    
    try:
        # Delete file
        storage = get_storage_manager()
        success = storage.delete_file(
            path=file_path,
            tenant_id=tenant_id,
            user_id=user_id,
            permanent=permanent
        )
        
        if success:
            return jsonify({
                'message': 'File deleted successfully',
                'permanent': permanent
            }), 200
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except PermissionError:
        return jsonify({'error': 'Access denied'}), 403
    except Exception as e:
        current_app.logger.error(f"File deletion error: {str(e)}")
        return jsonify({'error': 'Failed to delete file'}), 500


@files_bp.route('/', methods=['GET'])
@jwt_required()
@require_tenant
def list_files(tenant_id):
    """List files for the tenant"""
    # Get current user
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid user'}), 401
    
    # Get parameters
    prefix = request.args.get('prefix', '')
    limit = min(int(request.args.get('limit', 100)), 1000)
    page_token = request.args.get('page_token')
    
    try:
        # List files
        storage = get_storage_manager()
        result = storage.list_files(
            tenant_id=tenant_id,
            prefix=prefix,
            limit=limit,
            page_token=page_token
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"File listing error: {str(e)}")
        return jsonify({'error': 'Failed to list files'}), 500


@files_bp.route('/copy', methods=['POST'])
@jwt_required()
@require_tenant
def copy_file(tenant_id):
    """Copy a file within the storage"""
    # Get current user
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid user'}), 401
    
    # Get parameters
    data = request.get_json()
    if not data or 'source' not in data or 'destination' not in data:
        return jsonify({'error': 'Source and destination paths are required'}), 400
    
    try:
        # Copy file
        storage = get_storage_manager()
        result = storage.copy_file(
            source_path=data['source'],
            dest_path=data['destination'],
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        return jsonify({
            'message': 'File copied successfully',
            'file': result
        }), 201
        
    except NotFound:
        return jsonify({'error': 'Source file not found'}), 404
    except PermissionError:
        return jsonify({'error': 'Access denied'}), 403
    except Exception as e:
        current_app.logger.error(f"File copy error: {str(e)}")
        return jsonify({'error': 'Failed to copy file'}), 500


@files_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_tenant
def get_storage_stats(tenant_id):
    """Get storage statistics for the tenant"""
    # Get current user
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid user'}), 401
    
    try:
        # Get stats
        storage = get_storage_manager()
        stats = storage.get_file_stats(tenant_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Stats retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to get storage statistics'}), 500


# Error handlers
@files_bp.errorhandler(413)
def request_entity_too_large(e):
    """Handle file too large error"""
    max_size_mb = current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024 * 1024)
    return jsonify({
        'error': f'File too large. Maximum size is {max_size_mb}MB'
    }), 413


@files_bp.errorhandler(Exception)
def handle_unexpected_error(e):
    """Handle unexpected errors"""
    current_app.logger.error(f"Unexpected error in files API: {str(e)}")
    return jsonify({
        'error': 'An unexpected error occurred'
    }), 500