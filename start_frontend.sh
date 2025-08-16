#!/bin/bash

# Crypto Trading Manager - Frontend Start Script
# Voor iMac Late 2013 + macOS Monterey - Nu met Vite + TypeScript!

echo "🌐 Starting Crypto Trading Manager Frontend with Vite + TypeScript..."

# Load NVM and use latest Node.js
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
echo "🔧 Loading Node.js..."
nvm use 22.18.0

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the crypto_trading_manager root directory"
    exit 1
fi

# Go to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Check if port 3000 is available
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 3000 is already in use. Killing existing process..."
    pkill -f "vite"
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    sleep 3
fi

# Start the frontend server
echo "🌟 Starting Vite + TypeScript development server on http://localhost:3000"
echo "🔧 Make sure backend is running on http://localhost:8000"
echo "⚡ Vite provides lightning-fast hot module replacement!"
echo "🎯 TypeScript provides type safety and better IDE support!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Vite development server (no more deprecation warnings!)
npm run dev
