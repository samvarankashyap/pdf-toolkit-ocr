#!/bin/bash
# Quick test runner for Linux/macOS

echo "========================================"
echo "Running PDF Toolkit Tests"
echo "========================================"
echo

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Warning: Virtual environment not found"
    echo "Please run: python3 -m venv venv"
fi

echo
echo "Running tests with coverage..."
echo

python -m pytest test_pdf_toolkit.py -v --cov=pdf_toolkit --cov-report=html --cov-report=term-missing

echo
echo "========================================"
echo "Test Results Summary"
echo "========================================"
echo "HTML coverage report: htmlcov/index.html"
echo
echo "To view coverage report:"
echo "  Linux: xdg-open htmlcov/index.html"
echo "  macOS: open htmlcov/index.html"
echo
