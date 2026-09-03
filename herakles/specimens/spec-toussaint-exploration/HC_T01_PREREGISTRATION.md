# H. HC-T01 PREREGISTRATION

**Status: DRAFT, WRITTEN BEFORE T0 COMPLETES AND BEFORE ANY DATA EXISTS.** Directive `roles/Herakles/prompts/DIRECTIVE_HC_T01_TOUSSAINT_MISSING_CELL_2026-09-03.txt`, sha256 `5cc0241fe85567e71201416cd16a88fd0672ff5cc4ae921996606e33c30b0354`.

Sections 1 and 2 are written now, deliberately, because they are design questions that do not depend on the historical record and are more honest written in ignorance of the data. Sections 3 onward are blocked on T0 and are marked so.

**No compute may run until T0 passes and this preregistration is frozen.**

---

## 1. TWO TRAPS THAT COULD MAKE THIS EXPERIMENT VACUOUS

These are stated first because if either holds, the experiment as conceived does not test anything, and that is better discovered now than after execution.

### TRAP 1 — the tautology: does the ablated knob *define* the detector?

The directive's core hypothesis is that the ablated mechanism changes the trajectory of the exploration distribution. But a prior pass reports the ablated parameter as controlling "second-type mutations", and the detector as a statistic of the phenotypic exploration distribution.

**If that parameter directly parameterises the variation operator that induces the exploration distribution, then "the ablation changes the detector" is TRUE BY CONSTRUCTION.** Turning the knob that generates the distribution and then observing that the distribution differs is not a finding. It is the definition of the knob.

This is the same defect this programme has recorded before, in a different guise: a gate scored by a classifier over the generator's own output shapes measures the generator's menu, not the phenomenon.

**Mandatory control if the trap is live — the MECHANICAL-EFFECT NULL.** Compute the detector under each ablation arm *with evolution disabled*: same initial population, same operator settings, no selection, no reproduction, measured at generation zero. That is the immediate, definitional effect of the parameter on the exploration distribution.

The claim of interest is then not "the arms differ" but:

> Does the detector divergence between arms **exceed the mechanical-effect null**, and does it **grow over generations** as populations restructure themselves?

Only the excess is evidence about evolutionary dynamics. The mechanical part is arithmetic.

If the observed divergence is fully accounted for by the mechanical null at all times, the verdict is **N5-adjacent**: the mechanism moves the detector definitionally and tells us nothing about accessibility dynamics. That is a legitimate and publishable-internally negative.

### TRAP 2 — mathematical coupling makes T2 invalid

The directive is explicit: *"If detector and outcome are mathematically coupled, T2 is invalid. State that explicitly."*

The risk is concrete. If the outcome is fitness on a smooth function and the detector is a spread statistic of the offspring phenotype distribution, then as a population converges, offspring spread contracts **because** the population has converged. Detector and fitness are then two readings of the same underlying convergence, and "the detector moved first" is a statement about which readout is noisier, not about precedence.

**Test for coupling, to be run BEFORE any T2 claim is made:**

1. Derive whether the detector statistic is a deterministic function of the same population state that determines the outcome statistic. If yes under the historical physics, **T2 is declared invalid in advance** and only T1 and T3 remain available.
2. If not analytically decidable, run the empirical check: within a single arm, regress the detector on the contemporaneous outcome across replicates and generations. A high deterministic relationship means the "lead" is a rescaling artifact.

**The only regime in which precedence is informative is a fitness plateau.** A detector change that occurs while the outcome is statistically indistinguishable from flat, and is followed by an outcome change, is a real precedence observation. A detector change that tracks a moving outcome is not.

So the T2 window is preregistered as: **detector change measured inside a window where the outcome's slope is not distinguishable from zero at the run level.** If no such window exists in the historical design, T2 is not attempted.

---

## 2. CLAIM LADDER, AND WHAT EACH REQUIRES

| Level | Claim | Minimum requirement | Currently |
|---|---|---|---|
| **T1** | The detector statistic differs across arms in association with acquisition differences | arms differ by more than the mechanical-effect null, at run-level uncertainty | available if T0 passes |
| **T2** | A preregistered detector change occurs consistently before an acquisition change | Trap 2 cleared: detector and outcome not mathematically coupled, and a genuine outcome plateau exists | **conditional, may be ruled out in advance** |
| **T3** | The intervention alters both detector trajectory and later acquisition in the predicted dependency pattern | the ablation is a genuine intervention and acquisition genuinely occurs | conditional on the ablation having an adaptive outcome at all |

**T3 is the strongest result the historical design can support. Nothing beyond it may be claimed.**

A prior pass reported that one candidate ablation ran on a unimodal sphere function, where "there is no *what* that gets acquired, only *how fast*". **If the ablation's outcome variable is a scalar optimisation speed rather than an acquisition of something, T3 is unavailable and the experiment can only reach T1.** That determination is part of T0.

---

## 3. UNIT OF ANALYSIS — frozen now

The independent replicate is **the run**. Not the generation, not the individual, not the offspring sample, not a lineage point.

Every uncertainty reported is computed across runs. Temporal points within a run are not independent and will not be counted as such. Offspring samples within an individual are estimator noise, not replication.

To be reported: historical n, modern n, and the reason modern replication is required.

---

## 4. PRIMARY DETECTOR STATISTIC — BLOCKED ON T0

Cannot be frozen until the historical definition is recovered. It **must be Toussaint's own statistic**, not a Prometheus substitute. GATE-3 is closed: no invented measure.

To be filled from `TOUSSAINT_DETECTOR_SPEC.md`: the exact statistic, the sampling scheme, the sample count and its unit, whether distributions or scalars are retained, and the reported estimator noise.

If his statistic proves inadequate, that is **reported after the faithful test**, never substituted before it.

## 5. SMOOTHING, LEAD-TIME WINDOW, CHANGE-POINT DEFINITION — BLOCKED ON T0

Cannot be chosen without knowing the estimator's noise level, since a change-point threshold below the noise floor is not a gate. This programme has already been burned twice by thresholds set without reference to their own standard error, and once by a gate above the maximum attainable value.

**Rule fixed now:** the detector change threshold must exceed the estimator's own noise, measured empirically in the shakedown, and the attainable range must be computed before the threshold is set.

## 6. NULL MODEL — BLOCKED ON T0

Two nulls are required, and the first is not optional:
1. **Mechanical-effect null** (section 1): the arms' detector difference with evolution disabled.
2. A null that perturbs the axis the statistic varies on. Its form depends on the recovered physics.

## 7. HISTORICAL VALIDATION TARGETS — BLOCKED ON T0

At least three independent historical observables must be hit before HC-T01 is interpreted at all. They must be independent of the missing-cell result. Recorded in `HISTORICAL_VALIDATION_TARGETS.md`. If the reconstruction misses them materially, the verdict is `RECONSTRUCTION_FAILS` and HC-T01 is not interpreted.

---

## 8. THE SENTENCE THAT STAYS IN THE REPORT

Per directive section 16, verbatim:

> Did the historical mechanism change the distribution of future variation in a way that altered what the population subsequently acquired?

Not "did one arm explore more".

---

## 9. ADMISSIBLE OUTCOMES, none preferred

Broader exploration precedes adaptation. Narrower exploration precedes adaptation. Distribution shape changes without fitness change. Detector changes simultaneously with adaptation. No detector difference between arms. Detector moves but has no relationship to future acquisition.

And the eight first-class negatives from directive section 20, of which N3, N5 and N7 are currently the most likely on the seat's own reading: the lead is mathematically coupled to the outcome; the mechanism changes fitness without changing accessibility; or the combined experiment already exists historically.

**No direction is preferred, and the missing-cell hypothesis will not be rescued.**
