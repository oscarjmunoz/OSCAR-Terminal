@echo off
setlocal

echo ======================================
echo OSCAR Lite Launcher - RESTART
echo ======================================

call "%~dp0stop_oscar.bat"
timeout /t 2 /nobreak >nul
call "%~dp0start_oscar.bat"

exit /b 0
