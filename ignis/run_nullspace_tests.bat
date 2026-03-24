@echo off
REM ============================================================================
REM  NULLSPACE TESTS — Titan Council Round 3 Decisive Experiments
REM
REM  Test A: Jacobian finite-difference (ChatGPT) — ~5 minutes
REM  Test B: RMSNorm suppression (Gemini) — ~5 minutes
REM  Test C: Random orthogonal baseline (Grok) — ~25 minutes
REM
REM  Usage: run_nullspace_tests.bat [GENOME_PATH] [MODEL_NAME] [TESTS]
REM  Default: Qwen3-4B best genome, all three tests
REM  Examples:
REM    run_nullspace_tests.bat                          (all tests, 4B)
REM    run_nullspace_tests.bat genome.pt model AB       (Tests A and B only)
REM ============================================================================

echo ============================================================================
echo  NULLSPACE TESTS — Phalanx Round 3
echo  Three decisive experiments. One truth.
echo ============================================================================
echo.

set PYTHON=%~dp0..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis\nullspace

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
if "%~3"=="" (
    set TESTS=ABC
) else (
    set TESTS=%~3
)

if not exist "%RESULTS%" mkdir "%RESULTS%"

echo   Genome: %GENOME%
echo   Model:  %MODEL%
echo   Tests:  %TESTS%
echo   Output: %RESULTS%
echo.

REM ── Single process: preflight runs inside nullspace_tests.py ──────────
REM    Model loads ONCE. Preflight checks run on the loaded model.
REM    If preflight fails, tests abort before any experiments run.
%PYTHON% "%SRC%\nullspace_tests.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%RESULTS%" --test %TESTS%

echo.
echo ============================================================================
echo  NULLSPACE TESTS COMPLETE
echo  Results in: %RESULTS%
echo ============================================================================
