@echo off
REM Evidence Wiki -- M2 / SPECTREX5 instance, serving M1's canonical Postgres.
REM M1's own service is started by MnemosyneEvidenceWikiWatchdog with
REM `python -m ew.service` (config.json defaults). See docs/RUNNING_M1_VS_M2.md.
set "PATH=C:\Program Files\Git\cmd;%PATH%"
"D:\Prometheus\.venv-m2\Scripts\python.exe" "D:\Prometheus\evidence_wiki\ops\pew_serve_m2.py" --db-host 192.168.1.202 --host 192.168.1.191 --port 8377 >> "D:\Prometheus\evidence_wiki\derived\pew_m2.log" 2>&1
