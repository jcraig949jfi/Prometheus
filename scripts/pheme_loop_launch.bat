@echo off
REM Launcher for Pheme (substrate demand voicer; lives inside Ergon).
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\pheme_loop_launch.bat" -WindowStyle Hidden
REM
REM See agents/pheme/CHARTER.md for the contract.
REM
REM Logs: agents/pheme/logs/pheme.log + agents/pheme/events.jsonl
REM       + agents/pheme/logs/pheme.stderr.log for crashes.

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
python -m agents.pheme.daemon --loop --interval 1800 >> agents\pheme\logs\pheme.stdout.log 2>> agents\pheme\logs\pheme.stderr.log
