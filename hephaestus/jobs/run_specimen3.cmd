@echo off
rem Specimen 3 (Q045) closure gauntlet, exactly as preregistered in
rem hephaestus/prereg/PREREG_Q045_specimen3_2026-09-01.md: R_imp depth 8,
rem 30,000,000-candidate budget. Run from a linked worktree (D-23); the
rem module refuses the canonical checkout. Output is written by the program
rem (hephaestus/closure_results/q045_lost_class.json) plus a console log
rem beside it; never shell-redirect a background job (base role s6).
cd /d %~dp0..\..
set PYTHONPATH=%CD%
python -m hephaestus.src.closure_q045 %1 %2 > hephaestus\closure_results\q045_console.log 2>&1
