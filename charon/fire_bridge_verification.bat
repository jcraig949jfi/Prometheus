@echo off
REM Fire Council + Deep Research for Cramer-Rao / Revelation Principle bridge
REM No VRAM needed. ~3 min for council, Deep Research is async.

cd /d "%~dp0"

echo === Bridge Verification: Cramer-Rao / Revelation Principle ===
echo.

echo [1/2] Firing Council (4 models in parallel)...
python src/fire_council_bridge_verify.py
echo.

echo [2/2] Submitting Deep Research package 37...
python research/submit_deep_research.py 37
echo.

echo === Done. Check reports/council_responses/ ===
pause
