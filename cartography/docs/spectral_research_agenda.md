# Spectral Research Agenda
## Post-Adversarial: The path through the zeros
### 2026-04-13 | Synthesized from council feedback + 17 kills + 10 negative dimensions

---

## The Constraint Set (what the primitive MUST be)

From 10 negative dimensions, the primitive must be simultaneously:
1. **Coordinate-free** — not dependent on human parameterization
2. **Transcendental** — requires complex analysis, not algebraic isomorphism
3. **Global** — not constructible from isolated local data (Euler factors)
4. **Analytically normalized** — invariant to magnitude and scaling
5. **Distributional** — lives in measures on spectral data, not feature vectors
6. **Family-dependent** — not just GUE universality (same everywhere = killed)

The only mathematical object fitting all six: **normalized spectral distributions of L-function zeros.**

---

## Experiment 1: Unfold the Zeros (PREREQUISITE)

**What:** Normalize 120K stored zeros by smooth density N(T).
**Formula:** theta_n = N(gamma_n), where N(T) = (T/2pi) log(NT/2pi*e)
**Stratify:** root_number (+1/-1), analytic_rank (0/1/2+), conductor range
**Success:** Unfolded gap variance = 0.180 +/- 0.005 for SO(even) EC family
**Data:** `charon/data/charon.duckdb`, table `object_zeros`
**Priority:** BLOCKING — nothing else proceeds until this calibrates

---

## Experiment 2: Spectral Feature Set

From properly unfolded zeros, compute per-object:
- **1-level density** of low-lying zeros (Katz-Sarnak diagnostic)
- **Pair correlation variance** (rigidity measure, not just spacing)
- **Rescaled first zero height** (gamma_1 * log(gamma_1/2pi) / 2pi)
- **Nearest-neighbor spacing ratios** (r_n = min(s_n,s_{n+1})/max)
- **Number variance** Sigma_2(L) for L = 0.5, 1.0, 2.0
- **Delta_3 rigidity** statistic

These are "spectral phonemes" — immune to F33-F38 by construction.

---

## Experiment 3: Cross-Family Zero Repulsion (THE NOVEL TEST)

**What:** Pair L-functions from DIFFERENT families at the same conductor.
Compute joint distribution of zero heights.
**Null:** Independence (zeros of EC and Maass at same conductor are uncorrelated)
**Alternative:** Repulsion or attraction across families
**Why unkillable:**
- Not invariants (F33 immune)
- Not small integers (F34 immune)
- Conductor-conditioned (F35 immune)
- Raw zero data (F38 immune)
**If repulsion found:** Zeros "know about each other" across families → spectral bridge
**If independence:** Primitive is family-local, not global
**Data:** Pair EC zeros with Maass zeros at matching conductors in DuckDB

---

## Experiment 4: Optimal Transport Between Spectral Measures

**What:** Compute Wasserstein distance between zero distributions of different families.
Use Sinkhorn algorithm on 2D histograms (zero height × conductor).
**Hypothesis:** Transport map from EC zeros to Maass zeros has low-entropy structure
(systematic shift in low-lying zeros due to conductor size, not random).
**Why unkillable:** Continuous distributional metric, not feature alignment.
Megethos-resistant by normalization. F33-resistant (continuous, not ordinal).
**Deliverable:** Transport plan matrix showing HOW zero distributions differ between families.

---

## Experiment 5: Convergence Rate Extraction (F39 candidate)

**What:** For each EC, compute rate of convergence of a_p/sqrt(p) distribution
to Sato-Tate semicircle as a function of the number of primes used.
**Measure:** Variance of error term vs log(conductor).
**Unkillable prediction:** Curves with repulsed zeros (high-rank) should converge
SLOWER to Sato-Tate than curves with clustered zeros (low-rank) at same conductor.
**Why novel:** Second-order spectral effect. F1-F38 killed first-order feature alignment.
This tests FLUCTUATIONS of spectral density.
**Deliverable:** Convergence rate as a scalar per EC. Correlate across families.

---

## Experiment 6: L(1/2) Moment Zoo (the Mobius Trap)

**What:** Compute L(1/2, chi_d) for quadratic fields. Stratify by omega(d).
**Prediction:** Skewness of L(1/2) distribution for prime conductors = ZERO (symmetric).
Skewness for highly composite conductors = POSITIVE and large.
**Why:** This is a multiplicative number theory effect orthogonal to local GUE.
**If signal dies (Maass shows same pattern):** Deep Universality stronger than Montgomery-Odlyzko.
**If signal lives:** New lens separating Spectral from Arithmetic inside the zero.
**Deliverable:** F39: The Mobius Trap — kills naive zero-statistic claims.

---

## Experiment 7: Discrete Ricci Curvature on Congruence Network

**What:** Build graph where nodes = L-functions, edges = a_p congruences mod ell.
Compute Ollivier-Ricci curvature on this graph.
**Hypothesis:** Regions of highly negative curvature (bottlenecks) predict
algebraic rank jumps or family transitions.
**Why unkillable:** Bypasses correlation matrices entirely. Metric is purely
geometric, constructed from arithmetic congruences. No feature vectors.
**Data:** 3.8M EC with a_p coefficients (Postgres). Build for ell = 2, 3, 5, 7.

---

## Experiment 8: Higher-Dimensional Cameras (919K newforms)

**What:** Load dim-2 newforms as a new domain. Point Megethos-zeroed TT-Cross at them.
**Hypothesis:** Higher-dimensional cameras converge faster to the same limiting object.
**Megethos analog:** Analytic conductor C(1/2, pi) = N * prod(1 + |mu_j|) (Iwaniec-Sarnak).
**Why:** Dim-2 newforms see twice as much of the primitive as EC. If spectral features
show family-dependent structure, dim-2 will reveal it immediately.
**Prerequisite:** Experiments 1-2 (need properly unfolded zeros first).

---

## Execution Order

| Day | Experiment | Prerequisite | Deliverable |
|-----|-----------|-------------|-------------|
| 1 | Exp 1: Unfold zeros | None | Calibrated gap variance = 0.180 |
| 1 | Exp 2: Spectral features | Exp 1 | Per-object spectral feature vectors |
| 2 | Exp 3: Cross-family repulsion | Exp 1+2 | Joint zero distribution, repulsion test |
| 2 | Exp 5: Convergence rate | None (uses a_p, not zeros) | Rate scalar per EC |
| 3 | Exp 4: Optimal transport | Exp 1+2 | Transport plan matrix |
| 3 | Exp 6: L(1/2) moments | Needs L-values (fetch from LMFDB) | Mobius trap test |
| 4 | Exp 7: Ricci curvature | Needs congruence graph built | Curvature-rank correlation |
| 5 | Exp 8: Dim-2 newforms | Exp 1-4 | Higher-res camera comparison |

---

## The Bar

3.8M objects. 7 theorems at 100.000%. 17 kills. 40 tests.
Any new finding must survive the full battery AND be immune to all 10 negative dimensions.
The spectral level is where the primitive lives. The zeros are the closest we can get.

---

*Synthesized: 2026-04-13*
*Sources: Council adversarial review, 17-kill analysis, 10 negative dimensions,*
*Iwaniec-Sarnak, Katz-Sarnak, Montgomery-Odlyzko, Connes, Keating-Snaith*
