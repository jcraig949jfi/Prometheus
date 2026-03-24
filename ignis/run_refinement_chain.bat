@echo off
REM ============================================================================
REM  REFINEMENT CHAIN — Validate signals, decode vector, decide next step
REM
REM  Step 0: Consolidate results from prior run
REM  Step 1: Controlled CoT test (is anti-CoT real or prompt artifact?)
REM  Step 2: SAE decomposition (what features does the vector activate?)
REM  Step 3: Decision gate (auto-analyze and recommend next step)
REM
REM  Usage: run_refinement_chain.bat [GENOME_PATH] [MODEL_NAME]
REM  Default: Qwen3-4B best genome
REM ============================================================================

echo ============================================================================
echo  REFINEMENT CHAIN
echo  Validate. Decode. Decide.
echo ============================================================================
echo.

set PYTHON=%~dp0..\..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis
set OUTPUT=%RESULTS%\refinement

if "%~1"=="" (
    set GENOME=%RESULTS%\archives\run_2026-03-22_115143\qwen_qwen3-4b\best_genome.pt
) else (
    set GENOME=%~1
)
if "%~2"=="" (
    set MODEL=Qwen/Qwen3-4B
) else (
    set MODEL=%~2
)

if not exist "%OUTPUT%" mkdir "%OUTPUT%"

echo   Genome: %GENOME%
echo   Model:  %MODEL%
echo   Output: %OUTPUT%
echo.

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 0: Consolidate prior results
echo ============================================================================

echo   Checking full_analysis outputs...
set ANALYSIS_DIR=%RESULTS%\full_analysis
if exist "%ANALYSIS_DIR%" (
    echo   Found results:
    dir /b "%ANALYSIS_DIR%\*.json" 2>nul
    dir /b "%ANALYSIS_DIR%\*.png" 2>nul
    echo.
) else (
    echo   [WARN] No full_analysis directory found
)

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 1: Controlled CoT Test
echo  Is the anti-CoT correlation real or a prompt-length artifact?
echo  Estimated: ~15 minutes
echo ============================================================================

%PYTHON% "%SRC%\controlled_cot_test.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 (
    echo   [WARN] Step 1 had errors
) else (
    echo   [OK] Controlled CoT test complete
)
echo.

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 2: SAE Decomposition
echo  What features does the vector activate?
echo  Estimated: ~30 minutes
echo ============================================================================

%PYTHON% "%SRC%\sae_decompose.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 (
    echo   [WARN] Step 2 had errors (SAE may not be available for this model)
) else (
    echo   [OK] SAE decomposition complete
)
echo.

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 3: Decision Gate
echo  Analyze Steps 1-2, recommend next experiment
echo ============================================================================

%PYTHON% "%SRC%\decision_gate.py" --results-dir "%OUTPUT%"
if errorlevel 1 (
    echo   [WARN] Decision gate had errors
) else (
    echo   [OK] Decision gate complete
)

echo.
echo ============================================================================
echo  REFINEMENT CHAIN COMPLETE
echo  Results in: %OUTPUT%
echo.
echo  Read: %OUTPUT%\decision_report.md
echo ============================================================================
