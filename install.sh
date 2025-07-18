#!/bin/bash
# Installation script for twat-os development

set -e

echo "Installing twat-os development environment..."

# Install uv if not available
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv --python 3.12

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev,test]"

echo "Installation complete!"
echo "To activate the virtual environment, run: source .venv/bin/activate"
echo "To run tests, run: uv run pytest tests/"
echo "To build the package, run: uv run python -m build"