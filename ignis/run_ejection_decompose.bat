@echo off
REM ============================================================================
REM  EJECTION DECOMPOSE — Component-level decomposition at L*
REM
REM  Identifies WHICH attention heads and MLPs are responsible for ejecting
REM  the correct answer at the critical layer L*.
REM
REM  Usage: run_ejection_decompose.bat [MODEL] [TOP_N] [EXTRA_ARGS]
REM  Default: Qwen2.5-1.5B-Instruct, top-5 components
REM  Examples:
REM    run_ejection_decompose.bat                                    (defaults)
REM    run_ejection_decompose.bat Qwen/Qwen2.5-1.5B-Instruct 10
REM    run_ejection_decompose.bat Qwen/Qwen2.5-1.5B-Instruct 5 "--trap Decimal Magnitude"
REM ============================================================================

echo ============================================================================
echo  EJECTION DECOMPOSE — Component-level decomposition at L*
echo  Which heads and MLPs eject the correct answer?
echo ============================================================================
echo.

set PYTHON=%~dp0..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis\ejection

if "%~1"=="" (
    set MODEL=Qwen/Qwen2.5-1.5B-Instruct
) else (
    set MODEL=%~1
)
if "%~2"=="" (
    set TOP_N=5
) else (
    set TOP_N=%~2
)

if not exist "%RESULTS%" mkdir "%RESULTS%"

echo   Model:  %MODEL%
echo   Top-N:  %TOP_N%
echo   Output: %RESULTS%
echo.

%PYTHON% "%SRC%\ejection_decompose.py" --model %MODEL% --device cuda --output-dir "%RESULTS%" --top-n %TOP_N% %~3

echo.
echo ============================================================================
echo  EJECTION DECOMPOSE COMPLETE
echo  Results in: %RESULTS%
echo ============================================================================
