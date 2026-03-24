@echo off
REM ============================================================================
REM Prometheus / Ignis — Precipitation Hunt Batch
REM
REM Runs 5 steps sequentially to test whether the 1.5B WEAK_SIGNAL
REM is real and whether mid-layer injection finds native circuits.
REM
REM Estimated total time: 3-6 hours (safe to leave unattended)
REM
REM Steps:
REM   1. Compute delta_proj at 1.5B (both cosine + subspace methods)
REM   2. Expanded RPH eval at 1.5B with 50+ prompt pairs
REM   3. Build reasoning subspace at layers 14, 18, 21
REM   4. Compute delta_proj at all available scales (0.5B, 1.5B, 3B, Qwen3-4B)
REM   5. Multi-layer Ignis run at 1.5B (layers 14, 18, 21)
REM ============================================================================

cd /d F:\Prometheus\ignis\src

echo.
echo ============================================================================
echo  STEP 1/5: Compute delta_proj at 1.5B
echo  Estimated: ~30 minutes
echo ============================================================================
echo.

python compute_delta_proj.py --model 1.5B --device cuda --method both

if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Step 1 failed with error %ERRORLEVEL% — continuing to step 2
)

echo.
echo ============================================================================
echo  STEP 2/5: Expanded RPH eval at 1.5B (50+ prompt pairs)
echo  Estimated: ~45 minutes
echo ============================================================================
echo.

python eval_rph_survivors.py --models 1.5B --device cuda --archive-dir results/ignis/archives --pairs ../data/rph_counterfactual_pairs_expanded.json

if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Step 2 failed with error %ERRORLEVEL% — continuing to step 3
)

echo.
echo ============================================================================
echo  STEP 3/5: Build reasoning subspace at layers 14, 18, 21
echo  Estimated: ~15 minutes
echo ============================================================================
echo.

python build_reasoning_subspace.py --model "Qwen/Qwen2.5-1.5B-Instruct" --layers 14 18 21 --device cuda

if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Step 3 failed with error %ERRORLEVEL% — continuing to step 4
)

echo.
echo ============================================================================
echo  STEP 4/5: Compute delta_proj across all scales
echo  Estimated: ~90 minutes (loads 4 models sequentially)
echo ============================================================================
echo.

python compute_delta_proj.py --model 0.5B 1.5B 3B Qwen3-4B --device cuda --method both

if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Step 4 failed with error %ERRORLEVEL% — continuing to step 5
)

echo.
echo ============================================================================
echo  STEP 5/5: Multi-layer Ignis run at 1.5B (layers 14, 18, 21)
echo  Estimated: 2-4 hours (15 gens x 40 pop x 3 layer configs)
echo ============================================================================
echo.

python main.py --config ../configs/marathon_1_5b_multilayer.yaml

echo.
echo ============================================================================
echo  PRECIPITATION HUNT COMPLETE
echo  Check results in:
echo    - results/ignis/delta_proj_*.json
echo    - results/ignis/rph_eval_*.json
echo    - results/ignis/subspaces/
echo    - results/ignis_multilayer/
echo ============================================================================
echo.

pause
