@echo off
REM Ergon Overnight Run — Tensor-native evolutionary hypothesis search
REM Expected: ~10,000 generations, ~200K hypotheses, ~8 hours at 7 hyp/s
REM Checkpoints every 1000 generations (~30 min)
REM Logs: ergon/logs/ergon_YYYYMMDD_HHMMSS.jsonl

echo ================================================================
echo  ERGON OVERNIGHT RUN
echo  Started: %date% %time%
echo ================================================================
echo.

cd /d D:\Prometheus\ergon

python -u autonomous_explorer.py ^
    --generations 10000 ^
    --per-gen 20 ^
    --seed %random% ^
    --log-interval 100 ^
    --checkpoint-interval 1000

echo.
echo ================================================================
echo  ERGON COMPLETE: %date% %time%
echo ================================================================

REM Now bridge survivors to Harmonia
echo.
echo Running Harmonia bridge on final archive...

for /f "delims=" %%F in ('dir /b /o-d results\archive_*.json') do (
    echo Bridging: results\%%F
    python -u harmonia_bridge.py results\%%F --top-k 20 --subsample 2000
    goto :done_bridge
)
:done_bridge

echo.
echo All done. Check ergon/logs/ and ergon/results/ for output.
pause
