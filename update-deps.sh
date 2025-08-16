#!/bin/bash

# 🚀 Dependency Update Script
# Automatically update dependencies and check for security issues

echo "🚀 Updating Dependencies..."
echo "==========================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Backend Updates
echo ""
echo "${BLUE}🐍 Updating Backend Dependencies...${NC}"
if [ -d "backend" ]; then
    cd backend

    echo "${BLUE}📦 Installing latest compatible versions...${NC}"
    pip install -e .[dev,test] --upgrade

    echo "${BLUE}🔍 Checking for security issues...${NC}"
    safety scan

    cd ..
else
    echo "${YELLOW}⚠️  Backend directory not found${NC}"
fi

# Frontend Updates
echo ""
echo "${BLUE}🌐 Updating Frontend Dependencies...${NC}"
if [ -d "frontend" ]; then
    cd frontend

    echo "${BLUE}📦 Updating NPM packages...${NC}"
    npm update

    echo "${BLUE}🔍 Checking for security issues...${NC}"
    npm audit

    echo "${BLUE}🧹 Fixing fixable issues...${NC}"
    npm audit fix

    cd ..
else
    echo "${YELLOW}⚠️  Frontend directory not found${NC}"
fi

echo ""
echo "${GREEN}✅ Update complete! Run './security-check.sh' to verify security.${NC}"
