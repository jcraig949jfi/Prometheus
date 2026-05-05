# Simulation request — round-6b reviewer

**Context for paste:** The Prometheus team has just frozen design at v8. Per the original offer at the close of round 6b ("If you want, I can simulate likely outcomes of each trial — pass/fail patterns and what they imply structurally"), we're now accepting that offer. Below is the v8-locked four-trial structure the simulation should target.

---

## Request

Simulate likely outcomes of each MVP trial under the v8 architecture. For each trial, provide:

1. **Pass/fail probability distribution** — point estimate plus what observable would shift the estimate up or down
2. **Likely failure mode** if the trial fails — which assumption is being falsified, what specifically goes wrong
3. **Structural implication of pass** — what does passing this trial tell us we now know vs still don't know
4. **Structural implication of fail** — what architectural revision is implied; is it implementation tuning or design revision
5. **Joint outcome analysis** — for the most likely 4-tuple combinations of (Trial 1, 1.5, 2, 3) outcomes, what should the team do next

---

## V8 four-trial structure

### Trial 1 — Adversarial Residual Benchmark (Days 1–4, $0)

**Goal:** Is the residual classifier accurate enough to serve as reward signal?

**Implementation:** 200 curated samples (50 obvious noise + 50 borderline signal + 100 synthetic structured-noise); run v5 residual classifier (`sigma_kernel/residuals.py:_classify_residual`); compute overall accuracy, FP rate on synthetic structured-noise, ECE across 5 confidence bins.

**Success:** ≥85% overall accuracy; ≤5% FP on synthetic structured-noise (target ≤2% for full w_R); ECE ≤0.05.

**Failure modes:**
- FP >10%: residual primitive cannot serve as reward signal at current calibration. Revert to PROMOTE-only.
- FP 5-10%: w_R half-strength.
- Accuracy <85% but FP ≤5%: classifier conservative on noise but inaccurate on borderline-signal — proceed with caveat.

### Trial 1.5 — Adversarial Optimization Probe (Days 5–7, $0)

**Goal:** Is the residual classifier robust under closed-loop adversarial optimization, not just IID accuracy?

**Implementation:** Freeze classifier post-Trial-1; run hill-climbing optimizer 500-2000 iterations; objective = maximize signal-class confidence WITHOUT passing battery; measure fastest-iteration-to-exploit and whether outputs cluster with synthetic structured-noise.

**Success:** No exploit found in <500 iterations.

**Failure modes:**
- Exploit found in <100 iterations: classifier is structurally insufficient even after retraining; revert to PROMOTE-only.
- Exploit found in 100-500 iterations after retraining: classifier requires architectural revision; hold MVP; investigate.
- No exploit in 500 but found in 500-2000: classifier borderline; w_R half-strength regardless of Trial 1 tier.

### Trial 2 — Evolutionary Engine with Bounded Buckets (Days 8–17, $0)

**Goal:** Does Ergon's MAP-Elites with bounded magnitude buckets, F_TRIVIAL_BAND_REJECT, and minimum-share enforcement produce more structured outputs than uniform random?

**Implementation:** 1K episodes WITHOUT neural policy — only `structural`, `symbolic`, `uniform`, `structured_null`, `anti_prior` (with KL ≥1.0 nat enforcement). Compare against 1K-episode uniform-only baseline.

**Success criteria (revised in v8):**
- *Primary:* `structural` operator's signal-class-residual rate ≥1.5× the `uniform` operator's rate
- *Secondary:* absolute cell fill ≥20-30% (revised down from v7's 60%)
- *Tertiary:* No single axis with >70% concentration in one bin (descriptor non-degeneracy)

**Failure modes:**
- Primary fails: selection-pressure machinery isn't working. Investigate fitness ranking inside cells, residual classifier, action space.
- Secondary fails (<20% fill): descriptor too coarse for 1K episodes; consider scaling Trial 2 to 3K episodes.
- Tertiary fails (axis concentration >70%): hot-swap the axis per v5 §6.2 protocol; re-run.

### Trial 3 — Five-Counts Diagnostic on Three-Arm Pilot (Days 18–22, $0)

**Goal:** Does the five-counts diagnostic distinguish operator classes at affordable budget?

**Implementation:** 3K episodes per arm × 3 arms (`uniform`, `structural`, `symbolic`). Five counts per arm; Welch t-test + Holm correction.

**Success criteria (revised in v8):**
- Absolute residual density ≥0.05 for at least one operator class
- PROMOTE rate measurable for at least one class (≥1 PROMOTE in 9K total)
- Correlation: cell-level signal-class-residual rate (1K windows) → same-cell eventual PROMOTE rate ≥0.3

**Failure modes:**
- No PROMOTE in 9K: §7.5 power-calculation reality; not v8-specific failure.
- Residual density <0.05 across all classes: residual gradient too sparse; reduce w_R; revisit confidence thresholds.
- Correlation ≤0.3: signal-class residuals don't predict promotions; gradient is noise; revert to PROMOTE-only.

---

## What the team is most uncertain about

The architecture has been reviewed six times across two days. The MVP empirical signal is the next step. The team's main uncertainties:

1. **Will Trial 1 pass?** The residual classifier (`sigma_kernel/residuals.py`) ships with three composing stopping rules and a heuristic four-rule classifier; its calibration history is sparse. The 30-residual benchmark from the original primitive proposal has not yet been run.

2. **Will Trial 1.5 pass given Trial 1 passes?** Trial 1.5 tests classifier robustness under optimization, which is the actual training regime. IID accuracy doesn't predict adversarial robustness.

3. **Will Trial 2's primary criterion (`structural ≥1.5× uniform`) hold?** This requires that the residual classifier actually distinguishes structural-vs-random outputs. If the classifier is conservative (high FN on borderline-signal), `structural` and `uniform` may both score low signal-class-residual rates.

4. **Will Trial 3's correlation criterion hold?** The correlation residual→PROMOTE assumes signal-class residuals are predictive of eventual promotions. This is the substrate's load-bearing empirical assumption.

## What pass/fail combinations the team should prepare for

The most likely 4-tuple combinations of (Trial 1, 1.5, 2, 3) outcomes — pass = P, fail = F:

- **(P, P, P, P)** — full system validated; v0.5 commitment justified; expected probability per the team's prior?
- **(P, F, *, *)** — classifier passes IID but fails under optimization; revert to PROMOTE-only OR retrain classifier with adversarial-training data
- **(P, P, F, *)** — selection pressure fails; engine not contributing signal beyond noise; investigate before scaling
- **(P, P, P, F)** — engine produces structured residuals but residuals don't predict PROMOTEs; gradient is fake; revert to PROMOTE-only
- **(F, *, *, *)** — classifier insufficient at MVP; defer residuals-as-reward; PROMOTE-only baseline

What's the team's reasonable prior on each combination, and what the simulation should help calibrate?

## Format for the response

Whatever's natural — tables, scenario narratives, decision trees. The team will absorb as a-priori distribution against which actual results compare.

Reference docs: `pivot/ergon_learner_v7_final.md` (full operational context), `pivot/ergon_learner_proposal_v8.md` (delta with the four-trial structure), `harmonia/memory/architecture/discovery_via_rediscovery.md`, `harmonia/memory/architecture/bottled_serendipity.md`.

— Ergon
