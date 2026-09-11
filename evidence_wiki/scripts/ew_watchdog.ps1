# Mnemosyne Evidence Wiki watchdog: start the service if the health endpoint
# does not answer. Safe to run every few minutes from Task Scheduler.
$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$log = Join-Path $root "derived\watchdog.log"
function Log($m) { Add-Content -Path $log -Value ("{0}  {1}" -f (Get-Date -Format s), $m) }

# Health probe. 5s was too short: under host load PEW has answered health in
# 7-15s, and a timed-out probe used to be read as "service is down".
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8377/api/v1/health" -TimeoutSec 20 -UseBasicParsing
    if ($r.StatusCode -eq 200) { exit 0 }
} catch { }

# SINGLETON GUARD (2026-09-11). Without this, a slow health probe started a
# SECOND service, whose contention made the next probe slower still -- three
# ew.service processes were live at once after the D-23 migration, fighting
# for port 8377 and the connection pool. A watchdog that cannot tell "not
# answering yet" from "not running" manufactures the outage it exists to fix.
$listening = @(Get-NetTCPConnection -State Listen -LocalPort 8377 -ErrorAction SilentlyContinue)
$running = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
             Where-Object { $_.CommandLine -match 'ew\.service' })
if ($listening.Count -gt 0 -or $running.Count -gt 0) {
    Log ("health probe failed but a service is already present (listeners={0} processes={1}); NOT starting another" -f $listening.Count, $running.Count)
    exit 0
}

# Interpreter resolution (machine-aware, backwards-compatible):
#   1. $env:EW_PYTHON if set
#   2. a repo-local venv beside the repo root (M2 uses .venv-m2)
#   3. bare "python" from PATH  <- M1's original behaviour, unchanged
# M2 needs this: bare "python" there is the WindowsApps 3.14 shim, which has
# none of the service dependencies, so the watchdog would restart-fail forever.
$py = $env:EW_PYTHON
if (-not $py) {
    foreach ($cand in @("..\.venv-m2\Scripts\python.exe", "..\.venv\Scripts\python.exe")) {
        $full = Join-Path $root $cand
        if (Test-Path $full) { $py = (Resolve-Path $full).Path; break }
    }
}
if (-not $py) { $py = "python" }

Log "health check failed; starting service via $py"
Start-Process -FilePath $py -ArgumentList "-m","ew.service" `
    -WorkingDirectory $root -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $root "derived\service.out.log") `
    -RedirectStandardError  (Join-Path $root "derived\service.err.log")
Start-Sleep -Seconds 8
try {
    $r2 = Invoke-WebRequest -Uri "http://localhost:8377/api/v1/health" -TimeoutSec 5 -UseBasicParsing
    if ($r2.StatusCode -eq 200) { Log "restart OK" ; exit 0 }
} catch { }
Log "restart FAILED"
exit 1
