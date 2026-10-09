@echo off
cd /d "F:/Prometheus-worktrees/ananke-c4T-pinned/roles/Ananke/pte/c4"
H:/Python312/python.exe run_c4.py "F:/Prometheus-worktrees/ananke-c4T-pinned/roles/Ananke/pte/c4/PLAN_C4_T.json" "C:/Users/jcrai/ananke_runs/c4/production_T/run" 0 --deadline-utc 2026-10-09T06:20:34+00:00 >> "C:/Users/jcrai/ananke_runs/c4/production_T/log_w0.txt" 2>&1
echo EXIT=%ERRORLEVEL% >> "C:/Users/jcrai/ananke_runs/c4/production_T/log_w0.txt"
