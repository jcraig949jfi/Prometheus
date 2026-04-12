# Complete Test Inventory — 2026-04-12
## All tests run or intended, across all sources, deduplicated and classified
## UPDATED after Round 2 (40 total tests, 20 per machine across 2 rounds)

---

## Round 1 Results (completed)

20 tests through frozen battery (F1-F24b). Results in `docs/round1_results_20260412/`.

- **9 confirmed** (4 conditional laws, 3 constraints, 1 scaling law, 1 tendency)
- **7 killed** (E_6 tautology, C48 false, S5/S6/C36/C56/C59 dead)
- **3 suspect** (C11, C5, interaction term)
- **1 skip** (C1 NIST data format)

## Round 2 Results (completed)

20 tests through battery v6 (F1-F27). M1: 8 scripts + 8 result JSONs. M2: 2 scripts + inline results.

### M2 Follow-ups (Round 1 suspects resolved)

| Test | Result | Verdict |
|------|--------|---------|
| R2.1 C11 random-prime ablation | Every prime set gives eta²≈0.493, z=-0.5 | **KILLED** (any hash works the same) |
| R2.2 C5 Jaccard threshold sweep | Partial r stable 0.33-0.57 across 0.2-0.8 | **SURVIVES** → CONSTRAINT |
| R2.3 Interaction class-balanced | Balanced: 11.0% (up from 8.5%) | **REAL** (not class imbalance) |
| R2.4 COD cross-validation | eta²(SG→Tc)=0.41 on 70 independent COD curves | **REPLICATES** externally |

### M2 New Tests

| Test | eta² | Classification |
|------|------|---------------|
| C86 Isogeny diameter scaling | R²=0.94, diam=0.97·log(p)-1.22 | **LAW** (likely known — Ramanujan graph) |
| C05 Maass spectral (level→R) | 0.824 | **LAW** (likely Weyl's law — needs F27 check) |
| C68 Selmer-root number parity | 0.013 (73.1% match confirmed) | CONSTRAINT |
| C87 ST→torsion order | 0.084, F25 CONTEXT_DEPENDENT | TENDENCY |
| C50-deep multi-variable | Confirms: 0.013, 0.005, 0.084 | No change from R1 |

### M1 New Tests

| Test | Key metric | Classification |
|------|-----------|---------------|
| C01 Paramodular conjecture | 7/7 levels matched (100%) | **REDISCOVERY** (paramodular conjecture) |
| C02 Mod-p starvation | 5.9% at p=3, <1% at p=5,7,11 | TENDENCY (starvation is real but rare) |
| C04 HMF congruences | Enrichment 1.21x (mod-2), 1.30x (mod-3) | TENDENCY (weak enrichment) |
| C08 Recurrence duality | EC rate 0.01% vs OEIS 48%, eta²=0.139 | **LAW** (EC traces are NOT recurrent) |
| C09 Moonshine class structure | eta²=0.601, 26 classes | **LAW** (class determines coefficient scale) |
| C21 NF class number by degree | eta²=0.280, F25 CONDITIONAL | **CONDITIONAL LAW** |
| C41-deep Unit circle identity | Jones-Alex cosine=0.919, crossing eta²=0.001 | **STRUCTURAL IDENTITY** |
| C43-ext Prime gap scaling | Slope refined to 0.37/decade, R²=0.88 | SCALING LAW (eta² as grouping=0.004) |

---

## Cumulative Summary (40 tests across 2 rounds)

| Category | Count |
|----------|-------|
| **Conditional Laws** | 6 (SC_class→Tc, SG×SC→Tc, N_elem→Tc, crossing→det, C21 NF class#, C09 moonshine) |
| **Laws (domain-internal / likely known)** | 4 (C41 unit circle, C86 isogeny diam, C05 Maass spectral, C08 EC non-recurrence) |
| **Constraints** | 4 (ST→conductor, endomorphism→uniformity, C5 curvature, C68 Selmer parity) |
| **Scaling Laws** | 1 (C43 prime gap 0.37/decade) |
| **Tendencies** | 4 (N_elem, C87 torsion, C02 starvation, C04 HMF congruences) |
| **Rediscoveries** | 2 (C01 paramodular, modularity theorem) + 23 prior genocide |
| **Identities** | 2 (C41-deep Jones≈Alexander, max Jones~det) |
| **Killed** | 11 (E_6 tautology, C48 false, C11 artifact, S5/S6/C36/C56/C59, KMT, C60) |
| **Skip / Data issue** | 2 (C1 NIST format, C71 not F24-classified) |

**Total tested: 40 | Remaining in queue: ~125**

**Novel findings that are NOT known math or rediscoveries:**
- SC_class → Tc (eta²=0.57) — quantified domain knowledge (conditional)
- (SG × SC_class) → Tc (14% + 11% interaction) — replicated on COD
- C5 composition curvature (partial r=0.42) — threshold-stable
- C09 moonshine class → coefficient scale (eta²=0.60) — needs F27 check

**Key battery improvement validated:** F25 (transportability) correctly classifies conditional vs universal. F27 (consequence checker) needs expansion for Weyl's law, Ramanujan graphs, paramodular conjecture.

---

## PART 1: THE CLEAN LIST — What to rerun with the frozen battery

### Tier A: Rerun immediately (high eta², strong prior, frozen battery ready)

These have data, have been tested before, and are the strongest candidates for the
LAW/CONDITIONAL LAW/CONSTRAINT/IDENTITY classification system.

| # | ID | Claim | Domain | Prior result | Why rerun |
|---|---|---|---|---|---|
| 1 | C85/SC.1 | SC_class → Tc | Superconductors | eta²=0.570 CONDITIONAL LAW | Anchor. Already classified. Baseline for comparison. |
| 2 | C32/SC.2 | SG → Tc | Superconductors | eta²=0.457 CONDITIONAL LAW | Anchor. Interaction structure mapped. |
| 3 | C4/SC.3 | N_elements → Tc | Superconductors | eta²=0.329, 0.018 after controls | Needs interaction classification |
| 4 | C59 | Crystal system → Tc | Superconductors | eta²=0.128 TENDENCY | Absorbed by SG? Confirm. |
| 5 | C36 | Galois group → class number | Number fields | eta²=0.138, KILLED by F17 (degree confound) | Rerun with interaction analysis |
| 6 | C35 | Crossing number → determinant | Knots | eta²=0.219 LAW | Need Alexander control (knot data issue) |
| 7 | C50/G2.1 | ST group → conductor | Genus-2 | eta²=0.013 CONSTRAINT | Confirmed real by stress test |
| 8 | C81 | ST → conductor exponent structure | Genus-2 | eta²=0.110 CONSTRAINT | Upgraded from 0.05, confirmed |
| 9 | E6_RN | E_6 forces root number = +1 | Genus-2 | 51/51, P=2^{-51} EXACT IDENTITY | Verify on full 66K dataset |
| 10 | C37/K1 | Knot det M4/M² = 2.155 | Knots | [2.092, 2.217], NOT SU(2) | Rerun with F24+F24b, classify |

### Tier B: Rerun with care (moderate signal, needs interaction analysis)

| # | ID | Claim | Domain | Prior result | Why rerun |
|---|---|---|---|---|---|
| 11 | C1 | Config enrichment by electron config | NIST atomic | 11.8x (detrended from 16.4x) | Needs F17 with Z as confound |
| 12 | C12/S4 | Lean proof power law B=0.47 | mathlib | Enrichment 2.64x (corrected) | Needs F18 on full mathlib |
| 13 | C5/S6 | SC composition curvature κ=-0.38 | Superconductors | r(Tc,κ)=-0.479 | F17: is curvature just node degree? |
| 14 | C48/S2 | S_n character M4/M² = p(n)/n | S_n characters | Exact mathematical identity | Verify derivation, classify as IDENTITY |
| 15 | C43/S3 | Prime gap M4/M² scales +0.23/decade | Primes | 4.60, monotonic toward Poisson | Extend to 10^8, 10^9 primes |
| 16 | C41/S1 | Knot poly unit circle profiles distinct | Knots | Rich 13-point profile | F18 stability, different knot databases |
| 17 | C52 | NF discriminant moments by degree | Number fields | Regulator scales with degree | F24 + interaction with Galois |
| 18 | C56 | NF regulator by Galois within degree | Number fields | Varies by Galois | F17 confound (degree mediates?) |
| 19 | C11 | 3-prime rigidity on SC compositions | Superconductors | 4.2x collapse, Tc enrichment 3.0x | F24 magnitude check |
| 20 | C55 | Enrichment meta-analysis | Cross-domain | 30+ enrichment values | Re-audit with F24 lens |

### Tier C: Rerun if time allows (weak signal, exploratory, or needs data work)

| # | ID | Claim | Domain | Prior result | Why rerun |
|---|---|---|---|---|---|
| 21 | C10 | Basis set exponent recurrence | Chemistry | R²=0.93 geometric | Possibly trivial |
| 22 | C8 | Logistic map phase coherence | Dynamical systems | Exact (chaos 0.028, periodic 0.247) | Classify as IDENTITY |
| 23 | C9 | Gamma pseudometric on CODATA | Physics constants | 0/100K triangle violations, weak enrichment | Probably noise |
| 24 | C26 | PDG particle mass analysis | Particle physics | M4/M²=69.6 | F24: what grouping? |
| 25 | C16 | Space group zeta derivative | Space groups | Z'/Z residues computed | Classify |
| 26 | C63 | mathlib moment landscape | mathlib | Moment hierarchy measured | Likely representation artifact |
| 27 | C53 | Maass coefficient moments | Maass forms | By symmetry/level | F24 classification |
| 28 | C54 | Conway polynomial moments | Knots | M4/M²=9.43 | F24 classification |
| 29 | C64 | Element identity enrichment | Atomic spectra | Predicts spectral properties | F17 confound |
| 30 | C38 | SG predictability landscape | Crystals | SG→Tc 1.70x, SG→bg null | Already subsumed by SC.2 |

### Tier D: BLOCKED or PARKED (need data or infrastructure)

| # | ID | Claim | Domain | Blocker |
|---|---|---|---|---|
| 31 | C01 | Paramodular conjecture | Genus-2/Siegel | Data available but matching complex |
| 32 | C02 | Mod-p starvation scan | LMFDB | 43.6% show starvation — needs deeper analysis |
| 33 | C04 | Hilbert congruence scan | HMF (368K) | Ready to run |
| 34 | C13 | Genus-3 Sato-Tate | Genus-3 | Need Frobenius computation |
| 35 | C14 | Maeda conjecture | Hecke algebra | Level-1 data available in LMFDB dump |
| 36 | C15 | Hida p-adic families | Modular forms | Need multi-weight forms at same level |
| 37 | C61/C74/C77/C79 | Isogeny graph analysis | Isogenies | NPZ format parsed, ready |
| 38 | C09 | Moonshine network expansion | OEIS/LMFDB | 307 bridges found, needs deeper filter |

### Tier E: KILLED or IDENTITY (no rerun needed, archive)

| # | ID | Claim | Kill reason |
|---|---|---|---|
| 39 | max Jones ~ det | Near-identity | R²=0.995, functional dependence |
| 40 | Jones length ~ crossing | Known theorem | Kauffman-Murasugi-Thistlethwaite |
| 41 | EC ~ MF count | Modularity theorem | Wiles 1995 (rediscovery) |
| 42 | K9/C36-Galois | Galois enrichment on CN | F17: degree confound dominates |
| 43 | K10 | Isogeny single-slope | F23: slopes vary 0.71-1.94 |
| 44 | K3/C2 | CMB Catalan chain | M4/M²=4.54, not automorphic |
| 45 | K4/C7 | Earthquake phase coherence | r=-0.16 null |
| 46 | K6/C60 | Formation energy C3 | M6 kills second moment |
| 47 | K7/C42 | Ionization enrichment | 0.97x null |
| 48 | K8/C47 | ST → discriminant enrichment | 0.82x anti-enrichment |
| 49 | C17 | Collatz algebraic sibling | Kills connection (x²-1)² |
| 50 | C3/C44 | Maass repulsion | Cannot reproduce (r≈0 null) |

---

## PART 2: CHARON SPECTRAL FINDINGS (separate track)

These are from the L-function zero geometry work, a different research program
from the cartography cross-domain work. They have their own battery (3 batteries,
16 kill tests).

| # | Finding | Status | Key metric | Rerun? |
|---|---|---|---|---|
| S1 | Spectral tail (z5-19) rank encoding | CONFIRMED | ARI=0.55, z=14.0 | No — already 16 kills survived |
| S2 | Three-layer decomposition | ESTABLISHED | GUE 90%, residual 0.05 | No — architecture validated |
| S3 | Zero-graph orthogonality | CONFIRMED | ρ=0.043 | No |
| S4 | Type-B form characterization | CHARACTERIZED | 27K objects, 1 cluster | No — not a discovery |
| S5 | Fricke enrichment 1.44x | OPEN | 1.44x, mechanism unknown | Yes — run through F24 |
| S6 | Oscillation shadow | TESTED | p=0.001 | Yes — needs F24 magnitude |
| S7 | Tamagawa fingerprint | ORTHOGONAL | p=1e-5, explains 1.1% | No — confirmed orthogonal |
| S8 | Spectral survey (5 families) | NO_EFFECT | EC-specific only | No — established negative |

---

## PART 3: RECOMMENDATIONS

### Option A: Focused rerun (2-3 hours, 1 machine)
Run Tier A (10 tests) through the frozen battery with interaction analysis.
Produces a clean, definitive classification of the top findings.
**Best if**: we want to publish or present results soon.

### Option B: Comprehensive rerun (6-8 hours, 2 machines split)
Tier A + B (20 tests) through frozen battery + interaction analysis.
M1 takes odd numbers, M2 takes even numbers.
**Best if**: we want a thorough sweep before moving to new territory.

### Option C: Full audit (12+ hours, 2 machines parallel)
All 50 tests from Tiers A-D through full pipeline.
Includes unblocking blocked tests (C01, C04, C14).
**Best if**: we want to close out the entire backlog.

### Recommendation: Option B

Tier A is already mostly done (session 2 today). Tier B has the best
risk-reward ratio — moderate signals that could upgrade or kill with
the new instrument. Tier C is mostly noise or trivia. Tier D needs
infrastructure work that may not pay off.

### Machine Assignments (Option B)

#### M1 — Skullport (10 tests)

| # | ID | Claim | Tier | Notes |
|---|---|---|---|---|
| 1 | C36 | Galois group → class number | A | Rerun with interaction (degree as secondary) |
| 2 | C35 | Crossing number → determinant | A | Fix knot loader, add Alexander control |
| 3 | C37/K1 | Knot det M4/M² = 2.155 | A | F24+F24b classification |
| 4 | C52 | NF discriminant moments by degree | B | F24 + interaction with Galois |
| 5 | C56 | NF regulator by Galois within degree | B | F17 confound (degree mediates?) |
| 6 | C41/S1 | Knot poly unit circle profiles | B | F18 stability |
| 7 | C48/S2 | S_n character M4/M² = p(n)/n | B | Verify derivation → IDENTITY |
| 8 | C43/S3 | Prime gap M4/M² scales +0.23/decade | B | Extend to larger primes |
| 9 | S5 | Fricke enrichment 1.44x | Charon | Run through F24 |
| 10 | S6 | Oscillation shadow | Charon | F24 magnitude check |

#### M2 — SpectreX5 (10 tests)

| # | ID | Claim | Tier | Notes |
|---|---|---|---|---|
| 1 | C85/SC.1 | SC_class → Tc | A | Already done. Anchor baseline. |
| 2 | C32/SC.2 | SG → Tc | A | Already done. Interaction mapped. |
| 3 | C4/SC.3 | N_elements → Tc | A | Needs interaction classification |
| 4 | C59 | Crystal system → Tc | A | Confirm absorbed by SG |
| 5 | C50/G2.1 | ST group → conductor | A | Confirmed CONSTRAINT |
| 6 | C81 | ST → conductor exponent structure | A | Confirmed CONSTRAINT |
| 7 | E6_RN | E_6 root number = +1 | A | Verify on full dataset |
| 8 | C1 | Config enrichment | B | F17 with Z confound |
| 9 | C5/S6 | SC curvature κ=-0.38 | B | F17: curvature vs node degree |
| 10 | C11 | 3-prime rigidity on SC | B | F24 magnitude check |

---

## PART 4: ARCHIVED FILES

Moved to `cartography/docs/challenges/archive/` on 2026-04-12:

5_From_Each.md, 5_From_Each_Part_2.md, 10_From_Each_Part_3.md,
10_From_Each_Part_4.md, problems_to_solve_frontier.md,
problems_to_solve_frontier2.md, challenges_from_frontier_models_v2.md,
challenges_from_frontier_models_v3.md, challenges_from_frontier_models_v4.md,
20_challenges_from_frontier.md (11 files)

**Retained** (authoritative reference):
- **This file** (test_inventory_20260412.md) — the authoritative test list
- challenge_run_20260411.md — main working log
- challenge_queue.md — consolidated queue (C01-C17)
- findings_tiered_20260411.md — tier classifications (pre-F24)
- audit_all_wins_20260411.md — audit trail
- all_new_challenges_20260411.md — frontier model originals
- prompt files — for reproducibility

---

## ROUND 2: Machine Assignments (battery v6: F1-F27)

### Follow-ups from Round 1 (must do first)

| # | Test | Machine | Why |
|---|------|---------|-----|
| R2.1 | **Random-prime ablation for C11** — test (2,3,5), (5,7,11), random hashes | M2 | Kills or validates our most suspect finding |
| R2.2 | **Jaccard threshold sweep for C5** — vary 0.3→0.7, plot partial r | M2 | Kills or promotes composition curvature |
| R2.3 | **Class-balanced interaction resampling** — subsample SGs to equal representation across classes | M2 | Addresses main council critique of 8.5% interaction |
| R2.4 | **ICSD/AFLOW cross-validation** — replicate SC_class→Tc and SG→Tc on independent structural data | M2 | CRITICAL external replication. Data already pulled. |

### M1 — Skullport (10 tests)

| # | ID | Claim | Source | Notes |
|---|---|---|---|---|
| 1 | C01 | Paramodular conjecture probe | Tier 1 queue | Siegel eigenvalues + genus-2 matching. Data available. |
| 2 | C04 | Hilbert modular form congruence scan | Tier 1 queue | 368K HMF records. Ready to run. |
| 3 | C02 | Mod-p residue starvation (deeper) | Tier 1 queue | 43.6% show starvation — which primes, which weights? |
| 4 | C09 | Moonshine network expansion | Tier 2 queue | 307 bridges found, needs F24 + F25 classification |
| 5 | C41-deep | Unit circle profile independence test | Round 1 follow-up | Jones-Alexander cosine=0.933 — is this known? F25 across crossing strata |
| 6 | C43-ext | Prime gap scaling extension to 10^9 | Round 1 follow-up | Confirm 0.43/decade at larger scale |
| 7 | C10 | Constraint collapse generalization | Tier 2 queue | Log-log slope ratio 1.71 vs theory 2.0 |
| 8 | C08 | Recurrence operator duality (OEIS vs EC) | Tier 2 queue | EC depleted 0.25x, genus-2 11.3x enrichment |
| 9 | C21 | Number field class number distribution shape | Tier B (C-series) | Sharp degree-dependence — F24 + F25 |
| 10 | C07 | Hecke congruence graph structure | Tier 2 queue | 83 cross-prime congruences |

### M2 — SpectreX5 (10 tests)

| # | ID | Claim | Source | Notes |
|---|---|---|---|---|
| 1 | R2.1 | Random-prime ablation for C11 | Follow-up | Kill or validate 3-prime fingerprint |
| 2 | R2.2 | Jaccard threshold sweep for C5 | Follow-up | Kill or promote curvature |
| 3 | R2.3 | Class-balanced interaction test | Follow-up | Deflate or confirm 8.5% interaction |
| 4 | R2.4 | ICSD/AFLOW SC replication | Follow-up | External validation of SC findings |
| 5 | C68 | Genus-2 Selmer-root number parity | C-series | 73.1% match rate — F24 classification |
| 6 | C86 | Isogeny graph diameter scaling | C-series | 3,240 primes — F24 + F25 |
| 7 | C05 | Spectral operator matching | Tier 1 queue | Maass spectral spacing vs EC/knots/lattices |
| 8 | C71 | Genus-2 adelic obstruction density | C-series | Completed but not F24-classified |
| 9 | C50-deep | G2 multi-variable interaction | Follow-up | ST→torsion, ST→disc, torsion→disc — F25 on each |
| 10 | C87 | Genus-2 torsion group analysis | C-series | Torsion distribution by ST group — F24 + F25 |

---

*Inventory updated: 2026-04-12 (post-Round 1)*
*Battery: v6 (F1-F27, unfrozen for F25-F27 only)*
*Round 1 results: docs/round1_results_20260412/*
*Round 2: 20 tests assigned (4 follow-ups + 16 new)*
