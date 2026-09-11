@echo off
rem D-23: run from the worktree this runner lives in (a PINNED worktree for a
rem scheduled task), never the canonical checkout. %~dp0 is ergon\ inside it.
cd /d %~dp0..
python ergon\probe\campaign.py >> ergon\probe\ledgers\campaign\campaign_console.log 2>&1
