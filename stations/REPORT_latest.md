# Alethelia report — 2026-08-20T14:22:27+00:00

**all 14 fields computed from live queries**

## postgres
- heartbeats: [34 items] [{"agent": "Acheron", "machine": "M2", "status": "online", "age_sec": 7078229}, {"agent": "Apollo", "machine": "M2", "status": "online", "age_sec": 7622472}, {"agent": "Aporia", "machine": "M1", "status": "online", "age_sec": 8122005}] ...  ← query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats`
- stale_over_6h: [31 items] ["Acheron", "Apollo", "Aporia"] ...  ← query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats WHERE age > 6h AND status != DEAD`

## git
- head: "5fefb672"  ← query: `git rev-parse --short HEAD`
- last_commits: ["5fefb672 Harmonia-A soak P4: mirror trap 1 is LIVE (14/26 cols) â€” and my own zero was vacuous", "756b7cf1 Aporia P29: Alethelia v0 â€” the reporter that cannot fabricate calm", "478b8454 Harmonia-A soak P3: P28 repairs verified adversarially â€” both complete, no regression", "097f05c4 Aporia P28: soak findings metabolized; v1 cohort claims retracted under exchangeable rerun", "f44d0aa7 Harmonia-A soak P2: R12 harness green 17/17; sandbox pow bound does NOT generalize"]  ← query: `git log --oneline -5`
- dirty_files: 3  ← query: `git status --porcelain -uno | wc -l`

## queues
- backlog_status_counts: {"DONE": 44, "PARKED": 601, "QUEUED": 137}  ← query: `parse BACKLOG.jsonl, count by status`
- top_unblocked: ["INFRA-DECOYS", "INFRA-DR-EVENTS", "INFRA-GATEWAY"]  ← query: `parse BACKLOG.jsonl, QUEUED+ungated, top-3 by priority`
- zombie_running: []  ← query: `parse BACKLOG.jsonl, RUNNING with generated age > 7d (or unparseable)`
- open_gates: 21  ← query: `count lines in GATE_ELI5.jsonl`

## shadow
- worklog_entries: 20  ← query: `count WORKLOG.jsonl records`
- last_pass: "2026-08-20T13:52Z-P29"  ← query: `last WORKLOG record pass_id`
- reviews: 7  ← query: `count REVIEWS.jsonl records`
- unanswered_reviews: []  ← query: `REVIEWS ids minus review_responses ids across WORKLOG`
- unreviewed_passes: ["2026-08-20T12:52Z-HARMA-P2", "2026-08-20T13:21Z-P28", "2026-08-20T13:26Z-HARMA-P3", "2026-08-20T13:52Z-HARMA-P4", "2026-08-20T13:52Z-P29"]  ← query: `last 5 WORKLOG pass_ids absent from REVIEWS target_pass_id`
