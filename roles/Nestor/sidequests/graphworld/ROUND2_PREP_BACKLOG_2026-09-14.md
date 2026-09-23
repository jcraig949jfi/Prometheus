# Round 2 prep backlog (graphworld swarm)

Currency: 2026-09-14 ~14:10, Nestor-A[m1-449a9e76]. Authority: operator
messages 03-06 in roles/Nestor/prompts/2026-09-14_graphworld_swarm/
(verbatim). Inputs: REVIEW_PACKET_ROUND1_2026-09-14.txt (suggestions
S/C/L/X), ROUND2_DESIGN_INPUTS_2026-09-14.md (R1-R8, T1-T6),
primordial/fabric/perf/PROFILE_ROUND1_2026-09-14.md (items 1-6),
roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md.

Rule for this file: every item closes with a commit and, where it applies,
a test or measurement. An item with no row, test or measurement is not
done.

## Phase 0: landed (operator authorization 06)

- P0.1 Redis clients on 127.0.0.1: 18 call sites across 16 lane D/E files;
  connect 10.0 s -> 15 ms. Test suite 39.8 s -> 25.1 s (97 passed).
- P0.2 `cache=True` on every static njit kernel (B6 fused, B6 probes, C
  row kernels). B6 first call in a fresh process 6.21 s -> 0.32 s, fitness
  identical (517,984). Runtime dual-flag kernels (genomes._kernel,
  tt_policy._nb) deliberately uncached.
- P0.3 `python -m primordial.ops.warmup`: compiles and caches the fused
  kernel per worktree.
- P0.4 primordial/tests/test_fabric_hygiene.py guards P0.1 and P0.2.

## Phase 1: stability and comms (lane A; gate: in place BEFORE lanes boot)

- F1 Launcher wrapper (S1): starts each lane session and logs start time,
  session id, exit code and end time to pm-data/launcher/. Owns the
  process tree, so a reap is possible.
- F2 Heartbeat (S2, T4): every bus call refreshes pm:alive:<L>:<tag>
  (TTL 180 s); a conductor monitor posts MISSING <L> on expiry. The
  operator default is a 2 min pulse.
- F3 Bus comms (C1, C2): structured to/cc fields; `bus inbox` with FULL
  bodies for messages addressed to the reader; read-only `bus tail`
  (XRANGE, no ack); PM_LANE must match a registered tag.
- F4 Commit-on-write rows helper (S5): rows are appended and committed by
  the writer, so a TTL death strands nothing. Bus auto-export to JSONL
  every N min (C4).
- F5 Receipt guards (L1, L2): the git SHA must be an ancestor of the pushed
  integration tip, and the rows must exist at that SHA; host load (CPU,
  GPU, live bursts) is captured automatically.
- F6 Pre-built sparse worktrees (S4): the conductor creates lane worktrees
  one at a time (sparse: primordial/, roles/Nestor/), runs the warm-up in
  each, and only then are prompts pasted.

## Phase 2: fast iteration fabric (lane A)

- F7 Warm worker per lane (profile item 3): a long-lived process holding
  kernels, a Redis pool and in-memory world caches. Job specs arrive on a
  Redis Stream and rows return on another stream. The task TTL kills the
  job, never the session (T1). An overrun sets status TIMEOUT and commits
  partial rows (R6).
- F8 Seed/world table cache (profile item 4): per-env stream states and
  init registers as packed arrays keyed by (world id, seed), shared across
  processes. Target: the 0.37 s FusedRollout construction.
- F9 Checkpointed long jobs (T2): a job longer than one epoch emits
  partial rows each epoch and resumes, charged to a declared budget share.

## Phase 3: measurement above the swarm (lane A code; the operator owns the rules)

- F10 Predicate hypotheses (R1): schema {metric, cells, comparator,
  threshold, seeds, ttl_cpu_s}, frozen on the bus before the run and
  resolved by code from rows. Yields the prior-vs-reality ledger.
- F11 Landscape retention (R5): every evaluated genome, cell, config and
  seed is kept as rows with a status tag (dev / record / aborted / timeout
  / cheat).
- F12 Scorer as a program (R2, R7): progress axes computed from rows only;
  own-hypothesis KILLs unscored; the promotion ladder as row predicates;
  correction lineage credited. The kill board and manual ZINCRBY retire.
- F13 Budget enforcement (operator split 40/25/20/15): the anti-prior share
  is drawn by RNG from the descriptor grid (R4), the anomaly share comes
  from an ANOMALY queue, and the tooling share is barred from primary
  tasks.
- F14 Epoch controller: 30 min generations. At 30:00, halt jobs, sync the
  streams, export the ledgers, then launch the next generation from the
  landscape.
- F15 Boot pack generator: one compact state file per lane per epoch,
  replacing ~70k tokens of doc reading (a fresh context each epoch).

## Science backlog carried from round 1 (lanes; enters round 2 when chosen)

- X4 oracle state-diff check and wforge free-action packet to its owner
- X6 per-episode randomized worlds for closed-loop claims
- X7 branch points (E2b) on B's real Encounter
- X8 lane D first: prospective test of D1b's 1enc+1dec operator; code
  transfer across worlds
- X9 CHIMERA-0 end-to-end receipt with a comm-ablated control
- X10 a non-Claude or scripted re-derivation of sampled receipts
- X11 hand-backs: A3 -> Daedalus, wforge packet, axes -> Theophrastus

## Open decisions for the operator

- D1 Lanes vs cohorts: round 1 had domain lanes (B soup, C brain, D
  lingua, E selection); the budget split names cohorts (exploit, anti-prior,
  anomaly, tooling). Either domain lanes each spend the split internally,
  or four sessions are cohorts working across the domains.
- D2 Contract bindings per round: "benchmark X" and baseline (A), the
  Domain A -> B graft pairs (B), the control task and baseline (C).
- D3 Round 2 target: CHIMERA-0 (X9), or contract-driven cells only.
- D4 Which Phase 1-3 items gate the first round 2 launch. Recommended:
  F1-F6 gate; F7-F15 land iteratively during the early test launches.
