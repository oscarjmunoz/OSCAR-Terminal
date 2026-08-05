@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."

set "VENV_PY=%ROOT_DIR%\.venv\Scripts\python.exe"
if exist "%VENV_PY%" goto run_with_venv

set "VENV_PY=%ROOT_DIR%\backend\.venv\Scripts\python.exe"
if exist "%VENV_PY%" goto run_with_venv

set "VENV_PY=%ROOT_DIR%\..\.venvs\oscar-terminal\Scripts\python.exe"
if exist "%VENV_PY%" goto run_with_venv

goto run_with_system

:run_with_venv
"%VENV_PY%" "%SCRIPT_DIR%stop_oscar.py"
set "EXIT_CODE=%ERRORLEVEL%"
goto end

:run_with_system
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 "%SCRIPT_DIR%stop_oscar.py"
    set "EXIT_CODE=%ERRORLEVEL%"
    goto end
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python "%SCRIPT_DIR%stop_oscar.py"
    set "EXIT_CODE=%ERRORLEVEL%"
    goto end
)

echo.
echo [ERROR] Python was not found.
echo Install Python 3.12+ and rerun this launcher.
set "EXIT_CODE=1"

:end
if not "%EXIT_CODE%"=="0" (
    echo.
    echo Stop script finished with errors. See messages above.
)
exit /b %EXIT_CODE%
