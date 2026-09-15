# THE PRIMORDIAL MACHINE -- round 6: SIX-HOUR BOUNDED ROUND (DRAFT, awaiting operator go + stage ruling)

Currency: 2026-09-15 ~09:20, Nestor-A[m1-449a9e76] (conductor).

Authority: operator message 21, verbatim in prompts/2026-09-14_graphworld_swarm/21_*. The operator's notes
are "suggestions, adapt as you see fit". This file is the adopted plan.
- Round 5 rules carry over (SWARM_R5, messages 12-20) unless changed here.
- Hard cap: 6 h END TO END, from builder launch to packet delivered. Nothing extends it. At the cap,
  unfinished work becomes PRODUCTION_CANDIDATE with measured cost, or UNSCREENED; never trimmed to fit.
- Governing principle (19 s18) unchanged: finding that a larger experiment is warranted is a valid result,
  not authorization to run it.

## 0. Budget of the 6 h

| phase | wall | contents |
|---|---|---|
| R6-BUILD | <= 90 min, hard cap | hygiene wave (s3); at the cap, unfinished items -> PC, the gate decides if the round can run |
| R6-GATE + launch | <= 15 min | s4, including a smoke launch of every lane letter used |
| R6-CLOCK | 240 min, code-owned | 5 x 40 min epochs (T+0..T+200), NO_NEW_WORK T+200, drain to T+220, close T+240 |
| R6-PACKET | <= 15 min | tally from code streams, packet, one ASCII block |

The clock starts only when the gate is green. If R6-BUILD + GATE run long, the CLOCK SHRINKS (fewer
epochs, same epoch length), so the 6 h end-to-end cap holds.

## 1. Conductor review of message 21 (bias check)

| # | message 21 text | prior it carries | adopted rule |
|---|---|---|---|
| O1 | "does a related compact mechanism survive another properly screened world" | "related" lets the replicator retune until something passes | REPLICATION = the FROZEN B-R5-1 recipe (code sha, int4 linear + a4 codebook layout rule, search budget, 32/4/8 sample, top1_train, check_r4), applied to the next SURVIVED cell. No hyperparameter change. A layout the recipe cannot express -> INAPPLICABLE, not a fail and not a retune. |
| O2 | "Later you can run an equal-search-budget comparator" | none; the question is when | Search-budget accounting (evals, generations, CPU-s) is recorded for candidate and baseline from committed rows. If candidate evals > baseline evals, the equal-budget float comparator on w13 runs THIS round (rule fixed now, 32/4/8, same judge). Both interpretations are reported. |
| O3 | "occasionally sample a predicted-success cell" | "occasionally" is a judgement call | Each assignment: seeded Bernoulli(0.25) picks the calibration arm (top rank quartile), else the anti-prior arm (bottom rank quartile). Seed published before priors are sealed. R is not told the arms, and R is not tuned. |
| O4 | re-screen to find a second world (implicit) | ordering cells by round 4 gate headroom uses the RETIRED top-16 reader and 8-seed data | R16 re-screen order = a seeded permutation of the 68 unscreened cells, published before the clock. Not headroom, not cost. |
| O5 | "gate R6 on one small hygiene wave" | none | Adopted as R6-BUILD. D8 and D9 deferred as the operator says. |
| O6 | "the coordinator is becoming optional" | a claim about A should be measured, not asserted | The packet counts A's manual interventions from the bus (manual push, relaunch, restart request, ruling carried). Success condition: 0 manual pushes. |

## 2. Stage for the round (NEEDS OPERATOR RULING)

The R16 cells and the Clause B live pair exceed the PILOT job ceilings (15 min wall). Round 6 proposes
campaign_stage PRODUCTION with a round-scoped ceiling table (one table, in envelope.py):
- cpu job segment wall <= 2400 s; a checkpointable job continues in the next segment;
- cpu_budget_s per job <= 14400 (4 CPU-h);
- gpu job <= 600 s (unchanged);
- projected completion <= drain_ts;
- round CPU = the broker's k* = 2 tokens (O3 profile, not re-probed); no reservation, FIFO grants,
  per-cohort budgets from the F13 ledger.
A train128 learner whose estimate exceeds 14400 CPU-s -> cell PENDING + PC, not run.
Without the ruling, round 6 runs at PILOT ceilings and the screen and Clause B end as PCs again.

## 3. R6-BUILD: hygiene wave (each item ships with a regression test)

F (fabric), worktree nestor-bld-f:
- F-R6-1 (D3) The epoch controller never dirties the checkout it publishes from. Cause (epoch.py
  _event): epoch_log.jsonl is appended AFTER the boundary commit, including the push_failed/pushed
  events, so ops.push refuses (rc 4). Fix: events go to a log outside the repo during the boundary;
  the boundary commit includes the log up to the commit; the next boundary commits the tail. Test: a
  boundary against a local bare remote leaves `git status` clean and push rc 0, at every boundary and at
  close.
- F-R6-2 (D4) Worker code fingerprint. The job carries code_file_sha256 of its fn module at submit
  (already computed in worker.py for resume). The warm child compares it with the module it has loaded.
  On mismatch it respawns the child and records CODE_RELOADED. If the fingerprint still mismatches, it
  refuses with CODE_FINGERPRINT_MISMATCH. Test: edit the module between two jobs; job 2 runs the new code.
- F-R6-3 (D6) envelope.file_candidate(stub_id, measured_cost, basis) + open_candidates(); the close
  tally reads open stubs from code.
- F-R6-4 The PRODUCTION round-scoped ceiling table (s2), in the ONE CEILINGS table (no copies).
- F-R6-5 Gate helper: launch_lane.ps1 dry-run switch that parses and exits 0 for each lane letter in the
  round (the D1 class).

H (measurement), worktree nestor-bld-h:
- H-R6-1 (D7) Predicate code stays reachable forever: at predicate post, ops pushes
  refs/pm/pred/<predicate_id> -> the cited commit. The receipt guard refuses PREDICATE_CODE_UNREACHABLE
  unless that ref exists on origin and resolves to the cited sha (or its patch-id equals the cited one).
  Test: a rebase that orphans the branch commit still verifies via the ref.
- H-R6-2 (D10) No silent rows. Every rows file committed in the round window is cited by a guarded
  receipt, or the close sweep emits UNRECEIPTED_OBSERVATION naming it. The gate runs the sweep on a
  planted unreceipted file.
- H-R6-3 Anti-prior v2 (O3): candidates n = 48; the ledger stores absolute prior_p_pass AND rank /
  quantile among the sealed set; assign() draws by arm (calibration top quartile / anti-prior bottom
  quartile, Bernoulli 0.25). Calibration reports both. Ties in p broken by seeded order, recorded.

G (metric), worktree nestor-bld-g:
- G-R6-1 Search-budget accounting fields in Clause A rows and receipts (evals, generations, cpu_s),
  plus a reader for B-R5-1 and the w13 baseline from committed rows (O2).
- G-R6-2 R16 resume as PER-CELL jobs from R16_CHECKPOINT_2026-09-15.json, in the seeded order (O4),
  checkpointable, under the s2 ceilings. The partial worlds_r4/v2 marks unfinished cells UNSCREENED,
  never CULLED.
- G-R6-3 Replication trigger: when eligibility first reports a new SURVIVED cell, code publishes one
  pm:replication record {cell, recipe = B-R5-1 frozen, predicate template}. B reads it; A does not relay.

## 4. Launch gate

The R5 items 1-16 still hold (item 16 now names pm:round:r6), plus:
17. controller boundary against a bare remote: clean + push rc 0 (F-R6-1);
18. stale-module job reloads or refuses (F-R6-2);
19. file_candidate closes a stub (F-R6-3);
20. every round lane letter dry-launches rc 0 (F-R6-5);
21. orphaned-predicate verify via refs/pm/pred (H-R6-1);
22. planted unreceipted rows -> UNRECEIPTED_OBSERVATION (H-R6-2);
23. anti-prior v2 arms + rank stored (H-R6-3);
24. the R16 seeded order and the calibration-arm seed are committed before T+0 (G-R6-2, H-R6-3);
25. full suite rc 0 on the gate tip.

## 5. R6-CLOCK: who does what (240 min)

- G (screen, builder worker, no LLM loop needed): per-cell R16 jobs in seeded order until NO_NEW_WORK.
  Expected coverage: about a third to a half of the 68 cells. The screen will NOT finish in this round.
  That is expected, and the remainder is a PC.
- B: (1) search-budget accounting for B-R5-1 (O2); (2) the equal-budget comparator on w13 if the rule
  fires; (3) a REPLICATION of the frozen recipe on any cell the trigger publishes. No second survivor by
  NO_NEW_WORK = reported as NOT_REACHED, not a failure of B-R5-1.
- D: leave-one-family-out on B-R5-1 ITSELF, from committed rows (no new QD). Family 3303 (3/32 runs below
  floor) is filed as an anomaly record. One minimum discriminator only if leave-one-family-out drops CI low
  below 0.95 for any held-out family.
- C: 2 anti-prior v2 assignments (the arm decided by code) + 1 DISTANT_QD whose predicate must FAIL a
  planted null first (the R5 PASS was vacuous).
- R: seals priors on the 48 code-published candidates before T+10.
- E: (1) the Clause B live pair w14 -> w13, seeds 16..31, control clauseB_ctrl_v2_featperm (R5 PC
  1789471324763-0), which gives the first Clause B verdict if s2 is ruled; (2) a B2 compiled/batched rollout
  build (SMOKE), exactness oracle vs RefB2 + measured throughput -> a new B2 cost estimate, no B2 screen;
  (3) the dispatch surface backend = f(world, batch, representation, residency, hardware) as a table from
  committed GPU-1/2 + D-R5-2 rows, with no new timing. GPU-3 stays a PC.

## 6. Conductor A

A does: launch, observe, resolve deadlocks, carry operator rulings, write the packet.
A does not: push controller records (F-R6-1 makes it code), relay the replication trigger, score, count
seeds, pick cells, extend the clock, or promote.

## 7. Output

Round 5 packet structure, plus: the A manual-intervention count (O6), the R16 coverage table (screened /
UNSCREENED), search-budget accounting, the calibration table by arm, and the UNRECEIPTED_OBSERVATION list
(it should be empty).
