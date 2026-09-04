# Serendipity Foundry Engine (M2) watchdog: start the Engine if /v2/version
# does not answer. Safe to run every few minutes from Task Scheduler.
#
# M1 runs the Engine as an always-on S4U scheduled task named SFEngine and has
# no watchdog. M2 uses the watchdog pattern instead (same one PEW uses here),
# because it also recovers from a crash, not only from a reboot.
$ErrorActionPreference = "SilentlyContinue"
$deploy = Split-Path -Parent $MyInvocation.MyCommand.Path
$log = Join-Path $deploy "sfengine_m2_watchdog.log"
$cert = Join-Path $deploy "m2.crt"
function Log($m) { Add-Content -Path $log -Value ("{0}  {1}" -f (Get-Date -Format s), $m) }

# The Engine binds 192.168.1.191 (never 0.0.0.0), so the health probe must use
# that address, not localhost. Self-signed cert -> curl with --cacert m2.crt.
$curl = "$env:SystemRoot\System32\curl.exe"
$probe = & $curl -s -m 5 --cacert $cert https://192.168.1.191:8811/v2/version 2>$null
if ($LASTEXITCODE -eq 0 -and $probe -match '"api"\s*:\s*"v2"') { exit 0 }

Log "version probe failed; starting engine"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", (Join-Path $deploy "sfengine_m2.cmd") -WindowStyle Hidden
Start-Sleep -Seconds 10
$probe2 = & $curl -s -m 5 --cacert $cert https://192.168.1.191:8811/v2/version 2>$null
if ($LASTEXITCODE -eq 0 -and $probe2 -match '"api"\s*:\s*"v2"') { Log "restart OK"; exit 0 }
Log "restart FAILED"
exit 1
