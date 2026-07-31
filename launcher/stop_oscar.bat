@echo off
setlocal

echo ======================================
echo OSCAR Lite Launcher - STOP
echo ======================================

echo Closing launcher windows...
taskkill /FI "WINDOWTITLE eq OSCAR Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq OSCAR Frontend*" /T /F >nul 2>&1

echo Stopping OSCAR-related Python/Node processes...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'OSCAR-Terminal' -and ($_.Name -match 'python|node|uvicorn') } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop; Write-Host ('Stopped PID ' + $_.ProcessId + ' (' + $_.Name + ')') } catch {} }"

echo Stopping fallback process names...
taskkill /IM uvicorn.exe /F >nul 2>&1
taskkill /IM vite.exe /F >nul 2>&1

echo OSCAR stop sequence completed.
exit /b 0
