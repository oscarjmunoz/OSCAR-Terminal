@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"

call "%SCRIPT_DIR%stop_oscar.bat"
set "STOP_CODE=%ERRORLEVEL%"

call "%SCRIPT_DIR%start_oscar.bat"
set "START_CODE=%ERRORLEVEL%"

if not "%START_CODE%"=="0" exit /b %START_CODE%
exit /b %STOP_CODE%
