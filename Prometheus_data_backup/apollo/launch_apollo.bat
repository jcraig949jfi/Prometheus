@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: Apollo v2 — Launch Script (Windows)
::
:: Usage:
::   cd F:\Prometheus\apollo
::   launch_apollo.bat              — resume or start
::   launch_apollo.bat --fresh      — clear old state, start from gen 0
::
:: Stop:   Ctrl+C
:: Resume: run the same command again
:: ============================================================

set APOLLO_DIR=%~dp0
set SRC_DIR=%APOLLO_DIR%src
set LOG_DIR=%APOLLO_DIR%logs
set CKPT_DIR=%APOLLO_DIR%checkpoints

echo ============================================================
echo   APOLLO v2 — Evolutionary Primitive Routing
echo   %date% %time%
echo ============================================================
echo.

:: ── Handle --fresh flag ───────────────────────────────────────
set FRESH=0
for %%a in (%*) do (
    if "%%a"=="--fresh" set FRESH=1
)

if %FRESH%==1 (
    echo [fresh] Clearing old state...
    if exist "%CKPT_DIR%\checkpoint_gen_*.pkl" del /q "%CKPT_DIR%\checkpoint_gen_*.pkl" 2>nul
    if exist "%APOLLO_DIR%lineage\lineage_v2.jsonl" del /q "%APOLLO_DIR%lineage\lineage_v2.jsonl" 2>nul
    if exist "%APOLLO_DIR%graveyard\graveyard_v2.jsonl" del /q "%APOLLO_DIR%graveyard\graveyard_v2.jsonl" 2>nul
    if exist "%APOLLO_DIR%dashboard\status_v2.jsonl" del /q "%APOLLO_DIR%dashboard\status_v2.jsonl" 2>nul
    if exist "%LOG_DIR%\apollo_run.jsonl" del /q "%LOG_DIR%\apollo_run.jsonl" 2>nul
    echo   Cleared. Starting from generation 0.
    echo.
)

:: ── Create output directories ─────────────────────────────────
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%CKPT_DIR%" mkdir "%CKPT_DIR%"
if not exist "%APOLLO_DIR%lineage" mkdir "%APOLLO_DIR%lineage"
if not exist "%APOLLO_DIR%graveyard" mkdir "%APOLLO_DIR%graveyard"
if not exist "%APOLLO_DIR%dashboard" mkdir "%APOLLO_DIR%dashboard"

:: ── Preflight checks ──────────────────────────────────────────
cd /d "%SRC_DIR%"
python preflight.py
if errorlevel 1 (
    echo.
    echo FATAL: Preflight checks failed. Fix the issues above and retry.
    exit /b 1
)

:: ── Launch ────────────────────────────────────────────────────
echo.
echo [launch] Starting Apollo v2 (no generation limit)
echo   Logs:        %LOG_DIR%\apollo_run.jsonl
echo   Checkpoints: %CKPT_DIR%
echo   Stop: Ctrl+C    Resume: launch_apollo.bat
echo.
echo ============================================================
echo.

python -u apollo.py
