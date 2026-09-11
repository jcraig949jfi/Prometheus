# Alethelia bootstrap — M1 (SKULLPORT), 2026-08-27

Second seat opened on M1 at James's request ("usually run on M3, want to run here as
well"). Constitutional posture unchanged: monitor and report only; every field carries
its query; UNKNOWN is never narrated over.

## Bootstrap checks (all run, all traceable)

- `python agents/alethelia/test_alethelia.py` -> **3/3 controls pass** (positive decoy
  surfaces; unreachable sources yield DEGRADED + UNKNOWN; degraded report does not
  render the calm banner). Charter section 6 gate satisfied.
- `python agents/alethelia/alethelia.py` -> 15/15 fields computed, no UNKNOWNs.
  Postgres reachable from this box. Previous `stations/REPORT_latest.*` was dated
  2026-08-20 10:52 — **the reporter had not run for 7 days**.
- Seat-identity discrepancy, recorded not resolved: `roles/Alethelia/RESPONSIBILITIES.md`
  names this an **M4** seat (parked DECISION); James refers to it as the **M3** seat;
  `stations/M3_STATUS.md` contains no Alethelia entry (M3 = Gandalf, point agent
  Hephaestus). UNKNOWN(which station owns the standing cron) — needs James.

## What the live report says (2026-08-27T11:40Z, HEAD 3e6811fc)

- postgres: 35 heartbeat rows, **33 stale >6h and still status='online'**; oldest
  ~100 days (Aporia 8,717,061s). This is DEC-001's lie shape occurring naturally, at
  scale, in production — not a plant.
- queues: BACKLOG is **644 PARKED / 138 DONE / 0 QUEUED**; `top_unblocked` = [].
  Every one of the 644 PARKED threads carries a gate. There is no unblocked work in
  the queue.
- queues: `engine/ledger/DR_EVENTS.jsonl` exists but is **0 bytes**. P31's commit
  message says "DR event trail live with a born-alive consumer"; the consumer leg is
  live, the trail is empty.
- shadow: 210 WORKLOG entries, last pass 2026-08-27T01:00Z-P175; 23 reviews, 0
  unanswered; **5 most recent passes (P171-P175) have no review targeting them**.

## Decoy-defined gaps, measured on live data (v0 does not compute these)

- **DEC-005 (GATE-WITHOUT-ELI5)** — join BACKLOG PARKED gates against GATE_ELI5.jsonl:
  **81 of 644 PARKED threads carry a gate string with no ELI5 entry** (e.g.
  CAT-MATH-0193, 0476-0479). The gap the decoy was written to define is real and large.
  63 ELI5 entries exist against 644 gated threads.
- **DEC-004 (CONSUMPTION-ORPHAN)** — 223 CONSUMPTION rows, 266 path-like refs in
  `consumed_by`; 142 repo-relative refs resolve, 120 bare basenames resolve against
  `git ls-files`. 4 flags raised, **all 4 adjudicated false positives of the extractor**
  (3 are shorthand double-refs of the form `attack_0348_pooled.py/_results.json`, whose
  files all exist; 1 is `memory/project_x_line_closed.md`, outside the repo). **0 true
  orphans.** A checker built on this would need DEC-004 planted to prove it can fire —
  a zero on live data is not evidence the check works.
- DEC-002 (QUEUE-ZOMBIE-RUNNING) closed in P30; `zombie_running` = [] on live data
  (there are no RUNNING threads at all).

## Honest limit on today's report

The banner read "all 15 fields computed from live queries" while 33 agents were
falsely 'online'. The banner reports **source reachability only**, not anomaly count —
so a skim of a fully-degraded fleet reads as calm. That is a legibility defect in the
renderer, not a fabrication (the stale list is right there in the field), but it is the
nearest thing to fabricated calm the current code permits.
