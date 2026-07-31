@echo off
setlocal

set "ROOT_DIR=%~dp0.."
set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"

echo ======================================
echo OSCAR Lite Launcher - SYSTEM CHECK
echo ======================================

echo.
echo [TOOLS]
call :check_tool python "Python"
call :check_tool node "Node.js"
call :check_tool npm "npm"
call :check_tool git "Git"

echo.
echo [PROJECT STRUCTURE]
call :check_path "%BACKEND_DIR%" "Backend folder"
call :check_path "%FRONTEND_DIR%" "Frontend folder"
call :check_path "%BACKEND_DIR%\run.py" "Backend entrypoint run.py"
call :check_path "%FRONTEND_DIR%\package.json" "Frontend package.json"

echo.
echo [MT5]
set "MT5_FOUND=0"
if exist "%ProgramFiles%\MetaTrader 5\terminal64.exe" set "MT5_FOUND=1"
if exist "%ProgramFiles(x86)%\MetaTrader 5\terminal64.exe" set "MT5_FOUND=1"
if "%MT5_FOUND%"=="0" (
  powershell -NoProfile -Command "$c = Get-ChildItem -Path \"$env:APPDATA\MetaQuotes\Terminal\" -Filter terminal64.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1; if ($c) { exit 0 } else { exit 1 }"
  if not errorlevel 1 set "MT5_FOUND=1"
)
if "%MT5_FOUND%"=="1" (
  echo [OK] MT5 installation detected
) else (
  echo [WARN] MT5 not detected in common paths
)

echo.
echo Check completed.
exit /b 0

:check_tool
where %~1 >nul 2>&1
if errorlevel 1 (
  echo [MISSING] %~2
) else (
  echo [OK] %~2
)
exit /b 0

:check_path
if exist "%~1" (
  echo [OK] %~2
) else (
  echo [MISSING] %~2
)
exit /b 0
