# Deep Research Batch 6 — Seed Candidates

**Drafted by:** Aporia (autonomous tick T86)
**Date:** 2026-04-23
**Status:** Proposal; not yet executed. Filed pre-emptively while team in stand-down.

Batch 5 (reports 78–97) has been consumed. This file captures 20 candidate problems for Batch 6, keyed off the silences remaining after Batch 5 and the explicit voids from Aporia's running catalog. All entries follow the Batch 5 format (Charon/Harmonia/Ergon routing).

## Selection principle

Batch 5 was heavy on symmetry-class and ensemble statistics (KS, Sato–Tate, moments). Batch 6 pivots toward **operator-level** questions (per `feedback_verbs_over_nouns`) and **silent islands** (per `project_silent_islands`, `project_genus2_rosetta`). Where Batch 5 measured distributions, Batch 6 should measure *mechanisms*: Hecke orbits, isogeny graphs, congruence primes, mod-p reductions, stratifications.

## Candidate queue (20)

| # | Title | Target | Silence bridged | Est. CPU |
|---|---|---|---|---|
| 98 | **Hecke orbit equidistribution on HMF over real-quadratic** — empirical test of Zhang-Venkatesh | Harmonia | hmf × nf operator-level | 1 day |
| 99 | **Congruence prime distribution in HMF** — Ribet-style; deg-2 extension | Charon | hmf × mod-p gap | 4 hr |
| 100 | **Isogeny graph diameter on EC/Q at fixed conductor** — Mestre-Oesterle | Ergon | ec × graph-theoretic void | 6 hr |
| 101 | **p-adic uniformization rank for Shimura curves** — Drinfeld level structures | Harmonia | shimura × p-adic | 1 day |
| 102 | **Mod-p Galois image statistics for g=2 Jacobians** — Serre open-image at scale | Charon | g2c × mod-p | 8 hr |
| 103 | **Newton stratification on moduli of abelian varieties mod p** — empirical density | Harmonia | moduli × mod-p mass | 1 day |
| 104 | **Bianchi modular form base change to GL(2) over Q(√d)** — CM-tower check | Harmonia | bianchi × hmf | 8 hr |
| 105 | **Heegner-point height distribution at rank-0 CM** — Gross-Zagier empirical | Charon | heegner × bsd | 6 hr |
| 106 | **Ceresa cycle non-triviality count for g=3 curves** — Beilinson's height pairing | Ergon | g3 × motivic-cohomology | 1 day |
| 107 | **Stark unit recovery at LMFDB scale** — regulator factorization, paired with Rep 93 | Charon | stark × brumer-stark | 1 day |
| 108 | **Cuspidal cohomology of GL(n,Z) for n=5,6** — Harder-type empirics | Harmonia | arithmetic-group × cohomology | 3 days |
| 109 | **Rogers-Ramanujan-type identities beyond level 5** — Bressoud-Andrews catalog | Ergon | oeis × modular-form identity | 4 hr |
| 110 | **Mahler measure of K3 surfaces** — Deninger-Boyd empirics | Charon | k3 × mahler (extends Lehmer) | 1 day |
| 111 | **Farey fraction statistics on Hecke triangle groups** — Sarnak spectral | Ergon | hyperbolic × spectral-void | 6 hr |
| 112 | **Random Belyi map genus distribution** — Eskin-Okounkov vs Hurwitz | Harmonia | belyi × genus-distribution (V5) | 8 hr |
| 113 | **Euler product defect at small bad primes for g=2 L-functions** — extend Batch 5 mechanism (c) | Charon | g2c × arithmetic-channel | 6 hr |
| 114 | **Sato-Tate refinement for rank-2 EC over Q** — conditional on BSD | Charon | ec-rank2 × sato-tate | 8 hr |
| 115 | **Rational cusps in noncongruence subgroups of PSL(2,Z)** — Atkin-Swinnerton-Dyer | Harmonia | noncong × cusps | 1 day |
| 116 | **Empirical distribution of regulator-to-torsion ratios** — BSD Tamagawa calibration | Ergon | bsd × quantitative | 6 hr |
| 117 | **Twist family collisions: discriminant-matched EC families at high conductor** — finite-size selection test | Charon | ec × selection-bias audit | 8 hr |
| 118 | **Operator-correlation matrix on the 5-domain tensor** — direct test of `project_operator_insight` | Harmonia | cross-domain operator tensor | 3 days |

## Priority ordering (Aporia recommendation)

**Tier 1 (fire first):**
- 118: most aligned with `project_operator_insight`; if it lands clean, reframes Aporia's void catalog.
- 98: extends Batch 5 #94 (Langlands GL(2,NF)) to operator level.
- 113: directly continues F011 mechanism (c) Euler-product investigation.

**Tier 2 (operator/silence pivots):**
- 102, 103, 112, 104 — all bridge currently-silent islands.

**Tier 3 (empirics extending known tools):**
- 100, 105, 106, 107, 116 — reuse Techne's existing tool chain.

**Deferred (long-budget, scope-risk):**
- 108, 115 — multi-day; park until a slot opens.

## Fire order when James greenlights

Recommended: three at a time, same cadence as Batch 5. First wave (118, 98, 113) costs ~5 days compute total across three agents — comparable to Batch 5 first round.

## Status

- Not yet posted to agora.
- Will propose to James at next wake-up.
- All prior Batch 5 reports available for cross-reference in `F:/Prometheus/aporia/docs/deep_research_batch5/`.
