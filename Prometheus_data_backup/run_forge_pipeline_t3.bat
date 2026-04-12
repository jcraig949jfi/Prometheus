@echo off
REM ============================================================
REM Forge Pipeline T3 — Nous T3 + Hephaestus T3
REM
REM Launches the Tier 3 pipeline in parallel Windows Terminal tabs:
REM   1. Nous T3       (cyan)    — cross-tier substrate mining (T1+T2)
REM   2. Hephaestus T3 (orange)  — forge via Qwen Coder 30B (Ollama local)
REM
REM Models:
REM   Code generation: Qwen Coder 30B (Ollama, local GPU)
REM   LLM fallback:    DeepSeek API
REM   NOT used:        Augment, Claude, Gemini, ChatGPT
REM
REM Prerequisites:
REM   - Ollama running with qwen2.5-coder:7b-instruct available
REM   - DEEPSEEK_API_KEY (fallback only, from DeepseekKey.txt or env)
REM   - GPU free (Qwen 2.5 Coder 7B needs ~4.7GB)
REM
REM Usage:
REM   run_forge_pipeline_t3.bat
REM   run_forge_pipeline_t3.bat --batch-size 10
REM   run_forge_pipeline_t3.bat --deepseek-only
REM ============================================================

echo ============================================================
echo  FORGE PIPELINE T3 — Tier 3 Autonomous Evolution
echo  Code gen: Qwen Coder 30B (Ollama local)
echo  Fallback: DeepSeek API
echo ============================================================
echo.

REM ============================================================
REM Parse optional flags (passed through to Hephaestus T3)
REM ============================================================
set HEPH_EXTRA_FLAGS=
set DEEPSEEK_ONLY=0

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
if /i "%~1"=="--deepseek-only" (
    set "DEEPSEEK_ONLY=1"
    set "HEPH_EXTRA_FLAGS=%HEPH_EXTRA_FLAGS% --deepseek-only"
    shift
    goto parse_args
)
echo WARNING: Unknown argument ignored: %~1
shift
goto parse_args
:args_done

REM ============================================================
REM Check Ollama is running and model is available
REM ============================================================
if "%DEEPSEEK_ONLY%"=="0" (
    echo Checking Ollama...
    ollama list 2>nul | findstr /i "qwen2.5-coder:7b-instruct" >nul
    if errorlevel 1 (
        echo WARNING: qwen2.5-coder:7b-instruct not found in Ollama.
        echo          Run: ollama pull qwen2.5-coder:7b-instruct
        echo          Or use --deepseek-only to skip local model.
        pause
        exit /b 1
    )
    echo   Ollama: qwen2.5-coder:7b-instruct available
)

REM ============================================================
REM Check DeepSeek key (fallback / deepseek-only)
REM ============================================================
set DS_KEY_FOUND=0
if not "%DEEPSEEK_API_KEY%"=="" set DS_KEY_FOUND=1
if exist "%~dp0DeepseekKey.txt" set DS_KEY_FOUND=1

if "%DS_KEY_FOUND%"=="1" (
    echo   DeepSeek: key found (fallback)
) else (
    echo   DeepSeek: key NOT FOUND
    if "%DEEPSEEK_ONLY%"=="1" (
        echo ERROR: --deepseek-only requires DEEPSEEK_API_KEY
        pause
        exit /b 1
    )
    echo            (Ollama primary will be used; no API fallback)
)

echo.
if "%DEEPSEEK_ONLY%"=="1" echo   Mode: DeepSeek API only (no local GPU)
if "%DEEPSEEK_ONLY%"=="0" echo   Mode: Qwen Coder 30B (local GPU) + DeepSeek fallback
echo   Hephaestus flags:%HEPH_EXTRA_FLAGS%
echo.

REM ============================================================
REM Launch Nous T3 (cyan tab)
REM ============================================================
echo [1/2] Starting Nous T3 (cross-tier substrate mining)...
start "Nous T3" wt new-tab --title "Nous T3 — Substrate Mining" --tabColor "#1abc9c" -- cmd /k "cd /d %~dp0forge\v3\nous_t3\src && python nous_t3.py --unlimited --delay 120.0 --n 50"

REM Brief pause to stagger
timeout /t 5 /nobreak >nul

REM ============================================================
REM Launch Hephaestus T3 (orange tab)
REM ============================================================
echo [2/2] Starting Hephaestus T3 (forge via Qwen Coder)...
start "Hephaestus T3" wt new-tab --title "Hephaestus T3 — The Forge" --tabColor "#e67e22" -- cmd /k "cd /d %~dp0forge\v3\hephaestus_t3\src && python hephaestus_t3.py --poll-interval 300 --batch-size 20 --delay 5.0%HEPH_EXTRA_FLAGS%"

echo.
echo ============================================================
echo  T3 pipeline launched in Windows Terminal tabs.
echo.
echo  Nous T3:       [CYAN]   substrate mining (T1+T2 cross-tier, 2min cycles)
echo  Hephaestus T3: [ORANGE] forge + validate (20-cat T3 battery, 5min cycles)
if "%DEEPSEEK_ONLY%"=="0" echo                  Primary: Qwen Coder 30B (Ollama local GPU)
if "%DEEPSEEK_ONLY%"=="0" echo                  Fallback: DeepSeek API
if "%DEEPSEEK_ONLY%"=="1" echo                  DeepSeek API only (no local model)
echo.
echo  Nemesis T3 and Coeus T3 not yet built — will be added later.
echo  Each tab can be stopped independently with Ctrl+C.
echo  T3 runs PARALLEL to T1/T2 — lower tiers are substrate generators.
echo ============================================================
pause
