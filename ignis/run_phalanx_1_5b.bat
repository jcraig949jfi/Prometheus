@echo off
REM ============================================================================
REM  PHALANX 1.5B — Nullspace Tests on Evolved 1.5B Genome (Z=40.6sigma)
REM
REM  Runs the same Titan Council Round 3 decisive experiments on the new
REM  Qwen2.5-1.5B-Instruct genome evolved via CMA-ES (28 layers, d_model=1536).
REM
REM  Test A: Jacobian finite-difference (ChatGPT) — ~3 minutes
REM  Test B: RMSNorm suppression (Gemini) — ~3 minutes
REM  Test C: Random orthogonal baseline (Grok) — ~15 minutes
REM
REM  Usage: run_phalanx_1_5b.bat [GENOME_PATH] [MODEL_NAME] [TESTS]
REM  Default: 1.5B best genome, all three tests
REM  Examples:
REM    run_phalanx_1_5b.bat                          (all tests, 1.5B)
REM    run_phalanx_1_5b.bat genome.pt model AB       (Tests A and B only)
REM
REM  Compatibility notes:
REM    nullspace_tests.py reads n_layers, d_model, and layer from the model
REM    config and genome file dynamically — no hardcoded 4B assumptions found.
REM    All hook names use blocks.{layer}.hook_* with the genome's layer value.
REM    Test B monitor range uses base.n_layers. Should work out of the box.
REM ============================================================================

echo ============================================================================
echo  PHALANX 1.5B — Nullspace Tests on Z=40.6sigma Evolved Genome
echo  Qwen2.5-1.5B-Instruct ^| 28 layers ^| d_model=1536 ^| layer=23
echo  Three decisive experiments. One truth.
echo ============================================================================
echo.

set PYTHON=%~dp0..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis\phalanx_1_5b

if "%~1"=="" (
    set GENOME=%~dp0src\results\ignis\evolve_20260323_192956\best_genome_1_5b.pt
) else (
    set GENOME=%~1
)
if "%~2"=="" (
    set MODEL=Qwen/Qwen2.5-1.5B-Instruct
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
echo  PHALANX 1.5B COMPLETE
echo  Results in: %RESULTS%
echo ============================================================================
