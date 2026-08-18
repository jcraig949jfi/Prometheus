# Deep Research Report #106: Ceresa Cycle Non-Triviality Count for Genus-3 Curves

**For:** Ergon
**Date:** 2026-04-23
**Topic:** Beilinson height pairing empirical census over 10^4 genus-3 curves

## 1. Problem Statement

For a smooth projective curve C of genus g ≥ 3 with basepoint p, the **Ceresa cycle**:

    Z(C,p) = [C − p] − [−C − p] ∈ CH_1(Jac(C))_{hom=0}

where [−C] is the image of C under x ↦ −x on the Jacobian. Ceresa (1983) proved this is **homologically trivial but not algebraically trivial** for very general genus ≥ 3. Its Beilinson-Bloch height

    ⟨Z(C,p), Z(C,p)⟩_{BB} ∈ ℝ

is a motivic invariant encoding arithmetic complexity of C.

**Question:** Over 10^4 genus-3 curves sampled uniformly from non-hyperelliptic plane quartics, what fraction have **detectably non-trivial** Ceresa cycle at 10^{-6} precision on archimedean height? Theory: 100% minus measure-zero exceptional locus. Empirical after finite precision + hyperelliptic/Shimura contamination: 97-99%.

## 2. Literature

- **Ceresa (1983)** Ann. Math. 117 — original; non-algebraic-triviality for very general g ≥ 3.
- **Beilinson (1984), Bloch (1984)** — conjectural height pairing on homologically trivial cycles; converges for g ≥ 3 Ceresa.
- **Harris (1983)** Duke Math J — Fermat quartic as first explicit non-trivial example via normal functions.
- **Beauville-Schoen (2020)** — Ceresa trivial for bielliptic curves; structural exception class.
- **Bloch (2010)** *Lectures on Algebraic Cycles* — archimedean height via Green currents and Deligne cohomology.
- **Eskandari-Murty (2021), Laga-Shnidman (2023)** — modern computational; explicit p-adic formula for CM Jacobians (validation).
- **Bisogno-Li-Litt-Srinivasan (2022)** — Fricke-symmetric quartics with **vanishing** Ceresa class: dim ≥ 1 exceptional locus in M_3.

## 3. LMFDB Data

LMFDB `g3c` has ~67K genus-3 curves; only ~8K non-hyperelliptic plane quartics with L-functions. Ceresa-relevant invariants (Faltings height, bielliptic flag) < 12% coverage.

**Mitigation:** generate 10K smooth plane quartics F(x,y,z)=0 via random integer coefs ∈ [−5,5]; reject singular (disc=0), bielliptic (28-bitangent extra-involution detection), hyperelliptic elevation. ~95% survival → 9.5K working sample.

## 4. Test Design

**Pipeline per curve** (~8 s/curve, parallel):

1. **Periods** via `abelfunctions` / `riemann_theta`: 3×6 big period matrix Ω = (A|B) at 80-digit precision.
2. **Archimedean height** h_∞(Z): integrate log|θ| against current on Z(C,p) − Z(C,p)^−; Zhang (2010) admissible pairing; iterated Siegel-theta truncated at AJ precision 10^{-8}.
3. **p-adic height** h_p(Z) for p ∈ {5,7,11}: Colmez formula, Balakrishnan-Besser-Müller Coleman integration. Non-triviality: |h_p(Z)| > 10^{-6} for some p OR |h_∞(Z)| > 10^{-6}.
4. **Validation anchors:** Fermat quartic x^4+y^4+z^4=0 (Harris: h_∞ = π · explicit); Klein quartic (CM by ℤ[ζ_7]; Eskandari closed form). Reproduce to 8 digits before accepting pipeline.
5. **Null battery:** (a) permute basepoint, height covariant; (b) Galois conjugation, height invariant; (c) hyperelliptic injection: height should be zero (Ceresa vanishing in genus 2).

## 5. Falsification

- Fermat/Klein anchors disagree with published beyond 10^{-5}.
- Null (c) nonzero on hyperelliptic sample → numerical noise floor above signal.
- Non-trivial fraction < 90% → either Fricke exceptional locus larger than expected (math) or precision issue (artifact). Distinguish by 160-digit resample.
- p-adic and archimedean disagree in sign under functoriality → pipeline bug.

## 6. Budget

~1 core-day:
- 2h period harness + anchors
- 2h p-adic Coleman module
- 16h × 8-core = 2.8h wall for 10K sweep
- 2h null + exceptional locus analysis
- 2h writeup → `ergon/logs/ceresa_census_*.jsonl`

## 7. Expected Outcome

**97.5 ± 1.0%** of genus-3 plane quartics detectably non-trivial at 10^{-6}. Residual ~2.5%: 1.5% BLLS Fricke locus (genuine vanishing), 0.5% near-bielliptic (filter leakage), 0.5% precision floor.

If observed < 95%: Fricke locus larger than conjectured — novel finding. If > 99.5%: precision too generous; tighten to 10^{-8}.

**Real prize:** distribution of h_∞(Z) / Falt(C) — test whether Ceresa scales with Faltings height (Hodge-theoretic conjecture, no empirical data exists).

**Word count: 798**
