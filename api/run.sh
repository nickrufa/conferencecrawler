#!/bin/bash

# Conference Crawler API Startup Script

echo "🚀 Starting Conference Crawler API..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📋 Installing requirements..."
pip install -r requirements.txt

# Initialize and populate database
echo "🗄️  Initializing database..."
python3 populate_data.py

# Start the Flask API
echo "✅ Starting Flask API on http://localhost:5000"
echo "📊 Health check: http://localhost:5000/api/health"
echo "👥 Users endpoint: http://localhost:5000/api/conferences/idweek2025/users"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py