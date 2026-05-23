@echo off
REM Launcher for Atalanta (E-track primitive hunter).
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\atalanta_loop_launch.bat" -WindowStyle Hidden
REM
REM See agents/atalanta/CHARTER.md for the contract.
REM
REM Logs: agents/atalanta/logs/atalanta.log + agents/atalanta/events.jsonl
REM       + agents/atalanta/logs/atalanta.stderr.log for crashes.

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
python -m agents.atalanta.daemon --loop --interval 1800 >> agents\atalanta\logs\atalanta.stdout.log 2>> agents\atalanta\logs\atalanta.stderr.log
