#!/bin/bash

# 🔐 Security Check Script for Crypto Trading Manager
# Run this before every commit to catch security issues early

echo "🔐 Running Security Checks..."
echo "================================"

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -f "backend/pyproject.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

echo ""
echo "${BLUE}🔍 Checking Backend Security...${NC}"
echo "================================"

# Backend Python Security Check
if [ -d "backend" ]; then
    cd backend

    # Install/update safety if needed
    if ! command -v safety &> /dev/null; then
        echo "${YELLOW}📦 Installing safety...${NC}"
        pip install safety
    fi

    echo "${BLUE}🐍 Running Python dependency security scan...${NC}"
    if safety scan --output screen --stage development; then
        echo "${GREEN}✅ No Python security vulnerabilities found${NC}"
    else
        echo "${RED}❌ Python security vulnerabilities detected!${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    echo ""
    echo "${BLUE}🔒 Running Python security linting (Bandit)...${NC}"
    if command -v bandit &> /dev/null; then
        if bandit -r app/ -f screen; then
            echo "${GREEN}✅ No Python security issues found${NC}"
        else
            echo "${RED}❌ Python security issues detected!${NC}"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    else
        echo "${YELLOW}⚠️  Bandit not installed, skipping Python security linting${NC}"
    fi

    cd ..
else
    echo "${YELLOW}⚠️  Backend directory not found, skipping Python checks${NC}"
fi

echo ""
echo "${BLUE}🌐 Checking Frontend Security...${NC}"
echo "================================"

# Frontend NPM Security Check
if [ -d "frontend" ]; then
    cd frontend

    echo "${BLUE}📦 Running NPM security audit...${NC}"
    if npm audit --audit-level=moderate; then
        echo "${GREEN}✅ No NPM security vulnerabilities found${NC}"
    else
        echo "${RED}❌ NPM security vulnerabilities detected!${NC}"
        echo "${YELLOW}💡 Try running: npm audit fix${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    cd ..
else
    echo "${YELLOW}⚠️  Frontend directory not found, skipping NPM checks${NC}"
fi

echo ""
echo "${BLUE}🔍 Checking for Secrets...${NC}"
echo "=========================="

# Basic secret detection
echo "${BLUE}🔑 Scanning for potential secrets...${NC}"
SECRET_PATTERNS=(
    "password\s*=\s*['\"][^'\"]*['\"]"
    "api[_-]?key\s*=\s*['\"][^'\"]*['\"]"
    "secret\s*=\s*['\"][^'\"]*['\"]"
    "token\s*=\s*['\"][^'\"]*['\"]"
    "-----BEGIN.*PRIVATE KEY-----"
)

SECRETS_FOUND=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -i --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --include="*.yaml" --include="*.yml" -E "$pattern" . 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "__pycache__" | grep -v ".venv" | grep -v "test_" | grep -v "/tests/" | head -20; then
        SECRETS_FOUND=1
    fi
done

if [ $SECRETS_FOUND -eq 0 ]; then
    echo "${GREEN}✅ No obvious secrets detected${NC}"
else
    echo "${RED}❌ Potential secrets detected in files above!${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

echo ""
echo "${BLUE}📊 Summary${NC}"
echo "=========="

if [ $ISSUES_FOUND -eq 0 ]; then
    echo "${GREEN}🎉 All security checks passed! Safe to commit.${NC}"
    exit 0
else
    echo "${RED}⚠️  Found $ISSUES_FOUND security issue(s). Please fix before committing.${NC}"
    echo ""
    echo "${YELLOW}💡 Quick fixes:${NC}"
    echo "  • Backend: Update dependencies in backend/pyproject.toml"
    echo "  • Frontend: Run 'npm audit fix' in frontend/"
    echo "  • Secrets: Remove or move secrets to environment variables"
    exit 1
fi
