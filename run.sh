#!/bin/bash

echo "🚀 Setting up Flask E-Commerce Store..."
echo "Installing dependencies..."

# Install Python and pip if not installed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    sudo dnf install python3 -y
fi

if ! command -v pip3 &> /dev/null; then
    echo "Installing pip3..."
    sudo dnf install python3-pip -y
fi

# Install Flask
pip3 install flask

echo "✅ Dependencies installed!"
echo "🌐 Starting the Flask application..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"

python3 app.py
