@echo off
REM Vivarium dead-man check -- M2 one-shot, fired by the Task Scheduler task
REM VivariumDeadmanM2 every 5 minutes (viv/deadman.py; backlog C11b).
REM TEMPLATE: deploy/prepare_m2.py copies it beside the consumer launcher in
REM D:\Prometheus-data\vivarium with the pinned worktree path filled in.
REM
REM Reads the consumer's heartbeat from the canonical store; relaunches the
REM consumer via vivarium_consumer_m2.cmd ONLY when its pid is gone from this
REM host AND the production ledger answers at the configured engine (rule 9);
REM parks itself after 3 consecutive failed ticks (rule 10), disables its own
REM task and posts once to the accountable seat. State file:
REM   D:\Prometheus-data\vivarium\var\deadman-vivarium@m2.state.json
set "PATH=C:\Program Files\Git\cmd;%PATH%"
set "VIV_WORKTREE=__PINNED_WORKTREE__"
set "EW_DB_HOST=192.168.1.202"
set "VIV_DB_HOST=192.168.1.202"
set "VIV_VAR_DIR=D:\Prometheus-data\vivarium\var"
set "VIV_SFE_BASE_URL=https://192.168.1.191:8811"
cd /d "%VIV_WORKTREE%\vivarium"
"D:\Prometheus\.venv-m2\Scripts\python.exe" -m viv.deadman ^
    --worker-id vivarium@m2 --task-name VivariumDeadmanM2 ^
    --launcher "D:\Prometheus-data\vivarium\vivarium_consumer_m2.cmd" ^
    --sfe-cacert "%VIV_WORKTREE%\SerendipityFoundry\SerendipityFoundryClient\config\m2.crt" ^
    --var-dir "%VIV_VAR_DIR%"
