# intelligence_watchdog.ps1
#
# Checks whether scripts/intelligence_loop.py is running. If not, starts it.
# Designed to be invoked by Windows Task Scheduler every 30 minutes.
#
# Kill switch: if scripts/.intelligence_loop.disabled exists, the watchdog
# does nothing. Create that file when you want to stop the pipeline for
# maintenance without fighting the watchdog.
#
# Logs each invocation to logs/intelligence_watchdog.log.
#
# One-time Task Scheduler registration: see scripts/register_intelligence_watchdog.ps1
# (run that script once as administrator).

$ErrorActionPreference = "Continue"

$RepoRoot = "C:\Prometheus"
$LoopScript = Join-Path $RepoRoot "scripts\intelligence_loop.py"
$KillSwitch = Join-Path $RepoRoot "scripts\.intelligence_loop.disabled"
$LogDir = Join-Path $RepoRoot "logs"
$LogFile = Join-Path $LogDir "intelligence_watchdog.log"
$PythonExe = "C:\Users\jcrai\AppData\Local\Programs\Python\Python312\pythonw.exe"
$LoopArgs = "--hourly-min 240 --email-every-cycle"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Write-WatchdogLog {
    param([string]$Level, [string]$Message)
    $ts = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
    Add-Content -Path $LogFile -Value "$ts [$Level] $Message"
}

if (Test-Path $KillSwitch) {
    Write-WatchdogLog "INFO" "kill switch present at $KillSwitch - skipping check"
    exit 0
}

$running = Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" | Where-Object { $_.CommandLine -like "*intelligence_loop.py*" }

if ($running) {
    $procIds = ($running | ForEach-Object { $_.ProcessId }) -join ","
    Write-WatchdogLog "INFO" "intelligence_loop.py alive (PID $procIds) - no action"
    exit 0
}

Write-WatchdogLog "WARN" "intelligence_loop.py not running - restarting"

if (-not (Test-Path $PythonExe)) {
    Write-WatchdogLog "ERROR" "python interpreter missing at $PythonExe - abort"
    exit 1
}
if (-not (Test-Path $LoopScript)) {
    Write-WatchdogLog "ERROR" "intelligence_loop.py missing at $LoopScript - abort"
    exit 1
}

try {
    $proc = Start-Process -FilePath $PythonExe -ArgumentList "$LoopScript $LoopArgs" -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru
    Write-WatchdogLog "INFO" "started intelligence_loop.py (PID $($proc.Id)) with args: $LoopArgs"
} catch {
    $msg = $_.Exception.Message
    Write-WatchdogLog "ERROR" "failed to start intelligence_loop.py: $msg"
    exit 1
}
