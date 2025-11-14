#!/bin/bash

# Claude-Analyst Setup Script
# This script sets up the development environment and initializes the database

set -e  # Exit on error

echo "=================================================="
echo "🚀 Claude-Analyst Setup"
echo "=================================================="
echo ""

# Check Python version
echo "📋 Checking prerequisites..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed"
else
    echo "✅ uv found: $(uv --version)"
fi

# Navigate to semantic-layer directory
cd "$(dirname "$0")/../semantic-layer" || exit 1
echo "📁 Working directory: $(pwd)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
uv sync
echo "✅ Dependencies installed"

# Generate sample data
echo ""
echo "🎲 Generating sample data..."
uv run python generate_sample_data.py
echo "✅ Sample data generated"

# Load data to DuckDB
echo ""
echo "💾 Loading data to DuckDB..."
uv run python load_to_duckdb.py
echo "✅ Database initialized"

# Run tests
echo ""
echo "🧪 Running tests..."
uv run python test_all_functionality.py

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. For Claude Desktop:"
echo "   - Add MCP configuration to Claude Desktop config"
echo "   - See: semantic-layer/docs/CLAUDE_DESKTOP_SETUP.md"
echo ""
echo "2. For ChatGPT Desktop:"
echo "   - Set OPENAI_API_KEY environment variable"
echo "   - Run: cd semantic-layer && uv run python run_openai_server.py"
echo ""
echo "3. Quick test:"
echo "   - cd semantic-layer"
echo "   - uv run python test_all_functionality.py"
echo ""
echo "📖 Full documentation: ../README.md"
echo "=================================================="
