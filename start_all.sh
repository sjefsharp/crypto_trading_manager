#!/bin/bash

# Crypto Trading Manager - Complete Start Script
# Voor iMac Late 2013 + macOS Monterey
# Start beide backend en frontend automatisch

echo "🚀 Starting Complete Crypto Trading Manager..."
echo "This will start both backend and frontend servers"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/app/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the crypto_trading_manager root directory"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    pkill -f uvicorn
    pkill -f "react-scripts start"
    exit
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🔧 Starting backend server..."
bash start_backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is ready!"
else
    echo "⚠️ Backend starting up..."
fi

# Start frontend in background
echo "🌐 Starting frontend server..."
bash start_frontend.sh &
FRONTEND_PID=$!

# Wait a bit more
echo "⏳ Waiting for frontend to compile..."
sleep 3

echo ""
echo "🎉 Both servers are ready!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "❤️ Health:   http://localhost:8000/health"
echo ""
echo "💡 The app runs in DRY-RUN mode (safe, no real trades)"
echo "💡 Configure API keys in Settings for live data"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
