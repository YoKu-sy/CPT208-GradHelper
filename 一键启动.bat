@echo off
setlocal

cd /d "%~dp0"

if exist "backend\IELTS\start_backend.bat" (
  echo [1/3] Starting IELTS backend...
  start "IELTS Backend" cmd /k "cd /d "%~dp0backend\IELTS" && call start_backend.bat"
) else (
  echo IELTS backend start script not found.
)

if exist "backend\AI_assistant\app.py" (
  echo [2/3] Starting AI assistant backend...
  if not exist "backend\AI_assistant\.venv\Scripts\python.exe" (
    echo Creating AI assistant virtual environment...
    py -3 -m venv "backend\AI_assistant\.venv"
    if errorlevel 1 (
      echo Failed to create AI assistant virtual environment.
      pause
      exit /b 1
    )
  )
  start "AI Assistant Backend" cmd /k "cd /d "%~dp0backend\AI_assistant" && ".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8001"
) else (
  echo AI assistant app.py not found.
)

if exist "package.json" (
  echo [3/3] Starting frontend...
  start "Frontend" cmd /k "cd /d "%~dp0" && npm run dev"
) else (
  echo package.json not found.
)

echo.
echo All services have been requested to start.
echo Frontend:    http://localhost:5173
echo IELTS API:   http://127.0.0.1:8000
echo AI API:      http://127.0.0.1:8001
pause
endlocal
