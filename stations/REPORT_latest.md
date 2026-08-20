# Alethelia report — 2026-08-20T13:52:24+00:00

**all 13 fields computed from live queries**

## postgres
- heartbeats: [34 items] [{"agent": "Acheron", "machine": "M2", "status": "online", "age_sec": 7076426}, {"agent": "Apollo", "machine": "M2", "status": "online", "age_sec": 7620669}, {"agent": "Aporia", "machine": "M1", "status": "online", "age_sec": 8120202}] ...  ← query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats`
- stale_over_6h: [31 items] ["Acheron", "Apollo", "Aporia"] ...  ← query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats WHERE age > 6h AND status != DEAD`

## git
- head: "478b8454"  ← query: `git rev-parse --short HEAD`
- last_commits: ["478b8454 Harmonia-A soak P3: P28 repairs verified adversarially â€” both complete, no regression", "097f05c4 Aporia P28: soak findings metabolized; v1 cohort claims retracted under exchangeable rerun", "f44d0aa7 Harmonia-A soak P2: R12 harness green 17/17; sandbox pow bound does NOT generalize", "a7f610f4 Merge branch 'main' of https://github.com/jcraig949jfi/Prometheus", "cdea4574 THESIS v4.2: the closure â€” the HITL is inside the thesis"]  ← query: `git log --oneline -5`
- dirty_files: 0  ← query: `git status --porcelain -uno | wc -l`

## queues
- backlog_status_counts: {"DONE": 43, "PARKED": 600, "QUEUED": 139}  ← query: `parse BACKLOG.jsonl, count by status`
- top_unblocked: ["INFRA-ALETHELIA", "INFRA-CI", "INFRA-DECOYS"]  ← query: `parse BACKLOG.jsonl, QUEUED+ungated, top-3 by priority`
- open_gates: 19  ← query: `count lines in GATE_ELI5.jsonl`

## shadow
- worklog_entries: 18  ← query: `count WORKLOG.jsonl records`
- last_pass: "2026-08-20T13:26Z-HARMA-P3"  ← query: `last WORKLOG record pass_id`
- reviews: 7  ← query: `count REVIEWS.jsonl records`
- unanswered_reviews: []  ← query: `REVIEWS ids minus review_responses ids across WORKLOG`
- unreviewed_passes: ["2026-08-20T12:40Z-HARMA-P1", "2026-08-20T12:46Z-P27", "2026-08-20T12:52Z-HARMA-P2", "2026-08-20T13:21Z-P28", "2026-08-20T13:26Z-HARMA-P3"]  ← query: `last 5 WORKLOG pass_ids absent from REVIEWS target_pass_id`
