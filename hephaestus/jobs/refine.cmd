@echo off
rem Queue refinement job (charter s10).
cd /d C:\prometheus
set PYTHONPATH=C:\prometheus
if not exist hephaestus\logs mkdir hephaestus\logs
python -m hephaestus.src.refine  >> hephaestus\logs\refine.log 2>&1
python -m hephaestus.src.handoff >  hephaestus\logs\handoff_last.log 2>&1
