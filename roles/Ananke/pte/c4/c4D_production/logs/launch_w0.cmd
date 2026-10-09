@echo off
cd /d "F:/Prometheus-worktrees/ananke-c4D-pinned/roles/Ananke/pte/c4"
H:/Python312/python.exe run_c4.py "F:/Prometheus-worktrees/ananke-c4D-pinned/roles/Ananke/pte/c4/PLAN_C4_D.json" "C:/Users/jcrai/ananke_runs/c4/production_D/run" 0 --deadline-utc 2026-10-09T09:23:49+00:00 >> "C:/Users/jcrai/ananke_runs/c4/production_D/log_w0.txt" 2>&1
echo EXIT=%ERRORLEVEL% >> "C:/Users/jcrai/ananke_runs/c4/production_D/log_w0.txt"
