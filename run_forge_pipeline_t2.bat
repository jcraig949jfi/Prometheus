@echo off
REM ============================================================
REM Forge Pipeline T2 — Nous T2 + Hephaestus T2 + Nemesis T2
REM
REM Launches the Tier 2 pipeline in three parallel terminals:
REM   1. Nous T2       (green)   — substrate mining from T1 tools
REM   2. Hephaestus T2 (yellow)  — forge + validate via DeepSeek/NVIDIA
REM   3. Nemesis T2    (magenta) — adversarial co-evolution
REM
REM T2 takes T1 outputs as input:
REM   - Nous T2 scans the T1 ledger for substrate (forged + near-miss tools)
REM   - Hephaestus T2 generates tools using T1 primitives + amino acids
REM   - Nemesis T2 tests T2 tools adversarially
REM
REM API priority: DeepSeek (primary) -> NVIDIA (fallback). No Augment.
REM
REM Prerequisites:
REM   - DEEPSEEK_API_KEY (or in DeepseekKey.txt)
REM   - NVIDIA_API_KEY (fallback, from agents\eos\.env or environment)
REM
REM Usage:
REM   run_forge_pipeline_t2.bat
REM   run_forge_pipeline_t2.bat --batch-size 24
REM ============================================================

echo ============================================================
echo  FORGE PIPELINE T2 — Tier 2 Autonomous Evolution
echo ============================================================
echo.

REM ============================================================
REM Parse optional flags (passed through to Hephaestus T2)
REM ============================================================
set HEPH_EXTRA_FLAGS=

:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--batch-size" (
    set "HEPH_EXTRA_FLAGS=%HEPH_EXTRA_FLAGS% --batch-size %~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--delay" (
    set "HEPH_EXTRA_FLAGS=%HEPH_EXTRA_FLAGS% --delay %~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--poll-interval" (
    set "HEPH_EXTRA_FLAGS=%HEPH_EXTRA_FLAGS% --poll-interval %~2"
    shift
    shift
    goto parse_args
)
echo WARNING: Unknown argument ignored: %~1
shift
goto parse_args
:args_done

REM ============================================================
REM Check for API keys
REM ============================================================

REM Check DeepSeek key
set DS_KEY_FOUND=0
if not "%DEEPSEEK_API_KEY%"=="" set DS_KEY_FOUND=1
if exist "%~dp0DeepseekKey.txt" set DS_KEY_FOUND=1

if "%DS_KEY_FOUND%"=="0" (
    echo WARNING: DEEPSEEK_API_KEY not found in environment or DeepseekKey.txt
    echo          DeepSeek calls will fail; NVIDIA fallback will be used.
)

REM Load NVIDIA key from .env if not already set
if "%NVIDIA_API_KEY%"=="" (
    if exist "%~dp0agents\eos\.env" (
        for /f "tokens=1,* delims==" %%a in ('findstr /i "NVIDIA_API_KEY" "%~dp0agents\eos\.env"') do (
            set "NVIDIA_API_KEY=%%b"
        )
    )
)

if "%NVIDIA_API_KEY%"=="" (
    echo WARNING: NVIDIA_API_KEY not found — fallback will not work
    if "%DS_KEY_FOUND%"=="0" (
        echo ERROR: No API keys available. Set DEEPSEEK_API_KEY or NVIDIA_API_KEY.
        pause
        exit /b 1
    )
)

echo API keys:
if "%DS_KEY_FOUND%"=="1" echo   DeepSeek: found (primary)
if "%DS_KEY_FOUND%"=="0" echo   DeepSeek: NOT FOUND
if not "%NVIDIA_API_KEY%"=="" echo   NVIDIA:   found (fallback)
if "%NVIDIA_API_KEY%"=="" echo   NVIDIA:   NOT FOUND
echo Hephaestus extra flags:%HEPH_EXTRA_FLAGS%
echo.

REM ============================================================
REM Launch Nous T2 (green tab)
REM ============================================================
echo [1/3] Starting Nous T2 (substrate mining, unlimited)...
start "Nous T2" wt new-tab --title "Nous T2 — Substrate Mining" --tabColor "#2ecc71" -- cmd /k "cd /d %~dp0forge\v2\nous_t2\src && python nous_t2.py --unlimited --delay 120.0 --n 50"

REM Brief pause to stagger
timeout /t 5 /nobreak >nul

REM ============================================================
REM Launch Hephaestus T2 (yellow tab)
REM ============================================================
echo [2/3] Starting Hephaestus T2 (forge, DeepSeek primary)...
start "Hephaestus T2" wt new-tab --title "Hephaestus T2 — The Forge" --tabColor "#f1c40f" -- cmd /k "cd /d %~dp0forge\v2\hephaestus_t2\src && python hephaestus_t2.py --poll-interval 300 --batch-size 12 --delay 2.0%HEPH_EXTRA_FLAGS%"

REM Brief pause
timeout /t 3 /nobreak >nul

REM ============================================================
REM Launch Nemesis T2 (magenta tab)
REM ============================================================
echo [3/3] Starting Nemesis T2 (adversarial, 2min cycles)...
start "Nemesis T2" wt new-tab --title "Nemesis T2 — Adversarial" --tabColor "#9b59b6" -- cmd /k "cd /d %~dp0forge\v2\nemesis_t2\src && python nemesis_t2.py --poll-interval 120"

echo.
echo ============================================================
echo  All three T2 agents launched in Windows Terminal tabs.
echo.
echo  Nous T2:       [GREEN]   substrate mining (re-scans T1 ledger each cycle)
echo  Hephaestus T2: [YELLOW]  forge + validate (DeepSeek primary, NVIDIA fallback)
echo                  API: DeepSeek -> NVIDIA (no Augment)
echo  Nemesis T2:    [MAGENTA] adversarial MAP-Elites (2min cycles)
echo.
echo  Each tab can be stopped independently with Ctrl+C.
echo  T2 runs PARALLEL to T1 — T1 is the substrate generator.
echo ============================================================
pause
