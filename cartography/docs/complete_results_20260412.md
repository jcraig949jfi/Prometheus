# Complete Test Results — Project Prometheus
## 2026-04-12 | 3 Rounds + Smoke Tests + Coarsening | ~100 tests | Battery v6 (F1-F27 + F25b)

---

## IDENTITIES (deterministic or known mathematical consequences)

| # | Finding | R²/r | Domain | Notes |
|---|---------|------|--------|-------|
| 1 | Alexander(-1) = Jones(-1) | r=1.000 | Knots | Exact on 2,977 knots. Both evaluate to determinant. |
| 2 | det = \|Alexander(-1)\| | 100% | Knots | 249/249 verified (Round 1), 2,977/2,977 (Round 3) |
| 3 | max Jones coeff ~ det | R²=0.995 | Knots | Near-deterministic functional dependence |
| 4 | det ~ max Alexander coeff | R²=0.924 | Knots | r=0.96, near-identity |
| 5 | Jones length ~ crossing | R²=0.507 | Knots | KMT theorem (Kauffman-Murasugi-Thistlethwaite) |
| 6 | Jones-Alexander unit circle cosine=0.919 | — | Knots | Structural identity (C41-deep) |
| 7 | C8 Logistic map phase coherence | Exact | Dynamical sys | AC(1) ranges -1.0 (periodic) to -0.5 (chaotic) |
| 8 | E_6 root number = +1 (51/51) | P=4e-16 | Genus-2 | TAUTOLOGY: CM by Q(√-3) forces it (council proved) |
| 9 | S_n character M4/M²=p(n)/n | FALSE | Rep theory | Ratio diverges to 0.068 at n=30 (M1 killed) |

## REDISCOVERIES (known math detected by pipeline)

| # | Finding | Metric | Domain |
|---|---------|--------|--------|
| 10 | C01 Paramodular conjecture | 7/7 matched | Genus-2/Siegel |
| 11 | EC count ~ MF count (modularity) | R²=0.397 | EC/MF |
| 12 | Polytope Euler chi = 0 or 2 | 980/980 (100%) | Polytopes |
| 13 | Deuring mass: nodes = (p-1)/12 | R²=0.99999968 | Isogenies |
| 14 | 23 genocide rediscoveries | z=33-93 | Various |
| 15 | C94 Jones mod-3 → determinant | eta²=1.000 | Knots | Perfect separation (likely identity via Alexander) |
| 16 | C94 Jones mod-5 → determinant | eta²=1.000 | Knots | Perfect separation (likely identity) |

## STRUCTURAL FINDINGS — Tier 1: Strong within-context, interaction-detected

*These pass eta² + stability + permutation null + interaction detection (ANOVA + rank inversion).*
*Transfer-verified: N/A (coarsening proves non-stationarity is genuine, not noise).*

| # | Finding | eta² | Interaction evidence | Domain |
|---|---------|------|---------------------|--------|
| 17 | SC_class → Tc | 0.570 | Replicated on COD (0.41). Within-SG mean eta²=0.34. | Superconductors |
| 18 | (SG × SC_class) → Tc | 0.457 global, 14.1% incr | 11% interaction (balanced). Rank rho=-0.04 across classes. Coarsening: no symmetry grouping transfers, confirming genuine non-stationarity. | Superconductors |
| 19 | C09 Moonshine class → coeff scale | 0.601 | 26 classes. F27: NOT_TAUTOLOGY. | Moonshine/OEIS |
| 20 | C05 Maass level → spectral param | 0.824 | 237 levels. F27: NOT_TAUTOLOGY. 100% Poisson spacing (not GUE). | Maass forms |
| 21 | C86 Isogeny diameter scaling | R²=0.940 | diam=0.97·log(p)-1.22. 3,240 primes. F27: NOT_TAUTOLOGY. Per-ell r=0.89-0.96. | Isogenies |
| 22 | C72 NF hR/√D ratio by degree | 0.294 | Brauer-Siegel ratio varies by degree. M4/M²=3.58. | Number fields |
| 23 | C21 NF class number by degree | 0.280 | F25 CONDITIONAL, F25b WEAK_NOISY. | Number fields |
| 24 | C41 Unit circle profiles | 0.143 | CV=0.77%. Exponential norm growth with crossing. | Knots |
| 25 | C27 Dimension → f-vector sum | 0.914 | 980 polytopes, 7 dimensions. Likely structural/definitional. | Polytopes |
| 26 | Fungrim module → n_symbols | 0.186 | 59 modules. Topic determines formula complexity. | Fungrim |
| 27 | C88 SG → nsites | 0.531 | 77 SGs. Space group determines atom count. | Crystals |
| 28 | C88 SG → volume | 0.394 | Same dataset. | Crystals |
| 29 | C08 EC traces non-recurrent | 0.139 | EC 0.01% vs OEIS 48% recurrence rate. | EC/OEIS |
| 30 | C94 Jones mod-2 → determinant | 0.701 | 71 fingerprint groups. | Knots |

## STRUCTURAL FINDINGS — Tier 2: Constraints (small but real, survive distributional nulls)

| # | Finding | eta² | Key evidence | Domain |
|---|---------|------|-------------|--------|
| 31 | Endomorphism → uniformity | 0.110 | M4/M² monotonic 5.01→1.32. CONSISTENT. | Genus-2 |
| 32 | R6 Isogeny nodes ~ MF count | 0.309 | r=-0.556, n=664. Cross-domain. | Isogeny/MF |
| 33 | ST → conductor | 0.013 | z=172 vs null. Log-normal replay z=24.9. | Genus-2 |
| 34 | R5 Isogeny-knot overlap | 0.047 | Primes that are knot dets differ in node count. | Cross-domain |
| 35 | C5 Composition curvature | partial r=0.42 | Stable across Jaccard 0.2-0.8 (CV=0.23). | Superconductors |
| 36 | C68 Selmer-root number parity | 0.013 | 73.1% match (48,392/66,158). | Genus-2 |
| 37 | G.R1.8 Crossing: det is conductor | 0.034 | Knot dets that are EC conductors have different CN. | Cross-domain |
| 38 | C84 Det → Alexander enrichment | 2.45x | Same-det knots have more similar Alexander polys. | Knots |
| 39 | G.R3.ec EC per conductor not Poisson | KS=0.46 | p=0. Mean 9.04 EC per conductor level. | EC |
| 40 | G.R4.mod Rank-2 conductor mod 12 | chi²=562 | p=2×10⁻¹¹³. Different residue distribution. | EC |
| 41 | C89 Torsion → root number proxy | 0.018 | 31K EC, 11 torsion groups. | EC |
| 42 | C88 SG → density | 0.190 | 77 SGs. | Crystals |
| 43 | C53 Level → coeff M4/M² | 0.071 | 14,989 Maass forms, 237 levels. | Maass forms |

## SCALING LAWS

| # | Finding | Slope | R² | Domain |
|---|---------|-------|-----|--------|
| 44 | C43 Prime gap M4/M² | 0.37/decade | 0.88 | Primes (10³ to 10⁸) |

## TENDENCIES (eta² 0.01-0.06, or weak consistent effects)

| # | Finding | eta² | Domain |
|---|---------|------|--------|
| 45 | N_elements → Tc | 0.018 after controls | Superconductors |
| 46 | C87 ST → torsion order | 0.084 | Genus-2 |
| 47 | C02 Mod-p starvation | 5.9% at p=3 | Modular forms |
| 48 | C04 HMF congruences | 1.21-1.30x enrichment | Hilbert MF |
| 49 | Fungrim type → n_symbols | 0.047 | Fungrim |
| 50 | C91 Galois → disc (degree 4) | 0.025 | Number fields |
| 51 | G.R5.3 Regulator ~ discriminant | R²=0.039 | Number fields |
| 52 | G.R2.pi Pi formulas → more symbols | 0.022 | Fungrim |
| 53 | Maass coeff AC(1) | 0.019 | Maass forms |
| 54 | C51 Rank → conductor | 0.011 | EC |
| 55 | G.alex Alexander entropy ~ crossing | 0.084 | Knots |
| 56 | C17 Knot det overlap with SG numbers | 115/167 | Cross-domain |
| 57 | G.R4.fung Within-module symbol growth | r=0.23 | Fungrim |
| 58 | R5.nfsg PG order / NF degree overlap | 5 values | Cross-domain |
| 59 | C93 Crystal nsites M4/M² | 13.7 | Crystals |

## NEGLIGIBLE (eta² < 0.01 or null)

| # | Finding | eta² | Domain |
|---|---------|------|--------|
| 60 | G.R2.d2 Div by 2 rank-0 vs rank-1 | 0.001 | EC |
| 61 | G.R2.d3 Div by 3 rank-0 vs rank-1 | 0.003 | EC |
| 62 | G.R2.d5 Div by 5 rank-0 vs rank-1 | 0.001 | EC |
| 63 | G.R2.d7 Div by 7 rank-0 vs rank-1 | 0.000 | EC |
| 64 | G.R2.d11 Div by 11 rank-0 vs rank-1 | 0.000 | EC |
| 65 | G.R2.d13 Div by 13 rank-0 vs rank-1 | 0.000 | EC |
| 66 | G.R3.3 Conductor digit entropy | 0.000 | EC |
| 67 | G.R5.nf NF disc: CN in knot dets | 0.000 | Cross-domain |
| 68 | G.R5.sg NF disc: CN in PG orders | 0.006 | Cross-domain |
| 69 | G2 ST → discriminant | 0.005 | Genus-2 |
| 70 | C78 Root number → conductor | 0.001 | Genus-2 |
| 71 | EC CM → conductor | 0.003 | EC |
| 72 | EC semistable → conductor | 0.003 | EC |
| 73 | NF degree → \|discriminant\| | 0.004 | Number fields |
| 74 | Maass Fricke → coeff shape | 0.000 | Maass forms |
| 75 | G.R2.zeta Zeta in fewer modules | 20/60 | Fungrim |
| 76 | C67 Alexander recurrence | 3/407 | Knots |

## KILLED (confirmed false, artifact, or confound)

| # | Finding | Kill mechanism |
|---|---------|---------------|
| 77 | C11 3-prime fingerprint | Artifact: every hash gives eta²≈0.49 (random-prime ablation) |
| 78 | C36 Galois → class number | Degree confound: partial eta²=0.000 after degree |
| 79 | C56 NF regulator by Galois | Degree confound: partial eta²=0.001 |
| 80 | C59 Crystal system → Tc | Absorbed by SG: partial eta²=0.000 |
| 81 | C48 S_n M4/M²=p(n)/n | False: ratio diverges (growth rates differ) |
| 82 | S5 Fricke enrichment | Null: 1.03x, p=0.18 |
| 83 | S6 Oscillation shadow | Already dead: z=0.84 |
| 84 | C60 Formation energy C3 | Second moment kills: M6≠C4 |

## SKIP (data format or insufficient data)

| # | Finding | Reason |
|---|---------|--------|
| 85 | C1 NIST config enrichment | Data has level energies, not wavelengths |
| 86 | C9 CODATA pseudometric | CODATA file not found in expected format |
| 87 | C10 Basis set recurrence | No standalone basis set data |
| 88 | C26 PDG mass | PDG file not found |
| 89 | C23 FindStat statistics | Format unexpected |
| 90 | C71 G2 adelic obstruction | No analytic rank data separate from torsion |
| 91 | Maass Fricke (F25b join) | Label mismatch partially resolved, eta²=0.0003 |

---

## SMOKE TEST RESULTS

| Test | Result | What it proved |
|------|--------|---------------|
| 1. Universal positive control (Euler chi) | **PASS** | F25 detects universal laws (OOS R²=0.66) |
| 2. Fake conditional law injection | **PASS** | 0/20 random groupings fool battery (real is 24x above) |
| 3. Representation sensitivity | **PASS** | SC_class→Tc degrades gradually under noise/transforms |
| 4. Synthetic interaction detection | **FAIL** | F25 conflates small groups with conditionality |
| 5. Continuous universal law (Deuring) | **PASS** | OOS R²=0.999999 (train p≡1, test p≡3) |

## COARSENING EXPERIMENT

| Grouping | n_groups | Med cell | F25b | Main R² |
|----------|----------|----------|------|---------|
| Full SG | 118 | 8 | WEAK_NOISY | -15.5 |
| Crystal system | 7 | 538 | WEAK_NOISY | -6.9 |
| Lattice type | 6 | 411 | WEAK_NOISY | -5.8 |
| Centro/non-centro | 2 | 1,464 | WEAK_NOISY | -6.6 |
| Tc k-means k=10 | 10 | 422 | UNIVERSAL | 0.61 |

**Conclusion:** Failure is NOT cell size — crystal system (538/group) fails while k-means (422/group) succeeds. The Tc mapping genuinely changes across chemical families at every symmetry level. This is true non-stationarity, not estimation noise.

---

## SUMMARY COUNTS

| Category | Count |
|----------|-------|
| Identities (deterministic/known) | 9 (1 false) |
| Rediscoveries | 7 + 23 genocide = 30 |
| Structural (Tier 1: strong, interaction-detected) | 14 |
| Constraints (Tier 2: small but real) | 13 |
| Scaling laws | 1 |
| Tendencies | 15 |
| Negligible | 17 |
| Killed | 8 |
| Skip | 7 |
| **Total classified** | **~100** |

## THE THREE KEY RESULTS

1. **The Tc variance decomposition** — SC_class 57%, SG 14%, interaction 11%, residual 15%. Replicated on COD. Coarsening proves non-stationarity is genuine.

2. **The methodological insight** — Detecting interaction ≠ verifying transportability. Different data requirements. Transfer tests fail on genuine conditional structure, not just noise. The 3-tier classification (Structural / Interaction-detected / Transfer-verified) is the correct framework.

3. **The meta-result** — Every categorical→continuous finding with a secondary grouping shows genuine non-stationarity (coarsening experiment). No symmetry-based grouping transfers Tc predictions across chemical families. This is a fact about the data-generating process, not the instrument.

---

*Compiled: 2026-04-12*
*Machines: M1 (Skullport) + M2 (SpectreX5)*
*Battery: v6 (F1-F27 + F25b)*
*Tests: ~100 across 3 rounds + 5 smoke tests + coarsening*
