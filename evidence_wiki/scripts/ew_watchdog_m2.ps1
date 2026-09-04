# Evidence Wiki watchdog -- M2 / SPECTREX5.
#
# 2026-09-04: James ruled M2 must be FULLY INDEPENDENT. PEW on M2 now serves
# M2's OWN local Postgres (config.json db_host=localhost), exactly the way M1's
# vanilla service serves M1's local Postgres. This is a DELIBERATE second world,
# not a fork accident: evidence no longer crosses machines (same posture as the
# M2 SFE engine). The earlier canonical-pointing launcher (ops\pew_serve_m2.cmd,
# EW_DB_HOST=192.168.1.202) is intentionally NOT used here anymore.
#
# Interpreter: M2's bare `python` is a dependency-less shim, so prefer .venv-m2.
$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$log  = Join-Path $root "derived\watchdog_m2.log"
function Log($m) { Add-Content -Path $log -Value ("{0}  {1}" -f (Get-Date -Format s), $m) }

try {
    $r = Invoke-WebRequest -Uri "http://localhost:8377/api/v1/health" -TimeoutSec 5 -UseBasicParsing
    if ($r.StatusCode -eq 200) { exit 0 }
} catch { }

$py = $env:EW_PYTHON
if (-not $py) {
    foreach ($cand in @("..\.venv-m2\Scripts\python.exe", "..\.venv\Scripts\python.exe")) {
        $full = Join-Path $root $cand
        if (Test-Path $full) { $py = (Resolve-Path $full).Path; break }
    }
}
if (-not $py) { $py = "python" }

Log "health check failed; starting M2-INDEPENDENT service (M2-local Postgres) via $py"
Start-Process -FilePath $py -ArgumentList "-m","ew.service" `
    -WorkingDirectory $root -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $root "derived\service_m2.out.log") `
    -RedirectStandardError  (Join-Path $root "derived\service_m2.err.log")
Start-Sleep -Seconds 10
try {
    $r2 = Invoke-WebRequest -Uri "http://localhost:8377/api/v1/health" -TimeoutSec 5 -UseBasicParsing
    if ($r2.StatusCode -eq 200) { Log "restart OK"; exit 0 }
} catch { }
Log "restart FAILED"
exit 1
