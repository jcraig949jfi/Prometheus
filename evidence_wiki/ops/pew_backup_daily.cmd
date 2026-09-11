@echo off
REM PEW daily backup (dump + sha256 + manifest + rotate). Task: PEWBackupDaily
REM D-23: path-relative, so this runs from whichever PINNED worktree the task
REM points at and never from the canonical checkout (ew/workspace.py refuses
REM that outright). %~dp0 is ...\evidence_wiki\ops\ ; its parent is the tree.
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
python ops\pew_backup.py >> F:\PrometheusBackups\pew\backup.log 2>&1
