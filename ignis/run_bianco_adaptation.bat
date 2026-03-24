@echo off
REM ============================================================================
REM  Bianco Adaptation — Three Missing Weapons
REM  Adapted from Bianco & Shiller 2026 "Beyond Behavioural Trade-Offs"
REM
REM  Step 1: Dose-response epsilon sweep (phase transition detection)
REM  Step 2: Directional ablation (causal necessity test)
REM  Step 3: Layer-wise probing (where does reasoning signal live?)
REM
REM  Runs on 1.5B and Qwen3-4B (our two most interesting scales)
REM  Estimated total: ~2-3 hours
REM ============================================================================

echo ============================================================================
echo  BIANCO ADAPTATION — Three Missing Weapons
echo  Adapted from Bianco ^& Shiller 2026
echo  "Beyond Behavioural Trade-Offs"
echo ============================================================================
echo.

set PYTHON=%~dp0..\..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis
set GENOME_15B=%RESULTS%\archives\run_2026-03-22_000632\qwen_qwen2_5-1_5b-instruct\best_genome.pt
set GENOME_4B=%RESULTS%\archives\run_2026-03-22_115143\qwen_qwen3-4b\best_genome.pt
set OUTPUT=%RESULTS%\bianco_adaptation

if not exist "%OUTPUT%" mkdir "%OUTPUT%"

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 1/6: Dose-response sweep — 1.5B
echo  Looking for phase transitions in the margin curve
echo  Estimated: ~20 minutes
echo ============================================================================
%PYTHON% "%SRC%\dose_response.py" --genome "%GENOME_15B%" --model Qwen/Qwen2.5-1.5B-Instruct --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Step 1 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 2/6: Dose-response sweep — Qwen3-4B
echo  The only model that self-corrects
echo  Estimated: ~30 minutes
echo ============================================================================
%PYTHON% "%SRC%\dose_response.py" --genome "%GENOME_4B%" --model Qwen/Qwen3-4B --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Step 2 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 3/6: Directional ablation — 1.5B
echo  Is the steering vector causally necessary?
echo  Estimated: ~15 minutes
echo ============================================================================
%PYTHON% "%SRC%\directional_ablation.py" --genome "%GENOME_15B%" --model Qwen/Qwen2.5-1.5B-Instruct --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Step 3 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 4/6: Directional ablation — Qwen3-4B
echo  Does the 4B self-correction survive ablation?
echo  Estimated: ~25 minutes
echo ============================================================================
%PYTHON% "%SRC%\directional_ablation.py" --genome "%GENOME_4B%" --model Qwen/Qwen3-4B --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Step 4 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 5/6: Layer-wise probing — 1.5B
echo  Where does reasoning signal live in the residual stream?
echo  Estimated: ~20 minutes
echo ============================================================================
%PYTHON% "%SRC%\layerwise_probe.py" --model Qwen/Qwen2.5-1.5B-Instruct --device cuda --output-dir "%OUTPUT%" --genome "%GENOME_15B%"
if errorlevel 1 echo [WARN] Step 5 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  STEP 6/6: Layer-wise probing — Qwen3-4B
echo  Cross-architecture comparison
echo  Estimated: ~30 minutes
echo ============================================================================
%PYTHON% "%SRC%\layerwise_probe.py" --model Qwen/Qwen3-4B --device cuda --output-dir "%OUTPUT%" --genome "%GENOME_4B%"
if errorlevel 1 echo [WARN] Step 6 had errors, continuing...

echo.
echo ============================================================================
echo  BIANCO ADAPTATION COMPLETE
echo  Results in: %OUTPUT%
echo  Look for:
echo    - dose_response_*.png  (phase transition = precipitation!)
echo    - ablation_*.json      (causal necessity test)
echo    - probe_heatmap_*.png  (where reasoning signal lives)
echo ============================================================================
