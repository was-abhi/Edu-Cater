@echo off
setlocal

REM Start Edu-Cater ML Recommendation Server on Windows (Port 8001)
set "MODEL_DIR=%~dp0"
set "REPO_ROOT=%MODEL_DIR%.."
cd /d "%REPO_ROOT%"

if exist "%MODEL_DIR%.venv\Scripts\python.exe" (
    set "PYTHON=%MODEL_DIR%.venv\Scripts\python.exe"
) ELSE (
    set "PYTHON=python"
)

echo Starting Edu-Cater ML Recommendation Server on Windows (port 8001)...
%PYTHON% -m uvicorn model.server:app --host 0.0.0.0 --port 8001 --reload
pause
