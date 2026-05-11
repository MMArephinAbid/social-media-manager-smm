#!/bin/bash
# AIOSOL Deployment Script
# Created by: Nila (DevOps Engineer)

set -e

echo "🚀 AIOSOL Deployment Script"
echo "============================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DEPLOY_USER=${DEPLOY_USER:-"deploy"}
DEPLOY_HOST=${DEPLOY_HOST:-"your-server.com"}
DEPLOY_PATH=${DEPLOY_PATH:-"/opt/aiosol"}
BRANCH=${BRANCH:-"main"}

echo -e "${YELLOW}Deploying to: ${DEPLOY_HOST}${NC}"
echo -e "${YELLOW}Branch: ${BRANCH}${NC}"
echo ""

# Build frontend
echo -e "${YELLOW}Building frontend...${NC}"
cd frontend
npm ci
npm run build
cd ..
echo -e "${GREEN}✓ Frontend built${NC}"

# SSH and deploy
echo -e "${YELLOW}Deploying to server...${NC}"

ssh ${DEPLOY_USER}@${DEPLOY_HOST} << EOF
    set -e
    cd ${DEPLOY_PATH}

    # Pull latest code
    echo "Pulling latest code..."
    git fetch origin
    git checkout ${BRANCH}
    git pull origin ${BRANCH}

    # Update backend
    echo "Updating backend..."
    cd backend
    source venv/bin/activate
    pip install -r requirements.txt
    alembic upgrade head
    cd ..

    # Restart services
    echo "Restarting services..."
    sudo systemctl restart aiosol-backend
    sudo systemctl restart aiosol-celery

    echo "Deployment complete!"
EOF

# Copy frontend build
echo -e "${YELLOW}Uploading frontend build...${NC}"
rsync -avz --delete frontend/dist/ ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/frontend/dist/

# Reload nginx
ssh ${DEPLOY_USER}@${DEPLOY_HOST} "sudo systemctl reload nginx"

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo "📍 Your application is live at: https://${DEPLOY_HOST}"
