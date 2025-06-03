#!/bin/bash
export PYTHONPATH=.
echo "🚀 Lancement de FastAPI sous Linux/macOS..."
uvicorn api.main:app --reload
