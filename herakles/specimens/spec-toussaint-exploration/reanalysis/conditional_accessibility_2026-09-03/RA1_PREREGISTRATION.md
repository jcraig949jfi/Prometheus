# RA1 PREREGISTRATION

**Frozen before any accessibility-to-acquisition association was computed.**
Prompt sha256 recorded in `RA1_DATA_AUDIT.json`. Analysed commit recorded there
too.

## What was inspected before freezing, and what was not

The prompt permits inspecting distributions needed to establish that a proposed
estimator is mathematically valid, and requires that the distinction be
preserved. So, explicitly:

**INSPECTED before freezing.** The data audit in full: run counts, arms,
checkpoint cadence, missing and duplicate rows, seed pairing, fitness and
detector conventions and directions, the `nops` distribution per arm, ceiling
occupancy per generation per arm, and the horizon-feasibility table giving, for
each candidate `(t, h)`, how many runs still had headroom at `t`, how many had a
non-zero gain, and how many distinct gain values existed. All of these are
properties of the outcome and the design, not of any relationship between
accessibility and acquisition.

**NOT INSPECTED, and not computed in any form, before this file was written.**
Any association, correlation, regression or residual involving the accessibility
detector `md_on` and the acquisition outcome. No such number existed anywhere
when the plan below was fixed.

## Two structural facts from the audit that drive the design

1. **`nops` is identically zero in every `beta=0.0` row, at every generation, in
   both alpha levels.** Fraction zero is 1.000. The ablated arm cannot possess
   the second-type machinery class at all. This is hazard H-3 in the data rather
   than in argument.
2. **Ceiling saturation is severe, arm-dependent and early in the treated arm.**
   In `alpha=0.06, beta=0.1`, 63 per cent of runs are already at the optimum by
   generation 80 and 90 per cent by generation 175. In `beta=0.0` arms, zero per
   cent are at the optimum through generation 175. This is hazard H-2, and it is
   asymmetric across exactly the arms HC-T01 compared.

---

## A. ACQUISITION OUTCOME

`gain(t, h) = best(t + h) - best(t)`, where `best` is the frozen HC-T01 column,
the negative fraction of mismatched target symbols. Higher is better, the
optimum is exactly 0.0, so `gain >= 0` always and `gain = 0` for a run already at
the optimum at `t`.

## B. CONDITIONING VARIABLE

`best(t)`, current best fitness, and nothing else. This is the variable that beat
the accessibility statistics in HC-T01's K7 test, and it is the variable the
ceiling argument implicates. No other conditioner is added: the prompt forbids
conditioning indiscriminately, and every other candidate in the frozen rows is
either a mediator (`nops`, `glen`) or a second accessibility statistic.

## C. TIME HORIZONS

Two, both inherited from HC-T01's own committed K7 windows rather than chosen
here:

    h = 150 generations   the span of the original 50 -> 200 window
    h = 400 generations   the span of the original 100 -> 500 window

A pair `(t, t+h)` is used only when BOTH are checkpoints in the frozen cadence.
No other horizon is examined. No sweep.

## D. ELIGIBLE GENERATIONS

A `(cell, t, h)` triple is ELIGIBLE only if all three hold:

    E1  n_with_headroom_at_t >= 15     at least half the 30 runs can still improve
    E2  n_distinct_gain_values >= 8    a rank statistic on fewer distinct values
                                       than this is dominated by ties at n = 30
    E3  the stability guard in section E passes

E1 and E2 are set on the principle that an outcome which is mostly a structural
zero cannot carry rank information, not on any observed association. They were
chosen after seeing the feasibility table and before computing any association,
and that ordering is disclosed here rather than hidden.

## E. ESTIMATOR

**Primary: partial Spearman**, on the runs that still have headroom at `t`.

    A = md_on(t)          accessibility detector at t
    G = gain(t, h)        acquisition outcome
    F = best(t)           current fitness

    rho_partial = (r_AG - r_AF * r_GF) / sqrt((1 - r_AF^2) * (1 - r_GF^2))

with all three `r` being Spearman correlations using average ranks for ties.

**Why this and not regression residualisation.** `gain` has heavy ties and
structural zeros and is bounded above by `-best(t)`; `best` is itself discretised
to multiples of 1/25. Ordinary-least-squares residualisation assumes a linear
conditional mean on variables that are neither continuous nor linearly related.
A rank-based partial makes no such assumption, and it is the conditional analogue
of the marginal Spearman that HC-T01 used, so the comparison to K7 is like for
like.

**Restriction to runs with headroom is the primary specification, and it is the
whole point.** A run already at the optimum contributes `gain = 0` by
construction and cannot inform any prospective question. Including it does not
add information; it adds a tie whose value is determined by `F`. This is the
direct treatment of hazard H-2. The unrestricted version over all 30 runs is
computed as a SECONDARY, for comparability with the original K7 number, and is
never the basis of the verdict.

**Stability guard.** If `|r_GF| > 0.95` or `|r_AF| > 0.95`, the denominator is
near zero and the partial is numerically meaningless. Such a point is recorded
as `UNSTABLE` and excluded from the series, never reported as a large effect.
This guard exists because the ceiling makes `gain = -best(t)` exactly for every
run that reaches the optimum, which drives `r_GF` toward minus one.

## F. TIES

Average ranks throughout. Ties are reported per point as
`n_distinct_gain_values` and `n_distinct_md_values`.

## G. UNCERTAINTY

Per point: bootstrap over runs, 2000 resamples, percentile 95 per cent interval
on `rho_partial`.

## H. MULTIPLICITY AND SERIES-LEVEL RULE

The series statistic for a cell is the **mean `rho_partial` over that cell's
eligible points**, one horizon at a time.

Its null is a **cross-seed permutation that preserves temporal structure**: within
a cell, the mapping from a run's accessibility trajectory to a run's acquisition
trajectory is permuted across seeds, keeping every run's own time series intact
and every marginal distribution unchanged. 2000 permutations. The reported
p-value is two-sided on the mean.

A cell yields a verdict only if it has **at least two eligible points** for a
horizon. With fewer, that cell and horizon is `INDETERMINATE`. No pointwise
threshold-crossing is ever reported as a result.

## I. NEGATIVE CONTROLS

**NC1, reverse precedence.** Replace `md_on(t)` with `md_on(t + h)` and recompute
the same conditional statistic against the same `gain(t, h)` conditioned on the
same `best(t)`. A genuinely prospective signal should not be reproduced, or
should be weaker, when the detector is read AFTER the outcome window. If the
backward version is as strong, the association is contemporaneous coupling
between accessibility and fitness rather than prospective information. This is
diagnostic precisely because it retains every distributional property and changes
only the temporal direction.

**NC2, the cross-seed permutation of section H**, which is simultaneously the
series null.

Neither control is constructed to be easy to beat: NC1 uses real data with the
same marginals, and NC2 preserves each run's entire internal structure.

## J. ARM HANDLING

**No pooling across `beta` arms, under any circumstance.** `nops` is identically
zero in `beta=0.0`, so a pooled analysis would let the arm label stand in for the
machinery class and would reproduce hazard H-3 inside RA-1.

Four cells, analysed separately, `n = 30` runs each:

    alpha=0.03 beta=0.1     TREATED, primary target: this is the arm HC-T01's
                            K7 claim was about
    alpha=0.06 beta=0.1     TREATED
    alpha=0.03 beta=0.0     ABLATED, parallel test. Free of H-3 by construction,
                            because no run in it has any second-type machinery,
                            and well powered because it never saturates.
    alpha=0.06 beta=0.0     ABLATED

The ablated cells are reported as a parallel result of independent interest, not
as support for a claim about the treated arm. If accessibility carries
prospective information in an arm with no operators at all, that is a statement
about the detector, not about the mechanism.

## K. DECISION RULE, FROZEN

`RA1_CONDITIONAL_SIGNAL_SURVIVES` requires ALL of:

1. the mean `rho_partial` has the prospective sign and is consistent in sign
   across the eligible points of the cell;
2. it is incremental, meaning the partial retains at least half the magnitude of
   the marginal `r_AG` rather than collapsing toward zero once `F` is removed;
3. the cell has at least two eligible points and the permutation p on the mean
   is below 0.05;
4. NC1 does not reproduce the same pattern at comparable magnitude;
5. `|mean rho_partial| >= 0.3`, a conventional medium effect, so that the result
   is scientifically nontrivial and not merely detectable.

`RA1_NO_INCREMENTAL_SIGNAL` applies when a cell has at least two eligible points,
the estimator is stable, and criteria 1, 2, 3 or 5 fail.

`RA1_INDETERMINATE` applies when a cell has fewer than two eligible points, or
every candidate point fails the stability guard, or eligibility is denied by E1
or E2. **Indeterminate is not failure and is not to be reported as failure.**

An overall RA-1 verdict is assembled from the cells, with the TREATED cells
deciding the verdict about HC-T01's K7 and the ABLATED cells reported
separately.

---

## RA-2, frozen at the same time

Within `beta=0.1` only. No `beta=0.0` contrast is used as evidence for any of A
to C.

    A  Spearman of md_on against nops, pooled over eligible generations,
       computed within the treated arm only
    B  the arm's accessibility trajectory over generations, recomputed with nops
       held fixed by stratification, using the nops strata that contain at least
       10 observations
    C  monotonicity: mean md_on per integer nops level, with counts
    D  sufficiency: the fraction of the treated arm's md_on variance explained by
       nops alone, and whether generation adds anything beyond it

`RA2_MACHINERY_COUNT_EXPLAINS_EFFECT` if md_on is strongly monotone in nops
(Spearman >= 0.7) AND stratifying on nops removes most of the generation-related
trend in md_on.

`RA2_HISTORY_EFFECT_SURVIVES_NOPS` if a substantial generation or trajectory
effect remains within nops strata.

`RA2_MIXED` if the two criteria split. `RA2_INDETERMINATE` if strata are too thin.

Conservative reading is mandatory: surviving conditioning on nops does NOT
demonstrate structural reorganisation, only that machinery COUNT is not a
sufficient statistic.
