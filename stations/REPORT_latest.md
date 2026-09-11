# Alethelia report -- 2026-09-11T11:48:26+00:00

**!! ANOMALIES: all 19 fields computed, 5 of 7 anomaly rules FIRED (stale_heartbeats, no_unblocked_work, shadow_input_dormant, unanswered_reviews, unreviewed_passes) !!**

## anomalies
- stale_heartbeats: FIRED -- 35 heartbeat rows older than 6h and not DEAD  <- rule: `len(postgres.stale_over_6h) > 0`
- zombie_running: CLEAR  <- rule: `len(queues.zombie_running) > 0`
- no_unblocked_work: FIRED -- no QUEUED+ungated thread in BACKLOG.jsonl  <- rule: `len(queues.top_unblocked) == 0`
- shadow_input_dormant: FIRED -- last Aporia pass 2026-09-01T00:00Z-P177 is 10.5 days old (threshold 48h)  <- rule: `age(shadow.last_pass) > 48h, timestamp parsed from the pass id`
- unanswered_reviews: FIRED -- 7 reviews with no review_response in WORKLOG  <- rule: `len(shadow.unanswered_reviews) > 0`
- unreviewed_passes: FIRED -- 5 of the last passes have no review targeting them  <- rule: `len(shadow.unreviewed_passes) > 0`
- dormant_on_comms: CLEAR  <- rule: `len(comms.dormant_on_comms) > 0; eligible = comms.comms_eligible`

## postgres
- heartbeats: [36 items] [{"agent": "Acheron", "machine": "M2", "status": "online", "age_sec": 8969788}, {"agent": "Apollo", "machine": "M2", "status": "online", "age_sec": 9514031}, {"agent": "Aporia", "machine": "M1", "status": "online", "age_sec": 10013564}] ...  <- query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats`
- stale_over_6h: [35 items] ["Acheron", "Apollo", "Aporia"] ...  <- query: `SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats WHERE age > 6h AND status != DEAD`

## comms
- seat_sync: [27 items] [{"seat": "Agora", "last_sync_age_sec": null, "unseen": 1, "oldest_unseen_age_sec": 1006}, {"seat": "Alethelia", "last_sync_age_sec": 594, "unseen": 0, "oldest_unseen_age_sec": null}, {"seat": "Apollo", "last_sync_age_sec": 664, "unseen": 1, "oldest_unseen_age_sec": 82}] ...  <- query: `per seat in comms.roster(): max(receipts.seen_at); count and oldest created_at of messages addressed to it or '*' with no seen receipt`
- comms_eligible: [22 items] ["Agora", "Apollo", "Aporia"] ...  <- query: `per seat in comms.roster(): max(receipts.seen_at); count and oldest created_at of messages addressed to it or '*' with no seen receipt WHERE unseen > 0 (seats the dormancy rule could fire on)`
- dormant_on_comms: []  <- query: `per seat in comms.roster(): max(receipts.seen_at); count and oldest created_at of messages addressed to it or '*' with no seen receipt WHERE oldest unseen message age > 24h`

## git
- head: "8600edd68"  <- query: `git rev-parse --short HEAD`
- last_commits: ["8600edd68 Lexis: same-day correction to the Archaeon manifest report (all 13 rows CRLF-hashed, per Diomedes f08c81c66, reproduced); calibration row; journal", "e09537480 Merge commit 'b2cb7267d73c1c0f86a68c2e923e106cfb315495' into lexis/base-role-adopt-2026-09-11", "4e8e63b41 Lexis adopts roles/base-role: two lanes made current, 13 writing scripts guarded, the frozen handoff re-verified at HEAD, and the prompt that would fire the seat's reopening criterion", "b2cb7267d Diomedes journal close 2026-09-11: commit f08c81c66 on main, comms message 14 to Archaeon, worktree retired", "f08c81c66 Diomedes adopts roles/base-role: parked seat made visible (STATUS, backlog, calibration, journal), the K0 instrument gains planted cheat/negative/vacuous controls, and the 2026-09-11 comms MANIFEST is found hashed over CRLF (13 of 13 entries; base self-test red on main, reported to Archaeon)"]  <- query: `git log --oneline -5`
- dirty_files: 12  <- query: `git status --porcelain -uno | wc -l`

## queues
- backlog_status_counts: {"DONE": 138, "PARKED": 644}  <- query: `parse BACKLOG.jsonl, count by status`
- top_unblocked: []  <- query: `parse BACKLOG.jsonl, QUEUED+ungated, top-3 by priority`
- zombie_running: []  <- query: `parse BACKLOG.jsonl, RUNNING with generated age > 7d (or unparseable)`
- open_gates: 63  <- query: `count lines in GATE_ELI5.jsonl`
- dr_events: {"count": 0, "last": null}  <- query: `parse DR_EVENTS.jsonl: count + last record`

## shadow
- worklog_entries: 212  <- query: `count WORKLOG.jsonl records`
- last_pass: "2026-09-01T00:00Z-P177"  <- query: `last WORKLOG record pass_id`
- reviews: 30  <- query: `count REVIEWS.jsonl records`
- unanswered_reviews: [7 items] ["ELEN-BOOTSTRAP-2026-08-27", "ELEN-2026-08-27T01:00Z-P175", "ELEN-2026-08-26T06:00Z-P174"] ...  <- query: `REVIEWS ids minus review_responses ids across WORKLOG`
- unreviewed_passes: ["2026-08-26T05:00Z-P173", "2026-08-26T06:00Z-P174", "2026-08-27T01:00Z-P175", "2026-08-27T02:00Z-P176", "2026-09-01T00:00Z-P177"]  <- query: `last 5 WORKLOG pass_ids absent from REVIEWS target_pass_id`

## workspace
- receipt: {"base_sha": "8600edd6857667052f2ab4db2584d27084cb754e", "branch": "alethelia/base-role-adopt-2026-09-11", "worktree_path": "F:\\Prometheus-worktrees\\alethelia-base-role", "dirty": true, "main_worktree": false}  <- query: `archaeon.workspace.receipt(): base_sha, branch, worktree_path, dirty, main_worktree`
