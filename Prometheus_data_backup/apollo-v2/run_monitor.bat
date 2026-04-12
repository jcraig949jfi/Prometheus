@echo off
set PYTHON=C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe

echo ============================================================
echo   Apollo Evolution Monitor
echo   Runs every 30 minutes. Reports pushed to GitHub.
echo   Press Ctrl+C to stop.
echo ============================================================

:loop
echo.
echo [%date% %time%] Running monitor...
%PYTHON% scripts\evolution_monitor.py

echo [%date% %time%] Sleeping 30 minutes...
timeout /t 1800 /nobreak
goto loop
