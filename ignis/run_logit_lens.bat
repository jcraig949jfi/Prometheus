@echo off
REM ============================================================================
REM  LOGIT LENS BACKWARD — L* ejection detector
REM  Traces how the correct answer's probability evolves through the network.
REM  Finds L*: the layer where the correct answer COLLAPSES.
REM
REM  Usage: run_logit_lens.bat [GENOME_PATH] [MODEL_NAME]
REM  Default: Qwen2.5-1.5B-Instruct, no genome (baseline only)
REM ============================================================================

echo ============================================================================
echo  LOGIT LENS BACKWARD — L* Ejection Detector
echo ============================================================================
echo.

set PYTHON=%~dp0..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis\logit_lens

if not exist "%RESULTS%" mkdir "%RESULTS%"

if "%~2"=="" (
    set MODEL=Qwen/Qwen2.5-1.5B-Instruct
) else (
    set MODEL=%~2
)

if "%~1"=="" (
    echo  Running baseline only (no genome)
    echo.
    %PYTHON% "%SRC%\logit_lens_backward.py" --model %MODEL% --device cuda --output-dir "%RESULTS%"
) else (
    echo  Running baseline + steered (genome: %~1)
    echo.
    %PYTHON% "%SRC%\logit_lens_backward.py" --model %MODEL% --genome "%~1" --steered --device cuda --output-dir "%RESULTS%"
)

if errorlevel 1 (
    echo.
    echo  *** LOGIT LENS FAILED ***
    echo.
    exit /b 1
) else (
    echo.
    echo  LOGIT LENS COMPLETE — check results in %RESULTS%
    echo.
    exit /b 0
)
