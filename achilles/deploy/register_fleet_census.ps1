# register_fleet_census.ps1 -- Achilles fleet census, every 6 hours (charter 2026-09-30)
#
# Registers PrometheusFleetCensus as a windowless Scheduled Task on this host (user level, no
# admin). The task runs achilles/census/run.py from a PINNED worktree (WORKING_CONTRACT s6) and
# commits outputs from a separate PUBLISH worktree; the canonical checkout is never touched.
# Registry row: roles/base-role/MONITORS.md "PrometheusFleetCensus / AchillesFleetCensus"
# (bound 4 non-productive runs, accountable seat Achilles; the runner parks itself at the bound).
#
#   .\register_fleet_census.ps1 -Pinned C:\Prometheus-worktrees\achilles-census-pinned `
#       -Publish C:\Prometheus-worktrees\achilles-publish -State C:\Prometheus-worktrees\achilles-census-state `
#       -Python C:\Users\<you>\AppData\Local\Programs\Python\Python311\python.exe
#
# Unregister:  Unregister-ScheduledTask -TaskName PrometheusFleetCensus -Confirm:$false
# Status:      Get-ScheduledTask -TaskName PrometheusFleetCensus | Get-ScheduledTaskInfo
# Run now:     Start-ScheduledTask -TaskName PrometheusFleetCensus
#
# LogonType Interactive: git push uses the user's credential store, which a non-interactive
# (S4U) logon cannot read, so the task runs while the user is logged on (a locked screen is fine).
# -StartWhenAvailable runs a missed slot at the next opportunity; a slot that never runs shows as
# a red STALE banner on the page and a STALE line in the status email.

param(
    [Parameter(Mandatory = $true)][string]$Pinned,
    [Parameter(Mandatory = $true)][string]$Publish,
    [Parameter(Mandatory = $true)][string]$State,
    [Parameter(Mandatory = $true)][string]$Python
)

$TaskName = "PrometheusFleetCensus"
$Cmd = Join-Path $Pinned "achilles\deploy\run_census.cmd"
if (-not (Test-Path $Cmd)) { Write-Error "runner not found at $Cmd"; exit 1 }
if (-not (Test-Path (Join-Path $Publish ".git"))) { Write-Error "publish worktree not found at $Publish"; exit 1 }
if (-not (Test-Path $Python)) { Write-Error "python not found at $Python"; exit 1 }
New-Item -ItemType Directory -Force $State | Out-Null

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute "conhost.exe" `
    -Argument "--headless cmd.exe /c `"`"$Cmd`" `"$Pinned`" `"$Publish`" `"$State`" `"$Python`"`"" -WorkingDirectory $Pinned
$trigger = New-ScheduledTaskTrigger -Daily -At "00:30"
$repeat = New-ScheduledTaskTrigger -Once -At "00:30" -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 1)
$trigger.Repetition = $repeat.Repetition
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 1) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Principal $principal -Description "Achilles fleet census (every 6 h: 00:30/06:30/12:30/18:30 local). Snapshot docs/fleet/fleet_state.json, page docs/fleet/index.html, email block docs/fleet/email_census.json. Parks after 4 non-productive runs. roles/Achilles" `
    -ErrorAction Stop | Out-Null
Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo | Format-List TaskName, NextRunTime, LastRunTime, LastTaskResult
