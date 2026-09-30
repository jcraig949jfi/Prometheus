# T-SWAP-REL4 PLAN (frozen by commit before any REL4 simulation)

Thread thr-5df816e9b844 (T-SWAP-LOWACC line), experiment E-ANANKE-W-W (to be
run by a delegated worker, who must NOT edit this file; it may only append a
PLAN_ADDENDUM.md in its own directory, labelled post-freeze). Authority:
CWO 2026-09-30 (ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md, ANANKE: CURRENT
= this plan, NEXT = REL4 when the rolling window admits it, RESERVE = analyze
before expanding). MWO-0004 R2: this item is capped at 8 CPU core-hours.
Freeze rule (Harmonia audit G1 / proposed F6): this file's first commit must
predate the first REL4 result commit; checkable with
`git log --diff-filter=A -- roles/Ananke/research/plans/T-SWAP-REL4_PLAN.md`.

## 1 Question
REL3 (W-U, workers/W-U/swap_rel3.py) uses a studentized pair bootstrap
(BOOTT, B=2000) for the relative carrier-swap certificates on
DF=(s-.5)+(a-.5)/2 and DN=(s-.5)-(a-.5)/2, with floor P>=32. It holds the 1%
false-certificate (FC) target at P>=32 but its POWER collapses when normal
accuracy a is near 1: near-constant pairs make many resamples have sd*=0,
t*=+-inf, and no certificate is issued (FLIP power .23 at P32 K11, p=.99;
p_min 1.0 for FLIP/NO_EFFECT at P32-P64). Can a hybrid keep FC <= 1% at every
design point AND restore power near a ~ 1?

## 2 Candidates (all two-sided 99%, same seed-0 resample counts as W-U)
- H0 = REL3 BOOTT unchanged (reference; must reproduce W-U's tables).
- H1 = BOOTT with degenerate-resample fallback: if the share of resamples with
  sd*_b = 0 exceeds 5%, use the t-interval on pair means (df P-1) for that
  statistic; else BOOTT.
- H2 = BOOTT with a variance floor: sd*_b := max(sd*_b, sd_floor), where
  sd_floor = sqrt(1/(4*K)) / sqrt(P) * 0.5 (a fixed binomial-scale floor for a
  pair statistic built from K scored trials per pair; set from design, not data).
- H3 = BOOTT on add-one smoothed pair statistics (one pseudo-pair at the
  statistic's null value, 0, appended before resampling).
- Must-fail controls: T90 (t-interval at 90%) must FAIL the FC target; PCT
  (percentile) must FAIL at P32 (both as in W-U).

## 3 Grid and simulation (reuse workers/W-U/fc_sim.py models via import)
- Designs P in {32, 64, 128, 256} x K in {3, 11, 12}; models worst, realistic,
  hetero; normal p in W-Q's 12 values .50-.99; boundary truths z = +-1/2
  (z = 0 at p = .50). P8/P16 excluded (REL3 floor stands; not re-opened).
- FC: n = 20,000 per point, +60,000 where any candidate lies in (0.8%, 1.2%].
  Pass iff pooled FC <= 1.00% for every verdict at every point; "robust" iff
  the Wilson 99% upper bound <= 1% too.
- Power: exact truths z = -1 (FLIP), z = +1 (NO_EFFECT), z = 0 (CHANCE) at
  p in {.60, .70, .80, .90, .95, .99}, P in {32, 64}, K in {3, 11}, worst and
  realistic, n = 2000.

## 4 Decision rule (frozen)
1. Eligible = candidates passing FC at every design point (not only robustly).
2. Among eligible, choose max over candidates of min(FLIP power, NO_EFFECT
   power) at p in {.95, .99}, P=64, K=11, realistic model.
3. Promotable iff the chosen candidate's FLIP and NO_EFFECT power at p=.99,
   P=64, K=11 is >= .80 (REL3: .72 FLIP) AND it recovers W-U's KA1/KA2/KA3
   known answers with 0 false certificates. Ties -> simplest (H1 < H2 < H3).
4. If no hybrid is eligible, or none is promotable: REL3 stays, with a
   documented blind spot (report FLIP/NO_EFFECT as NOT_ELIGIBLE when
   lo99(normal) >= .95 and P < 128), and the line is PARKED for promotion
   work. Do not scale the grid or add candidates in this item.

## 5 Expected discriminators
- H1 vs H0: identical wherever resamples are non-degenerate, so any FC change
  isolates the fallback region (a near 1). Risk: the t-interval's known
  undercoverage (W-U: TINT fails at P<=64 K3) re-enters exactly there.
- H2: shrinks t* in low-variance resamples; risk of anti-conservatism if the
  floor is too small, loss of power if too large (fixed a priori above).
- H3: pulls the statistic toward 0 by 1/(P+1); conservative by construction;
  expected to cost power at P32 more than at P256.

## 6 Controls and known answers
- Reproduce H0 = W-U max-FC table within simulation error (else harness bug:
  stop and report).
- T90 and PCT must fail as stated (else the grid is not discriminating).
- Engine-plant known answers: W-Q rep-1 arrays (workers/W-Q/out/plants_r1_*.npz)
  and W-U's KA2 disjoint-block splits: 0 false certificates required.

## 7 Failure interpretations
- H0 does not reproduce W-U: harness defect; no conclusion about hybrids.
- All hybrids fail FC near a ~ 1: power loss there is intrinsic to the
  pair-bootstrap on near-deterministic pairs at P<=64; the fix is more pairs,
  not a better interval (record; do not pursue further intervals).
- A hybrid passes FC but not the power bar: record as partial improvement;
  REL3 stays; no promotion.

## 8 Resources
<= 8 CPU core-hours (MWO-0004 R2 item cap; seat rolling 24 h <= 48), Fabric
lease skullport:cpu8 (or run <= 2 threads without a lease if it stays busy),
no GPU, outputs <= 3 MB.
