@echo off
REM PEW weekly restore PROOF (scratch restore + mechanical comparison).
REM A dump nobody has restored is decoration. Task: PEWRestoreVerifyWeekly
set PYTHONIOENCODING=utf-8
cd /d F:\Prometheus\evidence_wiki
python ops\pew_restore_verify.py >> F:\PrometheusBackups\pew\verify.log 2>&1
