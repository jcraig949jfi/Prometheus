# THE PRIMORDIAL MACHINE -- round 5: BOUNDED PILOT

Currency: 2026-09-15 ~06:10, Nestor-A[m1-449a9e76] (conductor).

Authority: operator message 19, verbatim in prompts/2026-09-14_graphworld_swarm/19_*. The operator
called it "suggestions" and gave the conductor final say, with an instruction to check it for smuggled
human bias. This file is the adopted plan.
- Everything in message 19 applies unless s1 overrides it.
- SWARM_R4 rules carry over where not changed.
- Operator messages 12-18 stand: world screen, one reader top1_train, runs_total 32 / rng_family_count
  4 / runs_per_family 8 for baselines, smoke-before-scale (17, 18).

Governing principle (19 s18): finding that a larger experiment is warranted is a valid result. It is
not authorization to run it. Code owns clocks, budgets, leases, sampling counts, admission,
checkpoints, eligibility, receipt integrity and quiescence. LLMs loop, propose, mutate, attack,
interpret and follow anomalies.

## 1. Conductor overrides of message 19 (bias review)

Each override replaces a choice a human or LLM prior would make with a rule fixed in code before data.

| # | message 19 text | why it carries a prior | override |
|---|---|---|---|
| O1 | "The existing w2 -> w4 candidate may be used" (s9) | A named pair recalled from a report-only look at 3 pairs: a winner picked after seeing data. w4 has no screened survivor (abstain beats its baselines), so "accelerates learning" there is uninterpretable. | The Clause B recipient must be a SURVIVED cell (w13 train128_held64). Donors come by a code rule fixed before the run: screened worlds with identical genome layout (D, A, W, bytes) to the recipient, listed from worlds_r4.json. The ONE candidate is the first donor in gen_seed order. Any pair previously seen (E-R4-1: w14, w20 into w13) runs only on run seeds disjoint from those used before. |
| O2 | B2 "has evidence of consequential observations... forager beat the blind policy" (s7) | The forager is a hand-written policy on an objective E authored, so it shows the ADAPTER is controllable, not that B2 is a hard world. | B2 admission uses only the standard trivial-policy suite + the learned float linear baseline under top1_train. Verdict rule fixed in code (s6.4). The forager result is reported as instrument evidence only. |
| O3 | "Choose the highest concurrency whose aggregate throughput materially improves" (s5) | "Materially" is a judgement call. | Rule: k* = the largest k in {1, 2, 3, 4, 6, 8} such that for every j <= k, throughput(j) >= 1.15 x throughput(j-1) AND p95 per-job wall(j) <= 1.5 x p95(1), AND no job errors. Threads per worker = floor(16 / k), capped at 8. The workload is a real pilot-sized M2 baseline run seed (not synthetic), so contention is measured on the code that will run. |
| O4 | "candidate seed count is still an open design question... post the candidate sampling rule before running" (s8) | B (hill climbers, incentive to pass) would choose its own bar. | Rule, symmetric with baselines: a Clause A candidate is ELIGIBLE for a verdict only with runs_total >= 32, rng_family_count >= 4, runs_per_family >= 8 (new judge refusal CANDIDATE_N). Fewer runs = PILOT label, the real judge refuses, no PASS possible. No agent chooses this. |
| O5 | "a predictor posts P(PASS)... a subset is assigned for attempted falsification" (s10-11) | If the experimenter sees the prior, it can fulfil the prediction (sandbagging or effort bias). | Predictor = a separate session (not C). Priors are written to a sealed ledger key the experimenter cannot read until its receipt is filed. Assignment is by code: among predictions with prior_p_pass <= 0.2, draw by seeded RNG. The experimenter gets only the cell. |
| O6 | Clause B "properly powered, properly controlled pilot" inside "<= 20 CPU-minutes" (s1, s9) | Both cannot hold. E-R4-1 (16 run seeds) took ~70 min of worker time. Implying a pilot can PASS invites under-powered claims. | Round 5 Clause B = validate the hardened sham + measure cost + power estimate. A verdict is emitted only if the real judge's sample rule is met inside the stage budget (not expected). Otherwise the outcome is PRODUCTION_CANDIDATE with measured cost. Not forced, not extended. |
| O7 | Epoch shape "pick one" (s4.1) | none | Frozen: 4 working epochs x 25 min (T+0..T+100), then NO_NEW_WORK, drain to T+110, close at T+120. |
| O8 | Progress axes error_metabolism etc. (s12) | Credit for "corrected erroneous claim" could reward the originator of the error. | error_metabolism is credited to the lane that FILED the refutation, never to the claim's originator. Own-claim refutations score 0 (already in F12). |
| O9 | "Test representative independent CPU jobs under 1..4 workers" (s5) | Stopping at 4 on a 16-thread host assumes the answer. | The probe also tests 6 and 8 workers (O3 grid) and stops early on the first failed step. |

Not overridden (no prior injected; adopted verbatim):
- stage-gated admission;
- explicit seed fields;
- one judge;
- F14/F7/liveness/receipts/requeue/NO_NEW_WORK in code;
- the GPU queue with its 600 s cap and GPU-1..3 questions;
- the B2 verdict names;
- DISTANT_QD naming;
- cohort shares 35/25/25/15;
- the success condition;
- the "what not to do" list.

## 2. Round 5 has two phases, each bounded

- PHASE P-BUILD (builders, before the clock). Stage SMOKE for the build itself.
  - Hard cap 2 h wall from builder hello.
  - If the launch gate is not green at the cap, A cuts scope (drops the least-critical gate items to
    PRODUCTION_CANDIDATE) rather than extending. The operator is told.
- PHASE P-PILOT (cohorts): the 120 min clock of message 19 s0. It starts only when the launch gate is
  green.

## 3. P-BUILD assignments (code; each item ships with a regression test)

F (fabric), worktree nestor-bld-f:
- F-R5-1 JOB ENVELOPE + STAGE ADMISSION.
  - Mandatory fields: campaign_stage, wall_budget_s, cpu_budget_s, gpu_budget_s,
    expected_output_rows, checkpointable, required_controls, required_oracles, cohort, predicate_id,
    experiment_class.
  - Stage ceilings in one table (PILOT: cpu job wall <= 900 s; gpu <= 600 s; cpu_budget_s <= 1200;
    projected completion <= round end).
  - Over-ceiling -> STAGE_BUDGET_REFUSAL event on the bus + a PRODUCTION_CANDIDATE stub; never an
    exception.
- F-R5-2 ROUND CLOCK: pm:round:r5 {start_ts, epochs 4x1500 s, no_new_work_ts = +6000, drain_ts =
  +6600, end_ts = +7200}.
  - The worker refuses new jobs after no_new_work_ts (event NO_NEW_WORK_REFUSAL).
  - F14 runs the 4 epochs and the drain automatically; A never announces boundaries.
- F-R5-3 RESUMABLE JOB OBJECT on checkpoint/interrupt: job_key, function, kwargs, checkpoint, rows,
  completed_units, remaining_units, budget_consumed, budget_remaining, code_sha (on pm:resumable).
- F-R5-4 LIVENESS STATES ACTIVE / BUSY_COMPUTE / IDLE / DRAINING / STALE / DEAD, from worker state +
  heartbeat + transcript; the monitor pages A only on STALE or DEAD of a lane holding a job.
- F-R5-5 CPU CAPACITY PROBE + BROKER.
  - The probe per O3, output NODE_CAPACITY_PROFILE_R5 (rows + a JSON profile).
  - The broker grants CPU tokens (k* workers x threads) to any cohort's queued job, while the budget
    ledger stays per cohort (F13 shares).
- F-R5-6 DRAIN_TIMEOUT sized to the job TTL; the epoch controller runs outside the conductor worktree
  (defects F7, F8 in SMOKE_TEST_FINDINGS).

G (metric), worktree nestor-bld-g:
- G-R5-1 SEED SCHEMA: runs_total, rng_family_count, runs_per_family in every new row, summary,
  receipt and worlds file stamp.
  - Invariant runs_total == rng_family_count * runs_per_family where families are equal.
  - A lint test fails the suite if a new receipt or table prints "N x M" for a run count.
- G-R5-2 CANDIDATE_N (O4) in qd_ledger check: the same three-field rule as BASELINE_N for Clause A
  candidates. Tests include the PILOT-sized refusal.
- G-R5-3 B2 ADMISSION RULE (O2), fixed in code before any B2 run:
  - pilot sample runs_total 16, rng_family_count 2, runs_per_family 8, on the B2 specs E's adapter
    exposes (<= 4 specs x 1 pressure);
  - floor suite + learned baseline under top1_train;
  - B2_SCREEN_INSTRUMENT_FAIL if any oracle fails;
  - B2_SCREEN_WORTHY if pilot baseline CI low > floor on >= 1 spec;
  - B2_SCREEN_UNPROMISING if CI high < floor on every spec;
  - else B2_SCREEN_INDETERMINATE.
  - Never SURVIVED.
  - Also a cost estimate for the full B2 screen.
- G-R5-4 w13 ELIGIBILITY LOOKUP: a code function returning w13 train128_held64 eligibility from G's
  R16 rows (checkpoint 1268ead0c) without a partial v2 file. check() must be able to judge a candidate
  on w13 alone.

H (measurement), worktree nestor-bld-h:
- H-R5-1 AUTOMATIC RECEIPT GUARD: all nine checks of 19 s4.4 (+ campaign_stage, + CANDIDATE_N /
  BASELINE_N sample rule).
  - A failure -> receipt refused with a machine-readable reason.
- H-R5-2 ANTI-PRIOR LEDGER (O5): sealed prior store (predictor-only write; experimenter read denied
  until its receipt is filed) with prior_p_pass, prior_expected_direction, prior_expected_mechanism,
  predictor_id, prediction_ts.
  - Code assignment by seeded draw among p <= 0.2.
  - Close-of-round calibration table (descriptive).
- H-R5-3 F12 PROGRESS AXES by rule from receipt type + lineage: boundary_resolution, instrument_gain,
  error_metabolism (O8).
- H-R5-4 EXPECTED_REFUSAL_OBSERVED classifier: a campaign-controller label when a deliberately
  under-sampled job gets the real judge's refusal. It does not touch the judge.

E (watchmakers), worktree nestor-r4-e:
- E-R5-1 HARDENED CLAUSE B CONTROL.
  - Preregister the sham appropriate to the linear genome: a structure-preserving displaced graft
    (the donor's weight matrix with the observation-feature axis permuted by a seeded permutation, so
    norms, sparsity and decoder are kept but feature mapping is destroyed) + equal-budget scratch.
  - Paired run seeds.
  - check-b requires beating BOTH.
  - Validate on a planted positive (self graft) and a planted negative (random donor) before any live
    pair.
- E-R5-2 GPU QUEUE + ARBITER: queue pm:gpu:jobs, max_gpu_wall_s 600, the lease held for every timing
  row, the recorded fields of 19 s6, timeout -> checkpoint + PRODUCTION_CANDIDATE.
- E-R5-3 GPU HARNESS WIRING for GPU-1..3 using the W (Warp), U (CUDA graphs) and P (precision) MVP
  code. Exactness oracle first. Numba at 1/2/4/8 threads. Transfer cost included unless resident.

## 4. Launch gate (19 s13, plus the override tests)

All green, each as a test or receipt:
1. stage-budget refusal;
2. seed-schema invariant + lint;
3. judge unchanged under PILOT (same verdicts on the planted set with campaign_stage in {SMOKE, PILOT,
   PRODUCTION});
4. EXPECTED_REFUSAL_OBSERVED;
5. NODE_CAPACITY_PROFILE_R5 written (O3 rule);
6. GPU lease/timeout;
7. NO_NEW_WORK refusal;
8. checkpoint -> resumable object -> resume reproduces rows;
9. receipt guard refuses each of its failure cases;
10. w13 eligibility lookup;
11. B2 adapter smoke;
12. transfer sham version id + planted positive/negative;
13. CANDIDATE_N;
14. sealed prior ledger read-denied to the experimenter;
15. full suite rc 0 on the gate tip;
16. at T+0, before any cohort launch, code asserts that pm:round:current exists and points at a pm:round:r5
    hash whose [start_ts, end_ts] contains now.
    The receipt guard triggers on the round clock, so an unset clock would let field-less receipts skip it
    (H e3412c04b; A 1789467821844-0).

## 5. P-PILOT (the 120 min clock), cohorts and GPU

Cohorts are fresh sessions on nestor-r5-{b,c,d,e} worktrees, launched one at a time. Budget shares
are 35/25/25/15; physical CPU comes from the broker.
- B (35%): one w13 train128 Clause A attempt. Its PILOT-sized results are labelled PILOT;
  CANDIDATE_N-eligible ones get a verdict.
- C (25%): one DISTANT_QD draw (draw_cell) and one ANTI_PRIOR assignment (code-drawn per O5).
- P (predictor, a separate light session or H's tool): posts sealed priors for the candidate cell list
  before T+10.
- D (25%): the anomaly queue only. Priority: candidate seed-count instability, sham control children,
  B2 discrepancies, GPU crossover reversals. Minimum discriminators within stage ceilings.
- E (15%): E-R5-1 live pair (O1 donor rule, disjoint seeds) under O6; tooling fixes found in the run.
- GPU worker (E-R5-2 queue): GPU-1, then GPU-2, then GPU-3 if time remains; each <= 600 s.
- B2 admission (G-R5-3 rule) runs as a queued job when broker capacity allows, T+50..T+75.

Frozen clock: epochs T+0-25, 25-50, 50-75, 75-100; NO_NEW_WORK at T+100; drain to T+110; close at
T+120. No exceptions.

## 6. Conductor A in round 5

A does: launch, observe machine state, resolve dependency deadlocks, integrate, report stage
violations, write the close packet (19 s16).

A does not: score, count seeds, watch job clocks, announce epochs, clear compute above the stage
ceilings, promote claims, or turn PILOT into PRODUCTION.

## 7. Output

The external review packet per 19 s16 (Operations / Science split as OBSERVATION, ELIGIBILITY,
VERDICT, INTERPRETATION / Instrumentation with FIXED_WITH_REGRESSION, OPEN, PRODUCTION_BLOCKER,
NONBLOCKING / Production candidates / Epistemic state), plus an s1 override audit: did each override
change an outcome.
