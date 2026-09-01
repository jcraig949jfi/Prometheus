@echo off
rem Sentinel job (Addendum 3, Q7: "work should trigger compute, not time").
rem This is the ONLY scheduled task. It is cheap: it refines the queue, and calls cheap models
rem only if some packet is actually in APPRENTICE-TESTING (apprentice.py exits immediately
rem otherwise; widen mode sleeps unless HEPHAESTUS_WIDEN=1). Rank + handoff regenerate after.
cd /d C:\prometheus
set PYTHONPATH=C:\prometheus
if not exist hephaestus\logs mkdir hephaestus\logs
python -m hephaestus.src.refine     >> hephaestus\logs\refine.log 2>&1
python -c "import sys; sys.path.insert(0,'.'); from hephaestus.src import packet as P; sys.exit(0 if any(p['STATUS']=='APPRENTICE-TESTING' for p in P.iter_packets()) else 1)"
if %ERRORLEVEL%==0 (
  echo [%DATE% %TIME%] work present: running apprentice >> hephaestus\logs\refine.log
  python -m hephaestus.src.apprentice >> hephaestus\logs\apprentice.log 2>&1
  python -m hephaestus.src.refine     >> hephaestus\logs\refine.log 2>&1
) else (
  echo [%DATE% %TIME%] no work in APPRENTICE-TESTING: apprentice not invoked >> hephaestus\logs\refine.log
)
python -m hephaestus.src.rank    >> hephaestus\logs\rank.log 2>&1
python -m hephaestus.src.handoff >  hephaestus\logs\handoff_last.log 2>&1
