@echo off
REM ============================================================================
REM  CMA-ES EVOLUTION — Find low-epsilon channels in 1.5B attractor basins
REM
REM  The basin escape histogram confirmed ridged geometry: random directions
REM  need epsilon>3.71 to flip traps, but oriented directions can do it at
REM  epsilon 2-4. CMA-ES finds those oriented directions.
REM
REM  Usage:
REM    run_evolve_1_5b.bat
REM    run_evolve_1_5b.bat 200
REM    run_evolve_1_5b.bat 500 2.5 23 results\ignis\custom_run
REM
REM  Arguments (all optional):
REM    %1 — Number of generations (default: 500)
REM    %2 — Epsilon for fitness eval (default: 3.0)
REM    %3 — Injection layer (default: 23)
REM    %4 — Output directory (default: auto-timestamped)
REM ============================================================================

echo ============================================================================
echo  CMA-ES EVOLUTION — Qwen2.5-1.5B-Instruct Steering Vector Search
echo  Finding low-epsilon channels through ridged attractor basins
echo ============================================================================
echo.

set PYTHON=%~dp0..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src

REM Parse optional arguments with defaults
set N_GENS=%~1
if "%N_GENS%"=="" set N_GENS=500

set EPSILON=%~2
if "%EPSILON%"=="" set EPSILON=3.0

set LAYER=%~3
if "%LAYER%"=="" set LAYER=23

set OUTDIR=%~4

echo   Generations: %N_GENS%
echo   Epsilon:     %EPSILON%
echo   Layer:       %LAYER%
if not "%OUTDIR%"=="" echo   Output:      %OUTDIR%
echo.

REM Build command
set CMD=%PYTHON% "%SRC%\evolve_1_5b.py" --model Qwen/Qwen2.5-1.5B-Instruct --device cuda --n-generations %N_GENS% --epsilon %EPSILON% --layer %LAYER%

if not "%OUTDIR%"=="" set CMD=%CMD% --output-dir "%OUTDIR%"

echo   Running: %CMD%
echo.

%CMD%

if errorlevel 1 (
    echo.
    echo [ERROR] Evolution failed. Check GPU memory and model availability.
    exit /b 1
)

echo.
echo ============================================================================
echo  Evolution complete. Check output directory for:
echo    best_genome_1_5b.pt    — Best evolved steering vector
echo    evolution_log_*.json   — Full generation-by-generation log
echo    final_eval_*.json      — Held-out evaluation results
echo    checkpoint_gen*.pt     — Periodic checkpoints
echo ============================================================================
