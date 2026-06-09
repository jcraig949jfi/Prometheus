# Proposed Battery Additions from Kill Audit
## 2026-04-11 Session

---

## F15: Log-Transform Invariance Test

**What it does:** For any claimed "moment ratio matches X" finding, apply log-transform to the distribution and recompute M4/M2^2. If the log-transformed ratio collapses to ~1.0, the original match is a tail-heaviness artifact, not structural.

**Kill mechanism:** A distribution can have M4/M2^2 = 2.0 simply because its log-distribution has a specific kurtosis, not because it shares algebraic structure with SU(2). The test separates "tail shape coincidence" from "genuine algebraic constraint."

**Implementation:**
```python
def F15_log_invariance(values, claimed_match):
    """Returns FAIL if log-transform collapses the ratio to ~1.0"""
    raw_ratio = compute_M4_M2_ratio(values)
    log_ratio = compute_M4_M2_ratio(np.log(values[values > 0]))
    
    # If log-ratio is near 1.0, the raw ratio is just measuring tails
    if log_ratio < 1.2:
        return "FAIL", f"Log-transform collapses ratio from {raw_ratio:.3f} to {log_ratio:.3f}"
    
    # If log-ratio is far from 1.0, the structure survives transformation
    return "PASS", f"Log-ratio {log_ratio:.3f} preserves structure"
```

**Threshold:** log_M4/M2^2 < 1.2 → FAIL (tail artifact). > 1.5 → PASS (structural).

**What it caught this session:**
- Knot det 2.16 → log 1.11 → **WOULD FAIL** (tail artifact)
- G2 conductor 3.01 → log 1.05 → **WOULD FAIL** (tail artifact)
- This means the moment hierarchy "constraint spectrum" interpretation is suspect

**What it DOESN'T catch:** The G2 conductor matching USp(4)=3.0 exactly. The log-collapse tells us the mechanism is tail-shape, but it doesn't explain WHY the tail shape gives 3.0 specifically. A secondary test (bootstrap CI against predicted value) is still needed.

**Pairing:** F15 should run alongside a new F16 (predicted value match):

## F16: Predicted Value Bootstrap Test

**What it does:** For any claimed "M4/M2^2 matches X" where X has a theoretical prediction, compute bootstrap 95% CI and check if X falls inside.

**Implementation:**
```python
def F16_predicted_match(values, predicted, n_bootstrap=1000):
    """Returns PASS only if predicted value is inside 95% CI"""
    ratios = []
    for _ in range(n_bootstrap):
        sample = rng.choice(values, len(values), replace=True)
        sn = sample / np.mean(sample)
        m2 = np.mean(sn**2); m4 = np.mean(sn**4)
        ratios.append(m4/m2**2)
    lo, hi = np.percentile(ratios, [2.5, 97.5])
    if lo <= predicted <= hi:
        return "PASS", f"Predicted {predicted} inside CI [{lo:.4f}, {hi:.4f}]"
    return "FAIL", f"Predicted {predicted} OUTSIDE CI [{lo:.4f}, {hi:.4f}]"
```

**What it caught this session:**
- Knot det 2.16 vs SU(2)=2.0: CI=[2.092, 2.217] → 2.0 OUTSIDE → **FAIL** (not SU(2))
- G2 conductor 3.01 vs USp(4)=3.0: CI=[2.984, 3.032] → 3.0 INSIDE → **PASS**

## F17: Confound Detrending Test

**What it does:** For any enrichment claim, identify the most obvious confounding variable (energy scale, group size, sample composition) and recompute enrichment after controlling for it.

**Kill mechanism:** If enrichment drops by >50% after controlling for one confound, the original enrichment was dominated by that confound. The finding may still survive but the corrected value must be reported.

**Implementation:**
```python
def F17_confound_detrend(within_pairs, across_pairs, confound_groups):
    """Recompute enrichment within confound strata"""
    # Stratify by confound, compute enrichment within each stratum
    # Return the pooled within-stratum enrichment
    # FAIL if enrichment drops > 50%
```

**What it caught this session:**
- C1: 16.4x → 11.8x after detrending by element energy scale (28% drop, PASS)
- C4: r=0.67 → r=0.37 after removing cuprates (44% drop, borderline)
- C12: 3.71x → 2.64x after controlling for module size (29% drop, PASS)

## Summary: Three new battery tests

| Test | What it kills | Threshold |
|------|--------------|-----------|
| F15 Log-Transform | Tail-heaviness masquerading as structure | log_ratio < 1.2 |
| F16 Predicted Match | Vague "near X" claims without statistical rigor | X outside 95% CI |
| F17 Confound Detrend | Enrichment inflated by lurking variable | >50% drop after control |

These three tests would have caught or refined 5 of our 37 wins. That's a 14% correction rate — significant. The battery should include them for all future measurements.
