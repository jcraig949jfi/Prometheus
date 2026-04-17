@echo off
REM ================================================================
REM  ERGON EXPLORER v2 — 20 domains, 4.6M objects, 400 domain pairs
REM  Run: double-click or: cmd /c run_explore_v2.bat
REM  Stop: Ctrl+C (checkpoints saved every 500 generations)
REM ================================================================
echo.
echo  ============================================================
echo   ERGON EXPLORER v2
echo   Started: %date% %time%
echo   Domains: 20 (core + extended)
echo   Objects: ~4.6M across EC, MF, NF, genus2, artin, knots,
echo            maass, lattices, polytopes, materials, space_groups,
echo            belyi, bianchi, groups, oeis, codata, pdg_particles,
echo            chemistry, metabolism, ec_rich
echo   Hypothesis space: 400 domain pairs x 181 features
echo  ============================================================
echo.

cd /d F:\Prometheus\ergon

REM Step 1: Build fresh tensor (takes ~40s)
echo [1/3] Building tensor (20 domains, ~40s)...
python -u tensor_builder.py --domains extended
if errorlevel 1 (
    echo TENSOR BUILD FAILED. Aborting.
    pause
    exit /b 1
)
echo.

REM Step 2: Run evolutionary explorer
echo [2/3] Starting evolutionary explorer...
echo   Generations: 5000
echo   Per generation: 20 hypotheses
echo   Checkpoint: every 500 generations
echo   Log interval: every 50 generations
echo   Estimated: ~100K hypotheses, 2-4 hours
echo.

python -u autonomous_explorer.py ^
    --generations 5000 ^
    --per-gen 20 ^
    --seed %random% ^
    --log-interval 50 ^
    --checkpoint-interval 500

echo.
echo  ============================================================
echo   EXPLORER COMPLETE: %date% %time%
echo  ============================================================
echo.

REM Step 3: Bridge survivors to Harmonia
echo [3/3] Bridging survivors to Harmonia...
for /f "delims=" %%F in ('dir /b /o-d results\archive_*.json 2^>nul') do (
    echo Bridging: results\%%F
    python -u harmonia_bridge.py results\%%F --top-k 30 --subsample 2000
    goto :done_bridge
)
echo No archive found to bridge.
:done_bridge

echo.
echo  ============================================================
echo   ALL DONE: %date% %time%
echo   Check: ergon\logs\ and ergon\results\
echo  ============================================================
pause
