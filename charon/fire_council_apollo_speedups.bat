@echo off
REM Fire Council — Apollo Speedups & Plateau Avoidance
REM Sends to ChatGPT, Claude, DeepSeek, Gemini in parallel
REM No VRAM needed. ~2 min.

cd /d "%~dp0"
echo === Firing Council: Apollo Speedups ===
python src/fire_council_apollo_speedups.py
echo.
echo === Done. Check reports/council_responses/ ===
pause
