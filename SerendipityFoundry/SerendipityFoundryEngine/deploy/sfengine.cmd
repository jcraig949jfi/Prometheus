@echo off
REM --max-artifact-bytes 33554432 is REQUIRED from schema 8 onward.
REM v8 introduced a per-artifact size ceiling where there was none, and it
REM applies on READ as well as on write. One artifact already in the live store
REM is 32 MiB (sha256:05f052c8..., wld_275033f4505ae3ac8a6b69c1, created
REM 2026-09-03); under the 16 MiB default it would become UNREADABLE the moment
REM the new build started -- not corrupted, just refused. A deploy may add a
REM limit; it must not silently retire data that was readable an hour earlier.
REM 33554432 keeps every existing artifact readable and still installs a ceiling
REM where there was none. See deploy\DEPLOY_SCHEMA8_2026-09-10.md section 5.
"F:\SerendipityD\.venv\Scripts\python.exe" "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\serve.py" --db "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\var\engine.db" --host 192.168.1.202 --port 8811 --max-artifact-bytes 33554432 --tls-cert "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\deploy\m1.crt" --tls-key "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\deploy\m1.key" >> "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\deploy\sfengine.log" 2>&1
