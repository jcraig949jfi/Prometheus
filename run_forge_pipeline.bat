@echo off
REM ============================================================
REM Forge Pipeline — Nous + Hephaestus + Nemesis
REM
REM Launches the full pipeline in three parallel terminals:
REM   1. Nous     — concept mining (continuous, Coeus-weighted sampling)
REM   2. Hephaestus — forge + validate (continuous, auto-triggers Coeus + reports)
REM   3. Nemesis  — adversarial co-evolution (continuous, MAP-Elites grid)
REM
REM All agents run indefinitely on timer loops. Ctrl+C in any window
REM to stop that agent. Close this window to stop all three.
REM
REM Prerequisites: NVIDIA_API_KEY environment variable set
REM ============================================================

echo ============================================================
echo  FORGE PIPELINE — Nous + Hephaestus + Nemesis
echo ============================================================
echo.

REM Check API key
if "%NVIDIA_API_KEY%"=="" (
    echo ERROR: NVIDIA_API_KEY not set
    echo   set NVIDIA_API_KEY=nvapi-...
    pause
    exit /b 1
)

echo NVIDIA_API_KEY: set
echo.

REM Launch Nous (continuous concept mining)
echo [1/3] Starting Nous (concept mining, unlimited)...
start "Nous — Concept Mining" cmd /k "cd /d F:\Prometheus\agents\nous\src && python nous.py --unlimited --delay 2.0"

REM Brief pause to stagger API calls
timeout /t 5 /nobreak >nul

REM Launch Hephaestus (continuous forge, auto Coeus + reports every 50)
echo [2/3] Starting Hephaestus (forge, continuous, Coeus every 50)...
start "Hephaestus — The Forge" cmd /k "cd /d F:\Prometheus\agents\hephaestus\src && python hephaestus.py --poll-interval 300 --coeus-interval 50 --reports-interval 50"

REM Brief pause
timeout /t 3 /nobreak >nul

REM Launch Nemesis (adversarial co-evolution, 2min cycles)
echo [3/3] Starting Nemesis (adversarial, 2min cycles)...
start "Nemesis — Adversarial" cmd /k "cd /d F:\Prometheus\agents\nemesis\src && python nemesis.py --poll-interval 120"

echo.
echo ============================================================
echo  All three agents launched in separate windows.
echo.
echo  Nous:       concept mining (unlimited, Coeus-weighted)
echo  Hephaestus: forge + validate (polls Nous every 5min)
echo              auto-triggers Coeus + reports every 50 forges
echo  Nemesis:    adversarial MAP-Elites (2min cycles)
echo.
echo  Close this window or press any key to continue.
echo  Each agent window can be stopped independently with Ctrl+C.
echo ============================================================
pause
