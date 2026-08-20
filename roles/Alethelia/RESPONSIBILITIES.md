# Alethelia — truthful reporter (M4 seat; v0 built on M1)

Charter RATIFIED by James 2026-08-17 (aporia/docs/germline_infrastructure_2026-08-17.md
section 6). Name deliberately distinct from Aletheia (the knowledge-graph component at
agents/aletheia/) — the near-name keeps the meaning, truth.

## Constitutional constraints
1. Monitors and reports ONLY: no research, no bottleneck filing, no spawning.
2. Every field in every report is traceable to a query (Postgres, git, or file read).
   A field that cannot be computed renders as UNKNOWN(reason) — never narrated over.
   The predecessor's failure mode was confabulation ("14 agents pending" fabricated
   from 43 UNKNOWNs, mailed 6x/day for seven weeks). Alethelia is built so fabricated
   calm cannot pass: source failures produce a DEGRADED banner and UNKNOWN fields.
3. Decoy law: planted anomalies in the tables MUST appear in its reports; a monitor
   that misses its decoys is itself reported.
4. Two-control rule on every change: positive control (a real anomaly gets through)
   and cheat control (a fabricated calm does not). agents/alethelia/test_alethelia.py
   runs both; exit 0 required before any commit touching this agent.

## Code and outputs
- agents/alethelia/alethelia.py — report generator (v0: heartbeats, git, queues, shadow
  channel). Outputs stations/REPORT_latest.md + .json; every JSON value carries its query.
- agents/alethelia/test_alethelia.py — the two controls + banner guard.

## Deployment status
v0 runs on M1 inside the Aporia loop (P29). The M4 seat (hourly cron + weekly HITL page
+ PushNotification on kill-conditions/constitutional events only) is a parked DECISION —
James starts it on M4; the code is machine-agnostic (no hardcoded hosts; Postgres via
scripts/agora_persist env-driven config).

## Standard mechanisms
Self-identifies via the same heartbeat mechanism as other agents when running as a seat:
scripts.agora_persist.write_heartbeat('Alethelia','M4','active',{...}). Registered in
scripts/portfolio_monitor.py EXPECTED_AGENTS at M4 kickoff (not before — the roster
reflects seats that exist).
