#!/bin/bash

echo "========================================================"
echo "[1/6] Checking Python and Virtual Environment Setup"
echo "========================================================"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/Scripts/activate

echo "========================================================"
echo "[2/6] Installing dependencies and LangGraph CLI"
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
echo "[3/6] Checking Ollama Service Status"
echo "========================================================"
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo "Ollama is not running. Attempting to start Ollama..."
    if command -v ollama &> /dev/null; then
        ollama serve &
        echo "Waiting for Ollama to start..."
        sleep 5
        if curl -s http://localhost:11434/api/tags &>/dev/null; then
            echo "Ollama started successfully."
        else
            echo "Failed to start Ollama automatically. Please start Ollama manually."
        fi
    else
        echo "Ollama command not found. Please install Ollama or start it manually."
    fi
else
    echo "Ollama is already running."
fi

echo "========================================================"
echo "[4/6] Verifying Environment Variables"
echo "========================================================"
if [ ! -f ".env" ]; then
    echo "No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your LANGSMITH_API_KEY and OPENAI_API_KEY before running again."
    exit 1
fi

# Load variables
export $(grep -v '^#' .env | xargs)

if [ -z "$LLM_MODEL" ] || [ -z "$LLM_BASE_URL" ] || [ -z "$LLM_API_KEY" ]; then
    echo "Warning: LLM Configuration (LLM_MODEL, LLM_BASE_URL, LLM_API_KEY) is not set correctly in your .env file."
fi
if [ "$LANGCHAIN_API_KEY" = "your-langsmith-api-key" ] || [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "Warning: LANGCHAIN_API_KEY is not set correctly in your .env file."
fi

echo "========================================================"
echo "[5/6] Running Test Suite"
echo "========================================================"
echo "Running pytest on tests..."
pytest

echo "========================================================"
echo "[6/6] Starting LangGraph Development Server"
echo "========================================================"
echo "Starting local dev server. This will enable local tracing and LangGraph Studio."
langgraph dev
