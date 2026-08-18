# Deep Research Report #112: Random Belyi Map Genus Distribution

**Target:** Harmonia (V5 Sleeping Beauty sweep, Belyi silent island)
**Date:** 2026-04-23
**Budget:** ~8 CPU-hours

## 1. Problem Statement

A Belyi map is a finite covering f: X → P^1 ramified only over {0, 1, ∞}. Combinatorially, degree-d Belyi maps correspond to triples (σ_0, σ_1, σ_∞) ∈ S_d^3 with σ_0 · σ_1 · σ_∞ = 1 and ⟨σ_0, σ_1, σ_∞⟩ transitive, modulo simultaneous conjugation.

**Central question:** Sample (σ_0, σ_1) uniformly from S_d × S_d, set σ_∞ = (σ_0 σ_1)^{-1}, condition on transitivity. What is the induced distribution of genus g(X) as d → ∞?

By Riemann-Hurwitz: 2g − 2 = −2d + Σ_{i ∈ {0,1,∞}} (d − c(σ_i)), where c(·) is cycle count. So g = 1 + d − (c_0 + c_1 + c_∞)/2. Reduces to joint distribution of c(σ_0) + c(σ_1) + c(σ_0 σ_1).

## 2. Literature

- **Grothendieck (1984)** *Esquisse d'un programme*: dessins d'enfants; Gal(Q̄/Q) acts faithfully on Belyi triples.
- **Shabat-Voevodsky (1989)** systematic combinatorial enumeration; genus formula via cycle counts.
- **Lando-Zvonkin (2004)** *Graphs on Surfaces*: Ch. 5 Riemann-Hurwitz reduction, Frobenius formula for fixed cycle types.
- **Eskin-Okounkov (2001), Invent. Math. 145:** generating function for simple Hurwitz numbers is Toda tau function. Implies quasi-modularity and asymptotics for fixed ramification as d → ∞.
- **Kulikov (2006):** fine asymptotics for random factorizations in S_d; cycle count of uniform product → log d + O(1) with Gaussian variance log d.

EO machinery predicts, for fixed g, N_g(d) ~ d! · d^{2g−2} · P_g(log d). Combined with Kulikov, typical genus of uniform triple scales as **g ~ d/2 − (3/2) log d / 2 + O(1)** — concentrates near d/2 with log corrections, **not** √d.

## 3. LMFDB Data

Table `belyi_galmaps` (~10^4 rows):
- `g`: genus
- `deg`: degree d
- `abc`: passport [a,b,c] = cycle-type signatures over 0,1,∞
- `monodromy`: group (often A_d or S_d)
- `lambdas`: full cycle-type partitions per branch point

Curation biases toward low g (≤ 4 dominant) and small d (≤ 10). This is opposite the uniform-triple distribution — LMFDB is the tail, random sampling is the bulk. The comparison is the point.

## 4. Test Design

For d ∈ {4, 5, ..., 20}:

1. Sample 10^6 pairs (σ_0, σ_1) uniformly from S_d × S_d.
2. σ_∞ = (σ_0 σ_1)^{-1}.
3. Count cycles c_0, c_1, c_∞ (O(d) each).
4. Transitivity check via BFS on Schreier graph; discard non-transitive.
5. g = 1 + d − (c_0 + c_1 + c_∞)/2.
6. Empirical histogram of g; mean, variance, skewness.

**Prediction check (EO-Kulikov):** E[g] = d/2 − (3/4) log d + C + o(1); Var[g] = (3/4) log d + o(log d).

Cross-check LMFDB: pull belyi_galmaps with deg ≤ 20, confirm curated histogram diverges from uniform (sanity: LMFDB is tail-biased).

## 5. Falsification

- **Primary kill:** E[d − 2g] scales as √d or d^α with α ≠ 0 — EO asymptotics fail. Report fitted exponent with bootstrap CI.
- **Secondary kill:** Var[g] / log d diverges or vanishes — Gaussian-log CLT (Kulikov) fails; tau-function prediction needs modification.
- **Sleeping-Beauty trigger:** bimodal genus histogram — unrecognized combinatorial obstruction; feed residue to Harmonia's V5 on Belyi island.

## 6. Budget

- Sampling + cycle counting: ~2e-5 s per triple at d=20 (numpy). 10^6 × 17 degrees ≈ 17e6 triples ≈ 6 CPU-hr.
- Transitivity BFS: ~1 CPU-hr amortized.
- LMFDB pull + histogram + plots: ~1 CPU-hr.
- **Total: ~8 CPU-hours**, single machine, no GPU.

## 7. Expected Outcome

First empirical check of Eskin-Okounkov random-Belyi genus prediction at d ≤ 20, ~17 × 10^6 uniform triples — ~10^3× LMFDB corpus in sample count, reaching the complementary high-genus regime. Harmonia consumes (d, g) joint histogram and EO-Kulikov fit residual as candidate Sleeping Beauty signal on Belyi island, which currently shows lowest cross-tensor coupling among the five silent islands.

Null result (clean log-scaling fit) still valuable: confirms EO applies outside proven fixed-ramification regime, hardens Belyi island as genuinely silent not unexplored.

**Word count: 782**
