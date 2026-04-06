@echo off
REM Charon Cartography Overnight Runner
REM Usage:
REM   run_charon_overnight.bat          (loops indefinitely)
REM   run_charon_overnight.bat once     (runs one cycle then exits)
REM
REM Runs research cycles with tensor review every 10 iterations.
REM External research feed on first run (daily budget).
REM Uses OpenAI for hypothesis generation (more reliable JSON).
REM DeepSeek for NLI checks (cheap).
REM
REM Logs to: cartography/convergence/logs/
REM Reports to: cartography/convergence/reports/

cd /d F:\Prometheus\cartography\shared\scripts

set TOPIC=What cross-domain bridges exist between mathematical constants, knot invariants, L-function spectral properties, formal proof structures, and metabolic network algebra? Find correlations that survive statistical testing.

if "%1"=="once" (
    echo === CHARON: Single cycle ===
    python research_cycle.py --provider openai --hypotheses 3 --loop 3 --tensor-review-every 3 --topic "%TOPIC%"
    echo === DONE ===
    pause
    goto :eof
)

echo === CHARON OVERNIGHT RUNNER ===
echo Looping indefinitely. Ctrl+C to stop.
echo Logs: cartography/convergence/logs/
echo.

set ITERATION=0

:loop
set /a ITERATION+=1
echo.
echo ============================================================
echo   OVERNIGHT ITERATION %ITERATION%  -  %date% %time%
echo ============================================================

REM Every 10th iteration: tensor review + external research
set /a MOD=%ITERATION% %% 10
if %MOD%==1 (
    echo Running with external research feed...
    python research_cycle.py --provider openai --hypotheses 3 --loop 5 --tensor-review-every 5 --external-research --topic "%TOPIC%"
) else (
    python research_cycle.py --provider openai --hypotheses 3 --loop 5 --tensor-review-every 5 --topic "%TOPIC%"
)

REM Brief pause between iterations (30 seconds)
echo.
echo Sleeping 30s before next iteration...
timeout /t 30 /nobreak >nul

goto loop
