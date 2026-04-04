@echo off
REM Submit Deep Research packages 31-33 (Apollo adjacent)
REM  31: Surrogate-assisted fitness evaluation
REM  32: Many-objective optimization beyond NSGA-II
REM  33: LLM mutation quality and 7B capability cliff
REM No VRAM needed. Submits async, check status later.

cd /d "%~dp0"
echo === Submitting Deep Research Packages 31-33 ===
python research/submit_deep_research.py 31 32 33
echo.
echo === Check status with: python research/submit_deep_research.py --status ===
pause
