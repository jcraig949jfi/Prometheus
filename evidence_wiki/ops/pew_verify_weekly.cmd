@echo off
REM PEW weekly restore PROOF (scratch restore + mechanical comparison).
REM A dump nobody has restored is decoration. Task: PEWRestoreVerifyWeekly
REM D-23: path-relative; see pew_backup_daily.cmd.
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
python ops\pew_restore_verify.py >> F:\PrometheusBackups\pew\verify.log 2>&1
