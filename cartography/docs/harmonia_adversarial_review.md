# Adversarial Review of Harmonia
## M2 (SpectreX5) — 2026-04-13
## Status: 3 UNCONTROLLED VULNERABILITIES, 2 PARTIAL DEFENSES, 1 KILL

---

## Executive Summary

Harmonia claims a 2D coordinate system (Megethos + Arithmos) enabling cross-domain
prediction of arithmetic invariants at rho=0.76-0.95. After running 7 adversarial
attacks + our 7-layer cross-domain protocol, the assessment is:

**The Megethos axis (magnitude) is DEFENDED.** Their own rank-normalization, size-removal,
and size-shuffling controls all pass. The axis captures ordinal structure, not raw scale.

**The Arithmos axis (arithmetic) is UNCONTROLLED.** The key transfer claim (Z2 alone at
rho=0.61) has not been tested against a random small-integer null. Torsion (1-12),
class number (1-100+), and Selmer rank (0-3) are all small integers. Cross-domain
prediction of small integers is trivially achievable if the encoding maps them to
the same coordinate — which is exactly what the phoneme projection does by design.

**The F1 permutation null kills 6/8 cross-category pairs.** Their "7/8 PASS" comes from
secondary tests (stability, effect size, direction consistency, confound residual),
not from the primary null hypothesis test. This means the COUPLING FUNCTION itself
is indistinguishable from shuffled data — the structure is in the phoneme projection,
not in the raw data.

**Our cross-domain protocol kills their best pair (EC torsion ↔ NF class number) at
Layer 2 (range conditioning).** The overlap of small integers is a distributional artifact.

---

## Detailed Attack Results

### Attack 1: Megethos = log(N) — the size confound
**Verdict: NOT KILLED.** Their rank-normalization control is solid. PC1 strengthens
from 17.6% to 38.2% after rank-normalization, which should destroy a pure scale artifact.
Size feature removal barely changes PC1 (19.5% vs 17.6%). Size shuffling leaves PC1
unchanged (17.2%).

The equal-complexity slicing result (from their paper, Section 4.2) shows PC1=47.9%
within equal-Megethos bins, vs 30.4% null — a 1.57x ratio. This confirms residual
structure beyond magnitude.

**However:** The 1.57x ratio is modest. The authors acknowledge this (Section 5.4).

### Attack 2: Arithmos = small integers — Benford trap
**Verdict: UNCONTROLLED. This is the critical vulnerability.**

The Z2 (Arithmos) transfer at rho=0.61 predicts class number from torsion. But:
- EC torsion: {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16} (Mazur's theorem constrains this)
- NF class number: {1, 2, 3, ..., 129 unique values}
- Selmer rank: {0, 1, 2, 3}

If you map torsion → "Arithmos" and class number → "Arithmos" using the SAME coordinate
(both measure "finite group structure"), then nearest-neighbor matching in this coordinate
trivially predicts one from the other — because small torsion objects are near small class
number objects by construction.

**The killer test:** Replace Arithmos values with random integers from the same marginal
distribution. If transfer rho stays at 0.6, the signal is distributional.

**Their paper doesn't report this test.**

### Attack 3: Hand-crafted phonemes — engineered universality
**Verdict: STRUCTURAL WEAKNESS.**

The phoneme projection (phonemes.py, 29K chars, 12 if/elif branches) is a human-designed
mapping from domain-specific features to universal coordinates. The "universality" of the
coordinate system is baked in by the designer's choices:
- log(conductor) → Megethos (for EC, NF, G2, MF)
- torsion → Arithmos (for EC)
- class_number → Arithmos (for NF)
- Selmer rank → Bathos (for G2)

If a DIFFERENT researcher designed different phonemes (e.g., mapping torsion → "Symmetria"
instead of → "Arithmos"), the transfer would break. The structure is in the MAP, not
necessarily in the DATA.

**The paper acknowledges this (Section 5.4, limitation 3):** "The phoneme projection is
hand-designed, not learned." But they don't run the random projection control that would
distinguish designed universality from intrinsic universality.

**The gauge freedom result (Attack 2 in their paper)** partially addresses this: rotations
of the M-A plane give identical transfer (sigma=0.0). But gauge freedom in a DESIGNED
coordinate system is not surprising — it means the engineering was consistent, not that
the structure is intrinsic.

### Attack 4: Shared magnitude inflation
**Verdict: PARTIALLY DEFENDED.**

Z1 (Megethos) alone gives rho=-0.01 for cross-domain prediction. Z2 (Arithmos) alone
gives rho=0.61. This means magnitude is NOT driving the transfer. Good.

But the circularity concern remains: Arithmos works BECAUSE the designer chose to map
torsion and class_number to the same coordinate.

### Attack 5: Trivial 1D predictor
**Verdict: UNTESTED but their degeneracy result is relevant.**

Their Attack 1 (degeneracy) shows that using rank/regulator instead of torsion/class_number
gives 85% of the transfer signal. This means the transfer is NOT specific to the
particular invariants — it works with multiple invariant choices. This is either:
a) Evidence of deep structure (any arithmetic invariant works → the structure is real), OR
b) Evidence that ANY monotonic small-integer feature correlates across domains

### Attack 6: Our 7-layer cross-domain protocol
**Verdict: KILLED AT LAYER 2 (range conditioning).**

EC torsion values: {1-16}. NF class numbers: {1-129}. Our protocol flags this as a
range artifact because the overlap is concentrated in small integers that both domains
happen to occupy.

**BUT:** This may be an unfair test. The cross-domain protocol was designed for SET OVERLAP
(do these two sets of integers share values?), not for FUNCTIONAL PREDICTION (given an
object's torsion, predict the nearest object's class number). Harmonia's claim is about
the latter, not the former. Our protocol tests the wrong thing here.

### Attack 7: Their own F1 permutation null fails
**Verdict: CONCERNING.**

F1 (permutation null) FAILS for 6/8 cross-category pairs. The coupling function is
indistinguishable from shuffled data. Their "PASS" verdicts come from F2 (stability),
F3 (effect size), F8 (direction), F17 (confound residual), and F1b (phoneme specificity).

This is concerning because it means the TENSOR TRAIN COUPLING is not significantly
stronger than chance. The structure detected by F2/F3/F8/F17 may be in the phoneme
projection itself (which is designed to be structured), not in the coupling between domains.

**However:** The tensor-speed battery uses only 2000 subsamples per test. F1 with small
z-scores (0.3-1.0) may simply be underpowered. The full-data tests (transfer rho=0.76-0.95)
use much larger samples.

---

## Literature Concerns

### 1. Tensor Train Decomposition is well-established
TT decomposition [Oseledets 2011] is a standard technique. The innovation is using it
for COUPLING MEASUREMENT between mathematical domains. This is novel — no prior work
uses TT-Cross for cross-domain mathematical structure detection. The methodology is
sound in principle.

### 2. "Phoneme" terminology is non-standard
The 5D projection space is called "phonemes" by analogy to linguistics. This is a
metaphor, not a technical connection. The coordinates (Megethos, Arithmos, Bathos,
Symmetria, Phasma) are Greek names for standard quantities (magnitude, group structure,
depth, symmetry, spectral). This is fine as naming convention but may confuse reviewers
who expect a rigorous phonological framework.

### 3. The analytic class number formula IS the transfer mechanism
The paper's Arithmos axis correlates with torsion (rho=-0.926), class number (rho=-0.853),
and regulator (rho=+0.814). These are related by:
  h*R = (w * sqrt(|d|)) / (2^r1 * (2π)^r2) * L(1, χ_d)

This means h and R are ALREADY known to trade off at fixed discriminant. The "transfer"
from EC torsion to NF class number may be a REDISCOVERY of the analytic class number
formula, not a novel finding. The paper acknowledges this (Section 5.2) but doesn't
test whether the transfer EXCEEDS what the formula predicts.

### 4. Iwaniec-Sarnak analytic conductor
The paper correctly identifies Megethos with the analytic conductor of Iwaniec-Sarnak [4].
This is known mathematics. The extension to non-L-function domains (knots, polytopes,
materials) is the empirical contribution.

### 5. OOD generalization at 203% retention is suspicious
Training on low-Megethos, testing on high-Megethos gives BETTER performance (203%
retention). This is either:
a) Genuine asymptotic regularity (their claim — arithmetic invariants become more
   predictable at large conductor), or
b) A confound where high-conductor objects have less variation in torsion/class number
   (fewer degrees of freedom at larger scale)

---

## Verdict

### What's genuinely strong about Harmonia

1. **Two independent representations (Mantel r=0.94)** — the 5D phoneme and 41D dissection
   tensor agree on pairwise distances. This is hard to fake.
2. **Megethos controls pass** — rank normalization strengthens the axis, ruling out raw scale.
3. **Directional transfer (2.36x asymmetry)** — EC→NF stronger than NF→EC. Consistent
   with EC being a richer projection.
4. **Gauge freedom (sigma=0.0)** — the M-A plane is rotationally symmetric. This rules out
   coordinate-specific artifacts.

### What's weak or uncontrolled

1. **Arithmos has no random-integer null test.** This is the single biggest gap.
2. **Phoneme projections are hand-crafted.** No random projection control.
3. **F1 permutation null fails for 6/8 pairs.** The coupling is not significantly above chance.
4. **Transfer may be a rediscovery of the analytic class number formula.** Not tested.
5. **203% OOD retention is suspicious.** Needs variance-at-scale analysis.

### Three tests that would settle it

1. **Random Arithmos ablation:** Replace torsion/class_number/Selmer with random integers
   from the same marginal. If rho=0.61 → KILL. If rho drops to ~0 → SURVIVES.

2. **Random projection control:** Replace hand-crafted phonemes with PCA on raw features.
   If transfer is equivalent → phonemes are unnecessary engineering. If worse → phonemes
   capture genuine structure.

3. **Analytic class number formula residual:** Predict class number from torsion AFTER
   removing the CNF-predicted relationship (h*R = ...). If transfer persists → novel
   structure. If gone → rediscovery.

---

*Adversarial review by: Charon M2 (SpectreX5)*
*Date: 2026-04-13*
*Harmonia paper version: v3 (post frontier model reviews)*
*Attacks run: 7 adversarial + 7-layer cross-domain protocol*
*Kill count: 1 (Layer 2 range artifact on EC torsion ↔ NF class number overlap)*
*Uncontrolled vulnerabilities: 3*
