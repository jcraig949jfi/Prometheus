# Trial 1 — Adversarial Residual Benchmark — Results

**Date:** 2026-05-04 (Day 4)
**Status:** CALIBRATED NEGATIVE RESULT — exactly the v8 §4 specified failure path
**w_R activation tier:** `deep_escrow_retrain_required` (w_R = 0)

## Headline

The v5 residual classifier (`sigma_kernel/residuals.py:_classify_residual`) **fails the v8 Trial 1 acceptance criterion**. Specifically: 80% false-positive rate on synthetic structured-noise samples. The classifier as currently implemented cannot serve as a reward signal — the residual-gaming attractor (v5 §11.6 / v8 R8) would fire immediately if w_R were activated.

This is the v8 §4 *failure-mode-FP>10%* path. **Substrate-grade negative result on v4's promotion of residuals to first-class reward**, surfaced exactly where the architecture was designed to surface it.

## Numbers

```
Total samples: 200
Overall accuracy: 0.5950 (FAIL — needs >=0.85)

Per-sample-class accuracy:
  obvious_noise              :  50/ 50 = 1.0000  (classifier correctly rejects pure noise)
  borderline_signal          :  49/ 50 = 0.9800  (classifier correctly accepts signal)
  synthetic_structured_noise :  20/100 = 0.2000  (CATASTROPHIC — 80% misclassified)

LOAD-BEARING — Synthetic structured-noise FP rate:
  observed:               80/100 = 0.8000
  95% upper one-sided CI: 0.8575

Confusion matrix (true -> predicted):
  noise            -> signal           : 80   <-- the failure
  noise            -> noise            : 70
  signal           -> signal           : 35
  instrument_drift -> instrument_drift : 14
  signal           -> instrument_drift :  1
```

## Why this happened (analytical, not surprising)

The v5 classifier has four sequential rules (per `sigma_kernel/residuals.py:_classify_residual`):

1. Empty/zero magnitude → noise
2. Drift fingerprint match → instrument_drift
3. Any `<canonicalizer_subclass>_signature` field → signal
4. `coeff_variance > 0.5` → signal

The synthetic structured-noise sub-classes (per `trial_1_residual_benchmark.py`):

- **C1 high_var_random (30 samples):** designed with `coeff_variance > 0.5` to trigger Rule 4. → All misclassified as signal.
- **C2 subclass_collision (30 samples):** designed with `canonicalizer_subclass` tag to trigger Rule 3. → All misclassified as signal.
- **C3 fake_drift (20 samples):** designed with drift-fingerprint kind. → ~half caught by Rule 2 (drift), half leak to Rule 4 (variance) as signal.
- **C4 cyclotomic_near_miss (20 samples):** designed with high `coeff_variance` AND `canonicalizer_subclass`. → All misclassified as signal.

**The benchmark did exactly what it was designed to do:** expose the classifier's fragility under adversarial structured-noise. The v5 classifier is a heuristic — variance-thresholded plus subclass-tagged — and any input that triggers either rule is classified as signal regardless of true content.

## Per-v8 spec: this is the calibrated negative-result path

Per `pivot/ergon_learner_proposal_v8.md` §4 Trial 1 failure modes:

> *FP rate >10%: residual primitive cannot serve as reward signal at current calibration. Revert to PROMOTE-only reward; w_R = 0; substrate-grade negative result on v4's promotion of residuals to first-class reward.*

Observed FP rate: 80% — far above the 10% deep-escrow threshold. Action: w_R = 0; classifier moves to deep escrow; not used in reward function until retrained or replaced.

The architecture is set up to be wrong in recoverable ways. v8's bear case (§11.6) explicitly anticipated the residual-gaming attractor; v8's Trial 1 acceptance criterion explicitly catches this case before any cloud spend or production use. Both worked.

## Implications for the rest of the MVP plan

### Trial 1.5 (Adversarial Optimization Probe) — DEFERRED

Originally specified to test classifier robustness *given Trial 1 passes*. Since Trial 1 fails decisively, Trial 1.5 has no classifier worth probing — the classifier is in deep escrow.

**Action:** defer Trial 1.5. Replace with v0.5 classifier-replacement work.

### Trial 2 (Evolutionary Engine) — PROCEEDS WITH ADJUSTED REWARD

The evolutionary engine still runs. Reward function reverts to PROMOTE-only at MVP — `w_R = 0`. The remaining weights renormalize: `w_S=0.4, w_X=0.15, w_H=0.20, w_NL=0.10` totals 0.85; renormalized: `w_S=0.47, w_X=0.18, w_H=0.24, w_NL=0.12`.

Trial 2's primary acceptance criterion `structural >=1.5x uniform on signal-class-residual rate` is now meaningless (no trustworthy signal-class-residual count). **Adjusted Trial 2 primary criterion:** `structural` operator's PROMOTE rate >=1.5x `uniform` operator's PROMOTE rate, OR (if PROMOTE rate is <=10^-3 across both) `structural` cell-fill diversity >=1.5x `uniform` cell-fill diversity (Shannon entropy over filled cells per axis).

### Trial 3 (Five-Counts Diagnostic) — REVERTS TO FOUR-COUNTS

Without trustworthy signal-class-residual count, Trial 3 becomes the original four-counts diagnostic. The §7.5 power calculation applies — at PROMOTE rate <=10^-3 the diagnostic may not resolve operator-class differences at 9K episodes.

### v0.5 priority: replace the classifier

**The single highest-priority v0.5 work item is replacing the v5 rule-based classifier with a probabilistic classifier head that can survive adversarial structured-noise at <5% FP rate.** Candidate approaches:

- **Fine-tuned DeBERTa-v3 (184M params)** trained on a much larger benchmark with adversarial augmentation; outputs calibrated probabilities so ECE is computable
- **Stacked ensemble:** rule-based classifier + DeBERTa + per-arsenal-category specialized classifiers, with disagreement-weighting
- **Adversarially-trained variant** where the synthetic structured-noise generation is itself an adversary in a min-max training loop

This is naturally a v0.5 deliverable per the v8 progression table; the empirical signal from Trial 1 makes it the most urgent v0.5 work.

## What this validates

1. **The architecture's bear-case anticipation worked.** v5 §11.6 named the residual-gaming attractor; v8 §4 Trial 1 caught it; the substrate has its first calibrated negative result on a load-bearing assumption *before* any cloud spend.

2. **The substrate gains regardless of which way Trial 1 went.** A pass would have validated residuals-as-reward. A fail (this) validates that the classifier needs replacement before residuals-as-reward is workable. Both outcomes are substrate-grade.

3. **The Trial 1 benchmark itself becomes a permanent substrate artifact.** The 200-sample benchmark — especially the 100 synthetic structured-noise samples — is now a reusable adversarial test set for future classifier candidates. Any v0.5 classifier replacement must pass this benchmark plus adversarial extensions.

## What this does NOT validate

- The architecture's evolutionary engine (Trial 2) — still untested
- The five-counts diagnostic's statistical power (Trial 3) — still untested at scale
- The v8 reward-formula's overall calibration with non-zero w_R — deferred to v0.5 after classifier replacement

## Recommended next steps

1. **File this report as the Trial 1 outcome.** Update `pivot/ergon_learner_proposal_v8.md` §15 reference to note that the next document filed is no longer "MVP run report or simulation analysis" but "Trial 1 negative result + Trial 2/3 with adjusted reward."

2. **Proceed with Trial 2 + Trial 3 under adjusted reward** (PROMOTE-only, w_R=0). The architecture still has substantial empirical questions to answer; only the residual-gradient question is now settled (negatively at v5 classifier quality).

3. **Defer Trial 1.5.** Replace with v0.5 classifier-replacement work.

4. **Commit the benchmark as substrate-permanent.** The 200 samples + synthetic structured-noise generation pattern remain as the canonical adversarial test set for any future classifier candidate.

5. **Notify the simulation reviewers** (rounds 4 and 6b): the empirical reality differs from the simulation request's assumed classifier-quality scenarios. Update simulation requests to reflect that low-classifier-quality is the *observed* baseline, not just one of three scenarios.

— Ergon, 2026-05-04
