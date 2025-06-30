"""
Google Cloud Storage Manager for BDC Platform
Handles file uploads, downloads, and management with enterprise features
"""

import os
import io
import mimetypes
import hashlib
import logging
from typing import Optional, Union, BinaryIO, Dict, List, Tuple
from datetime import datetime, timedelta
from urllib.parse import quote

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound, Conflict
    from google.api_core.retry import Retry
    from google.api_core import exceptions
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    storage = None
    NotFound = Exception
    Conflict = Exception
    Retry = None
    exceptions = None
from flask import current_app, url_for
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


class CloudStorageManager:
    """
    Manages file operations with Google Cloud Storage
    Features: encryption, signed URLs, lifecycle management, CDN integration
    """
    
    def __init__(self, bucket_name: Optional[str] = None, project_id: Optional[str] = None):
        """Initialize Cloud Storage client and bucket"""
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError("Google Cloud Storage libraries not available")
            
        self.project_id = project_id or current_app.config.get('GCS_PROJECT_ID')
        self.bucket_name = bucket_name or current_app.config.get('GCS_BUCKET_NAME')
        
        # Initialize client
        if current_app.config.get('GCS_CREDENTIALS_PATH'):
            self.client = storage.Client.from_service_account_json(
                current_app.config['GCS_CREDENTIALS_PATH']
            )
        else:
            # Use default credentials (App Engine, Compute Engine, etc.)
            self.client = storage.Client(project=self.project_id)
        
        # Get or create bucket
        self._bucket = None
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not"""
        try:
            self._bucket = self.client.get_bucket(self.bucket_name)
            logger.info(f"Using existing bucket: {self.bucket_name}")
        except NotFound:
            # Create bucket with production settings
            self._bucket = self.client.create_bucket(
                self.bucket_name,
                location='US-CENTRAL1',
                project=self.project_id
            )
            
            # Configure bucket settings
            self._configure_bucket()
            logger.info(f"Created new bucket: {self.bucket_name}")
    
    def _configure_bucket(self):
        """Configure bucket with lifecycle rules, CORS, and encryption"""
        # Set lifecycle rules
        self._bucket.add_lifecycle_rule(
            action={'type': 'Delete'},
            conditions={
                'age': 90,  # Delete temporary files after 90 days
                'matchesPrefix': ['temp/', 'tmp/']
            }
        )
        
        self._bucket.add_lifecycle_rule(
            action={'type': 'SetStorageClass', 'storageClass': 'NEARLINE'},
            conditions={
                'age': 30,  # Move to nearline after 30 days
                'matchesStorageClass': ['STANDARD']
            }
        )
        
        # Configure CORS
        self._bucket.cors = [
            {
                'origin': current_app.config.get('CORS_ORIGINS', ['*']),
                'method': ['GET', 'HEAD', 'PUT', 'POST', 'DELETE'],
                'responseHeader': ['Content-Type', 'Content-Length', 'Date'],
                'maxAgeSeconds': 3600
            }
        ]
        
        # Enable uniform bucket-level access
        self._bucket.iam_configuration.uniform_bucket_level_access_enabled = True
        
        # Enable versioning for important files
        self._bucket.versioning_enabled = True
        
        # Update bucket configuration
        self._bucket.patch()
    
    def upload_file(
        self,
        file: Union[FileStorage, BinaryIO],
        path: str,
        tenant_id: int,
        user_id: int,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None,
        public: bool = False
    ) -> Dict:
        """
        Upload a file to Cloud Storage with metadata
        
        Args:
            file: File object to upload
            path: Storage path (will be prefixed with tenant_id)
            tenant_id: Tenant ID for multi-tenancy
            user_id: User ID for audit trail
            content_type: MIME type (auto-detected if not provided)
            metadata: Additional metadata
            public: Whether file should be publicly accessible
            
        Returns:
            Dict with file information including URL
        """
        # Validate file
        if hasattr(file, 'filename'):
            filename = secure_filename(file.filename)
        else:
            filename = os.path.basename(path)
        
        # Check file extension
        if not self._is_allowed_file(filename):
            raise ValueError(f"File type not allowed: {filename}")
        
        # Generate secure path
        file_path = self._generate_path(tenant_id, path, filename)
        
        # Create blob
        blob = self._bucket.blob(file_path)
        
        # Set content type
        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        blob.content_type = content_type
        
        # Set metadata
        blob.metadata = {
            'tenant_id': str(tenant_id),
            'user_id': str(user_id),
            'original_filename': filename,
            'uploaded_at': datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        # Calculate file hash for integrity
        file_data = file.read()
        file_hash = hashlib.sha256(file_data).hexdigest()
        blob.metadata['sha256'] = file_hash
        
        # Reset file pointer
        if hasattr(file, 'seek'):
            file.seek(0)
        else:
            file = io.BytesIO(file_data)
        
        # Upload with retry
        retry = Retry(deadline=60.0)
        blob.upload_from_file(
            file,
            content_type=content_type,
            retry=retry
        )
        
        # Set caching
        blob.cache_control = 'public, max-age=3600' if public else 'private'
        blob.patch()
        
        # Make public if requested
        if public:
            blob.make_public()
        
        # Return file information
        return {
            'id': blob.id,
            'name': blob.name,
            'path': file_path,
            'size': blob.size,
            'content_type': blob.content_type,
            'hash': file_hash,
            'created_at': blob.time_created.isoformat(),
            'updated_at': blob.updated.isoformat(),
            'url': self.get_file_url(file_path, public=public),
            'metadata': blob.metadata
        }
    
    def download_file(
        self,
        path: str,
        tenant_id: int,
        user_id: int,
        version: Optional[str] = None
    ) -> Tuple[bytes, Dict]:
        """
        Download a file from Cloud Storage
        
        Args:
            path: File path
            tenant_id: Tenant ID for access control
            user_id: User ID for audit
            version: Specific version to download
            
        Returns:
            Tuple of (file_data, metadata)
        """
        # Generate full path
        file_path = self._generate_path(tenant_id, path)
        
        # Get blob
        blob = self._bucket.blob(file_path)
        
        if version:
            blob = blob.with_generation(version)
        
        # Check if exists
        if not blob.exists():
            raise NotFound(f"File not found: {path}")
        
        # Verify tenant access
        if blob.metadata.get('tenant_id') != str(tenant_id):
            raise PermissionError("Access denied to file")
        
        # Log access for audit
        logger.info(f"File downloaded: {file_path} by user {user_id}")
        
        # Download file
        file_data = blob.download_as_bytes()
        
        # Return data and metadata
        return file_data, {
            'name': blob.name,
            'size': blob.size,
            'content_type': blob.content_type,
            'hash': blob.metadata.get('sha256'),
            'created_at': blob.time_created.isoformat(),
            'updated_at': blob.updated.isoformat(),
            'metadata': blob.metadata
        }
    
    def delete_file(
        self,
        path: str,
        tenant_id: int,
        user_id: int,
        permanent: bool = False
    ) -> bool:
        """
        Delete a file (soft delete by default)
        
        Args:
            path: File path
            tenant_id: Tenant ID for access control
            user_id: User ID for audit
            permanent: Whether to permanently delete
            
        Returns:
            Success status
        """
        # Generate full path
        file_path = self._generate_path(tenant_id, path)
        
        # Get blob
        blob = self._bucket.blob(file_path)
        
        # Check if exists
        if not blob.exists():
            return False
        
        # Verify tenant access
        if blob.metadata.get('tenant_id') != str(tenant_id):
            raise PermissionError("Access denied to file")
        
        if permanent:
            # Permanent deletion
            blob.delete()
            logger.info(f"File permanently deleted: {file_path} by user {user_id}")
        else:
            # Soft delete - move to trash
            trash_path = f"trash/{file_path}"
            trash_blob = self._bucket.blob(trash_path)
            
            # Copy to trash with metadata
            trash_blob.metadata = {
                **blob.metadata,
                'deleted_at': datetime.utcnow().isoformat(),
                'deleted_by': str(user_id)
            }
            
            # Copy and delete original
            trash_blob.upload_from_string(blob.download_as_bytes())
            blob.delete()
            
            logger.info(f"File moved to trash: {file_path} by user {user_id}")
        
        return True
    
    def list_files(
        self,
        tenant_id: int,
        prefix: Optional[str] = None,
        limit: int = 100,
        page_token: Optional[str] = None
    ) -> Dict:
        """
        List files for a tenant with pagination
        
        Args:
            tenant_id: Tenant ID
            prefix: Optional path prefix
            limit: Maximum files to return
            page_token: Pagination token
            
        Returns:
            Dict with files and pagination info
        """
        # Build prefix
        base_prefix = f"tenants/{tenant_id}/"
        if prefix:
            base_prefix = f"{base_prefix}{prefix}"
        
        # List blobs
        blobs = self._bucket.list_blobs(
            prefix=base_prefix,
            max_results=limit,
            page_token=page_token
        )
        
        # Build response
        files = []
        for blob in blobs:
            # Skip trash files
            if '/trash/' in blob.name:
                continue
                
            files.append({
                'name': blob.name.replace(base_prefix, ''),
                'path': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created_at': blob.time_created.isoformat(),
                'updated_at': blob.updated.isoformat(),
                'url': self.get_file_url(blob.name),
                'metadata': blob.metadata
            })
        
        return {
            'files': files,
            'next_page_token': blobs.next_page_token,
            'total': len(files)
        }
    
    def get_file_url(
        self,
        path: str,
        expires_in: int = 3600,
        public: bool = False,
        download: bool = False
    ) -> str:
        """
        Generate a signed URL for file access
        
        Args:
            path: File path
            expires_in: URL expiration in seconds
            public: Whether to return public URL
            download: Whether to force download
            
        Returns:
            Signed URL
        """
        blob = self._bucket.blob(path)
        
        if public and blob.public_url:
            return blob.public_url
        
        # Generate signed URL
        response_disposition = None
        if download:
            filename = os.path.basename(path)
            response_disposition = f'attachment; filename="{filename}"'
        
        url = blob.generate_signed_url(
            version='v4',
            expiration=timedelta(seconds=expires_in),
            method='GET',
            response_disposition=response_disposition
        )
        
        return url
    
    def get_upload_url(
        self,
        path: str,
        tenant_id: int,
        user_id: int,
        content_type: str = 'application/octet-stream',
        expires_in: int = 3600
    ) -> Dict:
        """
        Generate a signed URL for direct upload
        
        Args:
            path: Target file path
            tenant_id: Tenant ID
            user_id: User ID
            content_type: MIME type
            expires_in: URL expiration in seconds
            
        Returns:
            Dict with upload URL and fields
        """
        # Generate secure path
        filename = secure_filename(os.path.basename(path))
        file_path = self._generate_path(tenant_id, path, filename)
        
        # Create blob
        blob = self._bucket.blob(file_path)
        
        # Set metadata
        metadata = {
            'tenant_id': str(tenant_id),
            'user_id': str(user_id),
            'uploaded_at': datetime.utcnow().isoformat()
        }
        
        # Generate signed URL for upload
        url = blob.generate_signed_url(
            version='v4',
            expiration=timedelta(seconds=expires_in),
            method='PUT',
            content_type=content_type,
            headers={'x-goog-meta-tenant-id': str(tenant_id)}
        )
        
        return {
            'url': url,
            'method': 'PUT',
            'headers': {
                'Content-Type': content_type
            },
            'path': file_path,
            'expires_at': (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        }
    
    def copy_file(
        self,
        source_path: str,
        dest_path: str,
        tenant_id: int,
        user_id: int
    ) -> Dict:
        """Copy a file within the bucket"""
        # Generate paths
        source_full = self._generate_path(tenant_id, source_path)
        dest_full = self._generate_path(tenant_id, dest_path)
        
        # Get source blob
        source_blob = self._bucket.blob(source_full)
        if not source_blob.exists():
            raise NotFound(f"Source file not found: {source_path}")
        
        # Verify tenant access
        if source_blob.metadata.get('tenant_id') != str(tenant_id):
            raise PermissionError("Access denied to file")
        
        # Create destination blob
        dest_blob = self._bucket.copy_blob(
            source_blob,
            self._bucket,
            dest_full
        )
        
        # Update metadata
        dest_blob.metadata = {
            **source_blob.metadata,
            'copied_from': source_full,
            'copied_by': str(user_id),
            'copied_at': datetime.utcnow().isoformat()
        }
        dest_blob.patch()
        
        return {
            'path': dest_full,
            'url': self.get_file_url(dest_full)
        }
    
    def get_file_stats(self, tenant_id: int) -> Dict:
        """Get storage statistics for a tenant"""
        prefix = f"tenants/{tenant_id}/"
        
        total_size = 0
        file_count = 0
        file_types = {}
        
        for blob in self._bucket.list_blobs(prefix=prefix):
            if '/trash/' not in blob.name:
                total_size += blob.size
                file_count += 1
                
                # Count by type
                ext = os.path.splitext(blob.name)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count,
            'file_types': file_types,
            'bucket_name': self.bucket_name
        }
    
    def _generate_path(self, tenant_id: int, path: str, filename: Optional[str] = None) -> str:
        """Generate a secure path with tenant isolation"""
        # Remove leading slashes
        path = path.lstrip('/')
        
        # Use filename if provided, otherwise extract from path
        if filename:
            # Ensure path is directory
            if not path.endswith('/'):
                path = os.path.dirname(path) + '/'
            path = path + filename
        
        # Build full path with tenant isolation
        return f"tenants/{tenant_id}/{path}"
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if '.' not in filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower()
        allowed = current_app.config.get('ALLOWED_EXTENSIONS', set())
        
        # Allow all if no restrictions
        if not allowed:
            return True
            
        return ext in allowed


# Singleton instance
_storage_manager = None


class LocalStorageManager:
    """Fallback local storage manager for development without Google Cloud"""
    
    def __init__(self, upload_folder: Optional[str] = None):
        """Initialize local storage with upload folder"""
        self.upload_folder = upload_folder or current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, exist_ok=True)
    
    def upload_file(self, *args, **kwargs):
        """Stub for upload_file"""
        raise NotImplementedError("Local storage not fully implemented. Please configure Google Cloud Storage.")
    
    def get_file_url(self, *args, **kwargs):
        """Stub for get_file_url"""
        return "/static/placeholder.png"
    
    def delete_file(self, *args, **kwargs):
        """Stub for delete_file"""
        pass


def get_storage_manager() -> Union[CloudStorageManager, LocalStorageManager]:
    """Get or create storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        if GOOGLE_CLOUD_AVAILABLE and current_app.config.get('GCS_BUCKET_NAME'):
            try:
                _storage_manager = CloudStorageManager()
            except Exception as e:
                logger.warning(f"Failed to initialize Google Cloud Storage: {e}")
                logger.info("Falling back to local storage manager")
                _storage_manager = LocalStorageManager()
        else:
            logger.info("Using local storage manager (Google Cloud not available)")
            _storage_manager = LocalStorageManager()
    return _storage_manager