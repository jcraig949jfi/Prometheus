# Register PrometheusMachineProbeM1 scheduled task.
# Mirrors the universal prompt at
# pivot/machine_probe_setup_prompts_2026-05-24.md step 8, with M1 label
# and F:\Prometheus working dir.

$TaskName = 'PrometheusMachineProbeM1'

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction `
    -Execute 'pythonw.exe' `
    -Argument 'F:\Prometheus\scripts\machine_probe.py --interval 60' `
    -WorkingDirectory 'F:\Prometheus'

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
$trigger.Repetition = (New-ScheduledTaskTrigger `
    -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration ([TimeSpan]::FromDays(3650))).Repetition

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -AllowStartIfOnBatteries `
    -MultipleInstances IgnoreNew

$user = "$env:USERDOMAIN\$env:USERNAME"
$principal = New-ScheduledTaskPrincipal `
    -UserId $user `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Restart Prometheus machine_probe.py on M1 (SKULLPORT) if not running"
