#!/bin/bash
# Infrastructure Testing Script for AMI System
# This script runs comprehensive infrastructure tests using Newman

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
POSTMAN_DIR="postman"
TEST_COLLECTION="$POSTMAN_DIR/infra_comprehensive.json"
RESULTS_FILE="$POSTMAN_DIR/test-results.json"
REPORT_FILE="docs/infrastructure-test-report.md"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AMI Infrastructure Testing${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if server is running
echo -e "${YELLOW}[1/5]${NC} Checking if server is running..."
if curl -s http://localhost:11121/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Server is running on port 11121"
else
    echo -e "${RED}✗${NC} Server is not running!"
    echo -e "${YELLOW}Please start the server first:${NC}"
    echo -e "  ${BLUE}make dev${NC} or ${BLUE}uv run uvicorn app.main:app --host 0.0.0.0 --port 11121 --reload${NC}"
    exit 1
fi

# Check if newman is available
echo -e "${YELLOW}[2/5]${NC} Checking Newman installation..."
if command -v newman > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Newman is installed globally"
    NEWMAN_CMD="newman"
elif command -v npx > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Using Newman via npx"
    NEWMAN_CMD="npx newman"
else
    echo -e "${RED}✗${NC} Newman not found!"
    echo -e "${YELLOW}Installing Newman...${NC}"
    npm install -g newman
    NEWMAN_CMD="newman"
fi

# Check if test collection exists
echo -e "${YELLOW}[3/5]${NC} Checking test collection..."
if [ ! -f "$TEST_COLLECTION" ]; then
    echo -e "${RED}✗${NC} Test collection not found: $TEST_COLLECTION"
    exit 1
fi
echo -e "${GREEN}✓${NC} Test collection found"

# Run tests
echo -e "${YELLOW}[4/5]${NC} Running infrastructure tests..."
echo ""

# Remove old results
rm -f "$RESULTS_FILE"

# Run newman with detailed output
if $NEWMAN_CMD run "$TEST_COLLECTION" \
    --reporters cli,json \
    --reporter-json-export "$RESULTS_FILE" \
    --color on \
    --timeout-request 10000 \
    --delay-request 100; then
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ All Tests Passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    TEST_STATUS="PASSED"
    EXIT_CODE=0
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  ✗ Some Tests Failed${NC}"
    echo -e "${RED}========================================${NC}"
    TEST_STATUS="FAILED"
    EXIT_CODE=1
fi

# Generate summary
echo -e "${YELLOW}[5/5]${NC} Generating test summary..."
echo ""

if [ -f "$RESULTS_FILE" ]; then
    # Extract stats using jq if available
    if command -v jq > /dev/null 2>&1; then
        echo -e "${BLUE}Test Statistics:${NC}"
        echo -e "  Total Requests:  $(jq '.run.stats.requests.total' "$RESULTS_FILE")"
        echo -e "  Total Tests:     $(jq '.run.stats.tests.total' "$RESULTS_FILE")"
        echo -e "  Total Assertions: $(jq '.run.stats.assertions.total' "$RESULTS_FILE")"
        echo -e "  Failed Assertions: $(jq '.run.stats.assertions.failed' "$RESULTS_FILE")"
        
        TOTAL_ASSERTIONS=$(jq '.run.stats.assertions.total' "$RESULTS_FILE")
        FAILED_ASSERTIONS=$(jq '.run.stats.assertions.failed' "$RESULTS_FILE")
        PASSED_ASSERTIONS=$((TOTAL_ASSERTIONS - FAILED_ASSERTIONS))
        
        if [ "$TOTAL_ASSERTIONS" -gt 0 ]; then
            SUCCESS_RATE=$((PASSED_ASSERTIONS * 100 / TOTAL_ASSERTIONS))
            echo -e "  Success Rate:  ${GREEN}${SUCCESS_RATE}%${NC}"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}Results saved to:${NC} $RESULTS_FILE"
fi

echo ""
echo -e "${BLUE}Full report available at:${NC} $REPORT_FILE"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Infrastructure is healthy!${NC}"
else
    echo -e "${RED}✗ Infrastructure has issues. Please check the report.${NC}"
fi

echo ""
exit $EXIT_CODE
