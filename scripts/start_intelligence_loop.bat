@echo off
REM Background launcher for the Intelligence Loop.
REM Uses pythonw.exe so no console window appears.
REM Logs to C:\Prometheus\dashboard\intelligence_loop.log

REM Ensure Agora env vars are set for this process (defaults match the on-disk .env).
if "%AGORA_REDIS_HOST%"=="" set AGORA_REDIS_HOST=192.168.1.176
if "%AGORA_REDIS_PASSWORD%"=="" set AGORA_REDIS_PASSWORD=prometheus
if "%PROMETHEUS_MACHINE%"=="" set PROMETHEUS_MACHINE=M4
set PYTHONPATH=C:\Prometheus

REM Find pythonw — adjust if it's not on PATH or in the expected location.
set PYTHONW=pythonw.exe
where pythonw.exe >nul 2>&1
if errorlevel 1 set PYTHONW=C:\Users\jcrai\AppData\Local\Programs\Python\Python312\pythonw.exe

REM Launch detached so this batch window can close.
start "" "%PYTHONW%" "C:\Prometheus\scripts\intelligence_loop.py" --immediate

echo Intelligence loop launched in background (pythonw, no console window).
echo Logs: C:\Prometheus\docs\intelligence_loop.log
echo To stop: kill the pythonw.exe process via Task Manager.
