@echo off
rem D-23: run from the worktree this runner lives in (a PINNED worktree for a
rem scheduled task), never the canonical checkout. %~dp0 is ergon\ inside it.
cd /d %~dp0..
python ergon\probe\coldband_m30_free.py >> ergon\probe\ledgers\coldband_m30_free\console.log 2>&1
