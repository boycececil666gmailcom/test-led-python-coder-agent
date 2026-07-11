#!/bin/bash

# Navigate to project root relative to the script location
cd "$(dirname "$0")/../.."

echo " ========================================================"
echo "1. Running Test-Led Coder Agent Demo"
echo "========================================================"
echo "[1/1] Launching agent on tests/manual_test/buggy_code.py..."

.venv/Scripts/python run_agent.py \
  --file tests/manual_test/buggy_code.py \
  --description "Verify the divide function correctly divides two numbers, and returns None if the divisor is 0"
