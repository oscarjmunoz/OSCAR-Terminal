@echo off
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0.."
set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"

echo ======================================
echo OSCAR Lite Launcher - START
echo Root: %ROOT_DIR%
echo ======================================

if not exist "%BACKEND_DIR%" (
  echo [ERROR] Backend folder not found: %BACKEND_DIR%
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%" (
  echo [ERROR] Frontend folder not found: %FRONTEND_DIR%
  pause
  exit /b 1
)

echo [1/6] Starting backend...
start "OSCAR Backend" cmd /k "cd /d "%BACKEND_DIR%" ^&^& if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) ^&^& python run.py"

echo [2/6] Waiting for backend warm-up...
timeout /t 4 /nobreak >nul

echo [3/6] Starting frontend...
start "OSCAR Frontend" cmd /k "cd /d "%FRONTEND_DIR%" ^&^& npm run dev"

echo [4/6] Waiting for Vite on http://localhost:5174 ...
set "READY=0"
for /l %%I in (1,1,40) do (
  for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":5174" ^| findstr "LISTENING"') do (
    set "READY=1"
  )
  if "!READY!"=="1" goto :open_browser
  timeout /t 1 /nobreak >nul
)

echo [WARN] Vite port 5174 not detected yet. Opening browser anyway...

:open_browser
echo [5/6] Opening browser...
start "" "http://localhost:5174"

echo [6/6] OSCAR launch sequence completed.
exit /b 0
