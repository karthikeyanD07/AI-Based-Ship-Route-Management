@echo off
echo Starting AI Ship Route Management Backend...
cd /d %~dp0
call venv\Scripts\activate.bat
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
pause
