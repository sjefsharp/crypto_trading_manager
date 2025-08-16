#!/bin/bash

# Crypto Trading Manager - Backend Start Script
# Voor iMac Late 2013 + macOS Monterey

echo "🚀 Starting Crypto Trading Manager Backend..."

# Check if we're in the right directory
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ Please run this script from the crypto_trading_manager root directory"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first"
    exit 1
fi

source .venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
cd backend
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Initialize database if needed
if [ ! -f "crypto_trading.db" ]; then
    echo "🗄️ Initializing database..."
    python init_db.py
fi

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 8000 is already in use. Killing existing process..."
    pkill -f uvicorn
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 3
fi

# Start the backend server
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "❤️ Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
