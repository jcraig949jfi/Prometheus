@echo off
cd /d "F:/Prometheus-worktrees/ananke-c3r1-pinned/roles/Ananke/pte/c3"
H:/Python312/python.exe run_c3r.py "F:/Prometheus-worktrees/ananke-c3r1-pinned/roles/Ananke/pte/c3/PLAN_C3R_S1.json" "C:/Users/jcrai/ananke_runs/c3r/production_s1/run" 1 --deadline-utc 2026-10-08T00:44:30+00:00 >> "C:/Users/jcrai/ananke_runs/c3r/production_s1/log_w1.txt" 2>&1
echo EXIT=%ERRORLEVEL% >> "C:/Users/jcrai/ananke_runs/c3r/production_s1/log_w1.txt"
