@echo off
REM Launcher for the Pythia (Gemini Deep Research dispatch) daemon.
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\pythia_loop_launch.bat" -WindowStyle Hidden
REM
REM Mirrors scripts\charon_loop_launch.bat / scripts\harmonia_loop_launch.bat.
REM The .bat wrapper exists because launching the python daemon directly
REM through `Bash run_in_background:true + nohup` on Windows does NOT
REM fully detach the child — the python process gets terminated when
REM the bash wrapper (and its parent Claude Code session) exits.
REM Start-Process -WindowStyle Hidden gives true Windows-native
REM detachment so the daemon survives the parent shell exiting.
REM
REM Logs stream to logs\pythia_daemon.log (append) and
REM logs\pythia_daemon.stderr.log (append).
REM
REM Flags:
REM   --loop --interval 60       — 60s tick cadence
REM   --in-flight-timeout-min 90 — requeue stale Gemini interactions after 90m
REM   --max-retries 2            — total 3 attempts before abandon

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
python scripts\pythia_daemon.py --loop --interval 60 --in-flight-timeout-min 90 --max-retries 2 >> logs\pythia_daemon.log 2>> logs\pythia_daemon.stderr.log
