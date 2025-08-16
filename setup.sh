#!/bin/bash

# Crypto Trading Manager Setup Script
# This script sets up the development environment for both backend and frontend

echo "🚀 Setting up Crypto Trading Manager development environment..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Setup backend
echo "📦 Setting up Python backend..."
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating environment configuration file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env file with your API keys if you want to enable live trading"
fi

echo "✅ Backend setup complete!"

# Setup frontend
echo "📦 Setting up React frontend..."
cd ../frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"

cd ..

echo ""
echo "🎉 Setup complete! To start the application:"
echo ""
echo "1. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open your browser to http://localhost:3000"
echo ""
echo "📝 Note: Edit backend/.env to add your Bitvavo API keys for live trading"
echo "   The app works without API keys for viewing market data only"
echo ""
echo "🔗 API Documentation: http://localhost:8000/docs"
