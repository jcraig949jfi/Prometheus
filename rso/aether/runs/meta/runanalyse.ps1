$wt='C:\Prometheus-worktrees\argus-c018-t050'; $env:EW_DB_HOST='192.168.1.202'
$p=Start-Process -FilePath python -ArgumentList '-B','-m','rso.aether.confirm','analyse' -WorkingDirectory $wt -RedirectStandardOutput "$wt\rso\aether\runs\meta\analyse_full.out" -RedirectStandardError "$wt\rso\aether\runs\meta\analyse_full.err" -WindowStyle Hidden -PassThru
$null=$p.Handle; $peak=0
while(-not $p.HasExited){ try{$p.Refresh(); if($p.PeakWorkingSet64 -gt $peak){$peak=$p.PeakWorkingSet64}}catch{}; Start-Sleep 2 }
$p.WaitForExit()
@{exit_code=$p.ExitCode;cpu_s=[math]::Round($p.TotalProcessorTime.TotalSeconds,1);peak=$peak;end=(Get-Date).ToUniversalTime().ToString('o')} | ConvertTo-Json | Set-Content "$wt\rso\aether\runs\meta\analyse.res.json"
