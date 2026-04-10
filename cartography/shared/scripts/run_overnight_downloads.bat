@echo off
REM Overnight Data Download Runner
REM Run from: F:\Prometheus\cartography\shared\scripts\
REM Estimated total time: ~6 hours
REM All scripts sleep between requests to avoid rate limiting

echo ============================================
echo  Prometheus Overnight Data Downloads
echo  Started: %date% %time%
echo ============================================
echo.

REM 1. NIST Atomic Spectra (~5 min, 92 elements, 3s sleep)
echo [1/4] NIST Atomic Spectra...
python fetch_nist_spectra.py
echo.

REM 2. DLMF Formulas (~2 hours, 36 chapters + sections, 5s sleep)
echo [2/4] DLMF Formulas...
python fetch_dlmf_formulas.py
echo.

REM 3. Calabi-Yau Database (~2 min, small files)
echo [3/4] Calabi-Yau Database...
python fetch_calabi_yau.py
echo.

REM 4. COD Crystal Structures (~3 hours, 50K structures, 2s sleep)
echo [4/4] COD Crystal Structures...
python fetch_cod_crystals.py
echo.

echo ============================================
echo  All downloads complete!
echo  Finished: %date% %time%
echo ============================================
pause
