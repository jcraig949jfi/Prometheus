@echo off
REM PEW daily backup, M2-OWNED (O2 of MNE-D1, operator ruling 2026-09-17):
REM dump the CANONICAL cluster over the LAN onto this host, hash, manifest,
REM rotate. Task: PEWBackupDailyM2. Runs from the PINNED worktree (D-23 s6);
REM %~dp0 is ...\evidence_wiki\ops\ ; its parent is the tree.
REM Host-specific values (canonical_db_host, backup_dir, backup_keep,
REM restore_target_host) live in the untracked evidence_wiki\config.local.json,
REM never here. The interpreter is the venv beside the canonical clone,
REM found through the repository's common git dir.
setlocal
set PYTHONIOENCODING=utf-8
set PROMETHEUS_MACHINE=M2
set PROMETHEUS_ENV=prometheus-canonical
if not defined GIT_ON_PATH set "PATH=C:\Program Files\Git\cmd;%PATH%"
cd /d "%~dp0.."
for /f "delims=" %%i in ('git rev-parse --path-format=absolute --git-common-dir') do set "COMMON=%%i"
set "PY=%COMMON%\..\.venv-m2\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
if not exist derived mkdir derived
"%PY%" ops\pew_backup.py >> derived\backup_m2.log 2>&1
