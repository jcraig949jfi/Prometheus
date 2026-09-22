# THE PRIMORDIAL MACHINE -- round 2: COHORTS

Currency: 2026-09-14, Nestor-A[m1-449a9e76] (conductor). Supersedes SWARM.md
for round 2; SWARM.md stays as the round 1 record.

Authority, verbatim in roles/Nestor/prompts/2026-09-14_graphworld_swarm/:
03 (thesis), 04 (success contract, epoch/TTL, budget split), 07 (cohorts,
clause A, contract-driven cells only, gate F1-F6). The contract is
roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md: agents work under it and never
edit it.

## 0. What changed from round 1

- Lanes are COHORTS. The budget split IS the identity of each session, and
  no session switches between exploiting and falsifying.
- The target is contract-driven cells in a cross-domain QD ledger, not
  CHIMERA-0, which is parked until a library of proven primitives exists.
- Contract clause A (compression) is live; clause B (transfer) opens in
  round 3 once cohort E lands its harness; clause C is not in round 2.
- The kills board is frozen. Nothing is scored by hand; a scoring program
  (backlog F12) comes later. Receipts, rows and the QD ledger are the record.
- Gate F1-F6 is in place: launcher log, heartbeat + liveness monitor, bus
  inbox/tail/tag guard, commit-on-write rows, receipt guard, and pre-built
  sparse worktrees.

## 1. Cohorts

    lane  cohort               share  cores  GPU        reads first
    ----  -------------------  -----  -----  ---------  -----------------------------------
    B     HILL CLIMBERS          40%      5  default    qd_ledger pareto / top
    C     ANTI-PRIOR             25%      3  ask B      draw_cell (the RNG picks the cell)
    D     ANOMALY HUNTERS        20%      2  ask B      bus anomaly list --status OPEN
    E     WATCHMAKERS            15%      2  ask B      bus inbox (asks for tools)
    A     conductor (logistics)   --     --  --         liveness, integration, asks

Cores are OMP_NUM_THREADS = NUMBA_NUM_THREADS per session. 12 threads in
total leave the host room for SFE and Vivarium. Bursts go through
`bus burst SECONDS NOTE`, which is recorded in every receipt's host_load.

## 2. Contract clause A: the round 2 binding

Target: the round 1 MAP-Elites baseline cells in the QD ledger
(primordial/ledger/qd/cells.jsonl, `python -m primordial.ops.qd_ledger`):
- worlds w1, w3, w4;
- pressures train8_held64 (E9, E7b) and train128_held64 (E10, E8);
- representations linear, lut_top, tt_feat, tt_digits (closed-loop brains
  + E codebook) and open-loop action tensors.

- Behaviour: the held-out median on E6's 64 held-out seeds (E7.HELD64),
  over >= 8 run seeds.
- Oracles, which must be clean: the wforge trace-hash + final-charge replay
  of recorded actions, and brain actions == reference logits on clear rows
  (E7.world_oracle / brain_oracle, or an equivalent that names its cheat).
  Cheat controls skip_lin and stride-2 must fail.
- Footprint: bytes of the packed genome, codebook included (G7.glen for
  C4 families). A new representation reports the bytes its decoder needs
  with no access to the target (C3 rule).
- PASS (`qd_ledger check`), on the same world and pressure:
  - parity (median >= baseline median - 0.5 x baseline IQR) at fewer
    bytes than that baseline; or
  - median > baseline median + 0.5 x IQR at <= its bytes.
  A claim across several worlds applies Holm across them.
- EVERY evaluated candidate is a ledger row with a status (record, dev,
  aborted, timeout, cheat, control), not only winners. The landscape is the
  product.

## 3. Cohort charters

### B -- HILL CLIMBERS (40%, exploitation)
- Start from `qd_ledger pareto --world wN` and `top`. Take the best cells
  and mutate them toward fewer bytes at parity, or more held-out at equal
  bytes: quantize, prune, share or shrink codebooks, lower rank, change
  genome packing, or port the cell to another world or pressure. Any
  domain.
- Must: oracles + cheats, >= 8 run seeds, RowWriter rows for every
  candidate, `qd_ledger check` before any PASS claim.
- Must not: build cells with no baseline (that is C's and D's ground), or
  edit shared library code (section 4).

### C -- ANTI-PRIOR (25%, falsification)
- Every experiment starts with `python -m primordial.ops.draw_cell`. You
  build and run THE DRAWN CELL. You may not choose, veto or redraw a cell by
  expected fitness. An infeasible combination is recorded as an `aborted`
  row with its reason, and then you draw again.
- Before each run, post a predicate plus the consensus prior: your own
  probability that it "works". The prior is never scored; it feeds the
  prior-vs-reality ledger.
- Forbidden: chasing high fitness, tuning a drawn cell beyond making it run
  honestly, and dropping failures.
- Output: landscape rows at every status, predicates resolved against your
  posted prior, and `bus anomaly add ...` whenever reality contradicts that
  prior.

### D -- ANOMALY HUNTERS (20%, serendipity)
- Work ONLY from `python -m primordial.bus anomaly list --status OPEN`
  (seeded with round 1's open anomalies). Claim `ANOM-<id>` before working.
  Build the anomaly's minimum discriminator, or a cheaper one that splits
  the same hypotheses.
- Close with `bus anomaly resolve ID RESOLVED|REFUTED|INDETERMINATE NOTE
  --exp EXP_ID`. A resolved "why" matters only if it survives the next
  generation or exposes being fooled.
- May add a child anomaly found while resolving. May not start work that
  has no anomaly id.

### E -- WATCHMAKERS (15%, tooling and instrumentation)
- Explicitly forbidden from primary cognitive tasks: no clause A cells, no
  anomaly resolutions.
- Round 2 mandate, in order:
  - E-T1 Domain A -> B transfer harness: graft a genome or topology evolved
    in world A into world B without modification; measure the acceleration
    of learning or inference against from-scratch at equal budget. Cheat: a
    grafted random genome of the same shape must not accelerate.
  - E-T2 A basic Transformer baseline behind the same genome/rollout
    interface: parameter count and bytes reported, oracles clean.
  - E-T3 Evaluation helpers and discriminators asked for by B, C or D
    (`post ask ... --to E`), plus maintenance of the shared library on
    request.
- When E-T1 and E-T2 are committed with tests, the conductor opens clause B
  for round 3.

## 4. The rules (round 2 physics)

1. Boot: the conductor pre-builds each worktree (nestor-r2-<l>, sparse,
   warmed, verified). The operator launches each session through
   primordial/ops/launch_lane.ps1, one at a time. `bus hello` within 10 min.
2. Liveness: the harness watches pid, transcript activity and heartbeat
   (ops/liveness.py). Every bus call refreshes your heartbeat; run
   `bus beat STATUS` at every loop step.
3. Task TTL (operator: 5-10 min): every experiment command runs under
   `timeout 600`. Work longer than that is a checkpointed job that writes
   rows as it goes, declared in its hypothesis and charged to your share. A
   task killed by its TTL leaves rows with status `timeout`.
4. Rows: RowWriter for every evaluated thing (primordial.fabric.rows), which
   commits on write. Clause A candidates ALSO append to the QD ledger.
   Nothing is filtered before commit.
5. Hypotheses: one line plus a predicate
   `{metric, cells, comparator, threshold, seeds, ttl_cpu_s, prior}` posted
   on the bus BEFORE the run.
6. Receipts: push the rows first, then file. The receipt guard refuses a
   SHA that is not on the integration branch, or rows absent at it. Cheat
   controls stay mandatory: they are how we notice being fooled. The "why"
   is optional.
7. Code ownership: primordial/{core,bus,fabric,ops,soup,brain,lingua,qd} is
   a shared library, changed only by E (on request) or the conductor. A
   cohort's new code, including copy-on-write variants of library code,
   lives in primordial/cohorts/<b|c|d|e>/. Rows go to
   primordial/ledger/rows/<L>/; the journal to journal/<L>.md.
8. Comms: `bus inbox` every iteration (full bodies for anything addressed to
   you); address with `--to`; observers use `bus tail`.
9. Epochs (operator: 30 min): until the epoch controller (F14) exists, every
   30 min of wall clock you close an epoch:
   - push rows;
   - post `EPOCH n: rows=K receipts=J open_claims=...`;
   - re-read inbox, QD ledger and anomaly queue.
   Test launch 1 = 2 epochs; then the conductor quiesces and reviews.
10. The hot path carries no str, JSON or English. Production seats (SFE,
    Vivarium, PEW, wforge) are read-only.
11. Git: branch nestor/r2-<l>-<date>; integrate by
    `git fetch; git rebase origin/nestor/sidequest-graphworld-2026-09-14;
    push HEAD:` that branch. Never force.

## 5. Conductor A (logistics only)

- Owns liveness (`python -m primordial.ops.liveness --watch 60 --post
  --export-every-min 10`), integration, resource scheduling, asks, missing
  receipts, and backlog F7-F15.
- Does not own scoring, closing another cohort's branch, judging whether a
  weird line is worthwhile, or the success criteria.
