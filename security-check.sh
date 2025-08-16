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
    if safety scan --output screen --stage development --disable-optional-telemetry; then
        echo "${GREEN}✅ No Python security vulnerabilities found${NC}"
    else
        echo "${RED}❌ Python security vulnerabilities detected!${NC}"
        echo "${YELLOW}💡 Try running: safety scan --output json for detailed info${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    echo ""
    echo "${BLUE}🔒 Running Python security linting (Bandit)...${NC}"
    if command -v bandit &> /dev/null; then
        if bandit -r app/ -f screen -ll -i; then
            echo "${GREEN}✅ No Python security issues found${NC}"
        else
            echo "${RED}❌ Python security issues detected!${NC}"
            echo "${YELLOW}💡 Run: bandit -r app/ -f json -o bandit-report.json for details${NC}"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    else
        echo "${YELLOW}⚠️  Bandit not installed, skipping Python security linting${NC}"
        echo "${YELLOW}💡 Install with: pip install bandit${NC}"
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
    if npm audit --audit-level=moderate --fund=false; then
        echo "${GREEN}✅ No NPM security vulnerabilities found${NC}"
    else
        echo "${RED}❌ NPM security vulnerabilities detected!${NC}"
        echo "${YELLOW}💡 Try running: npm audit fix${NC}"
        echo "${YELLOW}💡 For details: npm audit --json${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    cd ..
else
    echo "${YELLOW}⚠️  Frontend directory not found, skipping NPM checks${NC}"
fi

echo ""
echo "${BLUE}🔍 Checking for Secrets...${NC}"
echo "=========================="

# Check if pre-commit is available for additional security
if command -v pre-commit &> /dev/null; then
    echo "${BLUE}🛡️  Running pre-commit security hooks...${NC}"
    if pre-commit run detect-private-key --all-files; then
        echo "${GREEN}✅ Pre-commit security hooks passed${NC}"
    else
        echo "${YELLOW}⚠️  Pre-commit detected potential private keys${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
    echo ""
fi

# Basic secret detection
echo "${BLUE}🔑 Scanning for potential secrets...${NC}"
SECRET_PATTERNS=(
    "password\s*=\s*['\"][^'\"]{8,}['\"]"
    "api[_-]?key\s*=\s*['\"][^'\"]{16,}['\"]"
    "secret\s*=\s*['\"][^'\"]{16,}['\"]"
    "token\s*=\s*['\"][^'\"]{20,}['\"]"
    "-----BEGIN.*PRIVATE KEY-----"
)

SECRETS_FOUND=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    # Faster grep with specific file types and exclusions
    SECRET_MATCHES=$(grep -r -i --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir="__pycache__" --exclude-dir=".venv" --exclude-dir="venv" --exclude="*test*" -E "$pattern" . 2>/dev/null | head -3)
    if [ ! -z "$SECRET_MATCHES" ]; then
        echo "${RED}🚨 Found potential secrets:${NC}"
        echo "$SECRET_MATCHES"
        SECRETS_FOUND=1
        break  # Exit early if secrets found
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
    echo "  • Backend: Update dependencies - pip install --upgrade -r requirements.txt"
    echo "  • Frontend: Run 'npm audit fix' in frontend/"
    echo "  • Secrets: Remove or move secrets to .env files"
    echo "  • Pre-commit: Run 'pre-commit run --all-files' for full security scan"
    exit 1
fi
