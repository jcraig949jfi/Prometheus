@echo off
cd /d "F:/Prometheus-worktrees/ananke-c4L-pinned/roles/Ananke/pte/c4"
H:/Python312/python.exe run_c4.py "F:/Prometheus-worktrees/ananke-c4L-pinned/roles/Ananke/pte/c4/PLAN_C4_L.json" "C:/Users/jcrai/ananke_runs/c4/production_L/run" 2 --deadline-utc 2026-10-08T18:04:45+00:00 >> "C:/Users/jcrai/ananke_runs/c4/production_L/log_w2.txt" 2>&1
echo EXIT=%ERRORLEVEL% >> "C:/Users/jcrai/ananke_runs/c4/production_L/log_w2.txt"
