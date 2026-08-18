# Deep Research Report #109: Rogers-Ramanujan-Type Identities Beyond Level 5

**Target agent:** Ergon
**Date:** 2026-04-23
**Topic:** Bressoud-Andrews catalog extension via LMFDB coefficient mining

## 1. Problem Statement

Rogers-Ramanujan identities express partition generating functions as infinite products that are secretly η-quotients at level 5:

    Σ_{n≥0} q^{n²} / (q;q)_n = ∏_{n≥0} 1 / ((1−q^{5n+1})(1−q^{5n+4})) = η(5τ)/η(τ) · (correction)

Every such identity is a coincidence between (a) combinatorial sum over partitions with gap/congruence conditions and (b) modular form of weight 1/2 or 1 expressible as η-quotient. Bressoud-Andrews catalog stops around level 13 because hand-derivation of Bailey pairs becomes intractable.

**Mechanical reformulation:** for an η-quotient at level N with integer q-expansion, search LMFDB for newform or Eisenstein matching coefficient-wise. A match is a candidate new Rogers-Ramanujan-type identity; combinatorial interpretation follows from η-factorization structure.

## 2. Literature

- **Rogers (1894)** — original identities.
- **Ramanujan (1913)** — independent rediscovery; Hardy letter.
- **Andrews (1974)** PNAS 71 — modulus 2k+1 extension.
- **Bressoud (1980)** Memoirs AMS 227 — even and odd moduli.
- **Berkovich-Garvan (2002)** J. Comb. Theory A — modular form interpretations.
- **Ono (2004)** *Web of Modularity* — η-quotient tables level ≤ 24.
- **Sills (2017)** *Invitation to the Rogers-Ramanujan Identities* — modern survey, level-11/13 catalog.

## 3. LMFDB Data Inventory

- `mf_newforms` — filter `level IN (17,19,23,29,31,37,41,43,47)`, weight 1 or 2, trivial/quadratic character.
- `mf_hecke_cc`, `mf_hecke_nf` — q-expansion to N=1000+.
- `mf_newform_portraits` — CM and inner-twist flags.
- `artin_reps` — weight-1 Galois side.

Prime levels 17-47 yield ~180 newform orbits. Enumerate all η-quotients ∏_{d|N} η(dτ)^{r_d} with |r_d| ≤ 6 satisfying Ligozat-Newman modularity (weight integer, trivial character, holomorphic at cusps).

## 4. Test Design

```
For each level N in {17,19,23,29,31,37,41,43,47}:
  1. Enumerate η-quotients |r_d| ≤ 6 passing Ligozat-Newman
  2. q-expand to 500 terms (Sage eta_qexp / convolution)
  3. Pull mf_newforms at level N, weight ≤ 2, first 500 coefficients
  4. Also Eisenstein series E_k(dτ) for d | N
  5. For each (eta, mf) pair:
       diff = eta_coeffs − mf_coeffs
       if diff ≡ 0 to 500 terms: CANDIDATE
       else PSLQ([eta, mf_1, ..., mf_k], tol=1e-40)
       if small-coef integer relation: CANDIDATE
  6. Verify to 2000 terms
  7. Back out combinatorial side via Bailey-pair lookup (Sills)
```

**PSLQ:** `mpmath.pslq` at 80 digits, max_coeff = 50; reject relations with largest coef > 20 (Ockham).

## 5. Falsification

Self-falsifying at three layers:
1. **Numerical:** mismatch at any of 500 coefficients kills.
2. **Extension:** verify to 2000 before declaring; most false positives die here.
3. **Algebraic:** claimed identity must follow from Bailey-pair chain or modular weight/character computation. Else "empirical only" — not accepted until proof pathway exists.

Known attractor: Eisenstein reductions at non-prime levels produce trivially true relations (E_2(τ) − NE_2(Nτ) is modular). Filter by requiring nontrivial cusp-form component.

## 6. Budget

- η-quotient enum (9 levels × ~200): 20 CPU-min.
- LMFDB pulls (cached): 30 min.
- q-expansion to 500 terms: 10 CPU-min × 1800 ≈ 5 CPU-hr.
- PSLQ: 0.5 CPU-hr.
- Verification at 2000 on ~20 candidates: 30 CPU-min.
- **Total: ~6 CPU-hours.** Restrict to {17,19,23,29} first for 3 CPU-hr, expand if hits.

## 7. Expected Outcome

**2-5 new identities**, mostly at levels 17, 19, 23. Likely Bailey-pair-expressible but never written down as identities. High-value: level-29 or 31 identity with no known Bailey origin — genuine new combinatorial theorem. Null (zero hits) is informative: bounds η-quotient + newform coincidence rate, suggests Bressoud-Andrews close to complete at these moduli.

**Handoff:** Ergon runs sweep → `ergon/logs/rr_identities_*.jsonl`; Charon verifies Bailey-pair; Aporia combinatorial interpretation.

**Word count: 798**
