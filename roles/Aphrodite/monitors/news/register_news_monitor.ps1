# register_news_monitor.ps1 -- Aphrodite's bounded RSI news monitor (APHRODITE-12)
#
# Registers AphroditeNewsWatch as a weekly, windowless Scheduled Task on this
# host (M4 rule: no console windows). The task runs run_news_pass.py from a
# PINNED worktree (WORKING_CONTRACT s6), passed as -Pinned.
#
#   .\register_news_monitor.ps1 -Pinned C:\...\aphrodite-news-pinned -Python C:\...\python.exe
#
# Unregister:  Unregister-ScheduledTask -TaskName AphroditeNewsWatch -Confirm:$false
# Status:      Get-ScheduledTask -TaskName AphroditeNewsWatch | Get-ScheduledTaskInfo

param(
    [Parameter(Mandatory = $true)][string]$Pinned,
    [Parameter(Mandatory = $true)][string]$Python
)

$TaskName = "AphroditeNewsWatch"
$Runner = Join-Path $Pinned "roles\Aphrodite\monitors\news\run_news_pass.py"
if (-not (Test-Path $Runner)) { Write-Error "runner not found at $Runner"; exit 1 }

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute "conhost.exe" `
    -Argument "--headless `"$Python`" `"$Runner`"" -WorkingDirectory (Split-Path $Runner)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "03:00"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Principal $principal -Description "Aphrodite bounded RSI news monitor (weekly; max 8 inspected, 3 admitted; parks after 4 empty runs). roles/Aphrodite/monitors/news" `
    -ErrorAction Stop | Out-Null
Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo | Format-List TaskName, NextRunTime, LastRunTime
