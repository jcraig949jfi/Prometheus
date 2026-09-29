# WTP-LM01 adversarial design review (pre-data)

Reviewer: independent adversarial reviewer (subagent), 2026-09-28.
Target: D:\Prometheus-worktrees\ensorain-base-role, PREREG_WTP_LM01.md v0.3.1 and the frozen code under ensorain/lm01/.
Scope: the design only. No campaign seed was used, launch.py was not run, and no repo file was modified. Probes used
dev seeds 9_700_001..9_700_022 (single process, about 7.5 CPU-minutes). The power estimates below come from the
committed DEV rows (dev/margins/, dev/margins_f5real/, 16 worlds per stratum), recomputed with the frozen ci().
Probe scripts are next to this file (devpow.py, devpow2.py, p_budget.py, p_meter.py, p_init.py, p_recency.py).

Severity scale:
- S1: would change or pre-determine a verdict label, or make a reading impossible to fire in one direction.
- S2: weakens interpretation or replication; a label could fire for a reason other than the one named.
- S3: bookkeeping or prose/code mismatch with little effect on labels.

## Summary of the top findings

1. (S1) The headline cannot fire toward LOSSLESS in practice, and its "sufficiency" side is mostly floor
   equivalence. In 29 of the 38 headline strata the headline pair itself (L-R and the reservoir) is not learnable at
   DELTA. In the other 9, dev L-R minus the 2c rung has a CI lower bound of 0.01 or less. Expected headline output:
   UNRESOLVED almost everywhere, with B* "reported" at the floor.
2. (S1) The 6.2 secondary is dead by accounting. The "<= reads" filter rules out every SELECTIVE ladder point in 33 of
   the 38 non-F1 strata. In the other 5, only cap = 32 floats (a rank-1 CP) is eligible. Measured example: S-cp at
   cap 128 used 1.6% of L-R's bytes and scored AC 0.59 against L-R's 0.08, but it is ineligible on reads.
3. (S1) The eviction candidate keep_worst works as a recency buffer (median stream position of its buffer is 0.95,
   against 0.52 for random). The reference is recency-blind. In F3 (and F4/F5 where keep_worst is frozen), a support
   label (SELECTIVE_BUYS_BYTES / RESERVOIR_SELECTIVE_ADVANTAGE) or an F-C firing measures recency against no recency,
   not relevance selection. The code lets these fire in strata whose E6 control FAILS, which contradicts prose s7.
4. (S1) F-C@c INDISCRIMINATE_EQUIVALENT can fire where no policy has room to beat random. In F5-L3 pairwise and sum
   (E6 PASS), dev headroom (full minus random@c) is 0.24 and 0.16, both below DELTA.
5. (S2) The headline's "lossless" endpoint is a fixed rank-3 contraction. The readout capacity does not grow with
   retained data. The headline is therefore a learning curve of a fixed-capacity estimator and cannot separate
   "bounded state suffices" from "the readout saturates".

The numbered findings follow. The design strengths are listed at the end.

---

## A. Differences between arms other than retained memory (question 1)

### F1. L-R endpoint vs reservoir rungs (headline 6.1): differences beyond B
Claim: the headline is described as "same-optimizer", but the two sides still differ in several ways that are not B.
Evidence:
- Initialization is identical: both use np.random.default_rng(0) and N(0, .3) factors of the same shapes
  (arms.py:111-112 via LosslessR seed=0, and arms.py:411-413 via BufferALS seed=0). This is good.
- Fit path. L-R does ONE cold ALS fit at query time (arms.py:162-166). The reservoir does warm-started ALS refits all
  through the life: 28 / 64 / 112 refits at L1 / L2 / L3 (_feed batches of 50 plus the >= 64 threshold give an
  effective cadence of 100 admissions, margins.py:41-45 and arms.py:456-459). Probe p_meter.py on F3-L1: full
  reservoir used 7.35M ops over 28 refits, L-R used 0.34M ops over 1 fit (15 iterations). The warm path is a
  different optimizer trajectory: continuation from the previous optimum, with far more total iterations. The dev
  END column (warm full minus L-R) reaches +0.28 (F2-L3-cp) and -0.22 (F5-L3-cp). Those gaps are optimization, not
  memory.
- Stale-factor carry-over. Rows whose records were all evicted keep their last fitted values, because ALS only
  updates rows present in the buffer (arms.py:471-477). A rung-B arm is therefore online ALS with a B-record window
  plus a persistent summary of evicted data, not "B records of information". Probe p_init.py: at c/8 on F2-L3, only
  217-230 of 256 V rows are in the final buffer, yet 0.00-0.01 of test cells sit on a row that was never fitted.
  My first hypothesis was that unfitted random-init rows penalise small rungs. It is REFUTED: zeroing never-touched
  rows changed AC by 0.00 in all 12 probe runs.
- Unfitted tail. Records admitted after the last refit are in the buffer but not in the factors. L-R uses them. By
  construction (no fitting needed) the tail is 20 of the 420 scored fresh-field records at F4-L1 (4.8%), 30 of 1680
  at F4-L3, and 33 of each F3 final episode. The bias runs against the reservoir, on exactly the scored segment.
- Recency: neither uses it (declared). The frozen SECONDARY LOSSLESS is usually L-R-rec in F3/F4 (FROZEN_SELECTION),
  so "LOSSLESS" means different arms in 6.1 and 6.2.
Severity: S2. The endpoint comparison (a) vs (b) and B* depend on path and compute as well as B.
Resolve: (i) refit the reservoir once more at end of life (or at query time) so the tail is included. (ii) Add a
cold-refit-at-query rung: fit L-R's exact procedure on the rung's final buffer. Then "L-R minus rung" isolates B,
and "warm rung minus cold rung" isolates path and carry-over. Report both decompositions per stratum.

### F2. SELECTIVE-proper vs LOSSLESS (6.2): differences beyond retention
Claim: 6.2 is labelled "optimizer confounded (SGD vs ALS)". The confound is broader than the optimizer.
Evidence:
- Optimizer: online SGD/NLMS with a fixed learning rate. The "3 passes" are 3 repeats of each 50-record batch in
  stream order (arms.py:216-218), not epochs. LOSSLESS uses converged batch ridge ALS (up to 80 sweeps over all data).
- Regularization: SELECTIVE has none (organism.py Linear.learn). L-R uses ridge lam = 0.1.
- Model class: SELECTIVE is lowrank/cp/tt/dct/additive with rank derived from cap (organism.py:249, 361). LOSSLESS
  is a rank 1-3 unfolding, or a min-Hamming kernel.
- Readout: LowRank.predict ignores the tracked mean (organism.py:261-263). L-R has no intercept either, so this is
  symmetric for the low-rank pair but not for Additive (which has a bias).
- Tuning point: SELECTIVE hyperparameters were selected at cap = max(160, cells//4) (select_arms.py:54). The same
  recipe is then applied at every ladder cap (campaign.py:41-54) without retuning. LOSSLESS is selected at its
  operating point.
- Recency: LOSSLESS -rec reads stored timestamps. SELECTIVE has implicit recency through SGD.
Severity: S2, but moot given F6 (the secondary almost cannot be read).
Resolve: relabel 6.2 as "optimizer, regularization, model-class and tuning confounded". Better, add a SELECTIVE arm
with the same factor model and ridge ALS on a bounded window (this is the reservoir), so 6.2 reduces to 6.1.

### F3. HYBRID and eviction candidates
Evidence: HYBRID's key is online SGD lr 0.1, one pass (arms.py:284), with a kNN mean readout. The ablation permutes
factor rows (arms.py:309-314). Because query and store share the permuted key, records with the same row index stay
co-located. The ablation therefore removes learned cross-index similarity only, which is appropriate. The eviction
candidates differ from random in what they keep, and keep_worst also refreshes keys after each refit
(arms.py:460-461). See F7 for why that makes it a recency policy.
Severity: S3 for HYBRID. See F7 for eviction.

## B. Power asymmetries (question 2)

### F4. (S1) The headline pair is not learnable in 29 of 38 headline strata
Claim: TESTABLE's LEARNABLE gate uses the max over the frozen SELECTIVE/LOSSLESS/HYBRID arms
(margins_reduce_v2.py:341), not the headline pair. In most strata the headline pair barely beats the constant N1.
Evidence (devpow2.py, dev 90% CI of L-R minus N1):
- F3 (12 TESTABLE strata): L-R minus N1 lies between -0.07 and +0.03. L-R is at or below the constant, and the c/8
  rung is 0.12-0.28 below N1. F3 is TESTABLE only because the recency-using L-R-rec is the frozen LOSSLESS.
- F4 (14 strata): L-R minus N1 is 0.13-0.30, with CI lower bound <= 0.28 everywhere. The whole learnable range is
  below DELTA.
- F2-L3 pairwise (lo 0.05) and sum (lo 0.19); F5-L3-lowrank (-0.05).
- Total: 29 of 38 headline strata have CI.lo(L-R - N1) < DELTA.
Consequences:
- In these strata, "L-R WIN over every rung" needs every rung, including 2c, to sit more than 0.30 below L-R, i.e.
  below the constant baseline. That is practically impossible.
- B*, BOUNDED_SUFFICES and "all_rungs_equivalent_to_LR" (NULL) become equivalences of two arms that learned almost
  nothing. Example: F3-L1-pairwise has c/8 EQUIVALENT to L-R ([+0.04, +0.12]) with both below N1.
Severity: S1 for interpretation. B*/NULL would be reported as sufficiency when they are floor equivalence.
Resolve: add a headline-specific learnability gate before 6.1 is read: CI.lo(L-R - N1) > DELTA, and for any
equivalence reading also CI.lo(rung - N1) > 0. Otherwise the stratum's headline reads UNTESTED (headline pair not
learnable). This is a dev-only gate, consistent with s6.0.

### F5. (S1) EXACT_RETENTION_PAYS / F-B have near-zero power in all 38 strata, not only "F-B strict in latent families"
Claim: the top rung, 2c, is an exact store of 37% / 54% / 73% of the history at L1 / L2 / L3. It is fitted by the same
rank-3 model. The rule requires CI.lo(L-R - 2c) > 0.30.
Evidence (devpow.py): in the 9 strata where the pair is learnable (F2-L3 lowrank/cp/tt/spectral, F5-L3
cp/tt/pairwise/spectral/sum), the dev CI of L-R minus 2c is at most [+0.01, +0.69] (F5-L3-cp). Every other stratum has
lo <= 0.12. No stratum has lo > 0.30. The strict form also needs L-K EQUIVALENT to L-R, and L-K is about 0 on
never-seen cells (the prereg says so).
Why it matters: the headline can emit only UNRESOLVED (plus unweighted B* reports). An unfired F-B is correctly
declared "not support". But the design does not state that the non-strict LOSSLESS_TRANSIENT_CONTRACTION is also
~0-power, or that this follows from the rung grid (bounded rungs that are mostly-exact stores) rather than from the
world. Also, rung fractions of history differ by level (2c = 37% at L1 vs 73% at L3). So any level trend in "L-R
minus 2c" is partly a grid artefact, and could masquerade as CROSSOVER if that label were implemented (see F14).
Severity: S1 (the direction of the headline is pre-determined).
Resolve: state the dev power in s11 per label, not only for F-B strict. Consider making the headline "L-R vs rungs <=
c" (bounded rungs that are genuinely smaller than the cell count), with 2c reported. Or define the headline on the
curve shape (the smallest B with EQUIVALENT, compared across strata) instead of a WIN over every rung. Add a headline
positive control: a world where retaining all records must help at never-seen cells, e.g. a planted field whose
rank or complexity grows with the data the readout can use. Without it, UNRESOLVED on the headline cannot be told
apart from "instrument cannot see it".

### F6. (S1) The secondary 6.2 is almost unreadable: the read budget excludes SELECTIVE by accounting convention
Claim: within_budget needs SELECTIVE persistent <= LOSSLESS persistent AND SELECTIVE bytes_read <= LOSSLESS
bytes_read (analysis.py:241-242). The two sides accumulate reads under different conventions:
- SELECTIVE is charged nbytes(all parameters) x passes at EVERY training batch (arms.py:222-223, "dense-update upper
  bound"). Its reads scale with (#batches x passes x state size).
- LOSSLESS is charged one store read per predict call (arms.py:98, 152). The campaign makes exactly ONE predict call
  (the whole test set, campaign.py:90), so L-R's "per-query refit charged" is one refit.
- ALS reads are charged once per fit, although ALS sweeps the data up to 2 x 80 times (arms.py:152, 486). SGD is
  charged per pass.
Evidence: p_budget.py (analytic, from the meters) and p_meter.py (measured):
- 0 eligible caps in 33 of 38 non-F1 TESTABLE strata.
- In F3-L1 pairwise/spectral and F4-L1 cp/tt/spectral only cap 32 is eligible, i.e. rank-1 CP (R = 32 // 24).
- Measured on F3-L1-pairwise (seed 9_700_001): L-R-r2-rec.1 AC 0.075, 61.6 KB persistent, 61.6 KB read. S-cp cap 128:
  AC 0.588, 968 B persistent (1.6%), 166.5 KB read -> ineligible.
Consequence: SELECTIVE_ADVANTAGE cannot fire in 33 strata. Where the secondary can be read, "LOSSLESS WINS over EVERY
eligible point" means beating a single rank-1 model, which makes the secondary LOSSLESS side easy. This is a strong
tilt toward LOSSLESS in 6.2. It is secondary and never gates a falsifier, but s1 claims honestly accounted resources.
Severity: S1 for 6.2.
Resolve: charge reads on a common convention: records touched x passes for both sides (ALS: iterations x 2 x n; SGD:
touched rows, not all parameters). Charge L-R one refit per query for a declared realistic query count, or charge
SELECTIVE learning reads as writes/ops, not "reads". Alternatively make the secondary Pareto-report only (no
within_budget filter) and show the frontier.

### F7. (S1) keep_worst eviction is a recency buffer; eviction readings in F3/F4/F5 measure recency, not relevance
Claim: after each refit, keep_worst recomputes buffer keys as in-sample residuals (arms.py:460-461). New records arrive
with out-of-sample residuals, which are systematically larger, so they displace buffered records. The buffer drifts
to the most recent records.
Evidence (p_recency.py, F3-L1-pairwise, B = c/4, 3 dev seeds):
- random: 0.36 of the buffer from the final episode, median stream position 0.52.
- keep_worst: 0.70-0.79 from the final episode, median stream position 0.94-0.96.
Dev (devpow.py): F3 keep_worst minus random at c/4 = +0.24..+0.42, with CI.lo up to +0.37 (F3-L2-tt). SELECTIVE_BUYS_BYTES
or RESERVOIR_SELECTIVE_ADVANTAGE (a SUPPORT label for the law) can fire in F3.
Conversely, residual_reservoir and keep_worst prefer high-residual (noisy or hard) records. F5-L3-spectral keep_worst
minus random at c = -0.57 [-0.66, -0.49]. That is RANDOM_BEATS_SELECTIVE, i.e. an F-C firing caused by a surprise
heuristic that is not relevance-based.
Why it matters: 6.7 scopes F-C as testing "relevance-selective retention of exact records". Neither candidate uses
relevance. Only the oracle fixture does. Both support and falsifier labels are thus attributable to recency or
surprise heuristics. The code also does not gate these labels on E6 (F13), and E6 FAILS in all F3/F4.
Severity: S1 (both directions can fire for the wrong reason).
Resolve: add a recency-reservoir reference (FIFO, or exponentially-biased reservoir) at matched B. Read keep_worst
against both random and recency, and name a win over random but not over recency as RECENCY, not SELECTIVE. Rename
F-C's scope to "the two declared surprise-based policies". Gate every 6.3 label (not only INDISCRIMINATE) on E6 PASS,
as s7 prose says.

### F8. (S1) F-C@c INDISCRIMINATE_EQUIVALENT can fire where equivalence is guaranteed by saturation
Claim: at B = c the random reservoir is often already within DELTA of the full store. Then any eviction policy is
EQUIVALENT to random at (i), and plausibly at (ii), whether or not selection could matter.
Evidence (devpow2.py "room@c" = random full minus random c):
- F5-L3-sum 0.16 [-0.01, 0.33] and F5-L3-pairwise 0.24 [0.19, 0.28]. Both have E6 PASS, so INDISCRIMINATE_EQUIVALENT
  is live there.
- F5-L3-pairwise keep_worst minus random at c = -0.21 [-0.26, -0.15] lies inside +-0.30 (EQUIVALENT at (i)).
- F4 room@c is 0.02-0.13, but E6 fails there.
The E6 control is a different world (planted corrupted half, oracle at c/2). It shows the analysis can detect an
advantage that is built in. It does not show the tested world at B = c leaves room for one.
Severity: S1 (a falsifier can fire from a ceiling).
Resolve: add a per-point HEADROOM gate from dev: CI.lo(full - random@B) > DELTA, else the eviction reading at that
point is UNTESTED. Alternatively run E6 at the same B as each eviction point (c/4 and c), not only at c/2.

### F9. (S2) Replication block size is derived from the wrong variance and the wrong kind of test
Claim: N_REP = ceil(((1.645 + 0.842) sd / DELTA)^2), with sd = max of the SDs of (warm full - random c) and (candidate
- random at c/4) (margins_reduce_v2.py:356-365).
Evidence:
- The headline firings use L-R-based differences, and L-R carries the seed-mode instability that s6.1 documents (p97.5
  up to 1.11 AC). The warm reservoir used for N_REP does not.
- The formula is directional power at an effect of 2 x DELTA. It is not TOST power for equivalence firings
  (INDISCRIMINATE_EQUIVALENT).
- 37 of 41 TESTABLE strata get the floor N_REP = 8 (TABLES).
Consequence: replication of F-B/LTC is underpowered relative to the stated 80%. TOST at n = 8 needs 0.67 x sd < 0.30,
while the per-world SD of L-R-based differences is larger. Equivalence firings and win firings do not replicate
equally easily, so the "symmetric" replication rule is not symmetric in power.
Severity: S2.
Resolve: compute N_REP per reading type from that reading's own dev paired SD, and use a TOST sample-size formula for
equivalence readings.

### F10. (S2) Matched-HR2 (6.3 ii) matches on an outcome-correlated quantity
Claim: BufferALS has no _reconstruct, so its HR2 is the factor readout's in-sample fit on history (accounting.py:250-260,
recover.py:337-343). It is not a measure of the retained exact records. Matching random's B to the candidate's HR2 is
close to matching training fit, which predicts held-out AC.
Evidence: code path as cited. The interpolation np.interp clamps at the ladder ends (campaign.py:122). When the target
HR2 exceeds random's maximum, B_random is n (full).
Severity: S2. (ii) is biased toward EQUIVALENT, which makes INDISCRIMINATE_EQUIVALENT easier and
RESERVOIR_SELECTIVE_ADVANTAGE harder.
Resolve: match on a memory quantity: the HR2 of reconstruct = buffered record where present, factor readout otherwise.
Or match on bytes, which are already charged. Report clamped interpolations as UNMATCHED.

## C. Readout confounds (question 3)

### F11. (S2) The lossless endpoint is a fixed-capacity contraction; retained data cannot be exploited beyond rank 3
Claim: L-R refits a rank-3 unfolding (816 parameters at L3) whatever the store size, and rungs use the same rank. Past
the saturation point of that estimator, more exact records cannot raise AC. The headline then reflects the
misspecification and sample complexity of the rank-3 model on each generator (pairwise/sum are not low-rank in the
unfolding) more than retention.
Evidence: arms.py:104-137 (fixed r). Dev L-R minus 2c is about 0 in F2-L3 lowrank/cp/tt (-0.01..-0.10). L-K, the only
readout that does grow with data, is about 0 on never-seen cells (prereg s6.7).
Severity: S2 (the headline cannot distinguish memory from readout capacity).
Resolve: add a data-adaptive lossless readout charged at query time: rank chosen by CV on the full store, or a
kernel/GP readout on the full store. A rung-matched version would show whether exactness pays when the readout can use
it.

### F12. (S3) Other readout details
- F5: the SELECTIVE ladder starts at cells//16, where cells include the nuisance mode (campaign.py:45). The reservoir
  uses real_cells (campaign.py:28-32). This is inconsistent with the spirit of operator item 3.
- F1 lossless_must_win compares L-K with the per-world MAX over SELECTIVE ladder caps (analysis.py:295-297). That is
  winner's-curse inflation favouring SELECTIVE, but branch-trigger only.

## D. Capacity comparability (question 4)

### F13. Bytes per record are comparable; "bounded" is a misnomer at the upper rungs
Evidence: an L-R store record = int16 x D + f64 value + i64 step = 22 B at D = 3 (arms.py:35-39). A reservoir record =
int16 x D + f64 value + f64 bkey = 22 B (arms.py:421; bkey is kept even for random eviction), plus rank-3 factors.
Per-record bytes are matched, which is good. However:
- The rung scale is in cells, not bytes or records. 2c is 73% of the history at L3, so the "bounded coarse-grained"
  arm is mostly an exact store (F5).
- The SELECTIVE ladder is capped in floats up to LOSSLESS bytes but filtered on reads (F6), so the byte comparability
  that s4 claims is never exercised.
- The dual matching charges extra bytes (campaign.py:127), but no rule reads them.
Severity: S2.
Resolve: express rungs as a fraction of the history as well, and report persistent-bytes ratios next to every reading.

## E. Compute accounting (question 5)

### F14. Compute is measured but no verdict uses it; the conventions are asymmetric
Evidence:
- ops/wall/replay_ops are recorded (accounting.py) but used by no rule in analysis.py. The headline has no resource
  condition at all. Steward R2 defines "beaten" as "<= bytes, <= reads/ops", but the code uses bytes and reads only
  (analysis.py:241-242).
- Warm reservoir ops are about 20x L-R's (p_meter.py: 7.35M vs 0.34M; 563 KB vs 62 KB read), because L-R is charged
  for one query.
- ALS iterations are not multiplied into reads (F6).
- Query-time compute for L-R would scale with the number of queries. The campaign has one, so steward R1b ("summed
  over the life") is satisfied trivially.
Severity: S2 (not a label changer by itself, but "honestly accounted resources" in s1 is not what the verdicts use).
Resolve: declare a query count (e.g. one query per k admissions, or per test cell) and charge L-R per query. Report the
ops-ratio next to every headline and eviction reading. State in s1 that verdicts are bytes-only (headline) and
bytes-plus-reads (6.2).

## F. Readings that cannot distinguish competing explanations (question 6)

| Reading | Competing explanations it cannot separate |
|---|---|
| 6.1 EXACT_RETENTION_PAYS / LTC | data amount vs warm/cold path vs refit tail vs fixed rank-3 capacity (F1, F11); grid artefact of 2c = 37-73% of history (F5) |
| 6.1 B* / BOUNDED_SUFFICES | sufficiency vs floor equivalence of two non-learners (F4); stale-factor carry-over from evicted data (F1) |
| 6.1 endpoints (a)-(b) | persistence vs compute (about 20x) vs warm-start local-minimum escape (F1, F14) |
| 6.6 NULL | same as B* plus a positive control (E6) that tests eviction, not the headline (F15a) |
| 6.2 SELECTIVE_ADVANTAGE / COUNTERMODEL | optimizer, regularization, model class, tuning point, read-accounting convention (F2, F6) |
| 6.3 SELECTIVE_BUYS_BYTES / RESERVOIR_SELECTIVE_ADVANTAGE | relevance vs recency (keep_worst) vs hard-example emphasis (residual) (F7); HR2 matching on outcome-correlated fit (F10) |
| 6.3 INDISCRIMINATE_EQUIVALENT (F-C) | no effect of selection vs no headroom at B (F8) vs heuristic not relevance-based (F7) |
| 6.3 RANDOM_BEATS_SELECTIVE (F-C) | selection harmful vs the surprise heuristic keeping noisy records (F7) |
| 6.4 HYBRID_REQUIRED | learned similarity needed vs SGD key under-trained in one pass; acceptable given the positive control |

## G. Verdict rules vs prose (question 7)

### F15. Inconsistencies between analysis.py and PREREG v0.3.1
a. (S2) NULL (analysis.py:298) requires dev posctl_pass, which is the E6 EVICTION control. Prose 6.6 says "positive
   control PASS" without naming it. Steward #619 requires a positive control specific to the no-difference verdict
   (a world where the analysis detects the difference). There is no headline positive control.
b. (S1) Prose s7 says "Where [E6] fails, 6.3 reads UNRESOLVED by rule". The code gates only INDISCRIMINATE_EQUIVALENT
   on E6 (analysis.py:266-275). RANDOM_BEATS_SELECTIVE (an F-C firing), SELECTIVE_BUYS_BYTES and
   RESERVOIR_SELECTIVE_ADVANTAGE (supports) can fire in E6-failing strata (all F3, all F4). s11 states the narrower
   rule, so the prose contradicts itself. Given F7, this matters in F3.
c. (S2) The 6.2 secondary COUNTERMODEL prose says "every ladder point at <= LOSSLESS bytes". The code restricts to
   points within bytes AND reads (analysis.py:245-251).
d. (S2) The labels CROSSOVER, INSTRUMENT_FAILURE and UNREPLICATED (6.6/6.7) are not implemented. grep finds them in
   no .py file except a docstring. GENERATOR_DEPENDENT is computed only from HEADLINE labels (analysis.py:334-338),
   not for eviction, secondary or hybrid readings.
e. (S3) The s5 selectivity reading "relative to K = 5 HR2-matched blind references" and s4 "IM-rate / IM-bytes:
   RandomMerge" are not computed by campaign.py and not read by analysis.py. RandomMerge and selectivity are never
   imported there. The declared readouts will be absent from campaign rows.
f. (S3) The sensitivity labels at 0.15 / 0.60 reuse the 0.30 TESTABLE frame and E6 pass (analysis.py:320), whereas
   TABLES reports different frames at 0.15 / 0.60. This is descriptive only, but the two are inconsistent.
g. (S3) Falsifier firings are emitted in "firings" with no pending-replication marker, while supports are under
   "supports_pending_replication" (analysis.py:299-310). Prose 6.7 makes replication symmetric.
h. (S3) B* is the first EQUIVALENT rung from the bottom, with no monotonicity requirement (analysis.py:219). A
   non-monotone curve (F3: c/8 closer to L-R than c/4) yields B* = c/8 while larger rungs are not equivalent. The
   prose "B* < full" does not define which rung counts.
i. (S3) The campaign computes a per-world posctl (campaign.py:130-140), but analysis uses only the dev E6
   (margins_reduced_v2.json). No rule covers campaign-vs-dev disagreement.

## H. What the design does well

- The headline is optimizer-equalised: same ALS, same rank, same ridge, same convergence rule, and literally the same
  initial factors (seed 0) for L-R and every rung. Most of 6.1's residual confounds are path and compute, not model
  class.
- The fixed DELTA is not derived from an arm's own instability. Paired per-world CIs and TOST for equivalence are the
  right structure.
- The cheat fixtures for a kept fit and for a subsampled refit are good, with a separate store_read counter after D8.
  The prereg correctly states that an L-R win is contraction, not exactness.
- Both endpoints are reported side by side, and substitution is forbidden.
- F1 is excluded from the headline (D12). Full-coverage cells are excluded. Sealed hash-derived seeds come with a
  launch gate. The defect ledger records the direction of each cut.
- Limitations are candid (F-B strict power, optimizer confound, recency-blind reservoir, deferred intervention), and
  "an unfired falsifier is not support" is stated in advance.
- E6 and the HYBRID ablation positive controls exist and are checked per stratum.

## I. Recommended minimal pre-launch changes, in priority order

1. Add a headline-pair learnability gate (F4) and a headroom gate for eviction points (F8). Both are dev-only and
   rule-based.
2. Gate every 6.3 label on E6, as s7 says (F15b). Add a recency-reservoir reference, or re-scope keep_worst results as
   recency (F7).
3. Fix or drop the read filter in 6.2, and charge reads on a common convention (F6).
4. Add an end-of-life refit for the reservoir, and a cold-refit-on-rung-buffer control (F1).
5. State the dev power of every label in s11, including that EXACT_RETENTION_PAYS has no dev stratum with
   CI.lo(L-R - 2c) > 0.30 (F5). Implement or delete CROSSOVER / INSTRUMENT_FAILURE / UNREPLICATED, and the
   RandomMerge/selectivity readouts (F15d, e).
