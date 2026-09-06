@echo off
rem Archaeon producer: ONE decision cycle, then exit.
rem
rem Deployed as a Task Scheduler job (register_archaeon_tick.ps1), not as a
rem daemon. There is deliberately no long-lived process: every invocation is a
rem single tick(), cadence is enforced by the database, and a machine reboot or
rem a crash loses nothing because there is nothing to lose. Running it twice by
rem accident cannot double-issue -- the queue's unique index decides, not this
rem file.
rem
rem Logs one JSON record per run to deploy\archaeon_tick.log.
rem
rem Archaeon starts NOTHING else. It does not start Vivarium. If a proposal sits
rem queued, that is reported by the operator, never fixed here.

setlocal
set REPO=%~dp0..\..
cd /d "%REPO%"
set PYTHONPATH=%REPO%;%REPO%\vivarium
set LANE=%ARCHAEON_LANE%
if "%LANE%"=="" set LANE=prod

echo ---- %date% %time% lane=%LANE% >> "%~dp0archaeon_tick.log"
python -m archaeon.producer.loop --once --lane %LANE% >> "%~dp0archaeon_tick.log" 2>&1
echo exit=%errorlevel% >> "%~dp0archaeon_tick.log"
endlocal
