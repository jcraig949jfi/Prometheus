# Register the Archaeon producer as a Task Scheduler job: one tick() every
# 15 minutes. Same house pattern as the SFE-M2 and PEW watchdogs, except there
# is no watchdog because there is no daemon -- each run is a complete cycle.
#
# 15 minutes is how often to ASK, not how often to write. Against the
# four-hour cadence roughly 15 of every 16 runs return NO_WRITE_CADENCE, which
# is the design working; the cost is one refused database round-trip.
#
# User-level task; no admin required. Kill switch:
#   schtasks /Delete /TN ArchaeonTick /F
#
# Inspect:
#   schtasks /Query /TN ArchaeonTick /V /FO LIST
#   Get-Content archaeon\deploy\archaeon_tick.log -Tail 40
$deploy = Split-Path -Parent $MyInvocation.MyCommand.Path
$script = Join-Path $deploy "archaeon_tick.cmd"
schtasks /Create /F /TN "ArchaeonTick" /SC MINUTE /MO 15 `
    /TR "cmd.exe /c `"$script`""
if ($LASTEXITCODE -eq 0) {
    Write-Host "ArchaeonTick registered: one tick every 15 minutes -> $script"
    Write-Host "Log: $(Join-Path $deploy 'archaeon_tick.log')"
} else {
    Write-Host "schtasks failed with $LASTEXITCODE"
    exit $LASTEXITCODE
}
