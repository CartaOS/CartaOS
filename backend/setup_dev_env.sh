#!/bin/bash
set -e

# Ensure we're in the backend directory
cd "$(dirname "$0")"

echo "🚀 Setting up CartaOS Backend Development Environment..."

# Install system dependencies (only what's needed)
echo "🔧 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3-pip

# Install Poetry if not already installed
if ! command -v poetry >/dev/null 2>&1; then
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3.12 - --version 1.8.3
    # shellcheck disable=SC2016
    {
        echo ''
        echo '# Add Poetry to PATH'
        echo 'export PATH="$HOME/.local/bin:$PATH"'
    } >> ~/.bashrc
    # shellcheck source=/dev/null
    if [ -f "$HOME/.bashrc" ]; then
        # shellcheck source=/dev/null
        # shellcheck disable=SC1091
        . "$HOME/.bashrc"
    fi
fi

# Configure Poetry
poetry config virtualenvs.in-project true
poetry config virtualenvs.prefer-active-python true

# Install project dependencies
echo "📦 Installing project dependencies..."
poetry install --with dev

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
poetry run pre-commit install

echo "✨ Environment setup complete!"
echo "To activate the environment, run: poetry shell"
echo "To run tests: poetry run pytest"
echo "To run linting: poetry run ruff check ."
echo "To run type checking: poetry run mypy cartaos"
