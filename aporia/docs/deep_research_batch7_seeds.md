# Deep Research Batch 7 — Seed Candidates

**Drafted by:** Aporia
**Date:** 2026-04-23
**Status:** 20 candidates drafted, awaiting James greenlight to fire.

Batch 5 (78–97) covered KS/Sato-Tate ensemble statistics. Batch 6 (98–118) pivoted to operator-level and silent-island coverage. Batch 7 opens three new fronts not yet plumbed:

1. **Cross-domain operator transport** (can operators *move* between domains at scale?)
2. **Motivic / K-theoretic invariants** (beyond Dirichlet-Beilinson, beyond genus-3)
3. **Rare-structure probes** (mock modular, knot concordance, arithmetic dynamics, ray class structure)

## Candidate queue (20, numbered 119–138)

| # | Title | Target | New front | Est. CPU |
|---|---|---|---|---|
| 119 | **Hecke ↔ Frobenius transport at LMFDB scale** — can Hecke eigenvalues on HMF be recovered from Frobenius data on associated EC/g2c at prime ideals of O_K? | Harmonia | operator transport | 1 day |
| 120 | **p-adic L-function at LMFDB scale** — Mazur-Tate-Teitelbaum zeros across 10^4 ordinary EC | Charon | p-adic analytic | 6 hr |
| 121 | **Motivic height × Faltings height correlation** — Beilinson-Bloch pairing vs Faltings across g=2,3 Jacobians | Harmonia | motivic / K-theoretic | 1 day |
| 122 | **Mock modular completion statistics** — Zagier error term growth across LMFDB harmonic-Maass forms | Harmonia | rare structure | 8 hr |
| 123 | **Knot concordance rank empirics** — smooth vs topological slice genus across 10^4 knots | Ergon | knot-silence pivot | 6 hr |
| 124 | **Ray class group structure at LMFDB scale** — genus-theoretic decomposition across ~10^6 NF | Charon | class-field theory | 4 hr |
| 125 | **Arithmetic dynamics preperiodic density** — Morton-Silverman bounds at scale across rational-function iterates | Ergon | dynamics | 1 day |
| 126 | **Ш analytic order distribution** — Tate-Shafarevich order histogram across rank-0 EC at log cond > 8 | Charon | BSD-tail | 4 hr |
| 127 | **Higher L-function moments** — extend Conrey-Keating-Snaith beyond M_4 to M_6, M_8 for rank-0 EC | Charon | RMT moments | 8 hr |
| 128 | **Selberg trace formula empirics** — PSL(2,Z) Laplace spectrum low-lying zero statistics | Ergon | spectral | 6 hr |
| 129 | **Twisted L-function root number distribution** — ε(E, χ) for χ quadratic Dirichlet across 10^5 twists | Charon | root number | 4 hr |
| 130 | **Cohen-Lenstra across class-group strata** — stratified p-part density for p ∈ {3,5,7,11} | Harmonia | class groups | 6 hr |
| 131 | **Siegel modular forms genus 3** — first-pass cataloging from Bergström-Faber-van der Geer tables | Harmonia | Siegel | 1 day |
| 132 | **Local Langlands depth-zero census** — supercuspidal representations across GL(2)/Q_p, p ≤ 19 | Harmonia | local Langlands | 1 day |
| 133 | **Hypergeometric motives L-function empirics** — Rodriguez-Villegas HGM family Sato-Tate scan | Charon | HGM | 8 hr |
| 134 | **Hilbert scheme Göttsche generating function** — Euler characteristic sequences for Hilb^n(K3) | Ergon | moduli / OEIS | 4 hr |
| 135 | **Dedekind η-quotient rationality at level > 100** — complement to Batch 6 #109 at extended range | Ergon | modular | 6 hr |
| 136 | **Algebraic K-theory regulators** — Beilinson regulator at scale for number fields, matched to ζ_F'(0) | Charon | K-theory | 1 day |
| 137 | **Arithmetic progressions in OEIS prime sequences** — Green-Tao-style empirics across OEIS-indexed prime families | Ergon | OEIS / primes | 6 hr |
| 138 | **Minkowski constant sharpness across NF** — how close does disc lower bound come to Minkowski bound, stratified by degree/signature | Ergon | geometry of numbers | 4 hr |

## Priority ordering (Aporia recommendation)

**Tier 1 (fire first — genuinely new fronts):**
- 119 Hecke ↔ Frobenius transport: directly probes `project_operator_insight` claim that operators cross domains; combined with Batch 6 #118 operator tensor, gives the transport half of the picture.
- 121 Motivic height × Faltings: opens motivic cohomology channel not touched by Batches 5/6; pairs with Batch 6 #106 Ceresa.
- 120 p-adic L-function at scale: unlocks p-adic BSD family of tests.

**Tier 2 (rare-structure silent-island pivots):**
- 122, 123, 125, 131, 132 — targeted at silent islands (harmonic Maass, knots, dynamics, Siegel, local reps).

**Tier 3 (RMT / tail-empirics extending known tools):**
- 126, 127, 128, 129 — push existing L-function and trace-formula machinery further.

**Tier 4 (structural & combinatorial):**
- 124, 130, 134, 135, 137, 138 — clean cataloging runs that generate calibration data.

**Long-budget (defer):**
- 133, 136 — multi-day; park until slot opens.

## Fire order when James greenlights

Three at a time, same cadence as Batch 5 and 6. First wave (119, 121, 120) costs ~2.5 compute days in aggregate. Ready on signal.

## Status

- Not yet posted to agora.
- 20 candidates drafted; will expand queue by 5 if James prefers a larger pool.
- All prior Batch 5/6 reports available for cross-reference.
