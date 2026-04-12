@echo off
REM ============================================================
REM Noesis v3 — Full Pipeline: enrich + backfill + analysis
REM Fire and forget. No VRAM needed. ~7 hours total.
REM ============================================================

echo ============================================================
echo  Noesis v3 Overnight Pipeline
echo  Start: %date% %time%
echo ============================================================
echo.

REM --- Step 1: Enrich remaining 121 hubs (~2 hours) ---
echo [1/3] Enriching 121 remaining hubs...
cd /d "F:\Prometheus\noesis\v3\enrichment"
python auto_enrich.py --batches 25 --start-batch 49 --batch-size 5
if errorlevel 1 (
    echo WARNING: Enrichment had errors, continuing...
)
echo.

REM --- Step 2: Gemini backfill for all missing batches (~5 hours) ---
echo [2/3] Gemini backfill for all missing batches...
python gemini_backfill.py --cooldown 8
if errorlevel 1 (
    echo WARNING: Gemini backfill had errors, continuing...
)
echo.

REM --- Step 3: Re-run full analysis ---
echo [3/3] Running full-scale Noesis analysis...
cd /d "F:\Prometheus\noesis\v3"
python v3_analysis_full.py
echo.

echo ============================================================
echo  Noesis pipeline complete: %date% %time%
echo  Check: noesis/v3/analysis_full.json
echo ============================================================
pause
