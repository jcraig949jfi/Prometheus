@echo off
REM ---------------------------------------------------------------------------
REM Z80 x Atlas campaign launcher.
REM
REM Launched detached via schtasks so it outlives the session that started it: a
REM child of an interactive tool process dies with that process, and this run has
REM to survive 72 hours of them.
REM
REM The loop is a WATCHDOG, not a retry-until-it-works. run_campaign.py --resume
REM reloads the producer's counts and the campaign clock, so a crash at hour 40
REM costs the jobs that were in flight, not the campaign. The loop exits when the
REM scheduler writes DONE (its own wall clock reached), and it refuses to spin:
REM a fixed pause between attempts and a hard attempt cap, so a configuration that
REM refuses to start - a grammar-hash mismatch, a failed calibration gate - stops
REM instead of restarting forever.
REM ---------------------------------------------------------------------------
setlocal
cd /d F:\Prometheus-worktrees\nestor-sidequest-graphworld\roles\Nestor\campaigns\z80atlas-2026-09-19

set PY=H:\Python312\python.exe
set HOURS=72
set WORKERS=6
set ATTEMPT=0
set MAXATTEMPT=60

:loop
set /a ATTEMPT+=1
echo [%DATE% %TIME%] attempt %ATTEMPT% >> campaign.log
%PY% run_campaign.py --hours %HOURS% --workers %WORKERS% --seed 1 --resume >> campaign.log 2>&1
set RC=%ERRORLEVEL%
echo [%DATE% %TIME%] exited rc=%RC% >> campaign.log

if exist observatory\DONE goto done
if %RC%==2 goto refused
if %ATTEMPT% GEQ %MAXATTEMPT% goto capped
timeout /t 30 /nobreak > nul
goto loop

:refused
echo [%DATE% %TIME%] REFUSED by gate - not restarting >> campaign.log
goto end

:capped
echo [%DATE% %TIME%] attempt cap reached - not restarting >> campaign.log
goto end

:done
echo [%DATE% %TIME%] campaign complete >> campaign.log

:end
endlocal
