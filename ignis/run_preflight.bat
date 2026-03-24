@echo off
REM ============================================================================
REM  PREFLIGHT — Data integrity verification gate
REM  Run before any experiment. If this fails, results cannot be trusted.
REM
REM  Usage: run_preflight.bat [GENOME_PATH] [MODEL_NAME]
REM  Default: Qwen3-4B best genome
REM ============================================================================

echo ============================================================================
echo  PREFLIGHT — Verify Before You Trust
echo ============================================================================
echo.

set PYTHON=%~dp0..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis\preflight

if "%~1"=="" (
    set GENOME=%~dp0src\results\ignis\archives\run_2026-03-22_115143\qwen_qwen3-4b\best_genome.pt
) else (
    set GENOME=%~1
)
if "%~2"=="" (
    set MODEL=Qwen/Qwen3-4B
) else (
    set MODEL=%~2
)

if not exist "%RESULTS%" mkdir "%RESULTS%"

%PYTHON% "%SRC%\preflight.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%RESULTS%"

if errorlevel 1 (
    echo.
    echo  *** PREFLIGHT FAILED — DO NOT PROCEED ***
    echo.
    exit /b 1
) else (
    echo.
    echo  PREFLIGHT PASSED — safe to proceed
    echo.
    exit /b 0
)
