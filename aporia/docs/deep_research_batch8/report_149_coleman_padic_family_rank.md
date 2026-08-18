# Deep Research Report #149: Coleman p-adic Family Rank-Jump Distribution

**Target Agent:** Charon
**Front:** p-adic families
**Date:** 2026-04-25
**Predecessor:** Batch 8 void-detection program

## 1. Problem Statement

A Hida or Coleman p-adic family is a rigid-analytic path through the eigencurve E (Coleman-Mazur 1998) interpolating Hecke eigenforms of varying weight k that all share a fixed residual mod-p Galois representation. Along such a path, the analytic rank r_an(f_k) of the L-function L(f_k, s) at the central point can change discretely at "rank-jump" points: classical Heegner constructions, exceptional zeros of Greenberg-Stevens type, and weights where the p-adic L-function L_p(f, s) acquires an extra trivial zero.

Mazur-Tilouine conjecture (in the working form): the density of rank-jump points along a Coleman family of radius ρ around f is governed by p-adic L-function vanishing, with predicted rate ≈ ρ/p plus exceptional-zero corrections. The empirical question at LMFDB scale: for weight-2 newforms f at small primes p ∈ {3, 5, 7}, how many rank-jumps occur in a finite weight-radius around f, and does the observed density match the Mazur-Tilouine 1/p law?

## 2. Literature

- **Hida (1986):** ordinary p-adic families of modular forms via Λ-adic Hecke algebra.
- **Coleman (1996):** Banach-space families, finite-slope overconvergent forms beyond ordinary.
- **Coleman-Mazur (1998):** Eigencurve E_p as rigid-analytic moduli space; weight map κ: E_p → W.
- **Greenberg-Stevens (1993):** exceptional zero conjecture; first derivative formula for L_p when split-multiplicative reduction creates trivial zero.
- **Bertolini-Darmon (2007):** Heegner systems control rank growth; anticyclotomic Iwasawa theory.
- **Pollack-Stevens (2011):** overconvergent modular symbols, computational engine for Coleman families.
- **Mazur-Tilouine (1990):** original conjecture on rank growth in p-adic deformation neighborhoods.

## 3. LMFDB Data

- `mf_newforms`: weight-2 forms with `level`, `weight`, `char_orbit_label`, `analytic_rank`, `atkin_lehner_eigenvals`. ~1.6M forms; ~600K weight-2.
- `mf_hecke_nf`: `hecke_ring_numerators`, `hecke_ring_denominators`, `field_poly` — required for analytic continuation across the family.
- `ec_padic`: `lmfdb_iso`, `p`, `prec`, `padic_lseries_coefficients`, `slope` — direct p-adic L-series and Newton-slope data.
- `lfunc_lfunctions`: `central_value`, `order_of_vanishing`, `leading_term` for fiber-wise rank verification at integer weights.
- `mf_newform_portraits` / `mf_gamma1`: weight-k siblings sharing residual representation.

Family construction: Sage `pAdicLseries(E, p)` for ordinary case; `OverconvergentModularSymbol` (Pollack-Stevens) for finite-slope. Coleman p-adic interpolation via the Mahler-coefficient expansion in the weight variable.

## 4. Test Design

**Step 1.** Sample ~100 weight-2 newforms from `mf_newforms` with `level` ≤ 200, squarefree conductor, `analytic_rank` ∈ {0, 1, 2}, joined to `ec_padic` to ensure p-adic L-series exists for each p ∈ {3, 5, 7}.

**Step 2.** For each (f, p), build the Coleman family containing f using Pollack-Stevens overconvergent modular symbols at slope ≤ p−1. Restrict to a weight disc of radius ρ = 4 in W (the LMFDB-tractable window).

**Step 3.** Evaluate analytic rank at 5 weights k ∈ {2, 4, 6, 8, 10} and 3 quadratic twists per weight (15 fiber points per family). Use `order_of_vanishing` from `lfunc_lfunctions` where the integer weight is already in LMFDB; otherwise compute from `padic_lseries_coefficients` Newton polygon (rank = number of zero slopes at central point).

**Step 4.** Count rank-jumps: a fiber point counts as a jump if r_an differs from the family-generic rank r_0 (the rank at the base form f). Aggregate jump count J(f, p) over the 15 fiber points per family.

**Step 5.** Compare empirical density J(f, p) / (15 · ρ) to Mazur-Tilouine predicted rate 1/p. Pool 100 forms × 3 primes = 300 family measurements. Stratify by reduction type (good ordinary, supersingular, multiplicative) using `ec_padic.slope`.

**Metrics:** mean jump density per p; p-dependence slope (log-log fit); fraction of jumps explained by Greenberg-Stevens exceptional zeros (split-multiplicative primes).

## 5. Falsification

- **Confirms Mazur-Tilouine:** observed rank-jump rate within ±0.2 of 1/p for each p, and rate decreases monotonically in p.
- **Strong kill:** rate independent of p (flat across {3, 5, 7}) → contradicts Mazur — a p-adic feature should be p-dependent; jumps are an archimedean accident.
- **Structural finding:** jumps cluster at split-multiplicative primes only → reduces conjecture to Greenberg-Stevens exceptional zero phenomenon, not a generic p-adic density law.
- **Null:** randomize rank assignments at fiber points (preserve marginal rank distribution); empirical density must exceed null mean by ≥3σ to claim signal. Required to rule out the trivial "rank changes happen anyway" baseline.

## 6. Budget

~8 hours. Postgres pulls from `mf_newforms` + `ec_padic` (~1h). Sage Pollack-Stevens overconvergent modular symbols at precision 20, ~3 minutes per (f, p, weight) fiber × 100 × 3 × 5 = ~75 CPU-hours sequential, parallelize to ~5h on 16 cores. Stratification + null + plots ~2h.

## 7. Expected Outcome

First LMFDB-scale measurement of Coleman family rank-jump density across p ∈ {3, 5, 7}. Three publishable outcomes regardless of sign: (a) confirmation calibrates the Mazur-Tilouine rate constant for downstream Iwasawa work; (b) p-independence kills a 35-year-old folklore expectation; (c) exceptional-zero clustering identifies a new Greenberg-Stevens stratification of the eigencurve.

Connection to Aporia void-detection: p-adic families are a structural axis distinct from the archimedean L-function families that dominate prior void scans (V1-V3). Rank-jump pattern is a candidate "exceptional zero" channel for V4 — voids defined not by missing objects but by missing jumps in a deformation family. If Mazur-Tilouine holds, we get a population model for expected jump density; deficits become detectable voids in eigencurve coverage.

**Word count: 798**
