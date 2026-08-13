@echo off
REM Ergon — hourly NVIDIA/Nemotron availability sample for the Metabolization Probe.
REM Appends to ergon/probe_logs/soak_diurnal.jsonl. Delete task with:
REM   schtasks /delete /tn PrometheusApiDiurnalProbe /f
cd /d F:\Prometheus
H:\Python312\python.exe ergon\probe_api_soak.py diurnal --calls 6 --timeout 120 >> ergon\probe_logs\diurnal_console.log 2>&1
