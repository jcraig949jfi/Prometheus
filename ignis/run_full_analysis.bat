@echo off
REM ============================================================================
REM  FULL ANALYSIS SUITE — Seven Independent Verdicts
REM  Built from Bianco 2026 methodology + Titan Council contributions
REM
REM  Tests 1-3: Bianco adaptation (dose-response, ablation, probing)
REM  Test  4:   Activation patching (Claude + Gemini) + CoT patch (Grok)
REM  Test  5:   Distributed Alignment Search (DeepSeek)
REM  Tests 6-10: Generalization gauntlet (ChatGPT)
REM
REM  Runs on one model+genome at a time. Estimated: 3-5 hours total.
REM  If all say BYPASS — it's bypass. If two say PRECIPITATION — paper time.
REM ============================================================================

echo ============================================================================
echo  FULL ANALYSIS SUITE — Seven Independent Verdicts
echo  "Tell us what's wrong." — Titan Council Prompt 01
echo ============================================================================
echo.

set PYTHON=%~dp0..\..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis
set OUTPUT=%RESULTS%\full_analysis

if "%~1"=="" (
    echo Usage: run_full_analysis.bat GENOME_PATH [MODEL_NAME]
    echo.
    echo   GENOME_PATH: path to best_genome.pt
    echo   MODEL_NAME:  HuggingFace model name ^(default: Qwen/Qwen2.5-1.5B-Instruct^)
    echo.
    echo Example:
    echo   run_full_analysis.bat results\ignis\archives\run_...\best_genome.pt
    echo   run_full_analysis.bat results\ignis\archives\run_...\best_genome.pt Qwen/Qwen3-4B
    exit /b 1
)

set GENOME=%~1
set MODEL=%~2
if "%MODEL%"=="" set MODEL=Qwen/Qwen2.5-1.5B-Instruct

if not exist "%OUTPUT%" mkdir "%OUTPUT%"

echo   Genome: %GENOME%
echo   Model:  %MODEL%
echo   Output: %OUTPUT%
echo.

REM ============================================================================
echo.
echo ============================================================================
echo  TEST 1: Dose-Response Epsilon Sweep
echo  Phase transition = precipitation. Linear = bypass.
echo ============================================================================
%PYTHON% "%SRC%\dose_response.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Test 1 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  TEST 2: Directional Ablation
echo  Causal necessity: does removing the direction kill the effect?
echo ============================================================================
%PYTHON% "%SRC%\directional_ablation.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Test 2 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  TEST 3: Layer-wise Linear Probing
echo  Where does reasoning signal live in the residual stream?
echo ============================================================================
%PYTHON% "%SRC%\layerwise_probe.py" --model %MODEL% --device cuda --output-dir "%OUTPUT%" --genome "%GENOME%"
if errorlevel 1 echo [WARN] Test 3 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  TEST 4a/4b: Activation Patching (Claude + Gemini)
echo  Which circuits carry the causal signal?
echo ============================================================================
%PYTHON% "%SRC%\titan_patching.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Test 4 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  TEST 4c: CoT Patching (Grok)
echo  Does natural reasoning exist? Can we patch it in?
echo ============================================================================
%PYTHON% "%SRC%\titan_cot_patch.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Test 4c had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  TEST 5: Distributed Alignment Search (DeepSeek)
echo  What is the minimal causal subspace dimension?
echo ============================================================================
%PYTHON% "%SRC%\titan_das.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%OUTPUT%"
if errorlevel 1 echo [WARN] Test 5 had errors, continuing...

REM ============================================================================
echo.
echo ============================================================================
echo  TESTS 6-10: Generalization Gauntlet (ChatGPT)
echo  Token, prompt, multi-step, KL, attention pattern tests
echo ============================================================================
%PYTHON% "%SRC%\titan_generalization.py" --genome "%GENOME%" --model %MODEL% --device cuda --output-dir "%OUTPUT%" --test all
if errorlevel 1 echo [WARN] Tests 6-10 had errors, continuing...

echo.
echo ============================================================================
echo  FULL ANALYSIS COMPLETE
echo  Results in: %OUTPUT%
echo.
echo  Verdicts to check:
echo    dose_response_*.json      — PHASE_TRANSITION or LINEAR?
echo    ablation_*.json           — CAUSAL or BYPASS?
echo    probe_*.json              — Where does signal live?
echo    patching_*.json           — PRECIPITATION / BYPASS / LOGIT_STEERING?
echo    cot_patch_*.json          — NATIVE_REASONING or BYPASS?
echo    das_*.json                — Minimal subspace dimension?
echo    generalization_*.json     — CONCEPT or LEXICAL? ROBUST or BRITTLE?
echo.
echo  If they all agree: you have your answer.
echo  If they disagree: that's where the science is.
echo ============================================================================
