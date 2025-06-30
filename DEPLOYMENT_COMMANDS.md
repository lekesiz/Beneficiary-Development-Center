# BDC Platform - Google Cloud App Engine Deployment Commands

## Prerequisites Check

1. **Install Google Cloud SDK** (if not already installed):
```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

2. **Authenticate with Google Cloud**:
```bash
gcloud auth login
```

3. **Set your project ID**:
```bash
# Replace YOUR_PROJECT_ID with your actual project ID
gcloud config set project YOUR_PROJECT_ID
```

4. **Enable required APIs**:
```bash
gcloud services enable \
  appengine.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com
```

## Initial Setup (First Time Only)

1. **Create App Engine application**:
```bash
gcloud app create --region=us-central1
```

2. **Create Cloud SQL instance**:
```bash
gcloud sql instances create bdc-db-prod \
  --database-version=POSTGRES_15 \
  --tier=db-n1-standard-1 \
  --region=us-central1
```

3. **Create database**:
```bash
gcloud sql databases create bdc_production \
  --instance=bdc-db-prod
```

4. **Create database user**:
```bash
gcloud sql users create bdc_user \
  --instance=bdc-db-prod \
  --password=YOUR_SECURE_PASSWORD
```

5. **Create storage bucket**:
```bash
gsutil mb -c standard -l us-central1 gs://YOUR_PROJECT_ID-uploads
```

6. **Create VPC connector** (for Cloud SQL access):
```bash
gcloud compute networks vpc-access connectors create bdc-connector \
  --region=us-central1 \
  --subnet=default \
  --subnet-project=YOUR_PROJECT_ID \
  --min-instances=2 \
  --max-instances=10
```

## Environment Configuration

1. **Update app.yaml with your project details**:
```bash
# Edit the following in app.yaml:
# - YOUR_PROJECT_ID
# - YOUR_DB_PASSWORD
# - YOUR_JWT_SECRET
# - YOUR_FRONTEND_URL
```

2. **Create secrets in Secret Manager** (optional but recommended):
```bash
# Database URL
echo -n "postgresql://bdc_user:YOUR_DB_PASSWORD@/bdc_production?host=/cloudsql/YOUR_PROJECT_ID:us-central1:bdc-db-prod" | \
  gcloud secrets create database-url --data-file=-

# JWT Secret
echo -n "your-super-secret-jwt-key-change-this" | \
  gcloud secrets create jwt-secret-key --data-file=-

# App Secret Key
echo -n "your-flask-secret-key-change-this" | \
  gcloud secrets create app-secret-key --data-file=-
```

## Deployment Steps

1. **Build frontend**:
```bash
cd frontend
npm install
npm run optimize:build
cd ..
```

2. **Test locally** (optional):
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py
```

3. **Deploy with Cloud Build** (recommended):
```bash
gcloud builds submit --config=cloudbuild.yaml
```

4. **Or deploy directly**:
```bash
gcloud app deploy app.yaml --quiet
```

5. **Deploy cron jobs** (if any):
```bash
# gcloud app deploy cron.yaml
```

6. **Deploy dispatch rules** (if any):
```bash
# gcloud app deploy dispatch.yaml
```

## Post-Deployment

1. **View application**:
```bash
gcloud app browse
```

2. **Check logs**:
```bash
gcloud app logs tail -s default
```

3. **Run database migrations**:
```bash
# SSH into an instance or use Cloud Build
gcloud app instances ssh --service=default --version=LATEST

# Inside the instance:
cd /app/backend
python -m flask db upgrade
```

4. **Create admin user**:
```bash
# Inside the instance:
python -m flask create-admin
```

## Monitoring

1. **View logs**:
```bash
gcloud app logs read --limit=50
```

2. **Monitor metrics**:
```bash
# Open in browser
gcloud app open-console
```

3. **Check health**:
```bash
curl https://YOUR_PROJECT_ID.appspot.com/_ah/health
curl https://YOUR_PROJECT_ID.appspot.com/api/v1/admin/health/detailed
```

## Troubleshooting

1. **If deployment fails**:
```bash
# Check Cloud Build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

2. **If app doesn't start**:
```bash
# Check application logs
gcloud app logs read --service=default --limit=100
```

3. **Database connection issues**:
```bash
# Check Cloud SQL proxy
gcloud sql instances describe bdc-db-prod
```

## Rollback

If needed, rollback to previous version:
```bash
gcloud app versions list
gcloud app services set-traffic default --splits=PREVIOUS_VERSION=100
```

## Security Checklist

- [ ] Change all default passwords in app.yaml
- [ ] Enable Cloud SQL backups
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Set up monitoring alerts
- [ ] Configure custom domain and SSL
- [ ] Review IAM permissions

## Cost Optimization

1. **Set spending limits**:
```bash
gcloud app update --service-account=YOUR_SERVICE_ACCOUNT
```

2. **Configure auto-scaling**:
   - Review app.yaml scaling settings
   - Monitor instance usage

3. **Use Cloud CDN for static assets**:
   - Already configured in app.yaml

## Notes

- The application will be available at: https://YOUR_PROJECT_ID.appspot.com
- First deployment may take 10-15 minutes
- Subsequent deployments are faster (~5 minutes)
- Make sure to update YOUR_PROJECT_ID and passwords before deploying