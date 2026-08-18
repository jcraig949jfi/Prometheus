# Deep Research Report #99: Congruence Primes in Hilbert Modular Forms

**Target Agent:** Charon
**Topic:** Ribet-style congruence prime distribution for HMF over real quadratic fields
**Date:** 2026-04-23

## 1. Problem Statement

For a classical newform f of weight k and level N, a prime p is a **congruence prime** for f if there exists another newform g such that

    a_ℓ(f) ≡ a_ℓ(g) (mod 𝔭)    ∀ ℓ ∤ Np

for some prime 𝔭 above p. Ribet (1976) showed these are exactly primes dividing the congruence module, controlled by Hecke-algebra structure.

**Question:** For HMF over real quadratic K with discriminant d_K, does congruence-prime density follow a Hida-Tilouine asymptotic, or does base-field geometry inject anomalies invisible in the GL_2/Q case?

## 2. Literature

- **Ribet (1976)** "A modular construction of unramified p-extensions of Q(μ_p)": congruence primes from Eisenstein ideals.
- **Hida (1981)** "Congruence of cusp forms and special values": p-adic Hecke algebras, congruence number tied to L(f, k/2)/Ω_f.
- **Hida-Tilouine (1993)** "Anti-cyclotomic Katz p-adic L-functions and congruence modules": totally real extension; congruence primes divide adjoint L-value L(1, Ad f) up to periods, with d_K correction.
- **Ghate-Vatsal (2004)** local behaviour of ordinary Λ-adic representations; Λ-adic Hecke algebra rank constraints.

Implicit asymptotic: for parallel weight (k,k), level N, expected congruence primes scales as O(log N_K(N) + k log d_K).

## 3. LMFDB Data Shape

Postgres mirror:
- `hmf_forms` — label, field_label, level_norm, weight, dimension, hecke_ring_index, CM flag.
- `hmf_hecke` — hecke_eigenvalues indexed by prime ideals.
- `hmf_fields` — degree, discriminant, narrow class number, unit group.

Restrict to [K:Q]=2, d_K ∈ {5,8,12,13,17,21,24,28,29,33,37,40,41,44}. ~O(10^5) HMF; target ~1000 newforms per d_K with dimension ≥ 1 (irrational Hecke field — else no nontrivial congruences).

## 4. Test Design

**Step 1.** Pair enumeration: unordered pairs (f,g) sharing level ideal and parallel weight. ~C(1000,2)/(levels) ≈ 10^4–10^5 candidate pairs per d_K.

**Step 2.** Extract first 50 Hecke eigenvalues (norm ≤ 500). Clears Sturm bound for typical levels.

**Step 3.** Congruence detection: for each pair and p ≤ 100, compute resultant / ideal gcd of (a_𝔭(f) − a_𝔭(g)). Candidate if p | gcd across all sampled primes. Certify by pushing to Sturm bound.

**Step 4.** Density: ρ(d_K, k) = mean distinct congruence primes per form, excluding p | level-norm or d_K. Fit

    E[#cong primes] ≈ α log N_{K/Q}(N) + β k + γ log d_K

by weighted LS across 14 fields.

**Step 5.** Null: shuffle eigenvalue vectors within (d_K, level, weight) stratum; recompute ρ. 500 shuffles per stratum (mandatory per `feedback_permutation_null.md`).

## 5. Falsification

Kill (any suffices):
- Observed ρ within shuffle null 95% band for ≥ 10 of 14 fields.
- γ indistinguishable from 0 (|t| < 2 across bootstrap).
- d_K dependence explained entirely by N_K(N) conflation.
- Prime-detrending artifact: removing p | h_K or p | (d_K²−1) collapses signal → narrow-K arithmetic, not Ribet-style.

Soft kill: Hecke-field degree dominates (large-degree Hecke rings trivially produce more small residue characteristics) → pairing-geometry artifact.

## 6. Budget

- Data pull: 15 min.
- Pair enumeration + eigenvalue gcd (14 fields): ~2.5 CPU-hr single, ~25 min 8-core.
- Permutation null (500 × 14): ~1 CPU-hr.
- Fitting + diagnostics: < 30 min.
- **Total: ~4 CPU-hours.**

## 7. Expected Outcome

**(a) Confirms Hida-Tilouine (baseline):** γ ~ O(1), flat residuals, logarithmic d_K scaling. Calibrates pipeline; publishable as HMF analogue of Ghate.
**(b) Anomalous d_K dependence:** γ super-logarithmic or discriminant-class structure (e.g., ramified-in-K primes disproportionate). Potential bridge to Charon two-channel hypothesis.
**(c) Null:** HMF Hecke algebras decoupled from base-field geometry at this depth — another silent-island confirmation.

Prior from Charon track record: ~60% (c), 30% (a), 10% (b). Only (b) is worth continuing.

**Word count: 798**
