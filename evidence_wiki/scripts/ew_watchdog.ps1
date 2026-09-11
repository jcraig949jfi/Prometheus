# Mnemosyne Evidence Wiki watchdog (M1). Runs every 5 minutes from Task
# Scheduler out of the PINNED worktree (D-23 s6).
#
# It measures the PROPERTY, not presence (base rule: verify the property,
# never the label). History of this file, kept because each fix opened the
# next defect:
#   2026-09-11 am  no singleton guard: a slow health probe read as "down",
#                  three services were started, contention made every probe
#                  slower. Guard added: never start while a service is present.
#   2026-09-11 pm  the guard's mirror image: a service that was PRESENT and
#                  not ANSWERING (search wedged, health starved; Apollo #21)
#                  was never restarted for three hours. The host then rebooted
#                  and the cold start took ~4 minutes, so the 8-second
#                  post-start probe logged "restart FAILED" for a start that
#                  succeeded.
# Now: (1) probe 127.0.0.1, never "localhost" (::1 is tried first and the
# refusal costs ~2 s per call on this host); (2) health is liveness only, so
# a healthy tick also runs ONE bounded authenticated hybrid search -- the path
# that hung; (3) every healthy tick writes a last-success line (MONITORS.md
# row MnemosyneEvidenceWikiWatchdog asked for it); (4) a present service that
# fails FailThreshold consecutive ticks is stopped and started; (5) a fresh
# start gets StartGraceSec before it can be judged, and the next tick judges
# it, not an 8-second sleep. State lives in derived\watchdog_state.json.
#
# The bearer token is read from env EW_AUTH_TOKEN, else config.local.json,
# else config.json (machine_tokens.<Machine>, else auth_token). It is never
# written to the log.
#
# Parameters exist so the tests (tests\test_watchdog.py) can run this exact
# script against a fake service on another port without touching the live
# one: -Port, -ProcMatch, -StartFile/-StartArgs, -LogName, -StateName.
param(
    [int]$Port = 8377,
    [string]$HostAddr = "127.0.0.1",
    [string]$Machine = "M1",
    [string]$ProcMatch = 'ew\.service',
    [string]$StartFile = "",
    [string]$StartArgs = "-m ew.service",   # space-separated; -File passes strings only
    [string]$Root = "",
    [string]$LogName = "derived\watchdog.log",
    [string]$StateName = "derived\watchdog_state.json",
    [int]$FailThreshold = 3,
    [int]$StartGraceSec = 300,
    [int]$HealthTimeoutSec = 20,
    [int]$SearchTimeoutSec = 30
)
$ErrorActionPreference = "SilentlyContinue"
if (-not $Root) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$log = Join-Path $Root $LogName
$stateFile = Join-Path $Root $StateName
function Log($m) { Add-Content -Path $log -Value ("{0}  {1}" -f (Get-Date -Format s), $m) }

# Log cap: 288 lines a day at 5-minute ticks; roll at 2 MB, keep one.
if ((Test-Path $log) -and ((Get-Item $log).Length -gt 2MB)) {
    Move-Item -Force $log ($log + ".1")
}

# ---------------------------------------------------------------- state
$state = @{ consecutive_failures = 0; last_success = $null; last_start_at = $null; last_start_pid = $null }
if (Test-Path $stateFile) {
    try {
        $j = Get-Content $stateFile -Raw | ConvertFrom-Json
        foreach ($k in @("consecutive_failures", "last_success", "last_start_at", "last_start_pid")) {
            if ($null -ne $j.$k) { $state[$k] = $j.$k }
        }
    } catch { }
}
function Save-State { ($state | ConvertTo-Json -Compress) | Set-Content -Path $stateFile }

# ---------------------------------------------------------------- token
function Get-Token {
    if ($env:EW_AUTH_TOKEN) { return $env:EW_AUTH_TOKEN }
    foreach ($name in @("config.local.json", "config.json")) {
        $p = Join-Path $Root $name
        if (Test-Path $p) {
            try {
                $c = Get-Content $p -Raw | ConvertFrom-Json
                if ($c.machine_tokens -and $c.machine_tokens.$Machine) { return $c.machine_tokens.$Machine }
                if ($c.auth_token) { return $c.auth_token }
            } catch { }
        }
    }
    return $null
}

# ---------------------------------------------------------------- probes
$base = "http://{0}:{1}/api/v1" -f $HostAddr, $Port
$reason = $null
$healthMs = $null; $searchMs = $null; $hj = $null

$sw = [Diagnostics.Stopwatch]::StartNew()
try {
    $r = Invoke-WebRequest -Uri "$base/health" -TimeoutSec $HealthTimeoutSec -UseBasicParsing
    $healthMs = $sw.ElapsedMilliseconds
    if ($r.StatusCode -ne 200) { $reason = "health http $($r.StatusCode)" }
    else { try { $hj = $r.Content | ConvertFrom-Json } catch { $reason = "health body not JSON" } }
} catch {
    $reason = "health no answer in ${HealthTimeoutSec}s"
}

if (-not $reason) {
    $search = $hj.search
    if ($search -and -not $search.ready) {
        if ($search.error) { $reason = "model load error: $($search.error)" }
        elseif ($search.loading -and ($hj.uptime_s -lt $StartGraceSec)) {
            Log ("warming up: search model loading, uptime {0}s (grace {1}s); health {2}ms" -f $hj.uptime_s, $StartGraceSec, $healthMs)
            Save-State
            exit 0
        }
        else { $reason = "search model not ready after uptime $($hj.uptime_s)s (loading=$($search.loading))" }
    }
}

if (-not $reason) {
    $tok = Get-Token
    if (-not $tok) {
        $reason = "no bearer token available to the watchdog (env EW_AUTH_TOKEN, config.local.json, config.json)"
    } else {
        $hdr = @{ Authorization = "Bearer $tok"; "X-Prometheus-Machine" = $Machine; "X-Prometheus-Agent" = "watchdog" }
        $sw.Restart()
        try {
            $s = Invoke-WebRequest -Uri "$base/search?q=watchdog+probe&k=1&mode=hybrid" -Headers $hdr -TimeoutSec $SearchTimeoutSec -UseBasicParsing
            $searchMs = $sw.ElapsedMilliseconds
            if ($s.StatusCode -ne 200) { $reason = "search http $($s.StatusCode)" }
        } catch {
            $code = $null
            try { $code = [int]$_.Exception.Response.StatusCode } catch { }
            if ($code) { $reason = "search http $code" } else { $reason = "search no answer in ${SearchTimeoutSec}s" }
        }
    }
}

if (-not $reason) {
    $state.consecutive_failures = 0
    $state.last_success = (Get-Date -Format s)
    Save-State
    Log ("ok  health {0}ms  hybrid search {1}ms  last_success {2}" -f $healthMs, $searchMs, $state.last_success)
    exit 0
}

# ---------------------------------------------------------------- failure
$state.consecutive_failures = [int]$state.consecutive_failures + 1
$n = $state.consecutive_failures

$listeners = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
$listenerPids = @($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
$procs = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
           Where-Object { $_.CommandLine -match $ProcMatch })
$procPids = @($procs | Select-Object -ExpandProperty ProcessId -Unique)
$present = @($listenerPids + $procPids | Sort-Object -Unique | Where-Object { $_ })

if ($present.Count -gt 0) {
    $startAge = $null
    if ($state.last_start_at) {
        try { $startAge = [int]((Get-Date) - [datetime]$state.last_start_at).TotalSeconds } catch { }
    }
    if ($null -ne $startAge -and $startAge -lt $StartGraceSec) {
        Log ("not yet answering: {0}; started {1}s ago (grace {2}s); pids {3}; waiting" -f $reason, $startAge, $StartGraceSec, ($present -join ","))
        Save-State
        exit 0
    }
    if ($n -lt $FailThreshold) {
        Log ("probe failed ({0}/{1}): {2}; service present (listeners={3} processes={4}); waiting" -f $n, $FailThreshold, $reason, $listenerPids.Count, $procPids.Count)
        Save-State
        exit 0
    }
    Log ("probe failed {0} consecutive ticks: {1}; service present and not productive; stopping pids {2}" -f $n, $reason, ($present -join ","))
    foreach ($p in $present) {
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
        if (Get-Process -Id $p -ErrorAction SilentlyContinue) {
            $rc = (Get-CimInstance Win32_Process -Filter "ProcessId=$p" | Invoke-CimMethod -MethodName Terminate).ReturnValue
            Log ("Stop-Process denied on {0}; WMI Terminate rc={1}" -f $p, $rc)
        }
    }
    Start-Sleep -Seconds 2
}

# ---------------------------------------------------------------- start
# Interpreter resolution (machine-aware, backwards-compatible):
#   1. $env:EW_PYTHON if set
#   2. a repo-local venv beside the repo root (M2 uses .venv-m2)
#   3. bare "python" from PATH  <- M1's original behaviour, unchanged
$py = $env:EW_PYTHON
if (-not $py) {
    foreach ($cand in @("..\.venv-m2\Scripts\python.exe", "..\.venv\Scripts\python.exe")) {
        $full = Join-Path $Root $cand
        if (Test-Path $full) { $py = (Resolve-Path $full).Path; break }
    }
}
if (-not $py) { $py = "python" }

$startList = @($StartArgs -split " " | Where-Object { $_ })
if ($StartFile) { $startList = @(("`"{0}`"" -f $StartFile)) + $startList }
$proc = Start-Process -FilePath $py -ArgumentList $startList `
    -WorkingDirectory $Root -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $Root "derived\service.out.log") `
    -RedirectStandardError  (Join-Path $Root "derived\service.err.log")
$state.last_start_at = (Get-Date -Format s)
$state.last_start_pid = if ($proc) { $proc.Id } else { $null }
$state.consecutive_failures = 0
Save-State
Log ("started pid {0} via {1} after: {2}; next tick judges it (grace {3}s; cold start measured ~4 min after a reboot)" -f $state.last_start_pid, $py, $reason, $StartGraceSec)
exit 0
