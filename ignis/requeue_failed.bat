@echo off
REM Requeue the 4 experiments that failed on 2026-03-27
REM  - Basin escape L22/L23/L24 (was: Unicode cp1252 crash, now fixed)
REM  - Cross-arch Qwen-0.5B     (was: d_model assertion, now fixed)
REM Runs sequentially on GPU. Estimated ~4-6 hours total.

setlocal
set PYTHONUNBUFFERED=1
set PYTHONUTF8=1
set MODEL=Qwen/Qwen2.5-1.5B-Instruct
set DEVICE=cuda
set SRC=f:\Prometheus\ignis\src
set RESULTS=f:\Prometheus\ignis\results

echo ============================================================
echo  ATHENA REQUEUE — 4 failed experiments
echo  Started: %date% %time%
echo ============================================================

REM --- Clean stale logs from failed runs ---
del /q "%RESULTS%\basin_escape\L22\stdout.log" 2>nul
del /q "%RESULTS%\basin_escape\L23\stdout.log" 2>nul
del /q "%RESULTS%\basin_escape\L24\stdout.log" 2>nul
del /q "%RESULTS%\cross_arch\qwen05\stdout.log" 2>nul

REM --- Basin escape L22 ---
echo.
echo [1/4] Basin escape L22 (100 directions)
echo Started: %date% %time%
mkdir "%RESULTS%\basin_escape\L22" 2>nul
python -u "%SRC%\basin_escape_histogram.py" --model %MODEL% --device %DEVICE% --layer 22 --n-directions 100 --output-dir "%RESULTS%\basin_escape\L22" > "%RESULTS%\basin_escape\L22\stdout.log" 2>&1
if %errorlevel% neq 0 (
    echo   FAILED rc=%errorlevel% — see %RESULTS%\basin_escape\L22\stdout.log
) else (
    echo   OK
)
timeout /t 30 /nobreak >nul

REM --- Basin escape L23 ---
echo.
echo [2/4] Basin escape L23 (100 directions)
echo Started: %date% %time%
mkdir "%RESULTS%\basin_escape\L23" 2>nul
python -u "%SRC%\basin_escape_histogram.py" --model %MODEL% --device %DEVICE% --layer 23 --n-directions 100 --output-dir "%RESULTS%\basin_escape\L23" > "%RESULTS%\basin_escape\L23\stdout.log" 2>&1
if %errorlevel% neq 0 (
    echo   FAILED rc=%errorlevel% — see %RESULTS%\basin_escape\L23\stdout.log
) else (
    echo   OK
)
timeout /t 30 /nobreak >nul

REM --- Basin escape L24 ---
echo.
echo [3/4] Basin escape L24 (100 directions)
echo Started: %date% %time%
mkdir "%RESULTS%\basin_escape\L24" 2>nul
python -u "%SRC%\basin_escape_histogram.py" --model %MODEL% --device %DEVICE% --layer 24 --n-directions 100 --output-dir "%RESULTS%\basin_escape\L24" > "%RESULTS%\basin_escape\L24\stdout.log" 2>&1
if %errorlevel% neq 0 (
    echo   FAILED rc=%errorlevel% — see %RESULTS%\basin_escape\L24\stdout.log
) else (
    echo   OK
)
timeout /t 30 /nobreak >nul

REM --- Cross-arch Qwen-0.5B ---
echo.
echo [4/4] Cross-arch Qwen-0.5B (300 gen, L18)
echo Started: %date% %time%
mkdir "%RESULTS%\cross_arch\qwen05" 2>nul
python -u "%SRC%\evolve_1_5b.py" --model Qwen/Qwen2.5-0.5B-Instruct --device %DEVICE% --n-generations 300 --epsilon 3.0 --layer 18 --popsize 32 --stdev-init 0.05 --output-dir "%RESULTS%\cross_arch\qwen05" > "%RESULTS%\cross_arch\qwen05\stdout.log" 2>&1
if %errorlevel% neq 0 (
    echo   FAILED rc=%errorlevel% — see %RESULTS%\cross_arch\qwen05\stdout.log
) else (
    echo   OK
)

echo.
echo ============================================================
echo  ATHENA REQUEUE COMPLETE — %date% %time%
echo ============================================================
pause
