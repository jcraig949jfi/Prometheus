# register_intelligence_watchdog.ps1
#
# One-time setup: registers PrometheusIntelligenceWatchdog as a Windows
# Scheduled Task that fires every 30 minutes and runs the watchdog.
#
# Run this script ONCE as administrator:
#   Right-click PowerShell -> Run as Administrator
#   cd C:\Prometheus
#   .\scripts\register_intelligence_watchdog.ps1
#
# To unregister:
#   Unregister-ScheduledTask -TaskName "PrometheusIntelligenceWatchdog" -Confirm:$false
#
# To check status:
#   Get-ScheduledTask -TaskName "PrometheusIntelligenceWatchdog" | Get-ScheduledTaskInfo

$TaskName = "PrometheusIntelligenceWatchdog"
$WatchdogScript = "C:\Prometheus\scripts\intelligence_watchdog.ps1"

if (-not (Test-Path $WatchdogScript)) {
    Write-Error "watchdog script not found at $WatchdogScript"
    exit 1
}

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "task '$TaskName' already exists - unregistering before re-creating"
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $WatchdogScript"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration ([TimeSpan]::FromDays(3650))).Repetition

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

$result = Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Restart Prometheus intelligence_loop.py if it is not running" -ErrorAction Stop

Write-Host ""
Write-Host "Registered scheduled task '$TaskName'."
Write-Host "It will fire in 1 minute, then every 30 minutes thereafter."
Write-Host "Logs at C:\Prometheus\logs\intelligence_watchdog.log"
Write-Host ""
Write-Host "To stop the watchdog without unregistering, create the kill-switch file:"
Write-Host "  New-Item C:\Prometheus\scripts\.intelligence_loop.disabled"
