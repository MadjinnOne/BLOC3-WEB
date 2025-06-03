@echo off
set PYTHONPATH=.
echo 🚀 Lancement de FastAPI sous Windows...
uvicorn api.main:app --reload
