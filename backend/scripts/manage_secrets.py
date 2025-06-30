#!/usr/bin/env python3
"""
Secret management CLI for BDC Platform
Helps manage secrets in Google Secret Manager
"""

import os
import sys
import json
import click
import getpass
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.secrets_manager import SecretsManager


@click.group()
@click.option('--project-id', envvar='GOOGLE_CLOUD_PROJECT', help='GCP Project ID')
@click.pass_context
def cli(ctx, project_id):
    """BDC Platform Secret Management CLI"""
    if not project_id:
        click.echo("Error: Project ID is required. Set GOOGLE_CLOUD_PROJECT or use --project-id")
        sys.exit(1)
    
    ctx.ensure_object(dict)
    ctx.obj['manager'] = SecretsManager(project_id=project_id)
    ctx.obj['project_id'] = project_id


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize required secrets for BDC Platform"""
    manager = ctx.obj['manager']
    
    click.echo("Initializing BDC Platform secrets...")
    
    required_secrets = [
        {
            'id': 'app-secret-key',
            'description': 'Flask application secret key',
            'generate': True
        },
        {
            'id': 'jwt-secret-key',
            'description': 'JWT signing secret key',
            'generate': True
        },
        {
            'id': 'database-url',
            'description': 'PostgreSQL database URL',
            'prompt': 'Enter database URL'
        },
        {
            'id': 'redis-url',
            'description': 'Redis connection URL',
            'prompt': 'Enter Redis URL'
        },
        {
            'id': 'sendgrid-api-key',
            'description': 'SendGrid API key for emails',
            'prompt': 'Enter SendGrid API key (optional)',
            'optional': True
        },
        {
            'id': 'openai-api-key',
            'description': 'OpenAI API key for AI features',
            'prompt': 'Enter OpenAI API key (optional)',
            'optional': True
        },
        {
            'id': 'sentry-dsn',
            'description': 'Sentry DSN for error tracking',
            'prompt': 'Enter Sentry DSN (optional)',
            'optional': True
        },
        {
            'id': 'cloud-sql-connection',
            'description': 'Cloud SQL connection name',
            'prompt': 'Enter Cloud SQL connection name'
        }
    ]
    
    for secret_config in required_secrets:
        secret_id = secret_config['id']
        description = secret_config['description']
        
        # Check if secret already exists
        if manager.secret_exists(secret_id):
            if click.confirm(f"Secret '{secret_id}' already exists. Update it?"):
                if secret_config.get('generate'):
                    import secrets
                    value = secrets.token_urlsafe(64)
                else:
                    value = getpass.getpass(f"{secret_config.get('prompt', 'Enter value')}: ")
                    if not value and secret_config.get('optional'):
                        continue
                
                manager.update_secret(secret_id, value)
                click.echo(f"✓ Updated: {secret_id}")
        else:
            click.echo(f"\nCreating secret: {secret_id}")
            click.echo(f"Description: {description}")
            
            if secret_config.get('generate'):
                import secrets
                value = secrets.token_urlsafe(64)
                click.echo("Generated random value")
            else:
                value = getpass.getpass(f"{secret_config.get('prompt', 'Enter value')}: ")
                if not value and secret_config.get('optional'):
                    click.echo("Skipping optional secret")
                    continue
            
            labels = {
                'app': 'bdc-platform',
                'environment': 'production',
                'managed-by': 'cli'
            }
            
            manager.create_secret(secret_id, value, labels=labels)
            click.echo(f"✓ Created: {secret_id}")
    
    click.echo("\n✅ Secret initialization complete!")


@cli.command()
@click.argument('secret_id')
@click.option('--value', help='Secret value (will prompt if not provided)')
@click.option('--from-file', type=click.Path(exists=True), help='Read value from file')
@click.option('--label', multiple=True, help='Labels in key=value format')
@click.pass_context
def create(ctx, secret_id, value, from_file, label):
    """Create a new secret"""
    manager = ctx.obj['manager']
    
    # Get value
    if from_file:
        with open(from_file, 'r') as f:
            secret_value = f.read().strip()
    elif value:
        secret_value = value
    else:
        secret_value = getpass.getpass("Enter secret value: ")
    
    # Parse labels
    labels = {}
    for l in label:
        if '=' in l:
            k, v = l.split('=', 1)
            labels[k] = v
    
    # Add default labels
    labels.update({
        'app': 'bdc-platform',
        'managed-by': 'cli'
    })
    
    try:
        manager.create_secret(secret_id, secret_value, labels=labels)
        click.echo(f"✓ Created secret: {secret_id}")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('secret_id')
@click.option('--version', default='latest', help='Version to retrieve')
@click.option('--output', '-o', type=click.Choice(['text', 'json']), default='text')
@click.pass_context
def get(ctx, secret_id, version, output):
    """Get a secret value"""
    manager = ctx.obj['manager']
    
    try:
        value = manager.get_secret(secret_id, version=version)
        
        if output == 'json':
            click.echo(json.dumps({'secret_id': secret_id, 'value': value}))
        else:
            click.echo(value)
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('secret_id')
@click.option('--value', help='New secret value (will prompt if not provided)')
@click.option('--from-file', type=click.Path(exists=True), help='Read value from file')
@click.option('--disable-previous', is_flag=True, help='Disable previous version')
@click.pass_context
def update(ctx, secret_id, value, from_file, disable_previous):
    """Update a secret value"""
    manager = ctx.obj['manager']
    
    # Get value
    if from_file:
        with open(from_file, 'r') as f:
            secret_value = f.read().strip()
    elif value:
        secret_value = value
    else:
        secret_value = getpass.getpass("Enter new secret value: ")
    
    try:
        if disable_previous:
            version = manager.rotate_secret(secret_id, secret_value, disable_previous=True)
            click.echo(f"✓ Rotated secret: {secret_id}")
        else:
            version = manager.update_secret(secret_id, secret_value)
            click.echo(f"✓ Updated secret: {secret_id}")
        
        click.echo(f"  New version: {version.split('/')[-1]}")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--filter', help='Filter expression (e.g., labels.env:production)')
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
def list(ctx, filter, format):
    """List all secrets"""
    manager = ctx.obj['manager']
    
    try:
        secrets = manager.list_secrets(filter_string=filter)
        
        if format == 'json':
            click.echo(json.dumps(secrets, indent=2))
        else:
            if not secrets:
                click.echo("No secrets found")
                return
            
            # Table format
            click.echo(f"\nSecrets in project: {ctx.obj['project_id']}\n")
            click.echo(f"{'Secret ID':<30} {'Created':<20} {'Labels'}")
            click.echo("-" * 80)
            
            for secret in secrets:
                labels_str = ', '.join(f"{k}={v}" for k, v in secret['labels'].items())
                created = secret['create_time'][:19]  # Trim microseconds
                click.echo(f"{secret['secret_id']:<30} {created:<20} {labels_str}")
            
            click.echo(f"\nTotal: {len(secrets)} secrets")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('secret_id')
@click.confirmation_option(prompt='Are you sure you want to delete this secret?')
@click.pass_context
def delete(ctx, secret_id):
    """Delete a secret"""
    manager = ctx.obj['manager']
    
    try:
        manager.delete_secret(secret_id)
        click.echo(f"✓ Deleted secret: {secret_id}")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('secret_id')
@click.pass_context
def info(ctx, secret_id):
    """Get detailed information about a secret"""
    manager = ctx.obj['manager']
    
    try:
        metadata = manager.get_secret_metadata(secret_id)
        
        click.echo(f"\nSecret: {secret_id}")
        click.echo(f"Created: {metadata['create_time']}")
        click.echo(f"Replication: {metadata['replication']['type']}")
        
        if metadata['labels']:
            click.echo("\nLabels:")
            for k, v in metadata['labels'].items():
                click.echo(f"  {k}: {v}")
        
        click.echo(f"\nVersions ({metadata['version_count']} total):")
        for version in metadata['versions'][:5]:  # Show latest 5
            state_indicator = "✓" if version['state'] == "ENABLED" else "✗"
            click.echo(f"  {state_indicator} {version['version']:<10} {version['state']:<15} {version['create_time']}")
        
        if metadata['version_count'] > 5:
            click.echo(f"  ... and {metadata['version_count'] - 5} more")
            
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def export_env(ctx):
    """Export secrets as environment variables"""
    manager = ctx.obj['manager']
    
    click.echo("# BDC Platform Environment Variables")
    click.echo(f"# Project: {ctx.obj['project_id']}")
    click.echo()
    
    # Map of secret IDs to environment variable names
    secret_env_map = {
        'app-secret-key': 'SECRET_KEY',
        'jwt-secret-key': 'JWT_SECRET_KEY',
        'database-url': 'DATABASE_URL',
        'redis-url': 'REDIS_URL',
        'sendgrid-api-key': 'SENDGRID_API_KEY',
        'openai-api-key': 'OPENAI_API_KEY',
        'sentry-dsn': 'SENTRY_DSN',
        'cloud-sql-connection': 'CLOUD_SQL_CONNECTION_NAME'
    }
    
    for secret_id, env_var in secret_env_map.items():
        try:
            value = manager.get_secret(secret_id)
            click.echo(f'export {env_var}="{value}"')
        except Exception:
            click.echo(f'# export {env_var}="<not found>"')


@cli.command()
@click.option('--env', type=click.Choice(['production', 'staging']), default='production')
@click.pass_context
def validate(ctx, env):
    """Validate that all required secrets exist"""
    manager = ctx.obj['manager']
    
    click.echo(f"Validating secrets for {env} environment...\n")
    
    required_secrets = [
        'app-secret-key',
        'jwt-secret-key',
        'database-url',
        'redis-url',
        'cloud-sql-connection'
    ]
    
    optional_secrets = [
        'sendgrid-api-key',
        'openai-api-key',
        'sentry-dsn'
    ]
    
    all_valid = True
    
    # Check required secrets
    click.echo("Required secrets:")
    for secret_id in required_secrets:
        if manager.secret_exists(secret_id):
            click.echo(f"  ✓ {secret_id}")
        else:
            click.echo(f"  ✗ {secret_id} (MISSING)", err=True)
            all_valid = False
    
    # Check optional secrets
    click.echo("\nOptional secrets:")
    for secret_id in optional_secrets:
        if manager.secret_exists(secret_id):
            click.echo(f"  ✓ {secret_id}")
        else:
            click.echo(f"  - {secret_id} (not configured)")
    
    if all_valid:
        click.echo("\n✅ All required secrets are configured!")
    else:
        click.echo("\n❌ Some required secrets are missing!", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()