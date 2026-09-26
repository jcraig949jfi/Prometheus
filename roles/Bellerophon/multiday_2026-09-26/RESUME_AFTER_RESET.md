# RESUME AFTER RESET -- Bellerophon multi-day campaign (written 2026-09-26 ~16:45Z at launch)

Standing authority (operator rulings 2026-09-26, prompts/00_OPERATOR_RULINGS_verbatim.md): no further HITL for the
defined transitions. Recover crashes WITHOUT asking; stop for the operator only on an integrity failure or lost
evidence. Stay BLIND to outcomes until md_analysis.py runs after the stop (counts, voids, memory, cost only).

| item | location |
|---|---|
| worktree / branch | D:/Prometheus-worktrees/bellerophon-multiday, bellerophon/multiday-campaign-2026-09-26 |
| frozen prereg | roles/Bellerophon/multiday_2026-09-26/MULTIDAY_PREREG.md (freeze 12ce26e23, code a3086cece) |
| workdir (evidence) | C:/Users/James/md_campaign_2026-09-26 (results.jsonl, STATUS.json, supervisor.jsonl, memory.jsonl, driver.log) |
| pinned code | C:/Users/James/md_campaign_2026-09-26/code (git archive of a3086cece; CRLF bytes, LF-normalised sha256 = freeze record) |
| pinned inputs | C:/Users/James/md_campaign_2026-09-26/md_inputs.json |
| frozen analysis | roles/Bellerophon/multiday_2026-09-26/tools/md_analysis.py |

Launched 2026-09-26T16:40:28Z: supervisor pid in supervisor.pid (it writes it itself), 12 workers, 4,160 runs x 20,000
ticks, active-runtime cap 60 h (expected ~27 h).

IF THE MACHINE REBOOTED OR THE SUPERVISOR DIED:
  1. Read STATUS.json. If "stopped": true, go to step 4.
  2. Check the pid in supervisor.pid is a live python process (Windows reuses pids after a reboot). If not, measure
     free RAM (keep >= 4 GB reserve) and relaunch detached from PowerShell:
       Start-Process C:/Users/James/AppData/Local/Python/pythoncore-3.14-64/python.exe
         -ArgumentList "-m","prometheus.z80atlas.multiday_supervisor","--workdir","C:/Users/James/md_campaign_2026-09-26",
                       "--inputs","C:/Users/James/md_campaign_2026-09-26/md_inputs.json","--workers","12"
         -WorkingDirectory C:/Users/James/md_campaign_2026-09-26/code -WindowStyle Hidden
     The supervisor re-checks integrity; the driver closes the crashed active segment at its last heartbeat and
     re-executes only runs without a result line.
  3. Stop for the operator ONLY on HALT_integrity_failure in supervisor.jsonl or lost evidence.
  4. After "stopped": run (from the worktree)
       python roles/Bellerophon/multiday_2026-09-26/tools/md_analysis.py --workdir C:/Users/James/md_campaign_2026-09-26
              --code C:/Users/James/md_campaign_2026-09-26/code --inputs C:/Users/James/md_campaign_2026-09-26/md_inputs.json --replay 0.03
     then write MULTIDAY_CAMPAIGN_REPORT.md (dispositions per prereg s10 with failure shapes), a failure ledger,
     ops accounting (active/wall time, segments, concurrency, memory, NOT_RUN, co-running jobs), STATUS.md, journal,
     review packet; commit, push; merge to main when the closeout verifies integrity (ruling 3 pattern).
