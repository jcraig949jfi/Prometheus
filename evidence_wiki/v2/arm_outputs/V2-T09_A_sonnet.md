# PROPOSAL V2-T09 (arm A)

## Hypothesis

In the planned batch experiment, one model call emits a single decision (a
rule, a threshold, a routing choice, a label) that is then mechanically
applied to every row of its batch. The rows inside a batch are **not**
independent observations of that decision: they share one draw of whatever
process generated it. If the analysis pools rows and computes a per-row
standard error, it treats N = Σ(batch sizes) as the sample size when the
number of independent draws is actually B = number of batches. Because
batch size varies widely across the design, this error does not merely
shrink the SE by a constant factor — the amount of inflation itself varies
batch-to-batch, and a few oversized batches can dominate a row-pooled
statistic while contributing only one independent decision. The correct
analysis treats the batch as the unit of analysis and quantifies
uncertainty by resampling batches, not rows.

## Motivating evidence

Two committed instances of exactly this class of error, found in this
repository:

1. `ergon/gen1/REVIEW_PACKET_GEN1_BRIEF_2026-08-31.txt` (line ~321-325):
   retention policy acts at the *library* level, not the row/task level;
   "if the true independent unit is the lineage there are 5 of them, not
   290 rows. This is the same wrong-unit error that once inflated a
   precision estimate 57x elsewhere in this programme."
2. `ergon/probe/PREREG_P4_neighbourhood_assay_2026-08-25.md` §6.1 fixes,
   in advance, "UNIT OF ANALYSIS: the generator stratum … NOT the row,"
   pairs each stratum's contribution, and computes uncertainty by "paired
   bootstrap over strata, 10,000 resamples, fixed seed, BCa interval. Not
   a normal approximation: the stratum count is small and the differences
   are not assumed symmetric." The same document (§5) separately flags
   that a two-valued margin makes "improvement" a coin flip whose `n` is
   the number of *cells*, not rows — the same diagnosis in miniature.

Both cases are clusters of unequal size analyzed with a bootstrap over the
cluster axis rather than the row axis. Neither case involves batches that
vary as widely in size as this experiment's design does, so the specific
risk here (a handful of huge batches swamping a row-pooled mean while
counting as one decision) is new territory, not a re-run of either
precedent — hence this is a design specification, not a replication.

## Prospective predictions

Fixed before any data is collected:

1. A naive row-pooled SE (`sqrt(p(1-p)/N_rows)` or its continuous
   analogue) will be smaller than the batch-bootstrap SE by a factor that
   scales with the design effect implied by the batch-size distribution;
   the ratio will track `1 + CV²(batch_size)` (Kish-style approximation)
   to within a factor of 2, when batch outcomes are constant within batch.
2. The equal-batch-weighted estimand (Θ_equal, one vote per decision) and
   the row-exposure-weighted estimand (Θ_exposure, one vote per row) will
   differ by an amount detectable above their respective bootstrap CIs
   whenever batch size correlates with decision quality with |r| ≥ 0.2;
   if no such correlation exists in the real data, Θ_equal and
   Θ_exposure will agree within their overlapping CIs.
3. The number of batches B required for a target bootstrap CI half-width
   will be set by the *between-batch* variance of the batch-level outcome,
   not by the total row count; doubling average batch size while holding
   B fixed will not materially shrink the CI.

## Experiment

**Unit of analysis: the batch** (equivalently, the model call). Each batch
`b` yields exactly one decision `d_b` and a batch-level outcome `y_b`,
defined as a pre-registered scalar function of the row-level results
produced by applying `d_b` to that batch's rows (e.g., accuracy of `d_b`
against each row's own ground truth, or a margin analogous to
`PREREG_P4`'s per-relation margin). `y_b` is computed once per batch and
is the only quantity that enters inference; row-level correctness
indicators are retained for diagnostics but never fed directly into an SE
formula.

Two estimands are preregistered, both computed and reported, with the
primary one stated in advance:

- `Θ_equal = mean_b(y_b)` — unweighted mean across batches ("how good is
  the decision-making process, independent of how large a batch it was
  applied to"). **Primary estimand**, because the object under study is
  the model-call decision process, not any particular row's fate.
- `Θ_exposure = Σ_b(n_b · y_b) / Σ_b(n_b)` — row-weighted mean ("what
  fraction of rows, overall, ended up under a good decision"). Reported
  as a secondary, clearly labeled estimand; never substituted for
  `Θ_equal` in a headline, and never silently averaged with it.

**Uncertainty — primary method: cluster (batch) bootstrap.** Resample
batches with replacement, B draws per resample (each resampled unit is a
whole batch carrying all its rows and its single `y_b`), 10,000
resamples, fixed seed, recompute both `Θ_equal` and `Θ_exposure` on each
resample, report BCa 95% intervals. A normal approximation is not used:
batch count may be small relative to row count, and the batch-size
distribution is expected to be right-skewed (stated as "varies widely"),
which is exactly the condition under which BCa's skewness correction
matters.

**Uncertainty — secondary/diagnostic: cluster-robust (sandwich) SE** on
`Θ_equal`, computed for fast interim looks only. It never governs a
go/no-go decision; the bootstrap does.

**Forbidden quantity, stated explicitly:** any SE computed as if N = total
row count. Its presence in a report is treated as a defect, not a
different opinion.

## Controls

Three gate-fire synthetic worlds, run and passing **before** any real
batch is analyzed (pattern taken directly from `PREREG_P4` §8):

1. **Null world.** Batches carry IID noise decisions with no true batch-
   level signal. The batch-bootstrap CI must cover the true null at
   ≥ 93% empirical coverage over 1,000 simulated replications of the whole
   pipeline (nominal 95%, 2pp slack for Monte Carlo noise). The naive
   row-pooled SE, applied to the same synthetic data, must produce a
   false-positive (CI excludes 0) rate detectably above 5% — this
   reproduces the 57x-style inflation in a controlled setting where the
   right answer is known, before the real run is trusted.
2. **Deterministic-copy world.** One decision per batch, identical
   outcome value copied to every row in that batch (the degenerate case
   where within-batch variance is exactly 0). The batch bootstrap must
   recover an SE matching the closed-form SE for B independent Bernoulli-
   like trials to within 5% relative error. The naive row SE must
   understate this by a factor tracking `sqrt(mean batch size)`.
3. **Size-confound world.** Batches constructed so decision quality is a
   known function of batch size (planted correlation, e.g. r = 0.4).
   `Θ_equal` and `Θ_exposure` must diverge in the planted direction and by
   an amount within 20% of the analytically expected divergence. Failure
   here means the two estimands are not actually measuring different
   things in this implementation (a wiring bug), and the real run does
   not proceed until fixed.

## Confound defenses

- **Batch size as a confound of decision quality**, not just a nuisance
  weight (e.g., a single call may attend less carefully per item as batch
  size grows, or conversely batch composition may correlate with task
  difficulty). Defense: report `y_b` stratified by batch-size quantile
  (quartiles at minimum) in addition to the two pooled estimands; a
  monotone trend across quantiles is flagged even if the pooled Θs agree.
- **Non-independence across batches over time/session.** If batches are
  generated in a shared session (same context window, same running
  conversation, or same upstream routing state), consecutive `y_b` may be
  autocorrelated, which the batch bootstrap (i.i.d. resampling of
  batches) does not model. Defense: compute a lag-1 autocorrelation on
  the ordered sequence of `y_b`; if |ρ| exceeds 0.2, add a block bootstrap
  (moving blocks of batches) as a robustness check before trusting the
  i.i.d. batch bootstrap's width.
- **Non-random batch formation.** If batch size itself is driven by an
  upstream rule (e.g., overflow rows swept into one oversized trailing
  batch, or batches sized by source-document length), the batch-formation
  rule is recorded as a covariate for every batch, not discarded. A batch
  formed by a different mechanism than the rest (e.g., the single
  "leftover" batch) is flagged and its removal/retention is decided by a
  preregistered rule, not post hoc.
- **Nested clustering.** If several batches derive from one shared
  upstream source (e.g., multiple batches carved from the same source
  document or the same upstream generation run), the source is a coarser
  cluster than the batch. Defense: record the source id for every batch;
  if more than one batch per source is common, rerun the primary bootstrap
  with the source as the resampling unit (nesting rows within batches
  within sources) as a required robustness check, not an optional one.

## Preregistered falsifiers (numeric thresholds)

1. If, in the null gate-fire world, the batch-bootstrap empirical
   coverage of the 95% BCa interval falls below 90% (vs. nominal 95%)
   over 1,000 replications, the bootstrap implementation is rejected and
   not used on real data until fixed.
2. If the ratio (naive row-pooled SE) / (batch-bootstrap SE) on real data
   exceeds 0.8 — i.e., the two methods nearly agree — despite a batch-size
   coefficient of variation ≥ 1.0, this falsifies the prediction that
   batch-size heterogeneity drives meaningful design-effect inflation in
   this dataset, and the headline reverts to reporting the simpler,
   agreeing estimate (with the disagreement-check still reported).
3. `Θ_equal` is declared to differ from `Θ_exposure` only if their BCa 95%
   intervals do not overlap; MIN_EFFECT = 0.02 in the units of `y_b`
   (matching the `PREREG_P4` floor, chosen so an interval that merely
   excludes zero-difference but is smaller than plausible measurement
   noise is not over-read).
4. If B < 20 batches are available at analysis time, no inferential CI is
   computed at all — only descriptive statistics are reported, and the
   result is marked UNDECIDED pending more batches, never rounded to a
   side.

## Stopping rule

Run a pilot of ~30 batches first. Estimate the between-batch variance of
`y_b` from the pilot. Using that variance, compute the number of batches
B required for the primary bootstrap CI's half-width on `Θ_equal` to reach
a preregistered target margin (target margin fixed at design time, before
the pilot variance is known, so it cannot be chosen to flatter the pilot).
Collect batches up to that computed B and stop. If the resulting CI
straddles a preregistered decision threshold, the answer is UNDECIDED and
the quota is re-measured at a larger B — never rounded to a side. Total
row count is not part of the stopping rule at any point; only B and the
between-batch variance are.

## Expected failure modes

- **Reversion under time pressure.** An analyst re-derives a per-row SE
  because it is the default output of whatever library is at hand.
  Mitigation: any statistic-producing code path asserts
  `len(unique(batch_id)) < len(rows)` and requires an explicit
  `unit_of_analysis == "batch"` flag before an SE is emitted; absence of
  the flag is a hard error, not a warning.
- **Too few batches for a stable bootstrap.** With B in the single digits,
  BCa intervals are unstable and coverage claims are unreliable regardless
  of the row count. Handled by falsifier 4 above.
- **Silent conflation of Θ_equal and Θ_exposure** in a summary sentence
  ("the decisions were good X% of the time," ambiguous as to which
  weighting). Mitigation: both numbers are named in every report with
  their weighting stated inline, never as a single unqualified percentage.
- **Nested clustering ignored** even after fixing to the batch level —
  the CI is still too narrow if several batches share an un-modeled
  upstream source. Handled by the nested-clustering confound defense.
- **Nonstationary batch-generation process** (e.g., the model call's
  behavior drifts over the course of the run) masquerading as batch-size
  effects. Handled by the autocorrelation check above; a real drift signal
  should be reported as a time trend, not folded into the size analysis.

## Compute estimate

The bootstrap itself is cheap: 10,000 resamples over at most a few hundred
batches is sub-second, negligible compute, no model calls. The real cost
is the experiment's own model calls: one call per batch, B calls total,
where B is set by the stopping rule above (pilot of ~30 batches plus
however many the pilot variance estimate implies, typically expected in
the low hundreds given the `PREREG_P4` precedent's analogous target of
SE ≤ 0.02 requiring n ≥ 625 *units* — here units are batches, so if
between-batch variance is comparable this experiment should expect a
similar order of magnitude in B, substantially cheaper in wall-clock time
than 625 separate row-level calls would be, since one call serves an
entire batch). The three gate-fire synthetic worlds are pure simulation,
no model calls, and should be run and committed before B is spent on the
real experiment.

## Prior evidence that materially changed this design (or 'none found')

Yes. Two prior instances of the wrong-unit error (`ergon/gen1/REVIEW_PACKET_GEN1_BRIEF_2026-08-31.txt`,
`ergon/probe/PREREG_P4_neighbourhood_assay_2026-08-25.md`) directly shaped
this design: they establish (a) that this exact class of error has already
cost a 57x precision inflation in this programme, (b) that the correct
remedy is bootstrapping over the cluster axis with a BCa interval rather
than a normal approximation, precisely because cluster counts are small
and outcome distributions are not assumed symmetric, and (c) that gate-
fire synthetic worlds with a known answer must pass before the method is
trusted on real data. The size-confound gate-fire world and the dual
Θ_equal/Θ_exposure estimand split are new additions here, motivated by
this experiment's distinguishing feature (batches varying *widely* in
size) not present in either precedent.

## Unresolved uncertainty

- Whether the real batch-formation process introduces nested clustering
  (shared upstream sources across batches) is not yet known and cannot be
  resolved without inspecting the actual batching code/logs for this
  specific experiment, which were out of scope for this search.
- Whether `y_b` should be a binary/accuracy-style objective or a
  continuous margin (as `PREREG_P4` argues a continuous surrogate is
  needed when most outcomes stay on one side of a threshold) depends on
  the concrete decision type in this experiment and is not fixed by this
  specification; it must be fixed before data collection, per the general
  house doctrine of committing objectives before measurement.
- The planted-correlation magnitude (r = 0.4) and MIN_EFFECT = 0.02 in
  the size-confound gate-fire world are reasonable defaults borrowed from
  precedent but not derived from this experiment's actual expected effect
  size, which is unknown pre-pilot; the pilot's variance estimate may
  argue for revising these before the real run, and any such revision must
  be logged as a deviation, not silently substituted.
- Whether autocorrelation across batches (session/state effects) is a
  real risk for the specific model-call architecture used in this
  experiment is untested; the 0.2 threshold for triggering a block
  bootstrap is a generic guard, not a value estimated from this system.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Grep `batch.*(decision|size)|design effect|cluster.robust|effective sample size|one decision per` over F:\Prometheus — broad sweep, files_with_matches.
2. Grep `se_on_the_wrong_unit|per-row SE|per row SE|coin flip` over F:\Prometheus — broad sweep, files_with_matches.
3. Glob `**/feedback_se_on_the_wrong_unit.md` — not found (memory topic file lives outside the repo tree searched).
4. Read attempt on `v1b/proposals/T8_control.md` — resolved to a path under evidence_wiki (out of scope per rules), aborted; no content used from this attempt.
5. Grep `design effect|cluster.robust|effective sample size|coin flip` scoped to F:\Prometheus\ergon — files_with_matches.
6. Grep `design effect|cluster.robust|effective sample size|per-cell|per cell|batch.level` scoped to F:\Prometheus\aporia — files_with_matches.
7. Read `F:\Prometheus\ergon\probe\PREREG_P4_neighbourhood_assay_2026-08-25.md` (full file) — document opened #1; source of the unit-of-analysis, paired-bootstrap-over-strata, BCa, MIN_EFFECT, and gate-fire-world methodology reused above.
8. Grep `57x|14 coin flips|per-row SE inflated` scoped to F:\Prometheus\ergon — files_with_matches, located the review packet.
9. Grep `batch varies|batch size|varying batch|batches vary` over F:\Prometheus (*.md) — broad sweep, files_with_matches.
10. Grep (content mode, -C 4) `57x|coin flip|per-row SE|per-cell|cell count` on `F:\Prometheus\ergon\gen1\REVIEW_PACKET_GEN1_BRIEF_2026-08-31.txt` — document opened #2 (partial, via content-mode search), source of the "library not row, 5 lineages not 290 rows, same wrong-unit error that inflated a precision estimate 57x" citation.

Ops used: 10 / 15. Documents opened: 2 / 12. Budget stopped early: the
two documents opened (`PREREG_P4_neighbourhood_assay_2026-08-25.md` and
`REVIEW_PACKET_GEN1_BRIEF_2026-08-31.txt`) supplied a directly-applicable,
already-adjudicated methodology (bootstrap over the cluster axis, BCa,
gate-fire worlds, MIN_EFFECT floors) plus a concrete cost figure (57x)
for the exact failure mode this task specifies; further search was
judged to have diminishing return against the remaining budget.
