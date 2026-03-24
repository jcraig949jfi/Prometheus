@echo off
REM Multi-layer injection test — does injecting at L23-27 fix generation washout?
REM Defaults to the 1.5B genome.

setlocal

set SRC=%~dp0src
set GENOME=%~dp0src\results\ignis\evolve_20260323_192956\best_genome_1_5b.pt
set MODEL=Qwen/Qwen2.5-1.5B-Instruct
set EPSILON=3.0
set MAX_TOKENS=30
set OUTPUT_DIR=%~dp0src\results\ignis\multi_layer_inject

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo ============================================================
echo  Multi-Layer Injection Test
echo  Genome:  %GENOME%
echo  Model:   %MODEL%
echo  Epsilon: %EPSILON%
echo ============================================================

python "%SRC%\multi_layer_inject.py" ^
    --genome "%GENOME%" ^
    --model "%MODEL%" ^
    --epsilon %EPSILON% ^
    --max-tokens %MAX_TOKENS% ^
    --output-dir "%OUTPUT_DIR%" ^
    --device cuda

echo.
echo Done. Results in %OUTPUT_DIR%
