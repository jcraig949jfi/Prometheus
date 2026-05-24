@echo off
REM Launcher for Polyhymnia (one-tensor agent).
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\polyhymnia_loop_launch.bat" -WindowStyle Hidden
REM
REM Mirrors hypatia/atalanta/pheme/talos/clio/pythia launchers. Detached
REM via Start-Process so the daemon survives the parent shell exiting.
REM
REM See agents/polyhymnia/CHARTER.md for the contract.

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
python -m agents.polyhymnia.daemon --loop --interval 1800 >> agents\polyhymnia\logs\polyhymnia.stdout.log 2>> agents\polyhymnia\logs\polyhymnia.stderr.log
