#!/bin/bash

# MinIO Setup Verification Script
# Runs all checks to verify MinIO is properly configured

set -e  # Exit on error

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║                    MinIO Setup Verification Script                      ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Docker Compose
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 1: Docker Compose"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker is installed${NC}"
else
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

# Check 2: MinIO Container
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 2: MinIO Container Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if docker ps | grep -q ami_minio; then
    echo -e "${GREEN}✅ MinIO container is running${NC}"
    docker ps | grep ami_minio
else
    echo -e "${YELLOW}⚠️  MinIO container is not running${NC}"
    echo "Starting MinIO container..."
    docker compose up -d minio
    sleep 5
    
    if docker ps | grep -q ami_minio; then
        echo -e "${GREEN}✅ MinIO container started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start MinIO container${NC}"
        exit 1
    fi
fi

# Check 3: MinIO Health Endpoint
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 3: MinIO Health Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -sf http://localhost:9000/minio/health/live > /dev/null; then
    echo -e "${GREEN}✅ MinIO health endpoint is responding${NC}"
else
    echo -e "${RED}❌ MinIO health endpoint is not responding${NC}"
    echo "Waiting 10 seconds for MinIO to fully start..."
    sleep 10
    
    if curl -sf http://localhost:9000/minio/health/live > /dev/null; then
        echo -e "${GREEN}✅ MinIO is now healthy${NC}"
    else
        echo -e "${RED}❌ MinIO is still not responding${NC}"
        exit 1
    fi
fi

# Check 4: Python Dependencies
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 4: Python Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python -c "import minio" 2>/dev/null; then
    echo -e "${GREEN}✅ MinIO Python package is installed${NC}"
else
    echo -e "${YELLOW}⚠️  MinIO Python package not found${NC}"
    echo "Installing dependencies..."
    pip install -q minio pillow python-magic
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Check 5: Run Initialization Script
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 5: MinIO Initialization"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python scripts/init_minio.py; then
    echo -e "${GREEN}✅ MinIO initialization successful${NC}"
else
    echo -e "${RED}❌ MinIO initialization failed${NC}"
    exit 1
fi

# Check 6: Run Test Suite
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 6: Comprehensive Test Suite"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python test_minio_comprehensive.py; then
    echo -e "${GREEN}✅ All tests passed${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║                      ✅ ALL CHECKS PASSED! ✅                            ║"
echo "║                                                                          ║"
echo "║                   MinIO is ready for use! 🚀                            ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 MinIO Console: http://localhost:9001"
echo "📦 S3 API:        http://localhost:9000"
echo "📚 Docs:          MINIO_SETUP_GUIDE.md"
echo ""



