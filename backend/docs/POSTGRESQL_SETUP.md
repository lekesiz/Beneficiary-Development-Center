# PostgreSQL Setup Guide for BDC Platform

This guide walks you through setting up PostgreSQL for the BDC platform in production.

## Prerequisites

- PostgreSQL 12+ installed
- Python 3.11+ with pip
- Access to PostgreSQL with superuser privileges

## Setup Steps

### 1. Install PostgreSQL

**On macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**On Windows:**
Download and install from https://www.postgresql.org/download/windows/

### 2. Create Database and User

Run the provided setup script:

```bash
cd backend
psql -U postgres -f scripts/setup_postgresql.sql
```

Or manually:

```sql
-- Connect as superuser
psql -U postgres

-- Create database
CREATE DATABASE bdc_db;

-- Create user
CREATE USER bdc_user WITH ENCRYPTED PASSWORD 'your-secure-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE bdc_db TO bdc_user;

-- Connect to database
\c bdc_db

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### 3. Configure Environment

Copy the production environment template:

```bash
cp .env.production.example .env.production
```

Update the DATABASE_URL in `.env.production`:

```env
# For local PostgreSQL
DATABASE_URL=postgresql://bdc_user:your-secure-password@localhost:5432/bdc_db

# For Google Cloud SQL
DATABASE_URL=postgresql://bdc_user:password@/bdc_db?host=/cloudsql/PROJECT:REGION:INSTANCE

# For external PostgreSQL
DATABASE_URL=postgresql://bdc_user:password@your-host:5432/bdc_db
```

### 4. Test Connection

Run the test script:

```bash
python test_postgresql_connection.py
```

Expected output:
```
🔍 PostgreSQL Connection Test for BDC Platform
==================================================
Testing connection to: postgresql://****:****@localhost:5432/bdc_db
✅ Successfully connected to PostgreSQL!
📊 Database version: PostgreSQL 14.5 on x86_64-apple-darwin21.6.0
📁 Connected to database: bdc_db
👤 Connected as user: bdc_user
✅ uuid-ossp extension is installed
✅ pgcrypto extension is installed
📊 Number of tables in database: 0

✅ Database connection test passed!
You can now run migrations with: flask db upgrade
```

### 5. Run Migrations

Initialize and run database migrations:

```bash
# Set environment
export FLASK_ENV=production

# Initialize migrations (if not already done)
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

### 6. Seed Initial Data (Optional)

For production, you might want to create initial data:

```python
# Create a production_seed.py script
python production_seed.py
```

## Security Best Practices

1. **Use Strong Passwords**: Generate secure passwords for database users
   ```bash
   openssl rand -base64 32
   ```

2. **Restrict Access**: Configure pg_hba.conf to limit connections
   ```
   # IPv4 local connections:
   host    bdc_db    bdc_user    127.0.0.1/32    md5
   ```

3. **Use SSL**: Enable SSL connections in production
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

4. **Regular Backups**: Set up automated backups
   ```bash
   pg_dump -U bdc_user -h localhost bdc_db > backup.sql
   ```

## Google Cloud SQL Setup

If using Google Cloud SQL:

1. Create Cloud SQL instance:
   ```bash
   gcloud sql instances create bdc-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

2. Create database and user:
   ```bash
   gcloud sql databases create bdc_db --instance=bdc-db
   gcloud sql users create bdc_user --instance=bdc-db
   ```

3. Enable Cloud SQL Admin API:
   ```bash
   gcloud services enable sqladmin.googleapis.com
   ```

4. Update app.yaml:
   ```yaml
   env_variables:
     DATABASE_URL: postgresql://bdc_user:password@/bdc_db?host=/cloudsql/PROJECT:REGION:INSTANCE
   
   beta_settings:
     cloud_sql_instances: PROJECT:REGION:INSTANCE
   ```

## Troubleshooting

### Connection Refused
- Check if PostgreSQL is running: `pg_isready`
- Verify port 5432 is not blocked
- Check pg_hba.conf allows connections

### Authentication Failed
- Verify username and password
- Check user has proper permissions
- Ensure pg_hba.conf uses md5 or scram-sha-256

### Database Does Not Exist
- Create database: `CREATE DATABASE bdc_db;`
- Grant permissions: `GRANT ALL ON DATABASE bdc_db TO bdc_user;`

### Extension Not Found
- Connect as superuser to install extensions
- Some cloud providers pre-install common extensions

## Monitoring

Set up monitoring for production:

1. **Connection Pool**: Monitor active connections
2. **Query Performance**: Use pg_stat_statements
3. **Disk Usage**: Monitor database size
4. **Backup Status**: Verify backups are running

## Next Steps

After PostgreSQL is set up:

1. Run application tests
2. Configure backup strategy
3. Set up monitoring
4. Configure replication (optional)
5. Deploy to production