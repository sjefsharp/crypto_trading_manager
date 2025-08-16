#!/bin/bash

# Debug script om warnings en errors te zien tijdens opstarten
# Voor iMac Late 2013 + macOS Monterey

echo "🔍 Debug Mode - Catching All Warnings and Errors"
echo "=================================================="

# Cleanup eerst alle processen
echo "🧹 Cleaning up existing processes..."
pkill -f uvicorn 2>/dev/null
pkill -f "react-scripts" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
sleep 3

echo "✅ Cleanup complete"
echo ""

# Start backend met uitgebreide logging
echo "🔧 Starting Backend with verbose logging..."
echo "============================================="

cd backend
source ../.venv/bin/activate

# Check Python imports voor warnings
echo "🐍 Testing Python imports..."
python -c "
import warnings
warnings.filterwarnings('default')
try:
    from app.main import app
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
"

echo ""
echo "🌟 Starting FastAPI with debug logging..."

# Start uvicorn met uitgebreide logging
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level debug --reload &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed"
fi

echo ""
echo "🌐 Starting Frontend with verbose logging..."
echo "============================================="

cd ../frontend

# Check npm en node warnings
echo "📦 Checking Node.js and npm..."
node --version
npm --version

echo ""
echo "🔍 Installing/checking dependencies..."
npm install 2>&1 | grep -i warning || echo "✅ No npm warnings"

echo ""
echo "🌟 Starting React with debug output..."

# Start React met alle output
BROWSER=none npm start 2>&1 &
FRONTEND_PID=$!

echo ""
echo "⏳ Waiting for frontend to compile..."
sleep 10

echo ""
echo "📊 Final Status Check"
echo "===================="

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend: http://localhost:8000 - READY"
else
    echo "❌ Backend: FAILED"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: http://localhost:3000 - READY"
else
    echo "❌ Frontend: FAILED"
fi

echo ""
echo "🎯 Both servers are running in debug mode"
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to stop
wait $BACKEND_PID $FRONTEND_PID
