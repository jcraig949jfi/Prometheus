@echo off
REM Launcher for Clio (substrate paper-mining daemon, Muse of history).
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\clio_loop_launch.bat" -WindowStyle Hidden
REM
REM Mirrors pythia_loop_launch.bat / hypatia_loop_launch.bat. Detached
REM via Start-Process so the daemon survives the parent shell exiting.
REM
REM Config: scripts/clio_config.yaml (cycle interval, arxiv queries).
REM Logs:   logs/clio_daemon.log (existing convention)
REM         + logs/clio_daemon.stderr.log for crashes (new — captures
REM         the next MemoryError-style death loudly).
REM
REM Background: died 2026-05-20 10:20 with MemoryError during
REM paper_index.save() — same memory-pressure window as the Theseus
REM 107 GB leak that crashed Postgres. Theseus leak fixed by Techne;
REM Clio safe to restart.

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
python scripts\clio_daemon.py >> logs\clio_daemon.log 2>> logs\clio_daemon.stderr.log
