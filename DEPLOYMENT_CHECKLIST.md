# BDC Platform Deployment Checklist

## Pre-Deployment Checklist

### 1. Code Preparation ✅
- [x] All code changes committed
- [x] Frontend build working (`npm run build`)
- [x] Backend tests passing
- [x] API endpoints tested
- [x] PostgreSQL configuration ready

### 2. Google Cloud Setup
- [ ] Google Cloud Project created: `bilan-competence-449414`
- [ ] Billing account activated
- [ ] Required APIs enabled:
  - [ ] App Engine Admin API
  - [ ] Cloud SQL Admin API
  - [ ] Cloud Build API
  - [ ] Secret Manager API
  - [ ] Cloud Resource Manager API

### 3. Cloud SQL Setup
- [ ] Cloud SQL instance created in `europe-west1`
- [ ] Database created: `bdc_production`
- [ ] User created: `bdc_user`
- [ ] Password set securely
- [ ] VPC connector configured: `bdc-connector`

### 4. Secrets Configuration
- [ ] Generate secure SECRET_KEY:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Generate secure JWT_SECRET_KEY:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Store secrets in Google Secret Manager:
  ```bash
  echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
  echo -n "your-jwt-secret" | gcloud secrets create JWT_SECRET_KEY --data-file=-
  echo -n "your-db-password" | gcloud secrets create DB_PASSWORD --data-file=-
  ```

### 5. Environment Variables
- [ ] Update `app.yaml` with correct values
- [ ] Verify CORS_ORIGINS matches your domain
- [ ] Ensure DATABASE_URL format is correct

## Deployment Steps

### 1. Initial Setup
```bash
# Set project
gcloud config set project bilan-competence-449414

# Authenticate
gcloud auth login

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Create Cloud SQL Instance
```bash
# Create instance
gcloud sql instances create bdc-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=europe-west1

# Create database
gcloud sql databases create bdc_production --instance=bdc-db

# Set user password
gcloud sql users set-password bdc_user \
  --instance=bdc-db \
  --password=YOUR_SECURE_PASSWORD
```

### 3. Deploy Application
```bash
# Run deployment script
./deploy.sh

# Or manually:
cd frontend && npm run build && cd ..
gcloud app deploy --project=bilan-competence-449414 --quiet
```

### 4. Post-Deployment
```bash
# Run database migrations
gcloud app ssh --service=default
cd /srv
python -m flask db upgrade

# Create admin user (optional)
python -c "from app import create_app; app = create_app(); app.app_context().push(); from scripts.create_admin import create_admin_user; create_admin_user()"
```

## Verification Steps

### 1. Check Application
- [ ] Visit https://bilan-competence-449414.ew.r.appspot.com
- [ ] Login page loads
- [ ] Static assets load correctly
- [ ] No console errors

### 2. Test Authentication
- [ ] Login with test credentials
- [ ] JWT tokens generated
- [ ] Protected routes accessible

### 3. Test Database
- [ ] Data persists between sessions
- [ ] CRUD operations work
- [ ] No database errors in logs

### 4. Monitor Logs
```bash
# View application logs
gcloud app logs tail -s default

# View specific logs
gcloud logging read "resource.type=gae_app" --limit=50
```

## Rollback Plan

If deployment fails:
```bash
# List versions
gcloud app versions list

# Rollback to previous version
gcloud app versions migrate OLD_VERSION --service=default
```

## Common Issues

### 1. 502 Bad Gateway
- Check logs for startup errors
- Verify all dependencies in requirements.txt
- Check memory limits

### 2. Database Connection Failed
- Verify Cloud SQL instance is running
- Check VPC connector configuration
- Verify DATABASE_URL format

### 3. Static Files Not Loading
- Check app.yaml handlers configuration
- Verify frontend build completed
- Check CORS settings

### 4. Authentication Errors
- Verify JWT secrets are set
- Check CORS_ORIGINS includes your domain
- Verify tenant header configuration

## Security Checklist

- [ ] Remove all hardcoded secrets
- [ ] Use strong passwords for database
- [ ] Enable Cloud SQL backups
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts
- [ ] Review IAM permissions
- [ ] Enable audit logging

## Performance Optimization

- [ ] Enable Cloud CDN for static assets
- [ ] Configure caching headers
- [ ] Set appropriate instance class
- [ ] Monitor CPU and memory usage
- [ ] Configure autoscaling properly

## Next Steps After Deployment

1. **Configure Custom Domain** (optional)
   ```bash
   gcloud app domain-mappings create your-domain.com
   ```

2. **Set Up Monitoring**
   - Configure uptime checks
   - Set up alert policies
   - Enable error reporting

3. **Backup Strategy**
   - Enable automated Cloud SQL backups
   - Configure backup retention
   - Test restore procedures

4. **Documentation**
   - Update API documentation
   - Document deployment process
   - Create runbooks for common issues