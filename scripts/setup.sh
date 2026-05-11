#!/bin/bash
# AIOSOL Setup Script
# Created by: Nila (DevOps Engineer)

set -e

echo "🚀 AIOSOL Setup Script"
echo "======================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Create .env files if they don't exist
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating backend/.env from example...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ Created backend/.env${NC}"
    echo -e "${YELLOW}⚠ Please update backend/.env with your actual values${NC}"
fi

if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}Creating frontend/.env...${NC}"
    echo "VITE_API_URL=http://localhost:8000/api/v1" > frontend/.env
    echo -e "${GREEN}✓ Created frontend/.env${NC}"
fi

# Start services
echo ""
echo -e "${YELLOW}Starting services with Docker Compose...${NC}"
cd docker
docker-compose up -d

echo ""
echo -e "${GREEN}✓ Services started successfully!${NC}"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 Next steps:"
echo "   1. Update backend/.env with your API keys"
echo "   2. Run database migrations: docker-compose exec backend alembic upgrade head"
echo "   3. Create a super admin user"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"
