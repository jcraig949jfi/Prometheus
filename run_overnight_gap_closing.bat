@echo off
REM ============================================================
REM Overnight Gap Closing Run
REM
REM 1. CAITL the survivor — push 50%% categories toward 80%%+
REM 2. Add gap-targeted concept triples to Nous
REM 3. Re-score and update coverage map
REM 4. Commit everything
REM
REM Expected runtime: 30-60 minutes
REM ============================================================

echo ============================================================
echo  Overnight Gap Closing Run
echo  Started: %date% %time%
echo ============================================================
echo.

cd /d "F:\Prometheus\agents\hephaestus\src"

echo [1/4] CAITL-refining the forge survivor...
python overnight_gap_closing.py --step 1
echo.

echo [2/4] Adding gap-targeted concept triples to Nous...
python overnight_gap_closing.py --step 2
echo.

echo [3/4] Re-scoring and updating coverage map...
python overnight_gap_closing.py --step 3
echo.

echo [4/4] Committing...
cd /d "F:\Prometheus"
git add -A
git commit -m "Overnight gap closing: CAITL survivor, gap-targeted Nous triples, updated coverage

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
git push

echo.
echo ============================================================
echo  Overnight Gap Closing Complete
echo  Finished: %date% %time%
echo ============================================================
pause
