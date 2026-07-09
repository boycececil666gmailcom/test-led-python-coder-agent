#!/bin/bash
export PYTHONUTF8=1

echo "========================================================"
echo "[1/4] Checking Python and Virtual Environment Setup"
echo "========================================================"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/Scripts/activate

echo "========================================================"
echo "[2/4] Installing dependencies and LangGraph CLI"
echo "========================================================"
# Prefer uv if available, otherwise fallback to pip
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt
    uv pip install "langgraph-cli[inmem]"
else
    pip install -r requirements.txt
    pip install "langgraph-cli[inmem]"
fi

echo "========================================================"
echo "[3/4] Verifying Environment Variables"
echo "========================================================"
if [ ! -f ".env" ]; then
    echo "No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your LANGSMITH_API_KEY and OPENAI_API_KEY before running again."
    exit 1
fi

# Load variables
export $(grep -v '^#' .env | xargs)

if [ "$OPENAI_API_KEY" = "your-openai-api-key" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set correctly in your .env file."
fi
if [ "$LANGCHAIN_API_KEY" = "your-langchain-api-key" ] || [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "Warning: LANGCHAIN_API_KEY is not set correctly in your .env file."
fi

echo "========================================================"
echo "[4/4] Starting LangGraph Development Server"
echo "========================================================"
echo "Starting local dev server. This will enable local tracing and LangGraph Studio."
langgraph dev
