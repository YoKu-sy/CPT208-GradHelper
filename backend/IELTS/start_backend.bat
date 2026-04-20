@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [1/2] Creating virtual environment and installing dependencies...
  uv sync
  if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
  )
)

if "%APP_HOST%"=="" set APP_HOST=127.0.0.1
if "%APP_PORT%"=="" set APP_PORT=8000

echo [2/2] Starting backend server at http://%APP_HOST%:%APP_PORT%
".venv\Scripts\python.exe" -m uvicorn app:app --host %APP_HOST% --port %APP_PORT%

endlocal
