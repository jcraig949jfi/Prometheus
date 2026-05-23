@echo off
REM Launcher for Hypatia (D-track curator).
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\hypatia_loop_launch.bat" -WindowStyle Hidden
REM
REM Mirrors pythia_loop_launch.bat / charon_loop_launch.bat / harmonia_loop_launch.bat.
REM See agents/hypatia/CHARTER.md for the contract.
REM
REM Logs: agents/hypatia/logs/hypatia.log + agents/hypatia/events.jsonl
REM       + scripts-relative pipe to logs/hypatia_daemon.stderr.log for crashes.

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
python -m agents.hypatia.daemon --loop --interval 3600 >> agents\hypatia\logs\hypatia.stdout.log 2>> agents\hypatia\logs\hypatia.stderr.log
