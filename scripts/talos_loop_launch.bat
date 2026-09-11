@echo off
REM ==== RETIRED 2026-09-11 (Talos, TALOS-05; operator ruling on TALOS-01) ====
REM This launcher ran the daemon from the canonical checkout (cd /d %~dp0\..),
REM which D-23 forbids, and exported nothing that a linked worktree needs.
REM The daemon is PARKED by ruling and now refuses both the canonical checkout
REM and any run without roles/Talos/ledgers/DAEMON_UNPARKED.json on main
REM (agents/talos/daemon.py gates). This file is kept as the record of how
REM the May loop was started; it exits without launching anything.
echo TALOS LAUNCHER RETIRED 2026-09-11: the daemon is PARKED (roles/Talos/STATUS.md); nothing launched. 1>&2
exit /b 3
REM ==== original launcher text below, unchanged ====
REM Launcher for Talos (reasoning-code specialist corpus builder, Phase 0).
REM
REM Run via PowerShell:
REM   Start-Process -FilePath "scripts\talos_loop_launch.bat" -WindowStyle Hidden
REM
REM Mirrors hypatia/atalanta/pheme/clio/pythia launchers. Detached via
REM Start-Process so the daemon survives the parent shell exiting.
REM
REM See agents/talos/CHARTER.md for the contract.
REM
REM Phase 0 scope: corpus builder only. NO GPU training. Phase 1 wiring
REM is an explicit human gate (charter "Hard stops" section).

cd /d "%~dp0\.."
set PYTHONPATH=.
set PYTHONIOENCODING=utf-8
python -m agents.talos.daemon --loop --interval 3600 >> agents\talos\logs\talos.stdout.log 2>> agents\talos\logs\talos.stderr.log
