@echo off
REM ============================================================
REM Forge Pipeline — Nous + Hephaestus + Nemesis
REM
REM Launches the full pipeline in three parallel terminals:
REM   1. Nous       (blue)   — concept mining
REM   2. Hephaestus (orange) — forge + validate
REM   3. Nemesis    (red)    — adversarial co-evolution
REM
REM Uses Windows Terminal tab coloring via escape sequences.
REM All agents run indefinitely. Ctrl+C in any window to stop.
REM
REM Prerequisites: NVIDIA_API_KEY environment variable set
REM ============================================================

echo ============================================================
echo  FORGE PIPELINE — Nous + Hephaestus + Nemesis
echo ============================================================
echo.

REM Load API key from .env if not already set
if "%NVIDIA_API_KEY%"=="" (
    if exist "%~dp0agents\eos\.env" (
        for /f "tokens=1,* delims==" %%a in ('findstr /i "NVIDIA_API_KEY" "%~dp0agents\eos\.env"') do (
            set "NVIDIA_API_KEY=%%b"
        )
    )
)

REM Check API key
if "%NVIDIA_API_KEY%"=="" (
    echo ERROR: NVIDIA_API_KEY not set
    echo   Not found in environment or agents\eos\.env
    echo   set NVIDIA_API_KEY=nvapi-...
    pause
    exit /b 1
)

echo NVIDIA_API_KEY: set
echo.

REM Launch Nous (blue tab)
echo [1/3] Starting Nous (concept mining, unlimited)...
start "Nous" wt new-tab --title "Nous — Concept Mining" --tabColor "#3498db" -- cmd /k "cd /d F:\Prometheus\agents\nous\src && python nous.py --unlimited --delay 2.0"

REM Brief pause to stagger API calls
timeout /t 5 /nobreak >nul

REM Launch Hephaestus (orange tab)
echo [2/3] Starting Hephaestus (forge, 58-category battery)...
start "Hephaestus" wt new-tab --title "Hephaestus — The Forge" --tabColor "#e67e22" -- cmd /k "cd /d F:\Prometheus\agents\hephaestus\src && python hephaestus.py --poll-interval 300 --coeus-interval 50 --reports-interval 50"

REM Brief pause
timeout /t 3 /nobreak >nul

REM Launch Nemesis (red tab)
echo [3/3] Starting Nemesis (adversarial, 2min cycles)...
start "Nemesis" wt new-tab --title "Nemesis — Adversarial" --tabColor "#e74c3c" -- cmd /k "cd /d F:\Prometheus\agents\nemesis\src && python nemesis.py --poll-interval 120"

echo.
echo ============================================================
echo  All three agents launched in Windows Terminal tabs.
echo.
echo  Nous:       [BLUE]   concept mining (unlimited, Coeus-weighted)
echo  Hephaestus: [ORANGE] forge + validate (58-cat battery, polls 5min)
echo              auto-triggers Coeus + reports every 50 forges
echo  Nemesis:    [RED]    adversarial MAP-Elites (2min cycles)
echo.
echo  Each tab can be stopped independently with Ctrl+C.
echo ============================================================
pause
