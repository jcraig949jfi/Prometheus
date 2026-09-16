# Evidence Wiki watchdog -- M2 / SPECTREX5 wrapper (MNE-35, 2026-09-16).
#
# This file sets the ENVIRONMENT and the file names, then runs the one
# watchdog, scripts\ew_watchdog.ps1, which measures the property (an
# authenticated hybrid search answers), writes a last-success line on every
# healthy tick, restarts a present-but-dead service after FailThreshold
# ticks, and parks itself at the rule-10 bound. Nothing about the probe is
# restated here (base rule 1).
#
# WHAT THE M2 SERVICE FRONTS, and why (2026-09-16, Mnemosyne, journal of
# that date): the CANONICAL store on M1. The 2026-09-04 ruling that M2
# serves its own local fork rested on M1 being the ecosystem's home; on
# 2026-09-15 the operator handed M1 to Nestor and moved the SFE to M2
# carrying M1's engine.db (ccb26df01). A PEW on M2 fronting the quarantined
# fork would verify anchors against a world the engine no longer runs, and
# the fork had had no reader since 2026-09-05. The fork is NOT deleted; a
# fork-serving instance is one env change (PROMETHEUS_ENV=m2-local-fork,
# EW_DB_HOST unset) on a different port, if the operator wants one.
#
# History: 2026-09-04 fork-serving, presence probe (health only), deploy-
# aware auto-restart on canonical HEAD; the auto-restart is dropped because
# D-23 s6 advances a pinned worktree by an explicit logged command, never by
# a watchdog following HEAD. 2026-09-11..14: three `restart FAILED` lines,
# no ok line, no alarm; 2026-09-16 morning: the service it restarted ran
# from the canonical checkout with search permanently unready
# (sentence_transformers absent from the interpreter) and health 200.
$ErrorActionPreference = "SilentlyContinue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here                       # evidence_wiki/

# git for the service's workspace receipt (the S4U task context lacks it);
# the service now REFUSES to start when it cannot determine its worktree.
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    foreach ($g in 'C:\Program Files\Git\cmd') { if (Test-Path $g) { $env:PATH = "$g;$env:PATH"; break } }
}

# Store: the canonical environment (ew.db's default) at the host named in
# the untracked config.local.json (key canonical_db_host), else the M1
# address every other M2 launcher uses (ops\pew_serve_m2.py).
$dbHost = $null
$local = Join-Path $root "config.local.json"
if (Test-Path $local) { try { $dbHost = (Get-Content $local -Raw | ConvertFrom-Json).canonical_db_host } catch { } }
if (-not $dbHost) { $dbHost = "192.168.1.202" }
$env:EW_DB_HOST = $dbHost
$env:PROMETHEUS_ENV = "prometheus-canonical"
$env:PROMETHEUS_MACHINE = "M2"

# Interpreter: the M2 venv (.venv-m2, holding torch + sentence-transformers
# since 2026-09-16) lives beside the CANONICAL clone, not beside this pinned
# worktree, so it is found through the repository's common git dir -- no
# drive letter, and the same answer from every worktree. A bare `python`
# on M2 is a shim with no dependencies (measured 2026-09-16: the first
# pinned tick started the service "via python" and it never answered).
if (-not $env:EW_PYTHON) {
    $common = (& git -C $root rev-parse --path-format=absolute --git-common-dir 2>$null | Out-String).Trim()
    $cands = @()
    if ($common) { $cands += (Join-Path (Split-Path -Parent $common) ".venv-m2\Scripts\python.exe") }
    $cands += (Join-Path $root "..\.venv-m2\Scripts\python.exe")
    foreach ($cand in $cands) {
        if (Test-Path $cand) { $env:EW_PYTHON = (Resolve-Path $cand).Path; break }
    }
}

& (Join-Path $here "ew_watchdog.ps1") -Machine "M2" -HostAddr "127.0.0.1" -Port 8377 `
    -LogName "derived\watchdog_m2.log" -StateName "derived\watchdog_state_m2.json" `
    -ParkName "derived\watchdog_park_m2.json" -Seat "Mnemosyne" -AccountableSeat "Mnemosyne"
exit $LASTEXITCODE
