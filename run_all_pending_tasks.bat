@echo off
REM ============================================================
REM Run All Pending Tasks — Sequential Pipeline
REM
REM Runs 11 pending items without manual intervention.
REM Each step logs to pending_tasks.log and continues on error.
REM
REM Expected runtime: 15-30 minutes
REM ============================================================

echo ============================================================
echo  Running All Pending Tasks
echo  Started: %date% %time%
echo ============================================================
echo.

cd /d "F:\Prometheus\agents\hephaestus\src"

echo [1/11] Running v5 library against 89-category battery...
python run_all_tasks.py --step 1 2>&1
echo.

echo [2/11] Re-running behavioral fingerprints on 89-cat battery...
python run_all_tasks.py --step 2 2>&1
echo.

echo [3/11] Building generational trajectory (v1-v5 fitness curves)...
python run_all_tasks.py --step 3 2>&1
echo.

echo [4/11] Adding dedup gate...
python run_all_tasks.py --step 4 2>&1
echo.

echo [5/11] Building family-level RLVF weighting...
python run_all_tasks.py --step 5 2>&1
echo.

echo [6/11] Building tier-aware honesty metric...
python run_all_tasks.py --step 6 2>&1
echo.

echo [7/11] Fixing remaining 3 Tier B patterns...
python run_all_tasks.py --step 7 2>&1
echo.

echo [8/11] Updating Nous scoring weights...
python run_all_tasks.py --step 8 2>&1
echo.

echo [9/11] Building quartet compositor...
python run_all_tasks.py --step 9 2>&1
echo.

echo [10/11] Writing A/D interface evolution design doc...
python run_all_tasks.py --step 10 2>&1
echo.

echo [11/11] Committing all work...
cd /d "F:\Prometheus"
git add -A
git commit -m "Complete pending tasks: 89-cat eval, fingerprints, quartets, dedup, RLVF weighting, honesty metric, Tier B fix, Nous weights, A/D design

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
git push

echo.
echo ============================================================
echo  All Tasks Complete
echo  Finished: %date% %time%
echo ============================================================
pause
