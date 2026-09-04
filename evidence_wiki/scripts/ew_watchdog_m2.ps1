# Evidence Wiki watchdog -- M2 / SPECTREX5.
#
# 2026-09-04: James ruled M2 must be FULLY INDEPENDENT. PEW on M2 serves M2's
# OWN local Postgres (config.json db_host=localhost), like M1's vanilla service
# serves M1's. A deliberate second world; evidence does not cross machines. The
# canonical-pointing launcher (ops\pew_serve_m2.cmd, EW_DB_HOST=192.168.1.202)
# is intentionally NOT used here.
#
# DEPLOY-AWARE (CT-SFE-1 deploy-lag fix): a bare start-if-down watchdog keeps
# relaunching the OLD build forever -- IMPLEMENTED != DEPLOYED. This watchdog
# also restarts the service when its attested source_commit falls BEHIND repo
# HEAD, so a committed PEW change deploys within one interval without a human
# killing the process. The service is launched with EW_SOURCE_COMMIT set from
# HEAD, because the S4U task context has no `git` on PATH and the service could
# not otherwise self-identify its commit (it would report "unknown" and loop).
#
# Interpreter: M2's bare `python` is a dependency-less shim, so prefer .venv-m2.
$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$log  = Join-Path $root "derived\watchdog_m2.log"
function Log($m) { Add-Content -Path $log -Value ("{0}  {1}" -f (Get-Date -Format s), $m) }

$py = $env:EW_PYTHON
if (-not $py) {
    foreach ($cand in @("..\.venv-m2\Scripts\python.exe", "..\.venv\Scripts\python.exe")) {
        $full = Join-Path $root $cand
        if (Test-Path $full) { $py = (Resolve-Path $full).Path; break }
    }
}
if (-not $py) { $py = "python" }

# Resolve git (S4U PATH often lacks it) and stamp the service's commit via env.
$git = (Get-Command git -ErrorAction SilentlyContinue).Source
if (-not $git) { foreach ($g in 'C:\Program Files\Git\cmd\git.exe','C:\Program Files\Git\bin\git.exe') { if (Test-Path $g) { $git = $g; break } } }
$head = ""
if ($git) { $head = (& $git -C $root rev-parse HEAD 2>$null | Out-String).Trim() }
if ($head) { $env:EW_SOURCE_COMMIT = $head }

function Start-Service-Fresh {
    Log "starting M2-INDEPENDENT service (M2-local Postgres) via $py (commit=$env:EW_SOURCE_COMMIT)"
    Start-Process -FilePath $py -ArgumentList "-m","ew.service" `
        -WorkingDirectory $root -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $root "derived\service_m2.out.log") `
        -RedirectStandardError  (Join-Path $root "derived\service_m2.err.log")
    Start-Sleep -Seconds 10
}

# 1. Down? start it.
$health = try { (Invoke-WebRequest -Uri "http://localhost:8377/api/v1/health" -TimeoutSec 5 -UseBasicParsing).StatusCode } catch { 0 }
if ($health -ne 200) {
    Log "health check failed ($health); starting service"
    Start-Service-Fresh
    $health = try { (Invoke-WebRequest -Uri "http://localhost:8377/api/v1/health" -TimeoutSec 5 -UseBasicParsing).StatusCode } catch { 0 }
    if ($health -eq 200) { Log "restart OK" } else { Log "restart FAILED" ; exit 1 }
    exit 0
}

# 2. Up, but running an OLD commit? redeploy. Only on a real commit MISMATCH
#    (a pre-closure build reports no /identity and is treated as behind). Never
#    merely because the tree is dirty.
if (-not $head) { exit 0 }   # cannot determine HEAD; do not thrash
$running = try {
    (Invoke-WebRequest -Uri "http://localhost:8377/api/v1/identity" -TimeoutSec 5 -UseBasicParsing).Content | ConvertFrom-Json
} catch { $null }
$runningCommit = if ($running) { $running.source_commit } else { $null }
if ($runningCommit -ne $head) {
    $rc = if ($runningCommit) { $runningCommit.Substring(0,[Math]::Min(12,$runningCommit.Length)) } else { "pre-closure/unknown" }
    Log ("deploy-lag: running {0} != HEAD {1}; redeploying" -f $rc, $head.Substring(0,12))
    $pid8377 = (Get-NetTCPConnection -LocalPort 8377 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -Expand OwningProcess)
    if ($pid8377) {
        Stop-Process -Id $pid8377 -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        if (Get-Process -Id $pid8377 -ErrorAction SilentlyContinue) {
            $r = (Get-CimInstance Win32_Process -Filter "ProcessId=$pid8377" | Invoke-CimMethod -MethodName Terminate).ReturnValue
            Log "Stop-Process denied on $pid8377; WMI Terminate rc=$r"
        } else { Log "killed old service $pid8377" }
        Start-Sleep -Seconds 2
    }
    Start-Service-Fresh
    $r2 = try {
        (Invoke-WebRequest -Uri "http://localhost:8377/api/v1/identity" -TimeoutSec 5 -UseBasicParsing).Content | ConvertFrom-Json
    } catch { $null }
    if ($r2 -and $r2.source_commit -eq $head) { Log "redeploy OK -> $head" ; exit 0 }
    Log "redeploy FAILED (still not HEAD)" ; exit 1
}
exit 0
