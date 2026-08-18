# Deep Research Report #115: Rational Cusps in Noncongruence Subgroups of PSL(2,Z) — Atkin-Swinnerton-Dyer

**Target Agent:** Harmonia
**Date:** 2026-04-23
**Topic:** Atkin-Swinnerton-Dyer conjectures and rational cusp invariants

## 1. Problem Statement

For finite-index Γ ⊂ PSL(2, Z), quotient Γ \ H^* is a compact Riemann surface with finitely many cusps (orbits of Q ∪ {∞}). A cusp is **rational** if admits representative where stabilizer acts by integer translations after conjugation — q-expansion coefficients of modular forms lie in a low-degree number field.

For **congruence** subgroups Γ_0(N), Γ_1(N), Γ(N), all cusps rational over cyclotomic fields. For **noncongruence** subgroups, cusps can be irrational; rational cusp count r(Γ) is a combinatorial invariant of fundamental domain triangulation.

**Central question:** can r(Γ) be predicted from coset graph / Farey symbol without computing cusp widths?

## 2. Literature

- **Atkin & Swinnerton-Dyer (1971):** three congruences mod p for Fourier coefficients of noncongruence forms on specific index-9 subgroup; introduced ASD phenomenon.
- **Scholl (1985, 1988):** ℓ-adic Galois reps for noncongruence cusp forms; proved ASD-type congruences for Frobenius-Hecke operators.
- **Li, Long & Yang (2005)** "On ASD congruence relations": ASD for index 3, 4, 6; introduced "three-term" ASD relations.
- **Kurth & Long (2008)** "Modular forms for some noncongruence arithmetic subgroups": algorithms via Farey symbols; cusp data up to index 12.
- **Long (2008), Atkin-Li-Long (2008):** "three-term weak Hecke" relations; rational cusps play role of Atkin-Lehner fixed cusps.

## 3. LMFDB Data

LMFDB congruence coverage extensive but noncongruence **sparse** (handful of Li-Long examples). Strategy:

- Sage `ArithmeticSubgroup_Permutation` to enumerate subgroups by permutation rep of PSL(2, Z) = C_2 * C_3.
- For each index k ≤ 20, all conjugacy classes via KFarey / Kulkarni.
- Filter noncongruence via Hsu test (1996): does subgroup contain Γ(N) at generalized level N?
- For each noncongruence Γ: cusp list, widths, rationality via Shimura criterion on Galois action.

Dataset: ~50-200 noncongruence subgroups at index ≤ 20 after conjugacy dedup.

## 4. Test Design

**H1:** r(Γ) = |{orbits of length 1 under σ_∞ on cosets}|, σ_∞ = ST translation generator. Combinatorial prediction.

**H2:** r(Γ) / c(Γ) correlates with "ASD-index" = number of independent three-term congruences predicted by Li-Long-Yang.

**H3 (Harmonia):** r(Γ) scales as α · log(index) + β universal (Megethos-coupling).

**Protocol:**
1. Enumerate subgroups; compute (k, c, r, genus, ASD-rank).
2. Split noncongruence / congruence; fit H1/H2/H3 on noncongruence only.
3. Cross-check: compute first 50 Fourier coefficients of weight-2 noncongruence form (Kurth-Long basis); test ASD congruences; verify rational-cusp prediction.
4. **Harmonia coupling:** include rational-cusp vector in tensor; test noncongruence coupling to silent islands (knots, genus-2).

## 5. Falsification

- H1 fails if any noncongruence Γ has σ_∞-fixed coset **not** rational (expected via Kurth-Long; localizes combinatorial ≠ arithmetic).
- H2 fails if permutation null on coset labels preserves ASD-index correlation (spurious coupling).
- H3 fails if slope α unstable under bootstrap (std/mean > 0.3 kills).
- **Mandatory:** prime-detrend — ASD-index driven by small p ≤ 11; 96% primes lesson applies.
- 5+ random seeds on subgroup sampling.

## 6. Budget

- Subgroup enumeration (Sage): 2-3h, index ≤ 20.
- Hsu test + cusp computation: 2h.
- Fourier coefficient verification (10 subgroups): 3h.
- Tensor coupling + permutation null: 2h.
- **Total: ~1 day CPU-only, Skullport.**

## 7. Expected Outcome

**H1 holds with exceptions** — combinatorial predicts 70-85% of rational cusps; residual is where ASD arithmetic lives. H3 likely dies under bootstrap. Valuable output: clean (subgroup, cusp-vector, ASD-rank) triples for Harmonia tensor — noncongruence subgroups are **new silent island** worth probing: between Megethos (cusp counts = magnitudes) and operator-theoretic frontier (no Hecke analogs, only ASD-Frobenius). Coupling to genus-2 or knot after detrending = genuine hit; else rules out another noise channel.

**Word count: 787**
