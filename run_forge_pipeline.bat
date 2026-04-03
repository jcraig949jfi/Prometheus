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
REM
REM Optional flags:
REM   --use-aggie-api           Enable Augment API fallback when NVIDIA times out.
REM                             WARNING: burns Augment tokens — use during outages only.
REM   --force-aggie             Skip NVIDIA API entirely; always use Augment API.
REM                             WARNING: burns Augment tokens continuously; implies --use-aggie-api.
REM   --aggie-model <model>     Model for Augment (default: sonnet4.5).
REM                             Choices: haiku4.5, sonnet4.5, sonnet4, gpt5
REM
REM Usage:
REM   run_forge_pipeline.bat
REM   run_forge_pipeline.bat --use-aggie-api
REM   run_forge_pipeline.bat --use-aggie-api --aggie-model haiku4.5
REM   run_forge_pipeline.bat --force-aggie
REM   run_forge_pipeline.bat --force-aggie --aggie-model sonnet4.5
REM ============================================================

echo ============================================================
echo  FORGE PIPELINE — Nous + Hephaestus + Nemesis
echo ============================================================
echo.

REM ============================================================
REM Parse optional flags
REM ============================================================
set HEPH_EXTRA_FLAGS=
set USE_AGGIE_API=0
set FORCE_AGGIE=0

:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--use-aggie-api" (
    set "USE_AGGIE_API=1"
    set "HEPH_EXTRA_FLAGS=%HEPH_EXTRA_FLAGS% --use-aggie-api"
    shift
    goto parse_args
)
if /i "%~1"=="--force-aggie" (
    set "FORCE_AGGIE=1"
    set "USE_AGGIE_API=1"
    set "HEPH_EXTRA_FLAGS=%HEPH_EXTRA_FLAGS% --force-aggie"
    shift
    goto parse_args
)
if /i "%~1"=="--aggie-model" (
    set "HEPH_EXTRA_FLAGS=%HEPH_EXTRA_FLAGS% --aggie-model %~2"
    shift
    shift
    goto parse_args
)
echo WARNING: Unknown argument ignored: %~1
shift
goto parse_args
:args_done

REM ============================================================
REM Load API key from .env if not already set
REM ============================================================
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
echo Hephaestus extra flags:%HEPH_EXTRA_FLAGS%
if "%FORCE_AGGIE%"=="1" echo Augment API mode: PRIMARY -- skip NVIDIA, always use Augment
if "%FORCE_AGGIE%"=="0" if "%USE_AGGIE_API%"=="1" echo Augment API mode: FALLBACK -- use when NVIDIA fails
if "%FORCE_AGGIE%"=="0" if "%USE_AGGIE_API%"=="0" echo Augment API mode: disabled -- pass --use-aggie-api or --force-aggie to enable
echo.

REM Launch Nous (blue tab)
echo [1/3] Starting Nous (concept mining, unlimited)...
start "Nous" wt new-tab --title "Nous — Concept Mining" --tabColor "#3498db" -- cmd /k "cd /d F:\Prometheus\agents\nous\src && python nous.py --unlimited --delay 2.0"

REM Brief pause to stagger API calls
timeout /t 5 /nobreak >nul

REM Launch Hephaestus (orange tab)
echo [2/3] Starting Hephaestus (forge, 58-category battery)...
start "Hephaestus" wt new-tab --title "Hephaestus — The Forge" --tabColor "#e67e22" -- cmd /k "cd /d F:\Prometheus\agents\hephaestus\src && python hephaestus.py --poll-interval 300 --coeus-interval 50 --reports-interval 50%HEPH_EXTRA_FLAGS%"

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
if "%FORCE_AGGIE%"=="1" echo              !!! AUGMENT API PRIMARY MODE -- skip NVIDIA !!!
if "%FORCE_AGGIE%"=="0" if "%USE_AGGIE_API%"=="1" echo              Augment API fallback ENABLED
echo  Nemesis:    [RED]    adversarial MAP-Elites (2min cycles)
echo.
echo  Each tab can be stopped independently with Ctrl+C.
echo ============================================================
pause
