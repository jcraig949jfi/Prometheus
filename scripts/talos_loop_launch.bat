@echo off
REM Launcher for Talos (reasoning-code specialist corpus builder, Phase 0).
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\talos_loop_launch.bat" -WindowStyle Hidden
REM
REM Mirrors hypatia/atalanta/pheme/clio/pythia launchers. Detached via
REM Start-Process so the daemon survives the parent shell exiting.
REM
REM See agents/talos/CHARTER.md for the contract.
REM
REM Phase 0 scope: corpus builder only. NO GPU training. Phase 1 wiring
REM is an explicit human gate (charter "Hard stops" section).

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
python -m agents.talos.daemon --loop --interval 3600 >> agents\talos\logs\talos.stdout.log 2>> agents\talos\logs\talos.stderr.log
