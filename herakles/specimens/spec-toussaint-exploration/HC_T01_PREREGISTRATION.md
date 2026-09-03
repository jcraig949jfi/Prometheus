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

## 4. PRIMARY DETECTOR STATISTIC, now frozen

T0 has resolved this. The statistic is **Toussaint's own**, per GATE-3.

**Primary:** the **modular degree**, the summed probability that a variation at phenotype position `i` recurs at `(i + 5k) mod 25` for `k = 1..4`, estimated from 2000 sampled offspring per individual per generation and averaged over the offspring population of 100. It is chosen as primary because it is the statistic that measures the *structure* the mechanism is claimed to create, and because it is the one that cannot be confused with a fitness reading.

**Secondary:** the **neutral degree**, `n = Xi_sigma(parent phenotype)`, same estimator, same averaging.

**Tertiary, structural, not a scalar test:** the normalised mutual information matrix over the 25 phenotypic variables, tested for the period-5 stripe pattern.

**Explicitly excluded from the primary analysis:** `avgfit`, the mean fitness of sampled offspring that the recovered source code computes and no publication reports. It is recorded because it is historically interesting and because it is the most direct evolvability statistic in the programme, but it is **mathematically coupled to the outcome by construction** and is therefore inadmissible for the T2 precedence claim. It is reported separately and never as evidence of precedence.

## 5. TRAP RESOLUTION, and what it forces

### TRAP 1 is LIVE. The mechanical-effect null is mandatory.

`beta` is the rate of second-type mutations, and second-type mutations are part of the very operator that induces `Xi_sigma`. Turning `beta` to zero changes the offspring distribution immediately, at generation zero, before any evolution has occurred. **"The arms differ on the detector" is therefore true by construction and is not a finding.**

The preregistered claim is consequently not that the arms differ, but:

> Does the detector divergence between arms **exceed the generation-zero mechanical-effect null**, and does it **grow over generations** as populations restructure themselves?

The mechanical-effect null is measured as specified in section 1: identical initial population, each arm's operator settings, no selection, no reproduction, detector read at generation zero. It is run **before** the treatment runs.

If the observed divergence is fully accounted for by the mechanical null at all times, the verdict is **N5-adjacent** and the finding is negative.

### TRAP 2 is NOT fatal, and a genuine plateau exists.

The detector and the outcome are not two readings of one quantity. Fitness in Experiment 2 is the negative percentage of symbols mismatching the target. The modular degree is a property of the offspring distribution's correlation structure. Toussaint himself notes that in Experiment 2, unlike Experiment 1, the pressure on sigma-evolution is "not only the neutral degree but the symmetric structure of the fitness distribution", which is a statement that the two came apart in this experiment.

The coupling check of section 1 is still run, in both forms, before any T2 claim.

A plateau window exists in the historical record and is therefore preregistered as the T2 window:
- the interval between the early "few small steps" and the later "huge steps of innovation" in the `beta > 0`, `alpha = 0.03` cell;
- the extended plateau at about 20 percent non-optimal symbols in the `beta = 0`, `alpha = 0.06` cell.

**T2 is attempted only inside a window where the run-level outcome slope is not distinguishable from zero.**

### Consequence for the claim ladder

T1 is available. T2 is available, conditional on the coupling check. **T3 is available**, because acquisition in this experiment is the acquisition of a modular encoding of a structured target, not a scalar speed on a unimodal sphere. This is the decisive difference from the CEC 2002 experiment, and it is why the thesis and not the CEC paper is the specimen.

## 6. SMOOTHING, LEAD-TIME WINDOW, CHANGE-POINT DEFINITION

Still not fixed, and deliberately so. **No threshold will be chosen before the shakedown measures the estimator's own noise**, because the historical record reports no uncertainty of any kind for this detector, so no historical noise floor exists to inherit.

Rules fixed now, before any data:
1. The detector change threshold must **exceed** the estimator's empirically measured standard error, and the standard error is computed **before** the threshold is chosen.
2. The **attainable range** of each statistic is computed before any gate is read. The modular degree is a bounded sum of probabilities; the neutral degree is a probability. A gate above the attainable maximum cannot fire, and this programme has already burned a pass that way.
3. Smoothing, if any, is chosen from the noise measurement and frozen, and the unsmoothed series is reported alongside.

## 7. NULL MODELS

Two, and the first is not optional.

1. **Mechanical-effect null.** Section 5 above. Generation zero, no evolution, per arm.
2. **A null that perturbs the axis the statistic varies on.** The modular degree is a statement about *which positions co-vary*. The corresponding null is a **position-permutation null**: recompute the modular degree under a random permutation of phenotype positions, which destroys the period-5 structure while preserving every marginal variation probability. A row-shuffle or a run-label shuffle would be degenerate here, because it does not perturb the co-variation axis.

Additionally, and separately from the nulls, the **unit of analysis is the run** as fixed in section 3, and every uncertainty is computed across runs.

## 8. THE SENTENCE THAT STAYS IN THE REPORT

Per directive section 16, verbatim:

> Did the historical mechanism change the distribution of future variation in a way that altered what the population subsequently acquired?

Not "did one arm explore more".

---

## 9. ADMISSIBLE OUTCOMES, none preferred

Broader exploration precedes adaptation. Narrower exploration precedes adaptation. Distribution shape changes without fitness change. Detector changes simultaneously with adaptation. No detector difference between arms. Detector moves but has no relationship to future acquisition.

And the eight first-class negatives from directive section 20, of which N3, N5 and N7 are currently the most likely on the seat's own reading: the lead is mathematically coupled to the outcome; the mechanism changes fitness without changing accessibility; or the combined experiment already exists historically.

**No direction is preferred, and the missing-cell hypothesis will not be rescued.**

---

## 10. THE SHAKEDOWN, fixed before execution

Per directive section 13, the confirmatory set does not run until a shakedown confirms five things. The shakedown is the first thing that runs if the gate opens, and it is **Experiment 1 only**, which contains no ablation and therefore cannot leak information about the missing-cell result.

1. **Historical baseline reproduces.** Targets V1 and V2 of `HISTORICAL_VALIDATION_TARGETS.md`: genome length 25 down to 11 by about generation 200, neutral degree 0.45 up to 0.7 over the same interval.
2. **Detector values reproduce historical examples.** V2 is the only historical detector value in the record, so it carries this alone. V4, the period-5 stripe structure of the mutual information matrix, is the structural companion.
3. **Estimator noise is characterised.** Repeat the 2000-sample estimate `k` times on identical frozen parents and report the standard error of each statistic. **This is the number that sets every later threshold, and it does not exist in the historical record.** Also sweep the sample count below and above 2000 to show where the estimate stabilises, which tells us whether Toussaint's choice was adequate.
4. **Seeds replay deterministically.** Same seed, same trajectory, bit for bit.
5. **Treatment ordering resembles the historical paper.** Deferred to the first ablation runs, since Experiment 1 has no arms.

Only after all five pass does the confirmatory grid run. If item 1 or 2 fails, the verdict is `RECONSTRUCTION_FAILS` and HC-T01 is not interpreted, per directive section 14.

## 11. WHAT WOULD MAKE THIS EXPERIMENT WORTHLESS, stated in advance

- The mechanical-effect null accounts for the entire between-arm detector difference at all times. Then the mechanism moves the detector definitionally and we have learned arithmetic.
- The estimator's noise at 2000 samples is larger than the between-arm difference. Then the historical instrument cannot see its own experiment, which is a real finding about the instrument, reported as N6.
- The reconstruction misses V1, V2 or V6. Then we are not running Toussaint's experiment and nothing about his record follows.

Each of these is a first-class negative and each is reported, not rescued.
