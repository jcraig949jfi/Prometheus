@echo off
REM Noesis Experiments — Options 2, 3, 4
REM  2. Framing: multi-perspective tensor traversal
REM  3. Dream State: Hebbian feature learning from composition outcomes
REM  4. Tensor-guided vs Random exploration
REM
REM Estimated: 5-15 minutes total (CPU only, no GPU needed)

setlocal
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
cd /d f:\Prometheus\organisms

REM --- Create output directories first (batch redirect needs them) ---
mkdir framing_results 2>nul
mkdir dream_results 2>nul
mkdir tensor_vs_random_results 2>nul

echo ============================================================
echo  NOESIS EXPERIMENTS
echo  Started: %date% %time%
echo ============================================================

REM --- Experiment 2: Framing ---
echo.
echo [1/3] FRAMING — Multi-perspective tensor traversal
echo Started: %date% %time%
python -u experiment_framing.py > framing_results\stdout.log 2>&1
if %errorlevel% neq 0 (
    echo   FAILED rc=%errorlevel%
    type framing_results\stdout.log
) else (
    echo   OK
    echo   Results: framing_results\framing_experiment.json
)
echo.

REM --- Experiment 3: Dream State ---
echo.
echo [2/3] DREAM STATE — Hebbian feature learning
echo Started: %date% %time%
python -u experiment_dream_state.py > dream_results\stdout.log 2>&1
if %errorlevel% neq 0 (
    echo   FAILED rc=%errorlevel%
    type dream_results\stdout.log
) else (
    echo   OK
    echo   Results: dream_results\dream_experiment.json
)
echo.

REM --- Experiment 4: Tensor vs Random ---
echo.
echo [3/3] TENSOR vs RANDOM — Existence proof
echo Started: %date% %time%
python -u experiment_tensor_vs_random.py > tensor_vs_random_results\stdout.log 2>&1
if %errorlevel% neq 0 (
    echo   FAILED rc=%errorlevel%
    type tensor_vs_random_results\stdout.log
) else (
    echo   OK
    echo   Results: tensor_vs_random_results\tensor_vs_random.json
)
echo.

echo ============================================================
echo  NOESIS EXPERIMENTS COMPLETE — %date% %time%
echo ============================================================
echo.
echo  Results:
echo    framing_results\framing_experiment.json
echo    dream_results\dream_experiment.json
echo    tensor_vs_random_results\tensor_vs_random.json
echo.
pause
