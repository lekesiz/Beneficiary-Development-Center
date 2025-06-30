# CLAUDE.md - BDC Platform Development Notes

## Overview
This document contains important development notes and context for the BDC (Beneficiary Development Center) platform to help Claude Code understand the codebase and recent changes.

## Recent JWT Authentication Fix (2025-06-27)

### Issue
The platform was experiencing widespread JWT authentication errors across multiple endpoints. Users could login successfully but immediately received 401 Unauthorized errors when accessing protected endpoints.

### Root Cause
Flask-JWT-Extended expects the JWT identity (`sub` claim) to be a string, but the code was passing integer user IDs. This caused the error: "Subject must be a string".

### Solution
1. **Updated token generation** in `/backend/app/api/v1/auth.py`:
   - Changed `identity=user.id` to `identity=str(user.id)` when creating tokens
   
2. **Created utility function** in `/backend/app/core/jwt_utils.py`:
   - `get_current_user_id()` handles conversion from string back to integer
   
3. **Updated all endpoints** to use the new utility:
   - Replaced `get_jwt_identity()` with `get_current_user_id()`
   - Added proper error handling for invalid identities
   
4. **Fixed JWT callbacks** in `/backend/app/__init__.py` and `/backend/app/core/jwt_error_handler.py`:
   - Added string-to-integer conversion in user lookup callbacks

### Testing Commands
```bash
# Login and get token
TOKEN=$(curl -s -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: 1" \
  -d '{"email": "admin@bdc.local", "password": "admin123"}' | jq -r '.access_token')

# Test protected endpoint
curl -X GET http://localhost:5001/api/v1/beneficiaries \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 1"
```

## Authentication Headers
All API requests require:
- `Authorization: Bearer <JWT_TOKEN>` - The JWT access token
- `X-Tenant-ID: <TENANT_ID>` - The tenant ID (usually 1 for development)

## Development Environment Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python simple_seed.py  # Seeds database with test data
python wsgi.py  # Runs on port 5001
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Runs on port 3000
```

### Test Credentials
- Email: `admin@bdc.local`
- Password: `admin123`
- Tenant ID: `1`

## Key Architecture Decisions

### Multi-tenant Architecture
- All models include `tenant_id` for data isolation
- Tenant ID must be included in request headers
- SQLAlchemy queries automatically filter by tenant

### JWT Token Management
- Access tokens expire in 24 hours
- Refresh tokens expire in 30 days
- Tokens include tenant_id and user role in claims

### Password Hashing
- Uses Argon2 for password hashing (not Werkzeug)
- Configured in User model's `set_password` method

## Common Issues and Solutions

### Redis Connection Errors
- The app has fallback to in-memory cache when Redis is unavailable
- Safe to ignore Redis warnings in development

### CORS Issues
- Frontend runs on port 3000, backend on port 5001
- CORS is configured to allow credentials and required headers

### Database Issues
- Using SQLite for development (bdc.db file)
- Run `python simple_seed.py` to reset database with test data

## Testing Shortcuts

### Quick API Test
```bash
# All-in-one test command
curl -s -X GET http://localhost:5001/api/v1/auth/me \
  -H "Authorization: Bearer $(curl -s -X POST http://localhost:5001/api/v1/auth/login -H 'Content-Type: application/json' -H 'X-Tenant-ID: 1' -d '{"email": "admin@bdc.local", "password": "admin123"}' | jq -r '.access_token')" \
  -H "X-Tenant-ID: 1" | jq .
```

## Recent Bug Fixes (2025-06-29)

### Pagination Undefined Errors
All pagination access now uses optional chaining to prevent "Cannot read properties of undefined" errors:
- Change `data?.pagination.pages` to `data?.pagination?.pages`
- Affected files: EvaluationList, CoachNotesManager, CoachDashboard, QuestionBank, BeneficiaryList

### React Error #306 Fix
The `useToast` hook returns an object with methods, not a function:
```javascript
// Wrong
const toast = useToast();
toast('message', 'error');

// Correct
const { error: toastError, success: toastSuccess } = useToast();
toastError('message');
```

### toFixed Undefined Errors
Always use optional chaining with numeric operations:
```javascript
// Wrong
value.toFixed(1)

// Correct
value?.toFixed(1) || '0.0'
```

### Dynamic Import Errors
If you encounter "Failed to fetch dynamically imported module" errors:
1. Clear build cache: `rm -rf dist node_modules/.vite`
2. Rebuild: `npm run build`
3. Redeploy: `gcloud app deploy --quiet`

## Production Database Setup (PostgreSQL)

### Quick Setup
1. Install PostgreSQL
2. Run setup script: `psql -U postgres -f backend/scripts/setup_postgresql.sql`
3. Copy environment: `cp backend/.env.production.example backend/.env.production`
4. Update DATABASE_URL in `.env.production`
5. Test connection: `python backend/test_postgresql_connection.py`
6. Run migrations: `cd backend && flask db upgrade`

### Google Cloud SQL
For App Engine deployment:
```yaml
env_variables:
  DATABASE_URL: postgresql://user:pass@/db?host=/cloudsql/PROJECT:REGION:INSTANCE

beta_settings:
  cloud_sql_instances: PROJECT:REGION:INSTANCE
```

See `backend/docs/POSTGRESQL_SETUP.md` for detailed instructions.

## Recent Improvements (2025-06-30)
- ✅ Replaced console.log toast with react-hot-toast
- ✅ Error Boundary already implemented
- ✅ Fixed all critical API endpoint errors
- ✅ Set up PostgreSQL configuration for production

## Future Improvements
- Implement proper Redis connection for production
- Add comprehensive test suite for JWT authentication
- Consider using UUID for JWT identities instead of string conversion
- Implement proper loading states for all async operations
- Add more API endpoint implementations for 404 errors