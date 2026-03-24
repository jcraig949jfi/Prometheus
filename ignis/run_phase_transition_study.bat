@echo off
REM ============================================================================
REM  PHASE TRANSITION STUDY — 1.5B Model Investigation
REM
REM  PT-1: Phase Transition Map (layer x trap heatmap with BIC)
REM  PT-2: Precipitation-Specific Fitness Calibration (baseline trap survey)
REM  PT-3: Ordinal Trap Replication Study (20 ordinal traps)
REM
REM  Usage: run_phase_transition_study.bat [GENOME_PATH] [MODEL_NAME]
REM  Default: No genome (uses SVD probe), Qwen/Qwen2.5-1.5B-Instruct
REM  Examples:
REM    run_phase_transition_study.bat                             (all phases, SVD probe)
REM    run_phase_transition_study.bat genome_1.5b.pt              (with genome)
REM    run_phase_transition_study.bat genome.pt Qwen/Qwen2.5-1.5B-Instruct
REM ============================================================================

echo ============================================================================
echo  PHASE TRANSITION STUDY
echo  1.5B Model — Genuine Binary Phase Transitions
echo  PT-1: Map  ^|  PT-2: Calibrate  ^|  PT-3: Replicate
echo ============================================================================
echo.

set PYTHON=%~dp0..\venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

set SRC=%~dp0src
set RESULTS=%~dp0src\results\ignis\phase_transitions

REM ── Parse arguments ─────────────────────────────────────────────────────
if "%~1"=="" (
    set GENOME=
    set GENOME_FLAG=
) else (
    set GENOME=%~1
    set GENOME_FLAG=--genome "%~1"
)
if "%~2"=="" (
    set MODEL=Qwen/Qwen2.5-1.5B-Instruct
) else (
    set MODEL=%~2
)

if not exist "%RESULTS%" mkdir "%RESULTS%"

echo   Model:  %MODEL%
if "%GENOME%"=="" (
    echo   Genome: ^(none — using SVD probe direction^)
) else (
    echo   Genome: %GENOME%
)
echo   Output: %RESULTS%
echo.

REM ── Single process: preflight runs inside phase_transition_study.py ─────
REM    Model loads ONCE. Preflight gates before experiments run.
%PYTHON% "%SRC%\phase_transition_study.py" %GENOME_FLAG% --model %MODEL% --device cuda --output-dir "%RESULTS%" --phases 1 2 3

echo.
echo ============================================================================
echo  PHASE TRANSITION STUDY COMPLETE
echo  Results in: %RESULTS%
echo ============================================================================
