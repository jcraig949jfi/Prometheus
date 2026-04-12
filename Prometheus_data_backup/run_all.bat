@echo off
REM ============================================================
REM  PROMETHEUS MASTER LAUNCHER
REM
REM  Starts ALL autonomous loops in parallel:
REM    1. Intelligence Pipeline (Eos → Aletheia → Metis → Hermes)
REM    2. Forge Pipeline (Nous → Hephaestus → Nemesis + Coeus)
REM
REM  Both run continuously until stopped.
REM  GPU is NOT consumed — these are CPU + API only.
REM  GPU stays free for Ignis/Rhea/Athena CLI.
REM
REM  Usage:
REM    run_all.bat              -- both pipelines, default intervals
REM    run_all.bat forge        -- forge pipeline only
REM    run_all.bat intel        -- intelligence pipeline only
REM ============================================================

echo ============================================================
echo  PROMETHEUS — All Systems Launch
echo  %date% %time%
echo ============================================================
echo.

cd /d "%~dp0"

REM Check API key
if "%NVIDIA_API_KEY%"=="" (
    echo [WARN] NVIDIA_API_KEY not set — forge pipeline will fail
    echo   set NVIDIA_API_KEY=nvapi-...
    echo.
)

if "%1"=="forge" goto :forge_only
if "%1"=="intel" goto :intel_only

REM === LAUNCH BOTH ===

echo [1/2] Starting Intelligence Pipeline (Eos + Aletheia + Metis + Hermes)
echo       Cycles every 2 hours. CPU + API only.
start "Prometheus — Intelligence" cmd /k "cd /d %~dp0 && python pronoia.py scan --every 2 --publish"
timeout /t 5 /nobreak >nul

echo [2/2] Starting Forge Pipeline (Nous + Hephaestus + Nemesis)
echo       Continuous. CPU + API only.
call run_forge_pipeline.bat

goto :done

:forge_only
echo Starting Forge Pipeline only...
call run_forge_pipeline.bat
goto :done

:intel_only
echo Starting Intelligence Pipeline only...
start "Prometheus — Intelligence" cmd /k "cd /d %~dp0 && python pronoia.py scan --every 2 --publish"
goto :done

:done
echo.
echo ============================================================
echo  All pipelines launched.
echo  Intelligence: cycles every 2h (Eos + Aletheia + Metis + Hermes)
echo  Forge: continuous (Nous + Hephaestus + Nemesis + Coeus)
echo  GPU: FREE for Ignis / Rhea / Athena CLI
echo ============================================================
