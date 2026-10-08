# Timed pause for the operator demo: at the target time, stop ONLY the NPE-48h experiment processes
# (waiting queues first so none can start, then queue B's worker tree, then queue B). Runs are resumable by file.
param([string]$At = "15:10")
$log = Join-Path $PSScriptRoot "runs\PAUSE.log"
$target = [datetime]::ParseExact((Get-Date -Format "yyyy-MM-dd") + " " + $At, "yyyy-MM-dd HH:mm", $null)
Add-Content $log ("{0} armed: will pause at {1}" -f (Get-Date -Format s), $target.ToString("s"))
while ((Get-Date) -lt $target) { Start-Sleep -Seconds 20 }
function Tree($id) { $k = Get-CimInstance Win32_Process -Filter "ParentProcessId=$id" | Select-Object -ExpandProperty ProcessId; foreach ($c in $k) { Tree $c }; $id }
$order = @(27800, 29236) + (Tree 40112)
foreach ($p in $order) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 5
$left = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'runqueue|multiprocessing.spawn' } | Select-Object -ExpandProperty ProcessId
Add-Content $log ("{0} PAUSED: stopped {1}; experiment python left: [{2}]" -f (Get-Date -Format s), ($order -join ","), ($left -join ","))
