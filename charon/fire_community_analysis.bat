@echo off
REM Fire Council — Community Structure (ChatGPT + DeepSeek only)
REM No Gemini (rate limited), no Claude (out of credits)
cd /d "%~dp0"
echo === Community Structure Council (ChatGPT + DeepSeek) ===
python src/fire_council_communities.py
echo === Done. Check reports/council_responses/ ===
pause
