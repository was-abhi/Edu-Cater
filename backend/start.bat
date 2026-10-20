
@echo off
cd /d "%~dp0"

call venv\Scripts\activate.bat

start "" http://127.0.0.1:8000/docs

python -m uvicorn app.main:app --reload

pause
