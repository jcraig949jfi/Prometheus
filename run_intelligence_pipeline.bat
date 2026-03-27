@echo off
REM ============================================================
REM Prometheus Intelligence Pipeline
REM Eos → Aletheia → Skopos → Metis → Clymene → Hermes
REM
REM Horizon scanning, knowledge extraction, scoring, briefing,
REM archiving, and email digest delivery.
REM
REM Usage:
REM   run_intelligence_pipeline.bat           -- single cycle
REM   run_intelligence_pipeline.bat loop      -- continuous (every 2h)
REM   run_intelligence_pipeline.bat loop 4    -- continuous (every 4h)
REM ============================================================

echo ============================================================
echo  Prometheus Intelligence Pipeline
echo ============================================================
echo.

REM Check for Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found in PATH
    exit /b 1
)

REM Navigate to repo root
cd /d "%~dp0"

if "%1"=="loop" (
    set HOURS=%2
    if "%HOURS%"=="" set HOURS=2
    echo [MODE] Continuous — every %HOURS% hours
    echo.
    python pronoia.py scan --every %HOURS% --publish
) else (
    echo [MODE] Single cycle
    echo.
    python pronoia.py scan --publish
)
