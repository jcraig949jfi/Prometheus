@echo off
REM Launcher for the Harmonia swarm rotation orchestrator.
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\harmonia_loop_launch.bat" -WindowStyle Hidden
REM
REM This wrapper exists because launching the python daemon directly through
REM `Bash run_in_background:true + nohup` on Windows does NOT fully detach
REM the child — the python process gets terminated when the bash wrapper
REM exits (observed empirically on 2026-05-19 / 2026-05-20: two daemon
REM instances both died after 6-8 ticks). Using a .bat wrapper invoked via
REM Start-Process -WindowStyle Hidden gives true Windows-native detachment.
REM
REM Logs stream to harmonia\agents\_logs\swarm.log (append) and
REM harmonia\agents\_logs\swarm.stderr.log (append).

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
set AGORA_REDIS_HOST=192.168.1.176
set AGORA_REDIS_PASSWORD=prometheus
python scripts\harmonia_loop.py --loop --interval 90 >> harmonia\agents\_logs\swarm.log 2>> harmonia\agents\_logs\swarm.stderr.log
