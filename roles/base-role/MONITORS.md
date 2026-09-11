# Standing monitors, watchdogs, shadows and loops -- the registry (base rule 7)

Currency: 2026-09-11 (Archaeon; seeded from the M1 scheduled-task list and the
loops known on that day). A standing loop that is not in this registry is
UNMANAGED; a registry row whose freshness source cannot be read is DORMANT.
Silence is never health. Every seat updates its rows at boot (RESPONSIBILITIES.md
step 7) and the base-role self-test checks that every enabled Prometheus
scheduled task on the host has a row.

One row per loop. Columns:
  name | kind | owner seat | host | INPUT it consumes | FRESHNESS source (where last_input_at / last_success_at can be read) | dormancy threshold | alarm route | state

ArchaeonTick | scheduled task, every 15 min | Archaeon | M1 | the SFE ledger (recent fossils) and the queue | archaeon/deploy/archaeon_tick.log (one JSON record per run; `at`, `decision`); queue rows created_by=archaeon | 4 h without a run record | Archaeon's status file; the tick receipt carries `conformance` and `workspace` | ACTIVE (pinned worktree F:\Prometheus-worktrees\archaeon-tick)
MnemosyneEvidenceWikiWatchdog | scheduled task, every 5 min | Mnemosyne | M1 | GET http://localhost:8377/api/v1/health | evidence_wiki/derived/watchdog.log | 15 min without a log line | none yet (restarts the service; does not notify) | ACTIVE; NEEDS a last-success line when the service answers, not only when it restarts
PEWBackupDaily | scheduled task, daily | Mnemosyne | M1 | the Evidence Wiki database | the backup artifact's timestamp | 36 h | none yet | ACTIVE
PEWRestoreVerifyWeekly | scheduled task, weekly | Mnemosyne | M1 | the latest backup | the verify report | 8 d | none yet | ACTIVE
PrometheusBackupWeekly | scheduled task, weekly | operator | M1 | F:\Prometheus (canonical) | scripts/backup log | 8 d | none | ACTIVE; runs from the canonical checkout (read-only use; allowed)
PrometheusMachineProbeM1 | scheduled task, every 5 min | Daedalus? (unclaimed) | M1 | host metrics | machine_probe output | 15 min | none | ACTIVE; OWNER UNCLAIMED -- runs from F:\Prometheus\scripts (the canonical checkout): a seat claims it or it is moved to a pinned worktree
SFEngine | service (Task Scheduler, running) | Daedalus | M1 | the engine ledger | GET /v2/version; deploy/verify_deploy | 5 min without an answer | Vivarium's consumer halts on UNREACHABLE (conformance gate) | ACTIVE, schema 8, instance eng_8a37a5d3
Vivarium consumer (viv.cli run) | long-running process | Vivarium | M1 | the queue (schema viv) | viv worker_heartbeat rows; `viv.cli status` | 10 min without a heartbeat | stranded-row check; the operator | ACTIVE (harness worktree; pinned worktree pending, F-28)
Elenchus shadow loop | review loop over Aporia's passes | Elenchus | any | engine/shadow/WORKLOG.jsonl (Aporia's per-pass log) | engine/shadow/REVIEWS.jsonl last reviewed_at; WORKLOG last pass_id | 48 h without a new Aporia pass | none -- THIS IS THE DORMANT WATCHDOG | DORMANT since 2026-09-01 (P177): its INPUT stopped. Feeding it = Aporia's standing loop running again, or Elenchus repointing the shadow at a live input under its program-wide mandate (ELEN-03 decides; operator rules which)
Hermes portfolio brief mailer | scripts/send_brief_email.py after metis_portfolio.py | Eos/Hermes lineage (legacy) | NOT M1 (no task, no cron, no process found on M1 on 2026-09-11) | dashboard/portfolio_brief.md | the email itself | daily | the operator's inbox | UNLOCATED -- the emails the operator still receives come from this or from another host (M2 / cloud); the sender must be identified from one email's headers and either registered here with an owner or stopped
PrometheusCampaign / PrometheusColdbandDrip / PrometheusColdbandM30 / PrometheusRekeyObjectZeros | scheduled tasks | Ergon | M1 | (looping with no work, from the canonical checkout) | task LastRunTime | -- | -- | DISABLED by Ergon 2026-09-11 (772edf15e), correctly: a loop with no input is not a monitor

How to feed a watchdog (the mechanics every row must satisfy):
  1. an INPUT it consumes, named, with an owner who produces it;
  2. a FRESHNESS record it writes on every run -- last_input_at and last_success_at -- readable without running it;
  3. a DORMANCY threshold and an alarm that fires when the input or the success is older than the threshold, routed to a seat or the operator;
  4. an explicit state here: ACTIVE, DORMANT (input stopped), DISABLED (by whom, when), UNLOCATED (runs somewhere nobody has found).
A loop that only reports when something is wrong is dormant the moment its input stops, and its silence will be read as health. That is the defect base rule 7 exists to name.
