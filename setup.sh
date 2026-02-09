#!/bin/bash

# OCR MCP Server Setup Script

set -e

echo "=== OCR MCP Server Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.10+
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "Error: Python 3.10 or higher is required"
    exit 1
fi

echo "✓ Python version OK"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Install package in development mode
echo "Installing ocr-mcp package..."
pip install -e .
echo "✓ Package installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
    echo "   - MISTRAL_API_KEY"
    echo "   - DEEPSEEK_API_KEY"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Test installation
echo "Testing installation..."
python3 -c "from ocr_mcp import settings; print('✓ Import successful')"
echo ""

echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Test the server: python -m ocr_mcp.server"
echo "3. Configure LibreChat to use the MCP server"
echo ""
echo "See README.md for detailed instructions"