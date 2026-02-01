#!/bin/bash
echo "Starting AI Ship Route Management Backend..."
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
