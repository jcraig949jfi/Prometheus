@echo off
REM Serendipity Foundry Engine -- M2 / SPECTREX5 instance.
REM M1's launcher is sfengine.cmd (F: paths, binds 192.168.1.202, cert m1).
REM This one binds 192.168.1.191 with cert m2. Separate machine, separate
REM engine.db: the two engines share NO state. See docs/RUNNING_M1_VS_M2.md.
REM
REM PATH: git is installed on M2 but is NOT on the machine or user PATH, so a
REM service-launched engine reports source_commit=null and every experiment it
REM commits loses its git attribution. Prepending Git\cmd fixes that locally
REM without mutating the system PATH.
set "PATH=C:\Program Files\Git\cmd;%PATH%"
"D:\Prometheus\.venv-m2\Scripts\python.exe" "D:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\serve.py" --db "D:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\var\engine.db" --host 192.168.1.191 --port 8811 --tls-cert "D:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\deploy\m2.crt" --tls-key "D:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\deploy\m2.key" >> "D:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\deploy\sfengine_m2.log" 2>&1
