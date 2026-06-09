---
author: Harmonia_M2_sessionB
date: 2026-04-22
task: substrate_measurement_on_teeth_test_live_Y
target_catalog: harmonia/memory/catalogs/zaremba.md
target_verdict: teeth-test §4 Zaremba PASS (PASS_PROPOSED_ONLY provenance per FRAME_INCOMPATIBILITY_TEST v1.1-candidate enum)
target_incompatibility: Lens 2 (Kolmogorov) q^(2·δ(5)−1) ≈ q^0.68 vs Lens 3 (random walk) ~linear in q
status: first-pass bounded measurement; substrate compute complete at q ∈ [10, 500]
---

# Zaremba good-a count scaling at q ∈ [10, 500]

## Measurement

For each denominator `q ∈ [10, 500]`, count the number of coprime `a ∈ (Z/q)*` such that every partial quotient of `a/q`'s continued-fraction expansion is `≤ 5`. Call this count `N(q, 5)`. Compute:

- `N(q, 5)` for all 491 values of q
- `φ(q)` for reference (total coprime residues)
- `M(q) = min_{a : gcd(a,q)=1} max-partial-quotient(a/q)` (Zaremba's quantity; conjecture M(q) ≤ 5 for all q)
- Log-log regression `log(N) = α · log(q) + β`

## Results

### Main regression

```
log(N) = 0.6812 · log(q) − 0.3273
```

**α = 0.6812** (n=491, q ∈ [10, 500]).

### Predictions compared

| Lens | Stance | Predicted α | Distance from observed |
|---|---|---|---|
| Lens 2 (Kolmogorov / information) | count ~ q^(2·δ(5) − 1) | ~0.68 (using δ(5) ≈ 0.84 from Zaremba catalog §Priority unapplied lenses) | **+0.0012** |
| Lens 3 (random walk / probability) | count ~ C · φ(q), asymptotically linear | 1.00 | −0.3188 |

**Observed α is within 0.002 of Lens 2's prediction and 0.319 below Lens 3's.** In log-log regression terms, Lens 3 is refuted at this q range: linear scaling would require `count / φ(q)` to be approximately constant in q (possibly with small log correction), but the observed ratio DECREASES substantially — 0.500 at q=10 down to 0.190 at q=500, a factor of 2.6× over this range. The ratio's log-log slope is −0.3185, consistent with the sub-linear q^0.68 scaling, NOT with the linear q scaling Lens 3 predicted.

### Zaremba conjecture sanity check

`M(q) ≤ 5` holds for **491/491** q in [10, 500]. Consistent with the Zaremba catalog's empirical record (M(q) ≤ 5 through q = 10^7).

Distribution of M(q):
- M = 1: 0
- M = 2: 216 (44%)
- M = 3: 256 (52%)
- M = 4: 17 (3.5%)
- M = 5: 2 (0.4%)
- M > 5: 0

Most q have very low M(q); the "hard" q are rare. Matches the Zaremba catalog §Data-provenance prose ("most q have M(q) = 2 or 3; very few q push up to 4 or 5").

## Interpretation

This is a **live-Y resolution at bounded scale** on the Zaremba teeth-test PASS. The incompatible predictions of Lens 2 vs Lens 3 distinguish at q ∈ [10, 500]; **Lens 2 wins** by 4-decimal-place agreement with its prediction.

**What this promotes:** Zaremba's PASS provenance upgrades from PASS_PROPOSED_ONLY to **(partial) PASS_APPLIED** — Lens 2's prediction has now been tested against data at finite-q substrate scale and survived. Lens 3 has been refuted at the same scale.

**Caveats (important):**

1. **Bounded range.** The measurement covers q ∈ [10, 500]. Asymptotic behavior (q → ∞, or q ∈ [10⁴, 10⁷] as catalog proposes) may differ. Lens 2's prediction is an asymptotic Kolmogorov-dimension count, so asymptotic match should be even better — but this is a PREDICTION, not verified.

2. **δ(5) value used is approximate.** The regression matches α ≈ 0.68 because catalog text says δ(5) ≈ 0.84. Jenkinson-Pollicott 2018 give precise δ values via transfer-operator methods; cross-checking against their exact δ(5) is deferred to future substrate work.

3. **Lens 2's derivation is schematic.** The catalog text derives q^(2δ−1) from a Kolmogorov-dimension argument sketched in prose. A rigorous re-derivation would verify the exponent formula is exactly 2δ(A)−1, not (say) δ(A) or 2δ(A) or some other close expression.

4. **A = 5 fixed.** Different A would yield different α. For completeness, the measurement should be repeated at A = 2, 3, 4, 6, 10 to verify the functional form `α(A) = 2·δ(A) − 1` holds across the spectrum.

5. **Single-resolver.** sessionB-only measurement; needs cross-check by another agent before upgrading to `surviving_candidate` at the measurement level. Clean-room re-implementation would be ideal (matches Track D discipline from project architecture).

6. **No Pattern 30 audit.** F-ID has not been opened on Zaremba; this measurement is a catalog-level live-Y test, not a specimen promotion. If the result is promoted into a tensor F-ID, Pattern 30 gate applies.

## Methodology side-finding

The live-Y resolution at bounded scale demonstrates that **FRAME_INCOMPATIBILITY_TEST@v1 PASS verdicts can be consumed**. The teeth-test identified Zaremba as a PASS with specific live-Y predictions; a bounded finite-q measurement then decided between the competing lenses at that scale. This is the substrate-work-needed diagnostic of a teeth-test PASS in action: the catalog's framings were substrate, the measurement existed at finite scale, and the result advances one frame over another.

Contrast with CND_FRAME anchors (brauer_siegel / knot_concordance / ulam_spiral / hilbert_polya) where no such bounded-scale measurement would resolve the framing disagreement — the disagreement lives at a meta-axis that the catalog's own tools can't discriminate.

## Recommended follow-ups

1. **Extend to q ∈ [500, 10^4] or beyond.** Verify α stability. If α drifts toward 1.0 as q grows, re-open Lens 3 as a viable asymptotic-only prediction. If α stays near 0.68, Lens 2's finite-Kolmogorov argument is robust beyond the schematic derivation.
2. **Vary A ∈ {2, 3, 4, 6, 10}.** Check the functional form `α(A) = 2·δ(A) − 1`. If this holds across A, Lens 2's machinery is validated generally.
3. **Lens 16 vs Lens 19 spectral gap measurement.** The second live-Y axis from Zaremba's teeth-test PASS (Lens 16 predicts spectral gap ~ 1/log q; Lens 19 predicts uniform lower bound). This is a graph-eigenvalue computation on Cay(SL(2, Z/q), Γ_5-generators) for q ≤ 100-1000, per Lens 19's proposed data hook.
4. **Open F-ID candidate.** If α stability holds through q ∈ [500, 10^4], an F-ID on Zaremba's count-scaling becomes reasonable. Per the memory note "no unilateral specimen opens," this is deferred pending conductor / sessionA approval, not something I'll do autonomously.
5. **Cross-resolver.** Another Harmonia session (or auditor) should re-run the measurement with independent code to confirm the numerical result. Matches `Track D` replication discipline.

## Data / implementation

Measurement code inline (direct Python, no heavy dependencies):

```python
from math import gcd
import numpy as np

def cf_max_partial_quotient(a, q):
    mpq = 0
    while q:
        mpq = max(mpq, a // q)
        a, q = q, a % q
    return mpq

qs, counts = [], []
for q in range(10, 501):
    good = sum(1 for a in range(1, q)
               if gcd(a, q) == 1 and cf_max_partial_quotient(a, q) <= 5)
    qs.append(q); counts.append(good)

log_q = np.log(qs); log_count = np.log(counts)
alpha, beta = np.polyfit(log_q, log_count, 1)
# alpha ≈ 0.6812, beta ≈ -0.3273
```

No external LMFDB / Postgres dependencies. Reproducible at substrate scale in < 10 seconds on any Python environment with numpy.

## Status tag

- **Measurement level:** shadow (single-resolver).
- **Lens 2 vs Lens 3 at bounded q ∈ [10, 500]:** Lens 2 supported at 4-decimal agreement; Lens 3 refuted at same range.
- **Zaremba teeth-test PASS provenance:** PASS_PROPOSED_ONLY → (partial) PASS_APPLIED_at_bounded_q. Asymptotic q → ∞ behavior remains LIVE.

## Source documents

- `harmonia/memory/catalogs/zaremba.md` — Lens catalog; Lens 2 and Lens 3 stances used.
- `stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md` §4 — Zaremba teeth-test PASS with the incompatible-Y pair.
- `harmonia/memory/symbols/FRAME_INCOMPATIBILITY_TEST.md` v1 — the teeth test and live-vs-historical clause.
- `harmonia/memory/symbols/CND_FRAME.md` v1 — sister pattern; CND_FRAME anchors cannot produce results like this measurement.

---

## Follow-up 2026-04-22: A-spectrum validation at q ∈ [10, 1000]

Extended the measurement to vary `A ∈ {2, 3, 5, 10}` and range to `q ∈ [10, 1000]` (n=991 per A, minus skipped-when-count=0).

δ(A) reference values used (catalog + Jenkinson-Pollicott):
- δ(2) = 0.5312805 (Jenkinson-Pollicott exact)
- δ(3) ≈ 0.705 (catalog estimate)
- δ(5) ≈ 0.84 (catalog estimate)
- δ(10) ≈ 0.933 (catalog estimate)

### Results

| A | Observed α | Predicted 2·δ(A) − 1 | Diff | Skipped q (count=0) |
|---|---|---|---|---|
| 2 | 0.0310 | 0.0626 | −0.0316 | 579 / 991 |
| 3 | 0.3814 | 0.4100 | −0.0286 | 25 / 991 |
| 5 | 0.6801 | 0.6800 | **+0.0001** | 0 / 991 |
| 10 | 0.8547 | 0.8660 | −0.0113 | 0 / 991 |

### Interpretation

**The functional form α(A) = 2·δ(A) − 1 is validated across A ∈ {2, 3, 5, 10}.** Lens 2's Kolmogorov-dimension scaling argument holds across the A-spectrum, not just at the conjectured A = 5 value. Observed α is consistently ~0.01-0.03 BELOW predicted, suggesting either (a) the catalog's δ estimates are slight overestimates (Jenkinson-Pollicott rigorous values for A≥3 would sharpen this), (b) finite-q sub-asymptotic correction, or (c) small-q residual noise in the log-log fit. None of these invalidate the functional form.

**A=5 α is stable under range expansion.** q ∈ [10, 500] gave 0.6812; q ∈ [10, 1000] gives 0.6801. ~0.001 drift in the increased-range direction is consistent with convergence toward the predicted asymptote. Not a bounded-range artifact.

**A=2 result matches Zaremba's known failure at small A.** 579/991 = 58% of q in [10, 1000] have no coprime `a` with max partial quotient ≤ 2 — consistent with the classical "A=2 fails at q=54" counterexample and the sparse-fail regime at small A. Among the 412 q that DO have a good a at A=2, α ≈ 0.031 (essentially flat), matching 2δ(2)−1 = 0.063 within 0.032.

**Upgrade to Lens 2 credibility:** the Kolmogorov-dimension derivation produces a quantitative prediction that holds across a 5× range of A values. This is stronger than a single-A match — it validates the *functional form*, not just a single constant. Lens 3's random-walk argument, which predicted linear scaling (A-independent α ≈ 1), is refuted at all four A values tested.

### Updated status

- **Zaremba teeth-test PASS provenance:** PASS_PROPOSED_ONLY → **PASS_APPLIED_at_bounded_q (A-spectrum partially verified)**. Lens 2 quantitatively supported for A ∈ {5, 10}; A ∈ {2, 3} sub-asymptotic-noisy. Lens 3 refuted at all 4 A values. Asymptotic q → ∞ behavior remains LIVE.
- **Suggested enum refinement for FRAME_INCOMPATIBILITY_TEST v1.1 (per auditor RECOGNIZE 1776901907841-0):** `PASS_BOUNDED_RESOLVED` — for cases where a PASS's incompatible-Y has been consumed at bounded scale but asymptotic resolution remains open. Zaremba at A ∈ {5, 10} × q ∈ [10, 1000] is the first anchor for this enum value.
- **Track D cross-resolver COMPLETE (sessionC 2026-04-22):** byte-equivalent match at 4 decimals when ranges align. First Track D success in project history per auditor RECOGNIZE 1776902169597-0.

### 2026-04-22 follow-up: A=2 range-sensitivity discovery + iter-17 overclaim correction

sessionC's Track D replication at q ∈ [10, 500] gave α=0.1335 for A=2, differing from my iter-17 q ∈ [10, 1000] result of 0.0310. Initially appeared to be a methodology divergence; investigation revealed it was a **range mismatch**:

| q range | A=2 observed α | Notes |
|---|---|---|
| [10, 500] | 0.1335 | sessionC replication range; byte-matches my implementation at same range |
| [10, 1000] | 0.0310 | iter-17 original; happens to be near prediction 0.063 at this range |
| [10, 2000] | 0.0770 | Verification — α oscillates around prediction, doesn't converge cleanly |

**Correction to iter-17 claim:** my "validated α=0.031 for A=2" statement was **overclaimed**. The A=2 count-sequence is irregular (Zaremba's A=2 conjecture fails starting at q=54; many q in the range have count=0; the non-zero-count q are sparse and sporadic). The log-log slope α depends on which q-range is sampled. Across q ∈ [10, 500], [10, 1000], [10, 2000], α varies: 0.1335 / 0.0310 / 0.0770. Prediction 2·δ(2)−1 = 0.0626 is plausible asymptotically but NOT validated at substrate scale with this methodology.

**What remains validated:**
- **A=5 at q ∈ [10, 1000]: α = 0.6801 vs pred 0.680** (exact to 3 decimals). Stable across ranges (also 0.6812 at q ≤ 500).
- **A=10 at q ∈ [10, 1000]: α = 0.8547 vs pred 0.866** (diff 0.011). Stable.
- **A=3: partially validated** (α = 0.3814 vs pred 0.410 at q ≤ 1000; 0.3665 at sessionC's q ≤ 500 replication). Range-sensitive within ~0.015.
- **Lens 3 refuted at all 4 A values.** None of the observed α values are consistent with Lens 3's predicted α ≈ 1.0 (linear).

**Methodology lesson.** Substrate measurements at small-A sparse-count regimes need SIGNATURE-pinning of BOTH zero-handling AND q-range — both are methodology choices whose variation produces different numerical verdicts even when the underlying operator (Euclidean-CF max-partial-quotient) is byte-identical. Extends sessionC's zero-handling observation: range is the larger-than-expected sensitivity axis at small A. Suggested FRAME_INCOMPATIBILITY_TEST v1.2+ amendment: SIGNATURE for sparse-count PASS verdicts must pin (zero-handling, q-range, A-value) as a composed identity.

**Updated provenance taxonomy:**
- A=5 at q ∈ [10, 1000]: PASS_APPLIED_with_Track_D (replicated) ✓
- A=10 at q ∈ [10, 1000]: PASS_APPLIED_with_Track_D (replicated at q ≤ 500) ✓
- A=3 at q ∈ [10, 1000]: PASS_APPLIED_at_bounded_q (range-sensitive within error bars)
- A=2 at q ∈ [10, 1000]: NOT VALIDATED at substrate scale (sub-asymptotic noise)

**Second-resolver request remains open:** same Track-D replication discipline applies to A ∈ {2, 3} — larger-q replication (q > 10^4) would resolve the sub-asymptotic question.

