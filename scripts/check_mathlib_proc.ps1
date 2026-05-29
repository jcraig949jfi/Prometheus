$cmdProc = Get-Process -Id 26468 -ErrorAction SilentlyContinue
if ($null -eq $cmdProc) {
    Write-Output "BUILD_PROC_GONE"
    exit
}
Write-Output "cmd_proc_alive cpu=$($cmdProc.CPU)"

$children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq 26468 }
foreach ($c in $children) {
    Write-Output "child: pid=$($c.ProcessId) name=$($c.Name)"
    $grandchildren = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $c.ProcessId }
    foreach ($g in $grandchildren) {
        Write-Output "  gchild: pid=$($g.ProcessId) name=$($g.Name)"
    }
}
