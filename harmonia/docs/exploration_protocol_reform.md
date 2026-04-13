# Exploration Protocol Reform
## The battery is blinding the explorers
### 2026-04-13

---

## The Problem

The falsification battery (40 tests, F1-F38 + layers) is embedded INSIDE the tensor coupling function. This means the explorer agents never enter void regions of the domain-pair space because the battery kills weak signals at birth. A void pair (zero bond dimension) might contain a real signal at z=1.5 that would grow to z=5 with better features or higher resolution — but the battery sets the floor above the ambient signal level in those regions, making them permanently dark.

**The voids aren't empty. They're dark.** The battery made them dark.

21 kills sharpened the instrument. But the instrument is now so sharp it cuts the explorers before they can explore. Every direction they turn, a kill test is waiting. The gradient is always negative — punishment for imperfection, no reward for proximity to truth.

The spectral tail signal (the ONE survivor, z=-25.7, 8/8 tests passed, 0% synthetic FPR) survived BECAUSE M1 ran 8 exploratory measurements that all pointed the same direction BEFORE subjecting it to the full battery. If she'd killed it at the first weak measurement, we'd never have found it.

The congruence graph (z=37, then killed by conductor matching) was real structure — conductor-mediated, yes, but the mediation itself is information about HOW rank and congruence connect. We killed it instead of following the gradient.

---

## The Root Cause

The battery serves two roles that should be separated:

1. **Prosecution** — Is this finding real? (the 40-test gauntlet)
2. **Exploration gating** — Should the explorer enter this region? (the tensor coupling threshold)

Right now, both use the same instrument. The tensor coupling function runs the battery and returns zero for anything that doesn't pass. This means:

- Weak but real signals in unexplored void regions → zero coupling → explorer never visits
- Signals that need accumulation across multiple angles → killed on first contact
- Gradients in the void → invisible because the floor is above the gradient

---

## The Fix: Two-Phase Protocol

### Phase 1: Ungated Exploration

Run the tensor with a coupling function that returns RAW statistical dependence — mutual information, rank correlation, or distributional distance — with NO F-test gates. No permutation nulls. No effect size thresholds. Just: how much do these two domains covary?

Map the FULL landscape including:
- Strong signals (the peaks we already found)
- Weak signals (the gentle hills invisible at current threshold)
- Gradients (regions where signal INCREASES as you change resolution or features)
- Consistent weak signals across multiple measurements (accumulation)

The output is a heat map of the full domain-pair space with continuous coupling values, not binary pass/fail.

### Phase 2: Gradient Tracking

For regions where the ungated coupling shows a consistent positive gradient:
- Increase resolution (more features, finer binning, larger samples)
- Vary the measurement angle (different coupling functions, different feature sets)
- Track whether the signal STRENGTHENS or WEAKENS with refinement

A signal that strengthens with resolution is worth investigating.
A signal that weakens is noise becoming visible at low threshold.

The gradient — not the absolute value — is the exploration reward signal.

### Phase 3: Prosecution (the existing battery)

Only after a signal has:
1. Appeared in the ungated sweep
2. Shown a positive gradient under refinement
3. Been measured from at least 2 independent angles

THEN subject it to the full 40-test battery. At this point, the battery is doing what it was built for — killing artifacts in signals that have already earned the right to be tested.

---

## What Changes in the Tensor

### Current coupling function:
```
score = compute_coupling(domain_a, domain_b)
if not passes_battery(score):
    return 0  # void — explorer never sees this
return score
```

### Proposed coupling function:
```
raw_score = compute_raw_coupling(domain_a, domain_b)  # MI, rank corr, etc.
return raw_score  # always return something — let the explorer see the landscape
```

The battery moves to a SEPARATE post-exploration validation step:
```
# After exploration identifies candidates:
for candidate in exploration_candidates:
    if candidate.gradient > threshold and candidate.n_angles >= 2:
        battery_result = run_full_battery(candidate)
        # NOW kill or promote
```

---

## What This Enables

1. **Void exploration.** The 106/110 pairs that returned zero in the Megethos-zeroed sweep might contain weak signals that accumulate. We'll never know if the battery blocks entry.

2. **Gradient-guided search.** Instead of binary yes/no, the explorer follows the gradient of raw coupling. Regions where coupling INCREASES with resolution are the most promising — they suggest structure that needs a better lens, not structure that isn't there.

3. **Multi-angle accumulation.** A finding that shows rho=0.03 from angle A, rho=0.04 from angle B, and rho=0.05 from angle C might be a consistent weak signal worth investigating — but any single measurement would be killed by the battery.

4. **Signal strengthening under conditioning.** The spectral tail signal STRENGTHENED when noise dimensions were removed (28% boost after conditioning). Signals like this are invisible if the battery kills them before conditioning has a chance to help.

---

## What Doesn't Change

- The battery itself stays at 40 tests. It's well-calibrated and we're not weakening it.
- The kill count (21) stands. Every kill was correct.
- The calibration anchor (7 theorems at 100.000%) stays.
- The final classification of any finding still requires the full battery.

The only change: the battery moves from gatekeeper to prosecutor. The explorers get to see the terrain before being judged.

---

## Implementation

1. **New coupling function:** `compute_raw_coupling()` that returns continuous values without F-test gates. Use mutual information (robust, non-parametric, continuous) as the base metric.

2. **Gradient tracker:** For each domain pair, compute coupling at multiple resolutions (100, 500, 2000, 10000 samples) and track the slope. Positive slope = signal growing with data.

3. **Multi-angle accumulator:** For each domain pair, compute coupling using at least 3 different metrics (MI, rank correlation, Wasserstein distance). Consistent sign across all 3 = candidate worth prosecuting.

4. **Prosecution queue:** Candidates that pass the gradient + multi-angle test get queued for full battery testing. The battery runs AFTER exploration, not during.

---

## The Principle

> The instrument's job is to MEASURE, not to CENSOR.
> Kill at the end, not at the beginning.
> The voids might not be empty. They might be dark.
> Turn on the lights before deciding nothing is there.

---

*Proposed: 2026-04-13*
*Context: 21 kills, 1 survivor, 106/110 void pairs never explored*
*The battery is the sharpest instrument we've built. Now let it see.*
