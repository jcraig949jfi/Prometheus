@echo off
REM Vivarium consumer -- M2 / SPECTREX5 launcher (D-23 layout, 2026-09-16).
REM
REM This tracked file is a TEMPLATE. deploy/prepare_m2.py copies it to the
REM data directory (D:\Prometheus-data\vivarium\vivarium_consumer_m2.cmd) with
REM the pinned worktree path recorded; the Task Scheduler task runs THAT copy,
REM never this one (a supervisor whose code changes on someone else's pull is
REM not pinned -- Daedalus, M2 relocation receipt).
REM
REM code : a DETACHED worktree at a recorded SHA (WORKING_CONTRACT s6);
REM        nobody edits there; advanced only by an explicit, logged command
REM state: D:\Prometheus-data\vivarium\var (flags, park records, the log)
REM store: the CANONICAL PostgreSQL on M1 (viv/db.py proves the identity)
REM engine: the production LEDGER eng_8a37a5d3, wherever it runs (Daedalus
REM        ruling, comms #270); today expected at https://192.168.1.191:8811
REM        after the move. The consumer's conformance gate halts on any other.
REM PEW  : M2, http://192.168.1.191:8377/api/v1 (Mnemosyne, since 2026-09-04)
REM secrets: VIV_SFE_TOKEN / VIV_PEW_TOKEN come from the pinned worktree's
REM        gitignored vivarium/config.local.json; NOTHING here.
REM
REM Full interpreter path: an unqualified `python` does not resolve inside a
REM scheduled task (Pronoia #123). No output redirection: the daemon writes
REM its own flushed log under var_dir.
set "PATH=C:\Program Files\Git\cmd;%PATH%"
set "VIV_WORKTREE=__PINNED_WORKTREE__"
set "EW_DB_HOST=192.168.1.202"
set "VIV_DB_HOST=192.168.1.202"
set "VIV_VAR_DIR=D:\Prometheus-data\vivarium\var"
set "VIV_SFE_BASE_URL=https://192.168.1.191:8811"
set "VIV_SFE_CACERT=SerendipityFoundry/SerendipityFoundryClient/config/m2.crt"
set "VIV_PEW_BASE_URL=http://192.168.1.191:8377/api/v1"
cd /d "%VIV_WORKTREE%\vivarium"
"D:\Prometheus\.venv-m2\Scripts\python.exe" -m viv.cli run --worker-id vivarium@m2
