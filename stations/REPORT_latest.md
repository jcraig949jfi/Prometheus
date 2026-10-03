# Alethelia report — 2026-09-11T11:42:40+00:00

**all 15 fields computed from live queries**

## postgres
- heartbeats: [36 items] [{"agent": "Acheron", "machine": "M2", "status": "online", "age_sec": 8969441}, {"agent": "Apollo", "machine": "M2", "status": "online", "age_sec": 9513684}, {"agent": "Aporia", "machine": "M1", "status": "online", "age_sec": 10013217}] ...  ← query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats`
- stale_over_6h: [35 items] ["Acheron", "Apollo", "Aporia"] ...  ← query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats WHERE age > 6h AND status != DEAD`

## git
- head: "afd3548db"  ← query: `git rev-parse --short HEAD`
- last_commits: ["afd3548db Track E: D-18 amendment v1 measured, XOR correction, C3 and H5 fixtures", "5362ef6c7 Program level: the evolutionary substrate proposal, and why it is not a culmination", "25a8bdfe7 H1 gets a directory, and filing the feedback corrected my own review twice", "46d88eb02 PEW H0-H5 iter 1: typed reference index + idempotent publication", "52585727c H2 alpha: ca_stream_v1 runs, and the specified configuration is INERT"]  ← query: `git log --oneline -5`
- dirty_files: 35  ← query: `git status --porcelain -uno | wc -l`

## queues
- backlog_status_counts: {"DONE": 138, "PARKED": 644}  ← query: `parse BACKLOG.jsonl, count by status`
- top_unblocked: []  ← query: `parse BACKLOG.jsonl, QUEUED+ungated, top-3 by priority`
- zombie_running: []  ← query: `parse BACKLOG.jsonl, RUNNING with generated age > 7d (or unparseable)`
- open_gates: 63  ← query: `count lines in GATE_ELI5.jsonl`
- dr_events: {"count": 0, "last": null}  ← query: `parse DR_EVENTS.jsonl: count + last record`

## shadow
- worklog_entries: 212  ← query: `count WORKLOG.jsonl records`
- last_pass: "2026-09-01T00:00Z-P177"  ← query: `last WORKLOG record pass_id`
- reviews: 30  ← query: `count REVIEWS.jsonl records`
- unanswered_reviews: [7 items] ["ELEN-BOOTSTRAP-2026-08-27", "ELEN-2026-08-27T01:00Z-P175", "ELEN-2026-08-26T06:00Z-P174"] ...  ← query: `REVIEWS ids minus review_responses ids across WORKLOG`
- unreviewed_passes: ["2026-08-26T05:00Z-P173", "2026-08-26T06:00Z-P174", "2026-08-27T01:00Z-P175", "2026-08-27T02:00Z-P176", "2026-09-01T00:00Z-P177"]  ← query: `last 5 WORKLOG pass_ids absent from REVIEWS target_pass_id`
