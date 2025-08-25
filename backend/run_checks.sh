#!/bin/bash
set -euo pipefail

# Ensure we're in the backend directory
cd "$(dirname "$0")"

echo "🚀 Running CartaOS Backend Checks..."

# Run ruff linting
echo "🔍 Running ruff linting..."
poetry run ruff check . --output-format=github

# Run mypy type checking
echo "🔍 Running mypy type checking..."
poetry run mypy cartaos

# Run tests with coverage
echo "🧪 Running tests with coverage..."
poetry run python -m pytest -W error --cov --cov-report=term-missing --cov-report=xml:coverage.xml --junitxml=pytest-junit.xml

echo "✨ All checks completed successfully!"

exit 0
