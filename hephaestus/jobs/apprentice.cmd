@echo off
rem Apprentice model job (charter s8). Cheap/local models only. Never premium.
cd /d C:\prometheus
set PYTHONPATH=C:\prometheus
if not exist hephaestus\logs mkdir hephaestus\logs
python -m hephaestus.src.apprentice >> hephaestus\logs\apprentice.log 2>&1
python -m hephaestus.src.refine     >> hephaestus\logs\apprentice.log 2>&1
python -m hephaestus.src.handoff    >  hephaestus\logs\handoff_last.log 2>&1
