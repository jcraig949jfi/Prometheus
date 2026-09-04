# Register the M2 Engine watchdog as a Task Scheduler job (every 5 min).
# User-level task; no admin required. Kill switch:
#   schtasks /Delete /TN SFEngineM2Watchdog /F
$deploy = Split-Path -Parent $MyInvocation.MyCommand.Path
$script = Join-Path $deploy "sfengine_m2_watchdog.ps1"
schtasks /Create /F /TN "SFEngineM2Watchdog" /SC MINUTE /MO 5 `
    /TR "powershell -NoProfile -ExecutionPolicy Bypass -File `"$script`""
