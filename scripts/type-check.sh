#!/bin/bash

# Type Check Script
# Run MyPy type checking on the backend code

echo "🔍 Running MyPy Type Checking..."
echo "=================================="

cd backend

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install type stubs if missing
echo "📦 Installing type stubs..."
python -m pip install types-requests types-setuptools --quiet

# Run MyPy with strict configuration from pyproject.toml
echo "🔍 Running MyPy..."
python -m mypy . --strict

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ Type checking passed!"
else
    echo "❌ Type checking failed with $exit_code errors"
    echo ""
    echo "💡 Tips to fix type errors:"
    echo "  - Add type annotations to function parameters and return values"
    echo "  - Use Optional[Type] for nullable values"
    echo "  - Import missing types from typing module"
    echo "  - Check for typos in variable/function names"
fi

exit $exit_code
