@echo off
cd backend
echo Starting Contract Intelligence Parser Backend...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
