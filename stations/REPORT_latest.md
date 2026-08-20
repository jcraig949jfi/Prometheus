# Alethelia report — 2026-08-20T14:52:33+00:00

**all 15 fields computed from live queries**

## postgres
- heartbeats: [34 items] [{"agent": "Acheron", "machine": "M2", "status": "online", "age_sec": 7080035}, {"agent": "Apollo", "machine": "M2", "status": "online", "age_sec": 7624278}, {"agent": "Aporia", "machine": "M1", "status": "online", "age_sec": 8123811}] ...  ← query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats`
- stale_over_6h: [31 items] ["Acheron", "Apollo", "Aporia"] ...  ← query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats WHERE age > 6h AND status != DEAD`

## git
- head: "2b6fccc3"  ← query: `git rev-parse --short HEAD`
- last_commits: ["2b6fccc3 Harmonia-A soak P5: trap 6 CONFIRMED â€” raw join 0 keys, normalized 50,835", "e773576c Aporia P30: decoy law operational â€” plant, miss-as-predicted, grow the sense, re-catch", "5fefb672 Harmonia-A soak P4: mirror trap 1 is LIVE (14/26 cols) â€” and my own zero was vacuous", "756b7cf1 Aporia P29: Alethelia v0 â€” the reporter that cannot fabricate calm", "478b8454 Harmonia-A soak P3: P28 repairs verified adversarially â€” both complete, no regression"]  ← query: `git log --oneline -5`
- dirty_files: 3  ← query: `git status --porcelain -uno | wc -l`

## queues
- backlog_status_counts: {"DONE": 45, "PARKED": 601, "QUEUED": 136}  ← query: `parse BACKLOG.jsonl, count by status`
- top_unblocked: ["INFRA-DR-EVENTS", "INFRA-GATEWAY", "INFRA-PULSE-M4"]  ← query: `parse BACKLOG.jsonl, QUEUED+ungated, top-3 by priority`
- zombie_running: []  ← query: `parse BACKLOG.jsonl, RUNNING with generated age > 7d (or unparseable)`
- open_gates: 23  ← query: `count lines in GATE_ELI5.jsonl`
- dr_events: {"count": 0, "last": null}  ← query: `parse DR_EVENTS.jsonl: count + last record`

## shadow
- worklog_entries: 22  ← query: `count WORKLOG.jsonl records`
- last_pass: "2026-08-20T14:26Z-HARMA-P5"  ← query: `last WORKLOG record pass_id`
- reviews: 7  ← query: `count REVIEWS.jsonl records`
- unanswered_reviews: []  ← query: `REVIEWS ids minus review_responses ids across WORKLOG`
- unreviewed_passes: ["2026-08-20T13:26Z-HARMA-P3", "2026-08-20T13:52Z-HARMA-P4", "2026-08-20T13:52Z-P29", "2026-08-20T14:23Z-P30", "2026-08-20T14:26Z-HARMA-P5"]  ← query: `last 5 WORKLOG pass_ids absent from REVIEWS target_pass_id`
