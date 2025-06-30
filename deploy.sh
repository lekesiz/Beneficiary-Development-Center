#!/bin/bash

# BDC Platform Deployment Script
# This script prepares and deploys the application to Google App Engine

set -e  # Exit on error

echo "🚀 BDC Platform Deployment Script"
echo "================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
PROJECT_ID="bilan-competence-449414"
echo "📋 Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not logged in to gcloud. Please run: gcloud auth login"
    exit 1
fi

echo "✅ Logged in as: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"

# Build frontend
echo ""
echo "🔨 Building frontend..."
cd frontend
npm install --legacy-peer-deps
npm run build

# Check if build succeeded
if [ ! -d "dist" ]; then
    echo "❌ Frontend build failed. No dist directory found."
    exit 1
fi

echo "✅ Frontend build completed"

# Go back to root
cd ..

# Create .gcloudignore if it doesn't exist
if [ ! -f ".gcloudignore" ]; then
    echo "📝 Creating .gcloudignore file..."
    cat > .gcloudignore << EOF
# This file specifies files that are *not* uploaded to Google Cloud Platform
# using gcloud.

.gcloudignore
.git
.gitignore
.vscode/
.idea/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
*.md
!README.md
node_modules/
.env
.env.*
!.env.example
*.sqlite
*.db
frontend/node_modules/
frontend/src/
frontend/public/
frontend/.env*
frontend/package*.json
frontend/tsconfig*.json
frontend/vite.config.ts
frontend/index.html
backend/tests/
backend/scripts/
backend/docs/
test_*.py
*.test.py
EOF
fi

echo "✅ .gcloudignore file ready"

# Check for secrets
echo ""
echo "🔐 Checking for secrets configuration..."
echo "Make sure you have set the following secrets in Google Secret Manager:"
echo "  - SECRET_KEY"
echo "  - JWT_SECRET_KEY"
echo "  - DB_PASSWORD"
echo ""
echo "You can set them using:"
echo "  gcloud secrets create SECRET_KEY --data-file=-"
echo "  gcloud secrets create JWT_SECRET_KEY --data-file=-"
echo "  gcloud secrets create DB_PASSWORD --data-file=-"
echo ""
read -p "Have you configured the secrets? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Please configure secrets before deploying."
    exit 1
fi

# Deploy
echo ""
echo "🚀 Deploying to Google App Engine..."
echo "This may take several minutes..."

# Deploy with verbose output
gcloud app deploy app.yaml \
    --project=$PROJECT_ID \
    --version=$(date +%Y%m%d-%H%M%S) \
    --promote \
    --quiet

# Check deployment status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Your app is available at:"
    echo "   https://$PROJECT_ID.ew.r.appspot.com"
    echo ""
    echo "📊 View logs with:"
    echo "   gcloud app logs tail -s default"
    echo ""
    echo "🔍 View dashboard at:"
    echo "   https://console.cloud.google.com/appengine?project=$PROJECT_ID"
else
    echo ""
    echo "❌ Deployment failed. Check the error messages above."
    echo ""
    echo "Common issues:"
    echo "- Missing APIs: Enable required APIs in Cloud Console"
    echo "- Quota exceeded: Check your billing account"
    echo "- Invalid configuration: Check app.yaml syntax"
    exit 1
fi

# Run post-deployment tasks
echo ""
echo "📋 Post-deployment tasks:"
echo "1. Run database migrations:"
echo "   gcloud app ssh --service=default --version=latest"
echo "   cd /srv && python -m flask db upgrade"
echo ""
echo "2. Create initial admin user (if needed)"
echo "3. Configure custom domain (optional)"
echo "4. Set up monitoring and alerts"

echo ""
echo "🎉 Deployment script completed!"