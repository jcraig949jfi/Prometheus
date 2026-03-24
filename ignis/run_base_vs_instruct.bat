@echo off
REM base_vs_instruct.bat — Compare logit lens between base and instruct models
REM Runs Qwen/Qwen2.5-1.5B (no RLHF) vs Qwen/Qwen2.5-1.5B-Instruct (post-RLHF)

setlocal
set SCRIPT_DIR=%~dp0
set OUTPUT_DIR=%SCRIPT_DIR%results\base_vs_instruct

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo ============================================================
echo  BASE vs INSTRUCT — Logit Lens Comparison
echo  Output: %OUTPUT_DIR%
echo ============================================================

python "%SCRIPT_DIR%src\base_vs_instruct.py" ^
    --device cuda ^
    --output-dir "%OUTPUT_DIR%"

echo.
echo Done. Results in %OUTPUT_DIR%
pause
