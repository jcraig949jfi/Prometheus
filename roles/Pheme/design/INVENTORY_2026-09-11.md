# PHEME-02 step 1-2: inventory of existing signal machinery, and what survives from May

Currency: 2026-09-11. Read at origin/main db11b7e0b (worktree
F:\Prometheus-worktrees\pheme-base-role). Ruling: roles/Pheme/prompts/
2026-09-11_ruling/ (sha256 cad7cdd160fa...). Reuse before inventing.

Every row below is a mechanism that already emits, stores or judges
something a "did anything happen" seat could read. For each: where it
lives, what it emits, whether it reports LEVELS (a state) or TRANSITIONS
(a change), whether it deduplicates, and who consumes it. The column that
matters for Pheme is the level/transition one: almost everything in the
repository reports levels, and a level re-read every tick is the
firehose the ruling forbids.

## 1. Existing mechanisms (12 found; nothing invented)

M1  comms queue (comms/, Postgres schema comms; messages, receipts,
    task_queue, agents). Emits: typed messages (prompt, delegation,
    report, question, ruling, ack, broadcast) with sha256, receipts on
    sight, queue positions. Level/transition: TRANSITION (a message is an
    event; a receipt is an event). Dedup: by message id. Consumers: every
    seat at sync; the operator with --all. 43 messages as of 15:53 UTC.
    Gap: no kind means "state changed"; a ruling is routed to its
    recipients only.

M2  roles/base-role/MONITORS.md (Archaeon's registry). Emits: one row per
    standing loop with INPUT, FRESHNESS source, threshold, alarm, STATE
    (ACTIVE/DORMANT/DEAD/DISABLED/UNLOCATED) and PRODUCTIVITY signal.
    Level/transition: LEVEL, hand-edited; 42 revisions in one day, so
    its git history IS a transition log nobody reads as one. Dedup: n/a.
    Consumers: boot step 8; the base-role self-test (row shape only).

M3  Alethelia reporter (agents/alethelia/alethelia.py; stations/
    REPORT_latest.json). Emits: 7 anomaly rules each FIRED / CLEAR /
    INDETERMINATE(reason) over Postgres, comms, git, queues, shadow.
    Level/transition: LEVEL (each run re-evaluates; the banner reports
    "5 of 7 FIRED" whether or not that is new). Dedup: none; 4 committed
    reports since 2026-08-20. Consumers: whoever reads the report; no
    paging (ALET-18). This is the closest sibling: Pheme over Alethelia
    would be the derivative (d/dt) of its rule states.

M4  attacks/preflight.py --probes with attacks/known_failing.json
    (Charon, 2026-08-24; pre-commit hook in the canonical .git/hooks).
    Emits: PASS/FAIL per probe, BASELINE-RATCHETED: a known-still-failing
    probe is silent, a stale baseline entry that now passes is reported
    (the ratchet tightens), a new regression blocks. Level/transition:
    TRANSITION against a seen-set. Dedup: YES, by probe name. Consumers:
    the committer. This is the one existing novelty primitive in the
    repository and the model for Pheme's novelty layer. known_failing.json
    is currently {} (2 revisions).

M5  Kairos claim lint (roles/Kairos/science/claim_lint.py; 25 codes,
    UNDECLARED branch; negative/positive/cheat fixtures). Emits: findings
    per claim packet (null, effect size, gate reachability, controls,
    conclusion-vs-observation, kill geometry). Level/transition: LEVEL per
    packet. Dedup: none. Consumers: claim owners via comms; DORMANT (no
    read path). Covers, on packets, two of the retro corpus positives
    that no other surface covers (gate outside attainable range; gate
    inside its own SE).

M6  Evidence Wiki (evidence_wiki/ew/service.py). Emits: relations of
    class CONTRADICTS / REFUTES / FAILS_TO_REPLICATE (GET /contradictions,
    never auto-resolved), constraint lifecycle events with statuses
    PROPOSED / SUPPORTED / NARROWED / SUPERSEDED / REFUTED (POST
    /constraints/{id}/events), fossil anomalies (q2_anomalous_worlds:
    KL of a world's failure profile against its family marginal), and
    /telemetry. Level/transition: constraint events are TRANSITIONS;
    contradictions and anomalies are LEVELS. Dedup: idempotency_key on
    constraint events. Consumers: seats via the API. NOT MEASURED on this
    pass: the service at localhost:8377 answered HTTP 000 (connection
    refused) at 15:58 UTC from this worktree, so the count of
    contradiction relations and constraint transitions is UNKNOWN here;
    the Mnemosyne watchdog row in M2 owns that.

M7  SFE event ledger (SerendipityFoundry/.../sfe/events.py). Emits:
    per-world append-only hash-chained events with a fixed vocabulary
    (WORLD_*, WORK_*, OBSERVATION_RECORDED, FAILURE_RECORDED,
    CLAIM_FALSIFIED, ...). Level/transition: TRANSITION by construction.
    Dedup: chain position. Consumers: Vivarium, PEW fossil import,
    Archaeon tick. High volume (WORK_HEARTBEAT is an event type).

M8  Harmonia conformance gate (roles/Harmonia/contracts/
    conformance_check.py; archaeon/conformance.py). Emits: four states
    (CONFORMANT / DRIFT / UNREACHABLE / INCOMPLETE) with live build hash,
    contract hash, engine instance id, recorded on every consumer run.
    Level/transition: LEVEL per run; its history on run rows is a
    transition log. Consumers: the consumer itself (halts). Covers P11
    (a consumer on a stale build) if compared against origin/main.

M9  Archaeon tick (archaeon/deploy/archaeon_tick.log; MONITORS row).
    Emits: one JSON record per run with `decision` (NO_WRITE_CADENCE is
    the explicit no-op). Level/transition: TRANSITION-shaped, mostly
    no-ops (~96 runs/day). Consumers: Archaeon's status file.

M10 Vivarium stranded-row check (viv.cli status; 35f32116e: 119
    committed-but-unobserved experiments) and Daedalus's unattested-row
    finding (4d2804929: 13 rows). Emits: a count. Level/transition:
    LEVEL. Consumers: the seats. A count crossing 0 is the transition.

M11 engine/queues/BACKLOG.jsonl (782 rows: 644 PARKED, 138 DONE; 139
    revisions since 2026-08-18) and GATE_ELI5.jsonl (63 gate lines in
    prose + a plain-language explanation). Emits: thread status with
    gate, bottleneck, parked_reason. Level/transition: LEVEL; git history
    is the transition log. Alethelia's no_unblocked_work rule reads it.
    644 rows were generated in one batch (fleet_profiling, 2026-08-22):
    the bulk-collapse negative control.

M12 Per-seat calibration ledgers (11 files: roles/*/CALIBRATION.md,
    roles/*/calibration/*.md). Emits: one row per wrong call, appended by
    the seat that made it. Level/transition: an APPEND is a transition
    ("a seat admitted a wrong call about object X"). Dedup: none.
    Consumers: nobody, systematically. The cheapest typed surface for
    "contradiction of an accepted result" the repository has, because the
    seat itself types it.

Also present, not a signal mechanism but a route: session_telemetry
heartbeats and log_work (agora.agent_heartbeats; 35 of 36 rows stale and
labelled online on 2026-09-11 per Alethelia) -- a label table whose
meaning has expired; Pheme does not read it as evidence of anything.

## 2. What survives from the May design (primitives, not the daemon)

From agents/pheme/daemon.py (580 lines, Aporia 2026-05-23), read in full:

S1  Trend-by-band against a stored prior (aggregate_demand_profile,
    lines 279-289): trend = new / regressing / improving / stable using a
    +/-0.05 band around prior_top_patterns. This is a LEVEL-to-TRANSITION
    converter with a dead band; it is the shape Pheme needs for any
    numeric surface (a rate that moved past a band, not a rate).
    SURVIVES, generalised: band width becomes a per-surface parameter
    tied to the surface's own SE where one exists (base doctrine: a gate
    closer than its SE is not a gate).

S2  Actionability gate n >= 5 before any priority is assigned (line 292).
    SURVIVES as "eligibility count before a verdict" -- the doctrine's
    ELIGIBLE COUNT rule in code form.

S3  Sentinel vocabulary with an explicit no-op reason on every tick:
    NULL_TICK / UPSTREAM_NOT_FOUND / EVAL_DROUGHT (7-day staleness), plus
    anti_silence_counter and the 50-tick self-audit alarm (lines 64-66,
    run_tick). SURVIVES as the rule-8 productivity signal: every run
    says what it did or why it did nothing. What does NOT survive is
    re-emitting the same sentinel every 30 minutes for a week (354
    identical events, read as noise by 2026-05-24): the sentinel must be
    deduplicated against a seen-set (M4's ratchet), which May lacked.

S4  Atomic latest-pointer write (write_profile_atomic: full timestamped
    artifact + tmp-and-replace of *_latest.json). SURVIVES unchanged as
    the publication mechanic for any consumer-facing state file.

S5  Single-instance pid lock with liveness check (_is_pid_alive,
    acquire_lock). SURVIVES, but D-23 adds the canonical-checkout
    refusal in front of it (archaeon/workspace.py).

S6  Recency-over-marginals posture (charter, last paragraph: "a 30%-
    failing pattern that just spiked is more actionable than a
    10%-failing pattern that has been there for months"). SURVIVES as
    the seat's premise: Pheme reports what CHANGED since the last
    observation, never the standing marginal. This is the one sentence
    of the May charter that is already the ruling.

DOES NOT SURVIVE: the eval-root scan (input never existed); the A-E
substrate quota shift (no consumer names those types); the
target_reasoning_patterns schema (Learner-specific); the 30-minute loop
(no live monitor is proposed on this pass); operator=Ergon.

## 3. What the inventory says before any design

- Prometheus already has twelve places where "something happened" is
  written down, and eleven of them write LEVELS. Only M4 (the preflight
  ratchet) and M7 (the SFE chain) are transition-native, and only M4
  deduplicates against what is already known. The gap is not a missing
  producer; it is that nothing DIFFERENCES the level surfaces against
  their own last state and against a seen-set.
- The commit stream is not a surface: 222 commits on main on
  2026-09-11, of which 88 are named-SHA merges and 12 are receipts.
  Reading commits for signal is reading prose.
- Every mechanism above is owned by another seat. Pheme reads their
  outputs and never writes into them (base rule 6, auditor
  independence): Pheme's own state is a seen-set and an emitted-events
  ledger under roles/Pheme/, nothing else.
