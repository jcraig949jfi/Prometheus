<#
.SYNOPSIS
  Round 2 gate F1: launch one swarm lane session and log its whole life.

.DESCRIPTION
  Round 1 lost two sessions (A at 07:29, D at 07:35) and nothing recorded
  when or how they exited. This wrapper starts the session in the current
  console, then appends JSON lines to the launch log:
    start   {lane, pid, ts, worktree, exe, args, host}
    session {lane, pid, session_id}   (from ~/.claude/sessions/<pid>.json)
    exit    {lane, pid, session_id, exit_code, ts, duration_s}
  primordial/ops/liveness.py reads this log (pid alive, transcript age, bus
  heartbeat) and is the only thing allowed to reap a recorded pid.

.EXAMPLE
  # In a new Windows Terminal tab (one per lane, boot one at a time):
  powershell -ExecutionPolicy Bypass -File F:\Prometheus-worktrees\nestor-r2-b\primordial\ops\launch_lane.ps1 -Lane B -Worktree F:\Prometheus-worktrees\nestor-r2-b

.EXAMPLE
  # Self-test of the logging (no Claude):
  powershell -ExecutionPolicy Bypass -File primordial\ops\launch_lane.ps1 -Lane B -Worktree . -Exe cmd.exe -ExeArgs "/c exit 3"
  # (under -File an array like '/c','exit 3' binds as ONE literal string; pass one string)
  # Through a scheduled task, with disable-after-run: python -m primordial.ops.schtask_launch selftest
#>
param(
    [Parameter(Mandatory = $true)][ValidateSet('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'P', 'Q', 'W', 'T', 'U', 'R')][string]$Lane,  # must equal core/contract.py LANES (test_launch_lane_lanes.py)
    [Parameter(Mandatory = $true)][string]$Worktree,
    [string]$Name = "",
    [string]$Exe = "$env:USERPROFILE\.local\bin\claude.exe",
    [string[]]$ExeArgs = @('--dangerously-skip-permissions', '--remote-control'),
    [string]$LogDir = "C:\Users\jcrai\lab\pm-data\launcher",
    [switch]$BootPrompt,  # start the session on roles/Nestor/sidequests/graphworld/<PromptDir>/<Lane>.md
    [string]$PromptDir = "prompts_r2",
    [switch]$DryRun  # F-R6-5 gate helper: parse + build the launch line, print one JSON line, exit 0; no log, no env, no process
)
$ErrorActionPreference = 'Stop'
if (-not $Name) { $Name = "Nestor $Lane r2" }
$Worktree = (Resolve-Path $Worktree).Path

$parts = @()
if ($BootPrompt -and $Exe -like '*claude*') {
    # quote-free first prompt: the cohort's full paste block lives in the worktree (no multi-line quoting)
    $parts += ('"Read roles/Nestor/sidequests/graphworld/' + $PromptDir + '/' + $Lane + '.md in this worktree and follow it exactly."')
}
$parts += @($ExeArgs)
if ($Exe -like '*claude*') { $parts += ('"' + $Name + '"') }
$argline = ($parts -join ' ')

if ($DryRun) {
    $promptFile = $null
    $promptExists = $null
    if ($BootPrompt) {
        $promptFile = Join-Path $Worktree ('roles\Nestor\sidequests\graphworld\' + $PromptDir + '\' + $Lane + '.md')
        $promptExists = [bool](Test-Path -LiteralPath $promptFile -PathType Leaf)
    }
    $o = [ordered]@{ dry_run = $true; lane = $Lane; worktree = $Worktree; exe = $Exe; args = $argline;
                     prompt_file = $promptFile; prompt_exists = $promptExists }
    Write-Output ($o | ConvertTo-Json -Compress)
    exit 0
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$log = Join-Path $LogDir 'launch_log.jsonl'

function Write-LaunchLog([hashtable]$o) {
    $line = ($o | ConvertTo-Json -Compress)
    [System.IO.File]::AppendAllText($log, $line + "`n", (New-Object System.Text.UTF8Encoding($false)))
}

$env:PM_LANE = $Lane
$env:OMP_NUM_THREADS = '3'
$env:NUMBA_NUM_THREADS = '3'
$env:OPENBLAS_NUM_THREADS = '3'

$start = Get-Date
$p = Start-Process -FilePath $Exe -ArgumentList $argline -WorkingDirectory $Worktree -NoNewWindow -PassThru
$null = $p.Handle   # keep a handle so ExitCode is readable after exit
Write-LaunchLog @{ event = 'start'; lane = $Lane; pid = $p.Id; ts = $start.ToString('o'); worktree = $Worktree;
                   exe = $Exe; args = $argline; host = $env:COMPUTERNAME }

$sid = $null
$sessFile = Join-Path $env:USERPROFILE ".claude\sessions\$($p.Id).json"
while (-not $p.HasExited) {
    if (-not $sid -and (Test-Path $sessFile)) {
        try {
            $sid = (Get-Content $sessFile -Raw | ConvertFrom-Json).sessionId
            Write-LaunchLog @{ event = 'session'; lane = $Lane; pid = $p.Id; session_id = $sid; ts = (Get-Date).ToString('o') }
        } catch { }
    }
    Start-Sleep -Seconds 5
}
$p.WaitForExit()
$end = Get-Date
Write-LaunchLog @{ event = 'exit'; lane = $Lane; pid = $p.Id; session_id = $sid; exit_code = $p.ExitCode;
                   ts = $end.ToString('o'); duration_s = [int]($end - $start).TotalSeconds }
Write-Host "[launch_lane] lane $Lane pid $($p.Id) exited with code $($p.ExitCode) after $([int]($end - $start).TotalSeconds) s (logged to $log)"
