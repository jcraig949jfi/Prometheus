# Register the Evidence Wiki watchdog as a Task Scheduler job (every 5 min).
# User-level task; no admin required. Kill switch: delete the task
#   schtasks /Delete /TN MnemosyneEvidenceWikiWatchdog /F
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$script = Join-Path $root "scripts\ew_watchdog.ps1"
schtasks /Create /F /TN "MnemosyneEvidenceWikiWatchdog" /SC MINUTE /MO 5 `
    /TR "powershell -NoProfile -ExecutionPolicy Bypass -File `"$script`""
