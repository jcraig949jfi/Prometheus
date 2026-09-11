@echo off
rem D-23: run from the worktree this runner lives in (a PINNED worktree for a
rem scheduled task), never the canonical checkout. %~dp0 is ergon\ inside it.
cd /d %~dp0..
H:\Python312\python.exe ergon\probe\drip_coldband.py >> ergon\probe\ledgers\coldband_drip\console.log 2>&1
