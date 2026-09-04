@echo off
REM PEW daily backup (dump + sha256 + manifest + rotate). Task: PEWBackupDaily
set PYTHONIOENCODING=utf-8
cd /d F:\Prometheus\evidence_wiki
python ops\pew_backup.py >> F:\PrometheusBackups\pew\backup.log 2>&1
