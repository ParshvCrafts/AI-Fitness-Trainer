#!/bin/bash

# Setup HTTPS for AI Fitness Trainer - Linux/Mac

echo "====================================="
echo "  AI Fitness Trainer - HTTPS Setup"
echo "====================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install pyOpenSSL
echo "Installing pyOpenSSL..."
pip install pyOpenSSL

# Generate certificate
echo ""
echo "Generating SSL certificate..."
python generate_cert.py

echo ""
echo "====================================="
echo "  Setup Complete!"
echo "====================================="
echo ""
echo "Next step: Run the HTTPS server"
echo "  python app_https.py"
echo ""
echo "Then open: https://10.42.108.58:5000"
echo ""
echo "====================================="
