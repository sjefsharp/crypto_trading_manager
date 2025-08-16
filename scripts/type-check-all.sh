#!/bin/bash

# Full Project Type Check Script
# Run type checking on both backend (MyPy) and frontend (TypeScript)

echo "🔍 Full Project Type Checking"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

backend_exit_code=0
frontend_exit_code=0

# Backend Type Checking
echo -e "${YELLOW}🐍 Backend Type Checking (MyPy)${NC}"
echo "--------------------------------"
cd backend

if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
    echo "✅ Virtual environment activated"
fi

python -m mypy . --config-file=../mypy.ini
backend_exit_code=$?

if [ $backend_exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Backend type checking passed!${NC}"
else
    echo -e "${RED}❌ Backend type checking failed${NC}"
fi

echo ""

# Frontend Type Checking
echo -e "${YELLOW}⚛️  Frontend Type Checking (TypeScript)${NC}"
echo "---------------------------------------"
cd ../frontend

npm run type-check
frontend_exit_code=$?

if [ $frontend_exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend type checking passed!${NC}"
else
    echo -e "${RED}❌ Frontend type checking failed${NC}"
fi

echo ""
echo "Summary:"
echo "--------"

if [ $backend_exit_code -eq 0 ] && [ $frontend_exit_code -eq 0 ]; then
    echo -e "${GREEN}🎉 All type checks passed!${NC}"
    exit 0
else
    echo -e "${RED}💥 Type checking failed:${NC}"
    [ $backend_exit_code -ne 0 ] && echo -e "  ${RED}• Backend (MyPy)${NC}"
    [ $frontend_exit_code -ne 0 ] && echo -e "  ${RED}• Frontend (TypeScript)${NC}"
    exit 1
fi
