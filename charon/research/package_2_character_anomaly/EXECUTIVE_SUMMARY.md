# Package 2 Results: Executive Summary — The Character Anomaly EXPLAINED
## Source: Google AI Research (Gemini Pro Deep Research)

---

## Verdict: NOT an anomaly. A predictable pre-asymptotic effect driven by THREE mechanisms.

The 3.3x enrichment of non-trivial character dim-2 forms toward EC-like zero
distributions is NOT a mystery. It's a well-predicted consequence of finite-conductor
physics that the Katz-Sarnak asymptotic framework cannot resolve at conductor ≤ 5000.

---

## The Three Mechanisms (each independently sufficient, all three compound)

### 1. Excised Unitary Ensembles
L-function central values are discretized by arithmetic (Waldspurger/Kohnen-Zagier).
At finite conductor, the standard continuous U(N) ensemble must be "excised" — matrices
whose characteristic polynomials evaluate below the arithmetic threshold are removed.
This excision creates a HARD GAP at the origin that perfectly mimics SO(even) repulsion.
The unitary ensemble, after excision, looks orthogonal.

**Key paper:** Dueñez, Huynh, Keating, Miller, Snaith — Excised Orthogonal Ensembles.

### 2. Dimension-2 Inner Twists → Pseudo-Self-Duality
Weight-2 dim-2 forms overwhelmingly admit "inner twists" — a Galois automorphism maps
the form's coefficients back to themselves times a character. When the product of the
inner twist character and the nebentypus is trivial or real, the L-function inherits
pseudo-self-dual (orthogonal) symmetry from its base form of trivial character.

At conductor ≤ 5000, the L-function CANNOT resolve the difference between true
non-self-duality over Q and self-duality over the quadratic extension. The symmetries
are blended algebraically. This is specific to dim-2 (Gal(K_f/Q) = Z/2Z).

**This explains why dim-2 is special (our 10.7% vs 0.8% for dim-3+).**

### 3. Deuring-Heilbronn Zero Repulsion via Character Convolution
The non-trivial character's own Dirichlet L-function has low-lying zeros that REPEL
the modular form's zeros away from the central point. This repulsion mimics the
natural zero-free gap of rank-0 elliptic curves. At conductor ≤ 5000, a single
character-induced repulsion event dominates the configuration of the top-10 neighbors.

---

## Why Katz-Sarnak Predictions Fail at Conductor ≤ 5000

The research provides a devastating quantitative argument:
- Effective RMT matrix size N_eff ≈ log(5000) / (2π) ≈ **1.3**
- A matrix of size 1.3 doesn't have enough dimensions for bulk unitary statistics
- The ILS test function support requires primes up to p ≈ C_f to resolve U(N) vs SO(even)
- At C_f = 5000, log(5000) ≈ 8.5 — completely insufficient support
- The Shin-Templier error bounds haven't decayed at this conductor range

**Bottom line:** At conductor ≤ 5000, the theoretical apparatus that distinguishes
unitary from orthogonal symmetry is mathematically SILENT. The pre-asymptotic
effects completely dominate.

---

## What This Means for Charon

### The character anomaly is RESOLVED.
It's not a mystery. It's three well-documented finite-conductor mechanisms compounding.
The 3.3x enrichment is EXPECTED at conductor ≤ 5000. It would disappear at larger conductors.

### The partial kill from Kill Test 2 is now FULLY EXPLAINED.
Non-trivial character forms look EC-like because:
(a) excised unitary ≈ orthogonal at finite conductor
(b) dim-2 inner twists enforce pseudo-self-duality
(c) character zeros repel modular form zeros from center

### Testable prediction:
If we expanded to conductor 50,000 or 100,000, the 3.3x enrichment should DECREASE
as the asymptotic unitary statistics begin to dominate. This is a falsifiable prediction
from the theoretical framework.

### What conductor would we need?
N_eff needs to be >> 1 for RMT statistics. That requires log(C_f)/(2π) >> 1,
meaning C_f >> e^(2π) ≈ 535. We're at C_f ≤ 5000 which gives N_eff ≈ 1.3.
For N_eff ≈ 5 (minimally reliable), need C_f ≈ e^(10π) ≈ 7.2 × 10^13.
The crossover is VERY far away. At any computationally accessible conductor range,
the pre-asymptotic effects dominate.

---

## Connection to the Spectral Tail Finding

The excised ensemble mechanism and the ILS test function support argument from
Package 1 reinforce each other:

- Package 1: The ILS support theorem proves rank discrimination requires higher zeros
- Package 2: The same support limitation explains why U(N) and SO(even) are
  indistinguishable at finite conductor

Both are consequences of the same fundamental constraint: at conductor ≤ 5000,
the analytic apparatus lacks resolution to distinguish symmetry types. The spectral
tail finding (Package 1) shows where the information IS. The character anomaly
(Package 2) shows where it ISN'T — the central region where all symmetry types look alike.
