#!/bin/sh

echo " ========================================================"
echo "1. Running Tests via Python Module"
echo "========================================================"
echo "[1/1] Running pytest..."

# Navigate to project root relative to the script location
cd "$(dirname "$0")/.."

# Run pytest using the virtual environment's python command
# This automatically handles PYTHONPATH/import paths correctly
.venv/Scripts/python.exe -m pytest tests/test_test_coding.py
