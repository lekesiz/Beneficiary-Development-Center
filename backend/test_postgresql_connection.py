#!/usr/bin/env python3
"""Test PostgreSQL database connection."""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def test_connection():
    """Test PostgreSQL connection."""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in .env.production file")
        return False
    
    # Hide password in output
    display_url = database_url.replace(
        database_url.split('@')[0].split('://')[1], 
        '****:****'
    ) if '@' in database_url else database_url
    
    print(f"Testing connection to: {display_url}")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Successfully connected to PostgreSQL!")
            print(f"📊 Database version: {version}")
            
            # Test basic query
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            print(f"📁 Connected to database: {db_name}")
            print(f"👤 Connected as user: {user}")
            
            # Check for required extensions
            result = conn.execute(text("""
                SELECT extname 
                FROM pg_extension 
                WHERE extname IN ('uuid-ossp', 'pgcrypto')
            """))
            extensions = [row[0] for row in result]
            
            if 'uuid-ossp' in extensions:
                print("✅ uuid-ossp extension is installed")
            else:
                print("⚠️  uuid-ossp extension is not installed")
                
            if 'pgcrypto' in extensions:
                print("✅ pgcrypto extension is installed")
            else:
                print("⚠️  pgcrypto extension is not installed")
            
            # Check tables
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """))
            table_count = result.scalar()
            print(f"📊 Number of tables in database: {table_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check DATABASE_URL format: postgresql://user:password@host:port/database")
        print("3. Verify database, user, and password are correct")
        print("4. Check network connectivity to database server")
        print("5. Ensure user has proper permissions")
        return False

def main():
    """Main function."""
    print("🔍 PostgreSQL Connection Test for BDC Platform")
    print("=" * 50)
    
    # Check if production env file exists
    if not os.path.exists('.env.production'):
        print("⚠️  .env.production file not found")
        print("Creating from example...")
        if os.path.exists('.env.production.example'):
            import shutil
            shutil.copy('.env.production.example', '.env.production')
            print("✅ Created .env.production from example")
            print("Please update DATABASE_URL and run again")
            return
        else:
            print("❌ .env.production.example not found")
            return
    
    # Test connection
    if test_connection():
        print("\n✅ Database connection test passed!")
        print("You can now run migrations with: flask db upgrade")
    else:
        print("\n❌ Database connection test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()