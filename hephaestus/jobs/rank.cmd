@echo off
rem Daily wall ranking (charter s11).
cd /d C:\prometheus
set PYTHONPATH=C:\prometheus
if not exist hephaestus\logs mkdir hephaestus\logs
python -m hephaestus.src.rank    >> hephaestus\logs\rank.log 2>&1
python -m hephaestus.src.handoff >  hephaestus\logs\handoff_last.log 2>&1
