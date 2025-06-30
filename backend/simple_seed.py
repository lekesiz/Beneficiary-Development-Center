#!/usr/bin/env python3
"""Simple database seeding script for local development."""

from app import create_app, db
from app.models.user import User, Role
from app.models.tenant import Tenant
from argon2 import PasswordHasher

def simple_seed():
    """Create minimal test data for development."""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting simple database seeding...")
        
        # Clear existing data
        print("🗑️  Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create default tenant
        print("🏢 Creating default tenant...")
        tenant = Tenant(
            name="Default Organization",
            domain="localhost",
            is_active=True
        )
        db.session.add(tenant)
        db.session.commit()
        
        # Create system roles
        print("🔐 Creating roles...")
        roles = [
            Role(name="admin", description="Administrator", is_system=True),
            Role(name="trainer", description="Trainer", is_system=True),
            Role(name="student", description="Student", is_system=True)
        ]
        db.session.add_all(roles)
        db.session.commit()
        
        # Create test users
        print("👥 Creating test users...")
        
        # Initialize password hasher
        ph = PasswordHasher()
        
        # Admin user
        admin = User(
            email="admin@bdc.local",
            password_hash=ph.hash("admin123"),
            first_name="Admin",
            last_name="User",
            tenant_id=tenant.id,
            is_active=True,
            is_verified=True
        )
        admin.roles.append(roles[0])  # admin role
        
        # Trainer user
        trainer = User(
            email="trainer@bdc.local", 
            password_hash=ph.hash("trainer123"),
            first_name="John",
            last_name="Trainer",
            tenant_id=tenant.id,
            is_active=True,
            is_verified=True
        )
        trainer.roles.append(roles[1])  # trainer role
        
        # Student user
        student = User(
            email="student@bdc.local",
            password_hash=ph.hash("student123"),
            first_name="Jane",
            last_name="Student",
            tenant_id=tenant.id,
            is_active=True,
            is_verified=True
        )
        student.roles.append(roles[2])  # student role
        
        db.session.add_all([admin, trainer, student])
        db.session.commit()
        
        print("\n✅ Simple database seeding completed!")
        print("   - Test users created:")
        print("     • admin@bdc.local (password: admin123)")
        print("     • trainer@bdc.local (password: trainer123)")
        print("     • student@bdc.local (password: student123)")

if __name__ == "__main__":
    simple_seed()