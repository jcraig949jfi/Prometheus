@echo off
rem Supervisor for the 72 h Z80 x Atlas campaign: restarts the scheduler until CAMPAIGN_DONE.json exists. No LLM, no HITL.
cd /d D:\Prometheus-worktrees\archaeon-wse-2026-09-16
:loop
if exist archaeon\z80atlas\campaign\CAMPAIGN_DONE.json goto done
python -m archaeon.z80atlas.scheduler --resume >> archaeon\z80atlas\campaign\supervisor.log 2>&1
if exist archaeon\z80atlas\campaign\CAMPAIGN_DONE.json goto done
timeout /t 30 /nobreak > nul
goto loop
:done
echo done >> archaeon\z80atlas\campaign\supervisor.log
