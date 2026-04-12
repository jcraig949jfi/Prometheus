@echo off
REM ============================================================
REM Prometheus Intelligence Pipeline (green tab)
REM Pronoia → Eos → Aletheia → Skopos → Metis → Clymene → Hermes
REM
REM Continuous horizon scanning with publish. Defaults to every 2h.
REM
REM Usage:
REM   run_intelligence_pipeline.bat           -- continuous (every 2h)
REM   run_intelligence_pipeline.bat 4         -- continuous (every 4h)
REM   run_intelligence_pipeline.bat once      -- single cycle
REM ============================================================

REM Navigate to repo root
cd /d "%~dp0"

REM Load API keys from .env if not set
if "%NVIDIA_API_KEY%"=="" (
    if exist "agents\eos\.env" (
        for /f "tokens=1,* delims==" %%a in ('findstr /i "NVIDIA_API_KEY" "agents\eos\.env"') do (
            set "NVIDIA_API_KEY=%%b"
        )
    )
)

REM Check for Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found in PATH
    exit /b 1
)

if "%1"=="once" (
    echo [MODE] Single cycle with publish
    python pronoia.py scan --publish
) else (
    if "%1"=="" (set HOURS=2) else (set HOURS=%1)

    REM Launch in a colored Windows Terminal tab — use explicit path to avoid variable expansion issues
    start "Pronoia" wt new-tab --title "Pronoia — Intelligence Pipeline" --tabColor "#2ecc71" -- cmd /k "cd /d F:\Prometheus && python pronoia.py scan --every 2 --publish"

    echo ============================================================
    echo  Intelligence Pipeline launched in Windows Terminal tab.
    echo.
    echo  Pronoia:  [GREEN]  Eos + Aletheia + Skopos + Metis + Clymene + Hermes
    echo            Continuous — every %HOURS% hours with publish
    echo.
    echo  Stop with Ctrl+C in the Pronoia tab.
    echo ============================================================
)
