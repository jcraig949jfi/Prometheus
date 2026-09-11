# Serendipity Foundry Engine (M2) watchdog -- probe /v2/version, relaunch the
# Engine if it does not answer, and PARK ITSELF after a bounded number of
# consecutive failed relaunches (base rule 10, D-27).
#
# What changed on 2026-09-11 and why (Daedalus):
#   * Freshness. The old script wrote its log on FAILURE only, so a healthy
#     watchdog and a dead one left the same observable (Pronoia #120). Every
#     tick now overwrites a small STATE file with last_probe_at,
#     last_success_at, consecutive_failures and parked -- readable without
#     running anything. The log keeps transitions only, so it does not grow
#     288 lines a day.
#   * Bound. A restart that fails is retried every 5 minutes forever; that is
#     exactly the shape base rule 10 exists to contain. After BOUND
#     consecutive ticks in which the probe failed AND the relaunch failed,
#     the watchdog writes a typed park record, DISABLES ITS OWN TASK, and
#     stops. It resumes only when a person re-enables the task (explicit
#     clearance), never on the next fire. A tick in which the probe failed
#     but the relaunch succeeded is PRODUCTIVE (state advanced) and resets
#     the count. Productivity is keyed on the engine answering, never on this
#     script having emitted something.
#   * Accountable seat: Daedalus. The park record is the message; posting it
#     to comms from an S4U PowerShell task with no Python on the path is not
#     attempted here -- the registry row names the record's path as the alarm
#     route, and the row's owner reads it at boot (base role step 8).
#
# The Engine binds 192.168.1.191 (never 0.0.0.0), so the probe must use that
# address, not localhost. Self-signed cert -> curl with --cacert m2.crt.
#
# Test hooks (used by tests/test_sfe_watchdog_bound.py, never by the task):
#   -Deploy <dir>        where state/log/park live (default: this script's dir)
#   -SimulateProbe ok|fail   replace the HTTP probe with a fixed outcome
#   -NoLaunch            do not Start-Process; the relaunch counts as failed
#   -SimulateRelaunch ok|fail  do not Start-Process; the relaunch has this outcome
#   -NoDisable           do not call schtasks; the park record is still written
param(
    [string]$Deploy = "",
    [string]$Url = "https://192.168.1.191:8811/v2/version",
    [string]$TaskName = "SFEngineM2Watchdog",
    [int]$Bound = 3,
    [ValidateSet("", "ok", "fail")][string]$SimulateProbe = "",
    [ValidateSet("", "ok", "fail")][string]$SimulateRelaunch = "",
    [switch]$NoLaunch,
    [switch]$NoDisable
)
$ErrorActionPreference = "SilentlyContinue"
if (-not $Deploy) { $Deploy = Split-Path -Parent $MyInvocation.MyCommand.Path }
$log   = Join-Path $Deploy "sfengine_m2_watchdog.log"
$state = Join-Path $Deploy "sfengine_m2_watchdog.state.json"
$park  = Join-Path $Deploy "sfengine_m2_watchdog.park.json"
$cert  = Join-Path $Deploy "m2.crt"
$launcher = Join-Path $Deploy "sfengine_m2.cmd"
$now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

function Log($m) { Add-Content -Path $log -Value ("{0}  {1}" -f $now, $m) }

function Probe {
    if ($SimulateProbe -eq "ok")   { return $true }
    if ($SimulateProbe -eq "fail") { return $false }
    $curl = "$env:SystemRoot\System32\curl.exe"
    $out = & $curl -s -m 5 --cacert $cert $Url 2>$null
    return ($LASTEXITCODE -eq 0 -and $out -match '"api"\s*:\s*"v2"')
}

# -- load prior state ---------------------------------------------------------
$prev = $null
if (Test-Path $state) { $prev = Get-Content $state -Raw | ConvertFrom-Json }
$consecutive = 0
$lastSuccess = $null
if ($prev) {
    $consecutive = [int]$prev.consecutive_failures
    $lastSuccess = $prev.last_success_at
    if ($prev.parked -eq $true) {
        # Parked loops do not resume on their own. If the task fired anyway
        # (re-enabled without clearing the record), say so and stop.
        Log "PARKED since $($prev.parked_at); refusing to run until the park record is cleared"
        exit 3
    }
}

function Write-State($ok, $consecutive, $lastSuccess, $parked, $note) {
    $obj = [ordered]@{
        schema               = "sfengine_watchdog_state.v1"
        task                 = $TaskName
        url                  = $Url
        last_probe_at        = $now
        last_probe_ok        = $ok
        last_success_at      = $lastSuccess
        consecutive_failures = $consecutive
        bound                = $Bound
        parked               = $parked
        accountable_seat     = "Daedalus"
        note                 = $note
    }
    $obj | ConvertTo-Json | Set-Content -Path $state -Encoding ASCII
}

# -- tick -----------------------------------------------------------------------
if (Probe) {
    if ($consecutive -gt 0) { Log "engine answering again after $consecutive failed tick(s)" }
    Write-State $true 0 $now $false "engine answered"
    exit 0
}

Log "version probe failed; starting engine (consecutive failures so far: $consecutive)"
$relaunched = $false
if ($SimulateRelaunch -eq "ok")        { $relaunched = $true }
elseif ($SimulateRelaunch -eq "fail")  { $relaunched = $false }
elseif (-not $NoLaunch) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $launcher -WindowStyle Hidden
    Start-Sleep -Seconds 10
    $relaunched = Probe
}
if ($relaunched) {
    Log "restart OK"
    Write-State $true 0 $now $false "restarted and answering"   # productive: state advanced
    exit 0
}

$consecutive += 1
Log "restart FAILED ($consecutive of $Bound)"
if ($consecutive -lt $Bound) {
    Write-State $false $consecutive $lastSuccess $false "restart failed; will retry"
    exit 1
}

# -- park (rule 10a): typed record, task disabled, stop --------------------------
$record = [ordered]@{
    schema           = "loop_park.v1"
    loop             = $TaskName
    host             = $env:COMPUTERNAME
    parked_at        = $now
    bound            = $Bound
    consecutive_non_productive_ticks = $consecutive
    last_success_at  = $lastSuccess
    reason           = "probe failed and relaunch failed on $Bound consecutive ticks"
    accountable_seat = "Daedalus"
    clearance        = "delete this file, then Enable-ScheduledTask $TaskName; never on restart"
}
$record | ConvertTo-Json | Set-Content -Path $park -Encoding ASCII
Write-State $false $consecutive $lastSuccess $true "PARKED: bound reached"
Log "PARKED: $consecutive consecutive failed relaunches; record $park; task disabled"
if (-not $NoDisable) { & schtasks /Change /TN $TaskName /DISABLE | Out-Null }
exit 2
