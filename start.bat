@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Install Python 3.10 or newer and restart this file.
    pause
    exit /b 1
  )
)
.venv\Scripts\python.exe -c "import fastapi, sqlalchemy, uvicorn, dotenv" >nul 2>&1
if errorlevel 1 (
  .venv\Scripts\python.exe -m pip install -r backend\requirements.txt
  if errorlevel 1 (
    echo Dependency installation failed. Check internet access.
    pause
    exit /b 1
  )
)
echo Site: http://127.0.0.1:8000
echo Swagger: http://127.0.0.1:8000/docs
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
pause
