# Evidence Wiki watchdog -- M2 / SPECTREX5 ONLY.
#
# Differs from ew_watchdog.ps1 (which stays M1's) in two load-bearing ways:
#
#   1. It starts ops\pew_serve_m2.cmd, which forces EW_DB_HOST=192.168.1.202.
#      A bare `python -m ew.service` on M2 reads config.json's db_host=localhost
#      and serves the RESTORED COPY of prometheus_fire in M2's own Postgres --
#      a second writable evidence store. That is a provenance fork, not a
#      failover, so this watchdog must never start the service that way.
#   2. It probes 192.168.1.191:8377, because the M2 service binds that address
#      specifically rather than 0.0.0.0.
$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$log = Join-Path $root "derived\watchdog_m2.log"
function Log($m) { Add-Content -Path $log -Value ("{0}  {1}" -f (Get-Date -Format s), $m) }

try {
    $r = Invoke-WebRequest -Uri "http://192.168.1.191:8377/api/v1/health" -TimeoutSec 5 -UseBasicParsing
    if ($r.StatusCode -eq 200) { exit 0 }
} catch { }

Log "health check failed; starting M2 service (canonical store on M1)"
Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c", (Join-Path $root "ops\pew_serve_m2.cmd") -WindowStyle Hidden
Start-Sleep -Seconds 10
try {
    $r2 = Invoke-WebRequest -Uri "http://192.168.1.191:8377/api/v1/health" -TimeoutSec 5 -UseBasicParsing
    if ($r2.StatusCode -eq 200) { Log "restart OK"; exit 0 }
} catch { }
Log "restart FAILED"
exit 1
