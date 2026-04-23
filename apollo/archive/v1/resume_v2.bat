@echo off
REM Apollo v2 — Resume from checkpoint (no cleanup)
REM Usage: double-click or run from terminal

cd /d "%~dp0\.."
echo Apollo v2 — resuming from %cd%
echo Start time: %date% %time%

REM Show latest checkpoint
for /f "delims=" %%f in ('dir /b /o:n apollo\checkpoints\checkpoint_gen_*.pkl 2^>nul') do set LATEST=%%f
if defined LATEST (
    echo Resuming from: %LATEST%
) else (
    echo WARNING: No checkpoint found — will start from scratch
)

REM Launch detached
start "Apollo v2" /min cmd /c "set PYTHONUNBUFFERED=1 && python apollo\src\apollo.py > apollo\apollo_v2_run.log 2>&1"
echo Apollo v2 launched in background (minimized window)
echo Log: apollo\apollo_v2_run.log
echo.
echo Monitoring commands:
echo   type apollo\apollo_v2_run.log
echo   python apollo\src\dashboard.py
pause
