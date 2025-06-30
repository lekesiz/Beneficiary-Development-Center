-- PostgreSQL setup script for BDC Platform
-- Run this script as a PostgreSQL superuser

-- Create database
CREATE DATABASE bdc_db;

-- Create user
CREATE USER bdc_user WITH ENCRYPTED PASSWORD 'bdc_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE bdc_db TO bdc_user;

-- Connect to the database
\c bdc_db;

-- Create schema
CREATE SCHEMA IF NOT EXISTS bdc AUTHORIZATION bdc_user;

-- Set default search path
ALTER USER bdc_user SET search_path TO bdc, public;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant schema privileges
GRANT ALL ON SCHEMA bdc TO bdc_user;
GRANT ALL ON SCHEMA public TO bdc_user;

-- Create initial tables will be handled by Alembic migrations
-- Just ensure the user has the right permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA bdc GRANT ALL ON TABLES TO bdc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA bdc GRANT ALL ON SEQUENCES TO bdc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bdc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bdc_user;

-- Instructions:
-- 1. Install PostgreSQL if not already installed
-- 2. Run this script: psql -U postgres -f setup_postgresql.sql
-- 3. Update DATABASE_URL in .env with actual password
-- 4. Run Alembic migrations: flask db upgrade