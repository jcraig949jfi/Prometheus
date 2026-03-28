@echo off
REM ============================================================
REM  Overnight Triple Experiment — The Card Does Not Rest
REM  Run 1: 1.7B LoRA CMA-ES (~2h)
REM  Run 2: 360M Loop Closure (~15m)
REM  Run 3: 135M Coherence Evolution (~1h)
REM  Total: ~3.5 hours
REM ============================================================

set SCRIPT_DIR=%~dp0src
set TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo ============================================================
echo  OVERNIGHT TRIPLE EXPERIMENT
echo  Started: %date% %time%
echo  Estimated runtime: ~3.5 hours
echo ============================================================

REM --- Run 1: 1.7B gate_proj + v_proj CMA-ES (rank-8, ~2 hours) ---
echo.
echo ============================================================
echo  RUN 1/3: 1.7B LoRA CMA-ES (gate_proj + v_proj, rank-8)
echo  Target: ~2 hours
echo ============================================================
echo.

python "%SCRIPT_DIR%\evolve_lora_gate_v.py" --n-generations 500 --popsize 32 --stdev-init 0.005
if %errorlevel% neq 0 (
    echo [WARN] Run 1 exited with code %errorlevel%. Continuing...
)

echo.
echo  Run 1 complete: %date% %time%
echo.

REM --- Run 2: 360M Loop Closure (~15 min) ---
echo ============================================================
echo  RUN 2/3: 360M Loop Closure (generate/verify/train/eval)
echo  Target: ~15 minutes
echo ============================================================
echo.

python "%SCRIPT_DIR%\loop_closure.py" --n-attempts 300
if %errorlevel% neq 0 (
    echo [WARN] Run 2 exited with code %errorlevel%. Continuing...
)

echo.
echo  Run 2 complete: %date% %time%
echo.

REM --- Run 3: 135M Coherence-Preserving Evolution (~1 hour) ---
echo ============================================================
echo  RUN 3/3: 135M Coherence-Preserving CMA-ES
echo  fitness = 0.6*ejection + 0.4*survival - 0.3*ppl_increase
echo  Target: ~1 hour
echo ============================================================
echo.

python "%SCRIPT_DIR%\evolve_coherence.py" --n-generations 300 --popsize 32 --epsilon 3.0
if %errorlevel% neq 0 (
    echo [WARN] Run 3 exited with code %errorlevel%. Continuing...
)

echo.
echo  Run 3 complete: %date% %time%
echo.

REM --- Commit and push ---
echo ============================================================
echo  COMMITTING AND PUSHING RESULTS
echo ============================================================
echo.

cd /d "%~dp0.."
git add -A
git commit -m "Overnight triple: LoRA CMA-ES 1.7B, loop closure 360M, coherence evolution 135M

Run 1: Rank-8 LoRA perturbation on gate_proj + v_proj via CMA-ES
Run 2: Generate/verify/fine-tune loop closure on 360M
Run 3: Coherence-preserving evolution (ejection suppression + perplexity penalty)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"

git push

echo.
echo ============================================================
echo  ALL EXPERIMENTS COMPLETE
echo  Finished: %date% %time%
echo ============================================================
