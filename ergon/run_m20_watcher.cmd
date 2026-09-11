@echo off
rem D-23: run from the worktree this runner lives in, never the canonical checkout.
cd /d %~dp0..
H:\Python312\python.exe ergon\probe\relaunch_m20.py >> ergon\probe\ledgers\m20_watcher_console.log 2>&1
