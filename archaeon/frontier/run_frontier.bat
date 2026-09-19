@echo off
rem Supervisor for the Deep Frontier scheduler: keeps it alive independent of any LLM session (restarts on exit, 8 h walls).
cd /d D:\Prometheus-worktrees\archaeon-wse-2026-09-16
set EW_DB_HOST=192.168.1.202
:loop
if exist archaeon\frontier\GLOBAL_HALT.json goto halt
if exist archaeon\frontier\STOP_SUPERVISOR goto halt
python -m archaeon.frontier.scheduler --run --wall-hours 8 >> archaeon\frontier\logs\scheduler_supervised.log 2>&1
timeout /t 60 /nobreak > nul
goto loop
:halt
echo halted >> archaeon\frontier\logs\scheduler_supervised.log
