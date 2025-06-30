"""
Google Secret Manager integration for BDC Platform
Secure storage and retrieval of sensitive configuration data
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from functools import lru_cache
from datetime import datetime

from google.cloud import secretmanager
from google.api_core import exceptions
from flask import current_app

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Manages secrets using Google Secret Manager
    Features: automatic rotation, versioning, access control
    """
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize Secret Manager client"""
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        
        if not self.project_id:
            raise ValueError("Project ID is required for Secret Manager")
        
        # Initialize client
        self.client = secretmanager.SecretManagerServiceClient()
        self.parent = f"projects/{self.project_id}"
        
        # Cache for frequently accessed secrets
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def create_secret(
        self,
        secret_id: str,
        secret_value: str,
        labels: Optional[Dict[str, str]] = None,
        automatic_replication: bool = True
    ) -> str:
        """
        Create a new secret
        
        Args:
            secret_id: Unique identifier for the secret
            secret_value: The secret value to store
            labels: Optional labels for organization
            automatic_replication: Use automatic replication (recommended)
            
        Returns:
            Secret resource name
        """
        # Check if secret already exists
        if self.secret_exists(secret_id):
            raise ValueError(f"Secret {secret_id} already exists")
        
        # Build the secret
        secret = {
            "replication": {
                "automatic": {} if automatic_replication else {
                    "user_managed": {
                        "replicas": [
                            {"location": "us-central1"},
                            {"location": "us-east1"}
                        ]
                    }
                }
            }
        }
        
        if labels:
            secret["labels"] = labels
        
        # Create the secret
        try:
            response = self.client.create_secret(
                request={
                    "parent": self.parent,
                    "secret_id": secret_id,
                    "secret": secret
                }
            )
            
            # Add the initial version
            self.add_secret_version(secret_id, secret_value)
            
            logger.info(f"Created secret: {secret_id}")
            return response.name
            
        except exceptions.AlreadyExists:
            raise ValueError(f"Secret {secret_id} already exists")
        except Exception as e:
            logger.error(f"Failed to create secret {secret_id}: {str(e)}")
            raise
    
    def get_secret(
        self,
        secret_id: str,
        version: str = "latest",
        use_cache: bool = True
    ) -> str:
        """
        Retrieve a secret value
        
        Args:
            secret_id: Secret identifier
            version: Version to retrieve (default: latest)
            use_cache: Whether to use cached value
            
        Returns:
            Secret value
        """
        # Check cache first
        cache_key = f"{secret_id}:{version}"
        if use_cache and cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if (datetime.utcnow() - cached_data['timestamp']).seconds < self._cache_ttl:
                return cached_data['value']
        
        # Build the resource name
        name = f"{self.parent}/secrets/{secret_id}/versions/{version}"
        
        try:
            # Access the secret version
            response = self.client.access_secret_version(request={"name": name})
            
            # Extract the payload
            payload = response.payload.data.decode("UTF-8")
            
            # Update cache
            if use_cache:
                self._cache[cache_key] = {
                    'value': payload,
                    'timestamp': datetime.utcnow()
                }
            
            return payload
            
        except exceptions.NotFound:
            raise ValueError(f"Secret {secret_id} version {version} not found")
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_id}: {str(e)}")
            raise
    
    def update_secret(self, secret_id: str, secret_value: str) -> str:
        """
        Update a secret by adding a new version
        
        Args:
            secret_id: Secret identifier
            secret_value: New secret value
            
        Returns:
            Version resource name
        """
        return self.add_secret_version(secret_id, secret_value)
    
    def add_secret_version(self, secret_id: str, secret_value: str) -> str:
        """
        Add a new version to an existing secret
        
        Args:
            secret_id: Secret identifier
            secret_value: Secret value
            
        Returns:
            Version resource name
        """
        # Build the parent name
        parent = f"{self.parent}/secrets/{secret_id}"
        
        # Convert the string payload to bytes
        payload = secret_value.encode("UTF-8")
        
        try:
            # Add the secret version
            response = self.client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": payload}
                }
            )
            
            # Invalidate cache for this secret
            self._invalidate_cache(secret_id)
            
            logger.info(f"Added new version to secret: {secret_id}")
            return response.name
            
        except exceptions.NotFound:
            raise ValueError(f"Secret {secret_id} not found")
        except Exception as e:
            logger.error(f"Failed to add version to secret {secret_id}: {str(e)}")
            raise
    
    def delete_secret(self, secret_id: str) -> None:
        """
        Delete a secret and all its versions
        
        Args:
            secret_id: Secret identifier
        """
        name = f"{self.parent}/secrets/{secret_id}"
        
        try:
            self.client.delete_secret(request={"name": name})
            
            # Invalidate cache
            self._invalidate_cache(secret_id)
            
            logger.info(f"Deleted secret: {secret_id}")
            
        except exceptions.NotFound:
            raise ValueError(f"Secret {secret_id} not found")
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_id}: {str(e)}")
            raise
    
    def list_secrets(self, filter_string: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all secrets in the project
        
        Args:
            filter_string: Optional filter (e.g., "labels.env:production")
            
        Returns:
            List of secret metadata
        """
        request = {"parent": self.parent}
        if filter_string:
            request["filter"] = filter_string
        
        secrets = []
        try:
            # List all secrets
            for secret in self.client.list_secrets(request=request):
                secrets.append({
                    "name": secret.name,
                    "secret_id": secret.name.split("/")[-1],
                    "create_time": secret.create_time.isoformat(),
                    "labels": dict(secret.labels) if secret.labels else {},
                    "replication": self._get_replication_info(secret)
                })
            
            return secrets
            
        except Exception as e:
            logger.error(f"Failed to list secrets: {str(e)}")
            raise
    
    def secret_exists(self, secret_id: str) -> bool:
        """Check if a secret exists"""
        name = f"{self.parent}/secrets/{secret_id}"
        
        try:
            self.client.get_secret(request={"name": name})
            return True
        except exceptions.NotFound:
            return False
        except Exception as e:
            logger.error(f"Failed to check secret existence: {str(e)}")
            raise
    
    def enable_secret_version(self, secret_id: str, version: str) -> None:
        """Enable a disabled secret version"""
        name = f"{self.parent}/secrets/{secret_id}/versions/{version}"
        
        try:
            self.client.enable_secret_version(request={"name": name})
            logger.info(f"Enabled secret version: {secret_id}:{version}")
        except Exception as e:
            logger.error(f"Failed to enable secret version: {str(e)}")
            raise
    
    def disable_secret_version(self, secret_id: str, version: str) -> None:
        """Disable a secret version"""
        name = f"{self.parent}/secrets/{secret_id}/versions/{version}"
        
        try:
            self.client.disable_secret_version(request={"name": name})
            
            # Invalidate cache
            self._invalidate_cache(secret_id, version)
            
            logger.info(f"Disabled secret version: {secret_id}:{version}")
        except Exception as e:
            logger.error(f"Failed to disable secret version: {str(e)}")
            raise
    
    def destroy_secret_version(self, secret_id: str, version: str) -> None:
        """Permanently destroy a secret version"""
        name = f"{self.parent}/secrets/{secret_id}/versions/{version}"
        
        try:
            self.client.destroy_secret_version(request={"name": name})
            
            # Invalidate cache
            self._invalidate_cache(secret_id, version)
            
            logger.info(f"Destroyed secret version: {secret_id}:{version}")
        except Exception as e:
            logger.error(f"Failed to destroy secret version: {str(e)}")
            raise
    
    def get_secret_metadata(self, secret_id: str) -> Dict[str, Any]:
        """Get metadata about a secret"""
        name = f"{self.parent}/secrets/{secret_id}"
        
        try:
            secret = self.client.get_secret(request={"name": name})
            
            # List versions
            versions = []
            for version in self.client.list_secret_versions(request={"parent": name}):
                versions.append({
                    "version": version.name.split("/")[-1],
                    "state": version.state.name,
                    "create_time": version.create_time.isoformat(),
                    "destroy_time": version.destroy_time.isoformat() if version.destroy_time else None
                })
            
            return {
                "name": secret.name,
                "secret_id": secret_id,
                "create_time": secret.create_time.isoformat(),
                "labels": dict(secret.labels) if secret.labels else {},
                "replication": self._get_replication_info(secret),
                "versions": versions,
                "version_count": len(versions)
            }
            
        except exceptions.NotFound:
            raise ValueError(f"Secret {secret_id} not found")
        except Exception as e:
            logger.error(f"Failed to get secret metadata: {str(e)}")
            raise
    
    def rotate_secret(
        self,
        secret_id: str,
        new_value: str,
        disable_previous: bool = True
    ) -> str:
        """
        Rotate a secret by adding new version and optionally disabling previous
        
        Args:
            secret_id: Secret identifier
            new_value: New secret value
            disable_previous: Whether to disable the previous version
            
        Returns:
            New version resource name
        """
        # Get current version before rotation
        current_version = None
        if disable_previous:
            try:
                metadata = self.get_secret_metadata(secret_id)
                active_versions = [
                    v for v in metadata['versions'] 
                    if v['state'] == 'ENABLED'
                ]
                if active_versions:
                    current_version = active_versions[0]['version']
            except Exception:
                pass
        
        # Add new version
        new_version = self.add_secret_version(secret_id, new_value)
        
        # Disable previous version if requested
        if disable_previous and current_version:
            try:
                self.disable_secret_version(secret_id, current_version)
            except Exception as e:
                logger.warning(f"Failed to disable previous version: {str(e)}")
        
        return new_version
    
    def _get_replication_info(self, secret) -> Dict[str, Any]:
        """Extract replication information from secret"""
        replication = secret.replication
        
        if hasattr(replication, 'automatic') and replication.automatic:
            return {"type": "automatic"}
        elif hasattr(replication, 'user_managed') and replication.user_managed:
            replicas = []
            for replica in replication.user_managed.replicas:
                replicas.append({
                    "location": replica.location,
                    "kms_key": replica.customer_managed_encryption.kms_key_name
                    if replica.customer_managed_encryption else None
                })
            return {"type": "user_managed", "replicas": replicas}
        else:
            return {"type": "unknown"}
    
    def _invalidate_cache(self, secret_id: str, version: Optional[str] = None):
        """Invalidate cached secret values"""
        if version:
            cache_key = f"{secret_id}:{version}"
            self._cache.pop(cache_key, None)
        else:
            # Invalidate all versions of this secret
            keys_to_remove = [
                k for k in self._cache.keys() 
                if k.startswith(f"{secret_id}:")
            ]
            for key in keys_to_remove:
                self._cache.pop(key, None)


# Convenience functions for Flask integration
@lru_cache(maxsize=128)
def get_secret(secret_id: str, version: str = "latest") -> str:
    """
    Get a secret value (with caching)
    
    Args:
        secret_id: Secret identifier
        version: Version to retrieve
        
    Returns:
        Secret value
    """
    manager = SecretsManager()
    return manager.get_secret(secret_id, version)


def get_database_url() -> str:
    """Get database URL from Secret Manager"""
    try:
        return get_secret("database-url")
    except Exception:
        # Fallback to environment variable
        return os.environ.get('DATABASE_URL', '')


def get_redis_url() -> str:
    """Get Redis URL from Secret Manager"""
    try:
        return get_secret("redis-url")
    except Exception:
        # Fallback to environment variable
        return os.environ.get('REDIS_URL', '')


def get_api_key(service: str) -> str:
    """Get API key for a service from Secret Manager"""
    try:
        return get_secret(f"{service}-api-key")
    except Exception:
        # Fallback to environment variable
        return os.environ.get(f'{service.upper()}_API_KEY', '')


def get_jwt_secret() -> str:
    """Get JWT secret from Secret Manager"""
    try:
        return get_secret("jwt-secret-key")
    except Exception:
        # Fallback to environment variable
        return os.environ.get('JWT_SECRET_KEY', '')


# Initialize secrets on startup
def init_app_secrets(app):
    """
    Initialize application with secrets from Secret Manager
    
    Args:
        app: Flask application instance
    """
    if not app.config.get('TESTING'):
        try:
            manager = SecretsManager()
            
            # Load critical secrets
            secrets_to_load = [
                ('SECRET_KEY', 'app-secret-key'),
                ('JWT_SECRET_KEY', 'jwt-secret-key'),
                ('DATABASE_URL', 'database-url'),
                ('REDIS_URL', 'redis-url'),
                ('SENDGRID_API_KEY', 'sendgrid-api-key'),
                ('OPENAI_API_KEY', 'openai-api-key'),
                ('SENTRY_DSN', 'sentry-dsn'),
            ]
            
            for config_key, secret_id in secrets_to_load:
                try:
                    if not app.config.get(config_key):
                        value = manager.get_secret(secret_id)
                        app.config[config_key] = value
                        logger.info(f"Loaded {config_key} from Secret Manager")
                except Exception as e:
                    logger.warning(f"Failed to load {config_key} from Secret Manager: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to initialize secrets: {str(e)}")
            # Continue with environment variables or defaults