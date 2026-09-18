@echo off
REM PEW weekly restore QUALIFICATION, M2-OWNED (O2 of MNE-D1, 2026-09-17):
REM restore the newest dump into a scratch database on THIS host's cluster
REM (restore_target_host in config.local.json) and compare it against the
REM live canonical cluster table-for-table. A dump nobody has restored is
REM decoration; a restore only ever proven on the source host is not
REM independence. Task: PEWRestoreVerifyWeeklyM2. Runs from the PINNED
REM worktree; see pew_backup_daily_m2.cmd for the resolution rules.
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
"%PY%" ops\pew_restore_verify.py >> derived\verify_m2.log 2>&1
