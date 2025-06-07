#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate
uvicorn apis.main:app --host 0.0.0.0 --port 8000 