@echo off
REM ============================================================================
REM  HARVEST & ANALYZE — Stop, gather, and analyze what just ran
REM
REM  Steps:
REM    1. Kill running Ignis process (if any)
REM    2. Run Night Watchman on results
REM    3. Run review_watchman for narrative synthesis
REM    4. Run RPH eval on best genomes
REM    5. Run full analysis suite (7 verdicts) on best genome
REM
REM  Usage:
REM    harvest_and_analyze.bat                          (auto-detect results dir)
REM    harvest_and_analyze.bat ignis_multilayer          (specify results subdir)
REM    harvest_and_analyze.bat ignis Qwen/Qwen3-4B      (results dir + model)
REM ============================================================================

echo ============================================================================
echo  HARVEST ^& ANALYZE
echo  Stop. Gather. Understand.
echo ============================================================================
echo.

set PYTHON=%~dp0..\..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS_BASE=%SRC%\results

REM Default results dir and model
set RESULTS_DIR=%RESULTS_BASE%\ignis
set MODEL=Qwen/Qwen2.5-1.5B-Instruct

if not "%~1"=="" set RESULTS_DIR=%RESULTS_BASE%\%~1
if not "%~2"=="" set MODEL=%~2

echo   Results: %RESULTS_DIR%
echo   Model:   %MODEL%
echo.

REM ============================================================================
echo [STEP 1/7] Checking for running Ignis processes...
echo ============================================================================

set PID_FILE=%RESULTS_DIR%\orchestrator.pid
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    echo   Found PID file: %PID_FILE%
    tasklist /FI "PID eq %PID%" 2>nul | findstr /I "python" >nul
    if not errorlevel 1 (
        echo   Ignis is RUNNING (PID %PID%). Killing...
        taskkill /PID %PID% /F >nul 2>&1
        timeout /t 3 /nobreak >nul
        echo   Killed.
    ) else (
        echo   PID %PID% is not running. Stale PID file.
    )
) else (
    echo   No PID file found. Nothing to kill.
)

REM Also check for any python processes using significant GPU memory
echo.
echo   Checking GPU processes...
nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv,noheader 2>nul
echo.

REM ============================================================================
echo [STEP 2/7] Archiving results snapshot...
echo ============================================================================

set TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%
echo   Timestamp: %TIMESTAMP%
echo   Results directory: %RESULTS_DIR%

REM Count genomes in each model dir
for /d %%d in ("%RESULTS_DIR%\qwen*") do (
    if exist "%%d\discovery_log.jsonl" (
        echo   %%~nxd:
        for /f %%c in ('find /c /v "" "%%d\discovery_log.jsonl"') do echo     %%c genomes
    )
)
echo.

REM ============================================================================
echo [STEP 3/7] Running Night Watchman...
echo ============================================================================

if exist "%SRC%\night_watchman.py" (
    echo   Launching Night Watchman on %RESULTS_DIR%
    %PYTHON% "%SRC%\night_watchman.py" --results-dir "%RESULTS_DIR%"
    if errorlevel 1 (
        echo   [WARN] Night Watchman had errors
    ) else (
        echo   [OK] Night Watchman complete
    )
) else (
    echo   [SKIP] night_watchman.py not found
)
echo.

REM ============================================================================
echo [STEP 4/7] Running review_watchman (narrative synthesis)...
echo ============================================================================

if exist "%SRC%\review_watchman.py" (
    echo   Launching review_watchman on %RESULTS_DIR%
    %PYTHON% "%SRC%\review_watchman.py" --results-dir "%RESULTS_DIR%" --latest
    if errorlevel 1 (
        echo   [WARN] review_watchman had errors
    ) else (
        echo   [OK] review_watchman complete
    )
) else (
    echo   [SKIP] review_watchman.py not found
)
echo.

REM ============================================================================
echo [STEP 5/7] Running RPH eval on best genomes...
echo ============================================================================

if exist "%SRC%\eval_rph_survivors.py" (
    echo   Launching RPH eval (archive dir: %RESULTS_DIR%\archives)
    %PYTHON% "%SRC%\eval_rph_survivors.py" --archive-dir "%RESULTS_DIR%\archives" --device cuda
    if errorlevel 1 (
        echo   [WARN] RPH eval had errors
    ) else (
        echo   [OK] RPH eval complete
    )
) else (
    echo   [SKIP] eval_rph_survivors.py not found
)
echo.

REM ============================================================================
echo [STEP 6/7] Finding best genome for full analysis...
echo ============================================================================

REM Find the most recent best_genome.pt
set BEST_GENOME=
for /r "%RESULTS_DIR%\archives" %%f in (best_genome.pt) do (
    set BEST_GENOME=%%f
)

REM Also check non-archive model dirs
if "%BEST_GENOME%"=="" (
    for /r "%RESULTS_DIR%" %%f in (best_genome.pt) do (
        set BEST_GENOME=%%f
    )
)

if "%BEST_GENOME%"=="" (
    echo   [SKIP] No best_genome.pt found — skipping full analysis
    goto :summary
)

echo   Best genome: %BEST_GENOME%
echo.

REM ============================================================================
echo [STEP 7/7] Running Full Analysis Suite (7 verdicts)...
echo ============================================================================

if exist "%~dp0run_full_analysis.bat" (
    echo   Launching full analysis suite...
    echo   Model: %MODEL%
    echo   This will take 3-5 hours. Safe to sleep.
    echo.
    call "%~dp0run_full_analysis.bat" "%BEST_GENOME%" %MODEL%
) else (
    echo   [SKIP] run_full_analysis.bat not found
)

:summary
echo.
echo ============================================================================
echo  HARVEST COMPLETE
echo ============================================================================
echo.
echo  Check these outputs:
echo    %RESULTS_DIR%\watchman\digest_latest.md     (Night Watchman)
echo    %RESULTS_DIR%\rph_eval_*.json               (RPH eval)
echo    %RESULTS_DIR%\full_analysis\                 (7 verdicts)
echo.
echo  Next: review results, then run 'launch' for the next experiment.
echo ============================================================================
