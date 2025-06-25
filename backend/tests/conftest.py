"""Pytest configuration and fixtures."""
import pytest
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.beneficiary import Beneficiary, BeneficiaryStatus
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    # Set test configuration
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    return app


@pytest.fixture(scope='session')
def engine():
    """Create test database engine."""
    return create_engine('sqlite:///:memory:')


@pytest.fixture(scope='session')
def tables(app):
    """Create all tables."""
    with app.app_context():
        db.create_all()
        yield
        db.drop_all()


@pytest.fixture(scope='function')
def db_session(app, tables):
    """Create a new database session for each test."""
    with app.app_context():
        # Start a transaction
        db.session.begin()
        yield db.session
        # Rollback the transaction
        db.session.rollback()


@pytest.fixture(scope='function')
def client(app, db_session):
    """Create test client."""
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def test_tenant(db_session):
    """Create test tenant."""
    tenant = Tenant(
        name='Test Organization',
        subdomain='test-org',
        is_active=True,
        settings={'locale': 'en', 'timezone': 'UTC'}
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def super_admin_user(db_session, test_tenant):
    """Create super admin user."""
    user = User(
        email='superadmin@test.com',
        username='superadmin',
        password_hash=generate_password_hash('Test123!@#'),
        first_name='Super',
        last_name='Admin',
        role='super_admin',
        tenant_id=test_tenant.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session, test_tenant):
    """Create admin user."""
    user = User(
        email='admin@test.com',
        username='admin',
        password_hash=generate_password_hash('password123'),
        first_name='Admin',
        last_name='User',
        role='admin',
        tenant_id=test_tenant.id,
        is_active=True
    )
    user.set_password('password123')  # Ensure password is set properly
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def manager_user(db_session, test_tenant):
    """Create manager user."""
    user = User(
        email='manager@test.com',
        username='manager',
        password_hash=generate_password_hash('password123'),
        first_name='Manager',
        last_name='User',
        role='manager',
        tenant_id=test_tenant.id,
        is_active=True
    )
    user.set_password('password123')  # Ensure password is set properly
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def instructor_user(db_session, test_tenant):
    """Create instructor user."""
    user = User(
        email='instructor@test.com',
        username='instructor',
        password_hash=generate_password_hash('password123'),
        first_name='Instructor',
        last_name='User',
        role='instructor',
        tenant_id=test_tenant.id,
        is_active=True
    )
    user.set_password('password123')  # Ensure password is set properly
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def staff_user(db_session, test_tenant):
    """Create staff user."""
    user = User(
        email='staff@test.com',
        username='staff',
        password_hash=generate_password_hash('password123'),
        first_name='Staff',
        last_name='User',
        role='staff',
        tenant_id=test_tenant.id,
        is_active=True
    )
    user.set_password('password123')  # Ensure password is set properly
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def trainer_user(db_session, test_tenant):
    """Create trainer user."""
    user = User(
        email='trainer@test.com',
        username='trainer',
        password_hash=generate_password_hash('Test123!@#'),
        first_name='Trainer',
        last_name='User',
        role='trainer',
        tenant_id=test_tenant.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_user(db_session, test_tenant):
    """Create student user."""
    user = User(
        email='student@test.com',
        username='student',
        password_hash=generate_password_hash('Test123!@#'),
        first_name='Student',
        last_name='User',
        role='student',
        tenant_id=test_tenant.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_beneficiary(db_session, test_tenant, admin_user):
    """Create test beneficiary."""
    beneficiary = Beneficiary(
        tenant_id=test_tenant.id,
        first_name='John',
        last_name='Doe',
        email='john.doe@test.com',
        phone='+33123456789',
        status=BeneficiaryStatus.ACTIVE,
        created_by=admin_user.id,
        date_of_birth=datetime(1990, 1, 1).date()
    )
    db_session.add(beneficiary)
    db_session.commit()
    db_session.refresh(beneficiary)
    return beneficiary


@pytest.fixture
def multiple_beneficiaries(db_session, test_tenant, admin_user, trainer_user):
    """Create multiple test beneficiaries."""
    beneficiaries = []
    
    # Create 5 active beneficiaries
    for i in range(5):
        ben = Beneficiary(
            tenant_id=test_tenant.id,
            first_name=f'Test{i}',
            last_name=f'Beneficiary{i}',
            email=f'test{i}@example.com',
            phone=f'+3312345678{i}',
            status=BeneficiaryStatus.ACTIVE,
            created_by=admin_user.id,
            assigned_trainer_id=trainer_user.id if i % 2 == 0 else None,
            tags=['tag1', 'tag2'] if i % 3 == 0 else ['tag3']
        )
        beneficiaries.append(ben)
        db_session.add(ben)
    
    # Create 2 inactive beneficiaries
    for i in range(2):
        ben = Beneficiary(
            tenant_id=test_tenant.id,
            first_name=f'Inactive{i}',
            last_name=f'User{i}',
            email=f'inactive{i}@example.com',
            status=BeneficiaryStatus.INACTIVE,
            created_by=admin_user.id
        )
        beneficiaries.append(ben)
        db_session.add(ben)
    
    db_session.commit()
    for ben in beneficiaries:
        db_session.refresh(ben)
    
    return beneficiaries


@pytest.fixture
def auth_headers(client, admin_user):
    """Get authentication headers for admin user."""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        access_token = create_access_token(
            identity=admin_user.id,
            additional_claims={
                'tenant_id': admin_user.tenant_id,
                'role': admin_user.role
            }
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def trainer_auth_headers(client, trainer_user):
    """Get authentication headers for trainer user."""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        access_token = create_access_token(
            identity=trainer_user.id,
            additional_claims={
                'tenant_id': trainer_user.tenant_id,
                'role': trainer_user.role
            }
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def student_auth_headers(client, student_user):
    """Get authentication headers for student user."""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        access_token = create_access_token(
            identity=str(student_user.id),
            additional_claims={
                'tenant_id': student_user.tenant_id,
                'role': student_user.role
            }
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def admin_headers(client, admin_user):
    """Get authentication headers for admin user (alias for auth_headers)."""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        access_token = create_access_token(
            identity=str(admin_user.id),
            additional_claims={
                'tenant_id': admin_user.tenant_id,
                'role': admin_user.role
            }
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def manager_headers(client, manager_user):
    """Get authentication headers for manager user."""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        access_token = create_access_token(
            identity=str(manager_user.id),
            additional_claims={
                'tenant_id': manager_user.tenant_id,
                'role': manager_user.role
            }
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def instructor_headers(client, instructor_user):
    """Get authentication headers for instructor user."""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        access_token = create_access_token(
            identity=str(instructor_user.id),
            additional_claims={
                'tenant_id': instructor_user.tenant_id,
                'role': instructor_user.role
            }
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def staff_headers(client, staff_user):
    """Get authentication headers for staff user."""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        access_token = create_access_token(
            identity=str(staff_user.id),
            additional_claims={
                'tenant_id': staff_user.tenant_id,
                'role': staff_user.role
            }
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def multi_tenant_setup(db_session):
    """Create multiple tenants with users for testing multi-tenant scenarios."""
    from app.models.tenant import Tenant
    from app.models.user import User
    
    # Create two additional tenants
    tenant2 = Tenant(
        name='Second Organization',
        subdomain='org2',
        is_active=True,
        settings={'locale': 'fr', 'timezone': 'Europe/Paris'}
    )
    tenant3 = Tenant(
        name='Third Organization',
        subdomain='org3',
        is_active=True,
        settings={'locale': 'es', 'timezone': 'America/Mexico_City'}
    )
    
    db_session.add_all([tenant2, tenant3])
    db_session.commit()
    
    # Create admin user for each tenant
    admin2 = User(
        email='admin@org2.com',
        username='admin_org2',
        password_hash=generate_password_hash('password123'),
        first_name='Admin',
        last_name='Org2',
        role='admin',
        tenant_id=tenant2.id,
        is_active=True
    )
    
    admin3 = User(
        email='admin@org3.com',
        username='admin_org3',
        password_hash=generate_password_hash('password123'),
        first_name='Admin',
        last_name='Org3',
        role='admin',
        tenant_id=tenant3.id,
        is_active=True
    )
    
    db_session.add_all([admin2, admin3])
    db_session.commit()
    
    return {
        'tenant2': tenant2,
        'tenant3': tenant3,
        'admin2': admin2,
        'admin3': admin3
    }


@pytest.fixture
def api_client(client):
    """Wrapper for API client with helper methods."""
    class APIClient:
        def __init__(self, test_client):
            self.client = test_client
            
        def get(self, url, headers=None, **kwargs):
            return self.client.get(url, headers=headers, **kwargs)
            
        def post(self, url, json=None, headers=None, **kwargs):
            return self.client.post(url, json=json, headers=headers, **kwargs)
            
        def put(self, url, json=None, headers=None, **kwargs):
            return self.client.put(url, json=json, headers=headers, **kwargs)
            
        def delete(self, url, headers=None, **kwargs):
            return self.client.delete(url, headers=headers, **kwargs)
            
        def login(self, email, password):
            response = self.post('/api/v1/auth/login', json={
                'email': email,
                'password': password
            })
            if response.status_code == 200:
                data = response.get_json()
                return {
                    'Authorization': f'Bearer {data["access_token"]}',
                    'X-Tenant-ID': str(data['user']['tenant_id'])
                }
            return None
    
    return APIClient(client)


@pytest.fixture
def sample_program_data():
    """Sample data for creating programs."""
    return {
        'code': 'TEST-PRG-001',
        'name': 'Test Program',
        'description': 'A test program for unit tests',
        'category': 'education',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'budget': 50000.00,
        'objectives': {
            'primary': ['Objective 1', 'Objective 2'],
            'secondary': ['Secondary objective']
        },
        'eligibility_criteria': {
            'min_age': 18,
            'max_age': 65,
            'requirements': ['Requirement 1']
        }
    }


@pytest.fixture
def sample_course_data():
    """Sample data for creating courses."""
    return {
        'code': 'TEST-CRS-001',
        'name': 'Test Course',
        'description': 'A test course for unit tests',
        'course_type': 'lecture',
        'credits': 3,
        'duration_hours': 40,
        'max_students': 30,
        'prerequisites': ['Basic knowledge'],
        'learning_outcomes': ['Outcome 1', 'Outcome 2']
    }