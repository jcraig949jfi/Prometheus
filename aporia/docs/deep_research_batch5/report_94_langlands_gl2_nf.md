# Report #94 — Langlands Transfer GL(2, NF) → GL(2h, Q): Base-Change Compatibility at Real-Quadratic Scale

**Target agent:** Harmonia
**Date:** 2026-04-23

## 1. Precise Problem Statement

Let K/Q be a real quadratic field of discriminant d_K and narrow class number h_K^+ = 1. Let π be a cuspidal automorphic representation of GL(2, A_K) attached to a Hilbert modular newform f ∈ S_{(k_1,k_2)}(N) with parallel weight k_1 = k_2 = 2 and level N ⊂ O_K. Arthur–Clozel cyclic automorphic induction (K/Q cyclic of order h = 2) produces

    π on GL(2, A_K)  ⇢[AI]  Π := AI_{K/Q}(π) on GL(4, A_Q).

Π is cuspidal iff π is not a base change from GL(2, Q) (Asai-primitive case; Doi–Naganuma otherwise). Rankin–Selberg: L(s, Π) = L(s, π, AI), factoring as L(s, f)·L(s, f ⊗ χ_K) when π descends.

**Target.** For each HMF π over real-quadratic K, compute {a_P(π) : Norm(P) ≤ X} and compare against Dirichlet coefficients of Π via:

    p splits in K as P P̄:    a_p(Π) = a_P(π) + a_{P̄}(π),   a_{p²}(Π) = a_P(π)·a_{P̄}(π) + …
    p inert in K as P:         a_p(Π) = 0,   a_{p²}(Π) = a_P(π) − 2·p^{k−1}·ε_π(P)
    p ramified in K:           local Langlands for GL(2, K_p) (Kutzko 1980)

A mismatch at a good prime falsifies identification, Arthur–Clozel recipe at a bad prime, or LMFDB's HMF ↔ GL(4) labeling.

## 2. Literature

- **Jacquet–Langlands (1970)**, *Automorphic Forms on GL(2)* — base change for quadratic extensions.
- **Saito (1975), Shintani (1979), Langlands (1980)** — cyclic base change via trace formula.
- **Arthur–Clozel (1989)**, Annals of Math Studies 120 — cyclic base change for GL(n).
- **Doi–Naganuma (1969), Naganuma (1973)** — explicit lift classical newforms → HMF.
- **Asai (1977)** — L(s, f, Asai) = L(s, AI_{K/Q}(π)) / L(s, sym² f_Q).
- **Blasius (2004)** — effective bounds on a_P(π).
- **Dembélé–Voight (2013)** — algorithmic HMF underlying LMFDB tables.
- **Freitas–Le Hung–Siksek (2015)** — modularity of EC over real quadratic.
- **Booker–Lee–Strömbergsson (2015)** — HMF functional-equation numerical verification.

## 3. LMFDB Data

- **`hmf_forms`** (~30K rows): `label`, `field_label`, `level_ideal`, `level_norm`, `weight`, `dim`, **`is_base_change`** (critical selector), `is_CM`.
- **`hmf_hecke`**: a_P indexed by prime ideals of O_K, JSONB keyed by (Norm(P), gen).
- **`nf_fields`** filter `degree=2 AND r2=0 AND cm=false`: ≈160K real quadratics; HMF coverage on d_K ∈ {5,8,12,13,17,21,24,28,29,33,…} with ≈12K forms at d_K ≤ 100.
- **`ec_nfcurves`**: `is_base_change`, `related_objects` link HMF ↔ classical EC.
- **`lfunc_lfunctions`** (degree=4): target for coefficient match.

## 4. Test Design

**Sample.** 500 HMFs over real-quadratic K with `is_base_change = false`, weight (2,2), dim ≤ 4, level norm ≤ 10^4, across ≥ 15 distinct K.

**Protocol per form π.**
1. Pull {a_P(π) : Norm(P) ≤ 10^5} from `hmf_hecke`.
2. Assemble predicted {a_n(Π) : n ≤ 10^5} via §1 recipe.
3. Locate GL(4, Q) L-function in `lfunc_lfunctions`: degree 4, conductor = d_K² · Norm(N)², Γ-factors consistent with parallel weight 2.
4. Coefficient check: |a_n(Π)_predicted − a_n(Π)_LMFDB| < 10^{-10} for n ≤ X.
5. Functional equation: ε(Π) = N_{K/Q}(ε(π)) · W_K.

**Statistics.**
- Primary: fraction of (π, p) matching at good primes.
- Secondary: KS distance of {a_p(Π)/p^{(k-1)/2}} against USp(4) Plancherel (Shin–Templier 2016).
- Tertiary: split-vs-inert parity localizes any mismatch.

## 5. Falsification Criteria

- **Kill base-change recipe:** any π with > 3 good primes p ≤ 10³ failing match after excluding p | d_K·Norm(N). Expected count: zero.
- **Kill LMFDB labeling:** GL(4) L-function not found for ≥ 5% of sample despite degree/conductor/Γ match — HMF ↔ GL(4) identity join incomplete (actionable for Mnemosyne).
- **Kill Sato–Tate transfer:** KS vs USp(4) > 0.05 on ≥ 10^5 primes.

## 6. Expected Outcome

Base change is a theorem; expect **100% match** at good primes. Scientific value is not confirmation: (a) clean HMF ↔ GL(4) identity join for Mnemosyne's cross-domain tensor, (b) stress-test `is_base_change` flag and `related_objects` crosslinks, (c) baseline protocol for the *next* void — Siegel modular forms over K, where base change is open and the same machinery becomes a discovery instrument.

## 7. Budget

- HMF pull (500 × 10K primes): 45 min on Postgres mirror.
- Base-change recipe + matching: 2 CPU-hours.
- GL(4) cross-match + functional-equation checks: 1 CPU-hour.
- **Total: half a day end-to-end.** Low cost; reusable identity join for Batch 6.

**Word count: 792**
