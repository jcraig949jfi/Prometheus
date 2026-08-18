# Deep Research Report #135: Dedekind η-quotient Rationality at Level N > 100

**Target Agent:** Ergon
**Date:** 2026-04-23
**Complement to:** Batch 6 Report #109

## 1. Problem Statement

A Dedekind η-quotient:

    f(τ) = ∏_{d | N} η(dτ)^{r_d}, r_d ∈ Z

where η(τ) = q^{1/24} ∏(1 − q^n). By Ligozat–Newman conditions, f(τ) is modular (or cusp) on Γ_0(N) of weight k = (1/2)Σr_d and character χ when four arithmetic congruences on (r_d) hold.

For N ≤ 24, complete holomorphic η-quotient list in Ono's *Web of Modularity* and Rouse–Webb (2015). For N > 100, landscape empirically uncharted: (i) how many η-quotients exist, (ii) which Galois orbits in mf_newforms admit η-quotient realization, (iii) whether density of η-quotient-rational newforms collapses, stabilizes, or grows.

**Void:** at N > 100, what fraction of rational newforms are η-quotients, and is there a level N above which fraction drops to zero?

## 2. Literature

- **Ligozat (1975)** *Courbes modulaires de genre 1*: four congruence conditions (Σr_d ≡ 0 mod 24, Σ(N/d)r_d ≡ 0 mod 24, ∏d^{r_d} square, order-at-cusp positivity).
- **Ono (2004)** *Web of Modularity* ch. 1.4: weight-2 η-quotients up to N=24; conjectured sparsity at larger N.
- **Rouse–Webb (2015)** Adv. Math.: M_k(Γ_0(N)) spanned by η-quotients only for finitely many (N,k); explicit list for k=2.
- **Allen–Anderson–Bailey (2020)** *Eta-quotients of prime and prime-squared level*: classification at N=p and N=p² for p ≈ 97. Levels 101-200 composite and prime-squared largely open.
- **Bhattacharya (2017), Kilford (unpub.):** partial through N ≈ 60.

## 3. LMFDB Data

- `mf_newforms` — filter `level BETWEEN 101 AND 200 AND weight = 2`.
- `mf_hecke_cc` / `mf_hecke_nf` — q-expansion for matching.
- `mf_newform_portraits` — sanity metadata.

Expected at levels 101-200 weight 2 trivial character: ~8K-12K Galois orbits; rational-coefficient subset (dim=1) several hundred — population to match against.

## 4. Test Design

**Enumeration** for each N ∈ {101,...,200}:

1. Enumerate divisors d | N; call τ(N) count.
2. Generate integer vectors (r_d) with |r_d| ≤ R (start R=8, escalate to 12). Space size ~(2R+1)^{τ(N)}; for τ(N) ≤ 8 tractable (17^8 ≈ 7×10^9, pruned by Ligozat sieve).
3. Filter by Ligozat's four congruences — kills > 99.9%.
4. q-expansion to n ≤ 200 coefficients via Sage `etaproducts` or direct η series product.
5. Normalize leading coefficient.

**Matching** for each surviving η-quotient q-expansion:
- Hash first 50 Hecke coefficients at p ∤ N.
- Join `mf_hecke_nf` on `hecke_orbit_code` matching hash.
- Declare match if first 100 Hecke coefficients agree.

**Output:** table (N, (r_d), newform label, weight, char) of confirmed realizations; **void table** of rational newforms at N ∈ [101,200] with no η-quotient match.

## 5. Falsification

- **F1:** enumeration at specific N produces zero holomorphic η-quotients despite τ(N) ≥ 4 (Ligozat sieve sanity failure).
- **F2:** matched fraction at N ∈ [101,200] indistinguishable from N ∈ [25,100] — no level-dependent sparsity; "uncharted" framing wrong.
- **F3:** every rational newform at these levels matches some η-quotient — voids don't exist; Rouse–Webb extends beyond proven.

Preregister: report both match table AND void table; no selective reporting.

## 6. Budget

- Enumeration + Ligozat sieve: ~3 CPU-hr (Sage).
- q-expansion for survivors: ~1.5 CPU-hr.
- LMFDB Postgres join + verification: ~1 CPU-hr (Skullport → devmirror).
- Logging + void-table: ~0.5 CPU-hr.
- **Total: ~6 CPU-hr**, single-node. ≤ 50 MB output.

## 7. Expected Outcome

**60% partial void:** match fraction at N ∈ [101,200] drops to 20-40% of rational newforms vs ~70% at N ≤ 24. Void grows with N. Preregistered empirical curve: η-quotient density vs level.
**25% sharp cliff:** above some N* ∈ [120,180], match collapses to < 5%. Structural obstruction (modular-form Lie-algebra dim exceeding η-quotient monomial count).
**15% null:** density level-independent; Rouse-Webb finite-span applies only asymptotically. Still useful — negative constraint on literature.

Deliverable: `eta_quotient_voids_N101_200.json` — rational-newform stratum for Harmonia coupling tests against EC rank, NF class group, genus-2 tensor.

**Word count: 782**
