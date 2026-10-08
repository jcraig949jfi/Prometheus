@echo off
cd /d "F:/Prometheus-worktrees/ananke-c3r2-pinned/roles/Ananke/pte/c3"
H:/Python312/python.exe run_c3r.py "F:/Prometheus-worktrees/ananke-c3r2-pinned/roles/Ananke/pte/c3/PLAN_C3R_S2.json" "C:/Users/jcrai/ananke_runs/c3r/production_s2/run" 0 --deadline-utc 2026-10-08T16:58:51+00:00 >> "C:/Users/jcrai/ananke_runs/c3r/production_s2/log_w0.txt" 2>&1
echo EXIT=%ERRORLEVEL% >> "C:/Users/jcrai/ananke_runs/c3r/production_s2/log_w0.txt"
