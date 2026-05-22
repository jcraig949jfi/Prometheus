@echo off
REM Launcher for the Charon swarm rotation orchestrator
REM (Stygian / Lethe / Acheron / Moros / Hecate).
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\charon_loop_launch.bat" -WindowStyle Hidden
REM
REM Mirrors scripts\harmonia_loop_launch.bat (commit 9188c8c8). The
REM .bat wrapper exists because launching the python daemon directly
REM through `Bash run_in_background:true + nohup` on Windows does NOT
REM fully detach the child — the python process gets terminated when
REM the bash wrapper exits. Start-Process -WindowStyle Hidden gives
REM true Windows-native detachment so the daemon survives the parent
REM shell exiting.
REM
REM Logs stream to charon\agents\_logs\swarm.log (append) and
REM charon\agents\_logs\swarm.stderr.log (append).
REM
REM Interval: 240s = 4min (matches charon_loop.py default and v0.1
REM observation cadence in charon\agents\v02_PROPOSAL_2026-05-19.md).

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
set AGORA_REDIS_HOST=192.168.1.176
set AGORA_REDIS_PASSWORD=prometheus
python scripts\charon_loop.py --loop --interval 240 >> charon\agents\_logs\swarm.log 2>> charon\agents\_logs\swarm.stderr.log
