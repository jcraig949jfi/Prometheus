# Mnemosyne Evidence Wiki watchdog: start the service if the health endpoint
# does not answer. Safe to run every few minutes from Task Scheduler.
$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$log = Join-Path $root "derived\watchdog.log"
function Log($m) { Add-Content -Path $log -Value ("{0}  {1}" -f (Get-Date -Format s), $m) }

try {
    $r = Invoke-WebRequest -Uri "http://localhost:8377/api/v1/health" -TimeoutSec 5 -UseBasicParsing
    if ($r.StatusCode -eq 200) { exit 0 }
} catch { }

Log "health check failed; starting service"
Start-Process -FilePath "python" -ArgumentList "-m","ew.service" `
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
