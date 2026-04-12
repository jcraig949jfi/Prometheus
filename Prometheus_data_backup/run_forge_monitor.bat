@echo off
REM ============================================================
REM Forge V2 Pipeline Monitor — runs every 30 minutes
REM
REM Checks health of Nous T2, Hephaestus T2, Nemesis T2 via logs.
REM Summarizes each component via DeepSeek API.
REM Checks DeepSeek token balance.
REM Commits and pushes the report to remote.
REM
REM Usage:
REM   run_forge_monitor.bat             (30 min loop, default)
REM   run_forge_monitor.bat --once      (single report, no loop)
REM ============================================================

echo ============================================================
echo  FORGE V2 PIPELINE MONITOR
echo ============================================================
echo.

if /i "%~1"=="--once" (
    echo Running single report...
    python "%~dp0forge\v2\forge_monitor.py" --loop 0
) else (
    echo Running every 30 minutes. Press Ctrl+C to stop.
    echo.
    python "%~dp0forge\v2\forge_monitor.py"
)
