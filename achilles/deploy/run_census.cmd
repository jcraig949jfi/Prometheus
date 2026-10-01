@echo off
rem Achilles fleet census -- one cycle. Invoked by the PrometheusFleetCensus scheduled task on ELSA.
rem Arguments: %1 pinned code worktree, %2 publish worktree, %3 state dir, %4 python.exe
rem Comms and the evidence wiki live on M1 for every machine (base role s1 step 1).
set EW_DB_HOST=192.168.1.202
set PROMETHEUS_ENV=prometheus-canonical
set PYTHONIOENCODING=utf-8
cd /d "%~1"
"%~4" -m achilles.census.run --publish-root "%~2" --state-dir "%~3" >> "%~3\census.log" 2>&1
