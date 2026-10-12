param([string]$Sid)
$wt = 'C:\Prometheus-worktrees\argus-c018-t050'
$meta = "$wt\rso\aether\runs\meta"
$env:EW_DB_HOST = '192.168.1.202'
$t0 = Get-Date
$p = Start-Process -FilePath python -ArgumentList '-B','-m','rso.aether.confirm','run',$Sid,'--cleared-by','C018-T042-cleared-2026-10-12' -WorkingDirectory $wt -RedirectStandardOutput "$meta\$Sid.out" -RedirectStandardError "$meta\$Sid.err" -WindowStyle Hidden -PassThru
$null = $p.Handle
$peak = 0
while (-not $p.HasExited) { try { $p.Refresh(); if ($p.PeakWorkingSet64 -gt $peak) { $peak = $p.PeakWorkingSet64 } } catch {}; Start-Sleep -Seconds 2 }
$p.WaitForExit()
$t1 = Get-Date
$o = [ordered]@{ shard=$Sid; pid=$p.Id; exit_code=$p.ExitCode; start_utc=$t0.ToUniversalTime().ToString('o'); end_utc=$t1.ToUniversalTime().ToString('o'); wall_s=[math]::Round(($t1-$t0).TotalSeconds,1); cpu_s=[math]::Round($p.TotalProcessorTime.TotalSeconds,1); peak_working_set_bytes=$peak }
($o | ConvertTo-Json) | Set-Content -Encoding utf8 "$meta\$Sid.res.json"
