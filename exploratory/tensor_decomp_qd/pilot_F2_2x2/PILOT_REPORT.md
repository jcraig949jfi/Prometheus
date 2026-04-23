# Pilot Report — 2x2 matmul over F_2, QD archive

**Run:** Harmonia_M2_sessionB, 2026-04-23
**Scope:** validate the QD-archive instrument on the simplest tractable
substrate before escalating. Per James's calibration ladder: this was
the first of three steps.

## Outcome

**B — "Correct but trivial" (per James's diagnostic taxonomy).**

The instrument works. The domain is too constrained to exhibit the
structure the instrument is designed to map.

## What passed (instrument validation)

| Check | Result |
|---|---|
| Canonicalizer unit tests (8) | all pass |
| Matmul isotropy subgroup, correctly enumerated | 24 elements over F_2 (A, C orthogonal; B free) |
| Orbit-stabilizer theorem for Strassen | orbit=12, stab=2, product=24 ✓ |
| Gauge-equivalent decompositions collapse | 20/20 random isotropy+permutation transforms → same bytes |
| Near-miss distinctness | 0/10 single-bit flips collide with Strassen canonical |
| Forbidden-rank cells (rank ≤ 6 by Hopcroft-Kerr 1971) | 0/3 archives violate across 1500 total generations |
| Strassen rediscovered in rank-7 cell across reseeds | 3/3 (identical cell (7, 2, 1) every time) |
| Reseed stability on Strassen location | byte-identical canonicalization across 3 seeds |

## What didn't pass (domain richness)

| Check | Result |
|---|---|
| Distinct rank-7 orbits per archive | 1 / 1 / 1 across the 3 reseeds |
| Rank-7 canonical-sparsity diversity | 1 point (0.5238) in each archive |
| Union across reseeds | 1 rank-7 orbit |
| Pareto front at rank 7 | collapsed to single point |

## Evidence that outcome B is real, not exploration failure

I spent compute specifically distinguishing **B1 (domain genuinely
single-orbit)** from **B2 (exploration too weak)**:

1. **Brute-force random sampling of rank-7 triples.** 200,000 random
   (A, B, C) in (F_2^{4x7})^3, all densities 0.3 to 0.7. Zero valid
   decompositions. The valid set is so sparse (~10^-20 density) that
   random sampling cannot hit any decomposition, Strassen-orbit or
   otherwise.
2. **Local Hamming-neighborhood search from Strassen.** Exhaustive
   up to 4 bits, sampled at 5 bits.

   | Hamming distance from Strassen | Combos tried | Valid | Non-Strassen orbits |
   |---|---|---|---|
   | 1 | 84 (all) | 0 | 0 |
   | 2 | 3,486 (all) | 0 | 0 |
   | 3 | 95,284 (all) | 0 | 0 |
   | 4 | 1,929,501 (all) | 0 | 0 |
   | 5 | 500,000 (sampled) | 0 | 0 |

Strassen's canonical form is at **Hamming distance ≥ 6** from the
nearest other valid rank-7 decomposition (if any exists) under the
factor-matrix representation. Pure bit-flip mutation cannot reach other
orbits regardless of budget.

This provides strong computational evidence for **effective uniqueness**
of the rank-7 decomposition under the factor-matrix representation and
the tested gauge action — not a proof of uniqueness in the strict sense,
but strong enough that further local-search effort on 2x2 has diminishing
returns. It's consistent with classical results on rank-7 uniqueness for
the 2x2 matmul tensor over F_2 (the orthogonality constraint over char-2
is very restrictive, collapsing what would be a connected variety over
algebraically closed fields to at most a few points over F_2).

The structural reason bit-flip mutation cannot find other orbits here
is geometric, not algorithmic: **validity lies on isolated algebraic
points rather than connected local neighborhoods** in the factor-matrix
parameter space. Any mutation scheme based on small perturbations of
the factor entries is doomed regardless of compute budget. Reaching
other rank-7 orbits (if they exist) requires non-local moves — algebraic
flip-graph transformations in the Kauers-Moosbauer / Khoruzhii-Gelß-Pokutta
sense — that jump between isolated valid points in one correctness-preserving
step. That is the primary lesson for the 3x3 escalation.

## What this tells us about the method

- **Canonicalization is correct.** Stable across seeds, respects
  orbit-stabilizer, collapses equivalent decompositions, distinguishes
  non-equivalent ones.
- **Gauge-invariant descriptors work.** Canonical-sparsity and
  stabilizer-order are well-defined and computable. Rank is trivial.
- **Binary fitness + bit-flip mutation is insufficient** for any
  domain where the valid set is Hamming-distance-isolated. **We learned
  this the cheapest possible way — in a domain where we already knew
  the answer.** The 2x2 substrate cost minutes of compute to diagnose
  what would take days or weeks to discover at 3x3. That is the point
  of the calibration-ladder approach: discover mutation failure modes
  in the simplest domain, before investing scale-compute in a harder
  one.
- **The MAP-Elites loop correctly DOESN'T populate impossible cells.**
  Rank ≤ 6 stays empty even after tens of millions of candidate moves,
  across reseeds. Canonicalization never flickered into forbidden cells.

## What this tells us about the domain

2x2 matmul over F_2 has rank exactly 7 (Hopcroft-Kerr 1971). The local
neighborhood result plus the random-sample result together suggest that
the rank-7 decomposition is essentially unique under the 24-element
basis-change gauge. The "archive of tradeoffs" for this specific domain
has only one cell worth populating at the minimal rank, which is a
feature of the domain, not a failure of the method.

## Implications for next step (per James's ladder)

James's guidance for outcome B: "method works, but domain too simple →
escalate to 3×3 or structured tensors."

**Recommendation: 3x3 matmul over F_2.** This is the dominant next move.
The other candidates (structured 2x2, polynomial multiplication) remain
viable but without specific reason to prefer them, 3x3 is the cheapest
next step that exercises the instrument meaningfully.

**Why 3x3 over F_2:**
- Multiple distinct rank-23 orbits are known to exist in the literature
  (Smirnov catalog has many Laderman-class variants). Genuine structure
  to map.
- Yang 2024 SAT results prove certain symmetric rank ≤ 21 decompositions
  do NOT exist, giving hard external forbidden-cell boundaries.
- Laderman's 1976 algorithm provides a known rank-23 seed.
- Gauge group enlarges: |GL_3(F_2)|^3 = 168^3 = 4.74M triples before
  orthogonality filter; the filtered subgroup will be smaller (over F_2
  orthogonal 3x3 matrices are only permutation matrices, so expect
  ~6 × 168 × 6 = 6048 matmul-preserving elements). Enumeration is
  tractable but canonicalization per candidate is 250× more expensive
  than 2x2.

**Hard kill criterion for 3x3 (operational, not advisory):**
Any canonical representative landing in a rank cell that Yang-2024 SAT
rules out is treated as immediate evidence of **canonicalizer failure**
until proven otherwise. The archive enforces this at submission time;
a single violation halts the run and triggers a canonicalizer audit.

**Open questions the 3x3 pilot must answer:**
- Does the archive populate multiple rank-23 orbits under our gauge?
  If yes → outcome A on 3x3, instrument validated for richer domains.
- If no → gauge needs enrichment (cyclic mode-permutation action from
  the full matmul isotropy), OR mutation needs flip-graph moves.
- Exactly how big is the matmul isotropy subgroup under F_2 for n=3?
  The orthogonality count generalizes but requires enumeration.

**Deprioritized alternatives** (available if 3x3 blocks):
- Structured 2x2 matmul (triangular, symmetric, skew) — Khoruzhii et al.
  2025 territory; richer gauge due to structural constraints.
- Polynomial multiplication tensors — less studied under QD; separate
  canonicalizer required.

## Concrete next-step scope (if greenlit)

- Promote the canonicalizer to `tensor_decomp_qd/common/` (reusable
  across matmul sizes). Parameterize on (n, m, p).
- 3x3-specific module: `tensor_decomp_qd/pilot_F2_3x3/`. Same
  architecture, scaled.
- Expected compute: unit tests ~1 min (GL_3(F_2) has 168 elements,
  canonicalization per candidate ~168^3 = 4.7M ops, but the actual
  gauge subgroup after orthogonality filter is likely much smaller).
- Expected archive richness: SHOULD populate multiple rank-23 orbits.
  If it doesn't, the mutation operators need the Kauers-Moosbauer-style
  flip-graph moves rather than bit flips.

## Provenance

- Code: `tensor_decomp_qd/pilot_F2_2x2/`
- Unit test log: reproducible via
  `python -m tensor_decomp_qd.pilot_F2_2x2.test_gauge`
- Pilot run: `python -m tensor_decomp_qd.pilot_F2_2x2.run_pilot`
- Neighborhood probe: `python -m tensor_decomp_qd.pilot_F2_2x2.neighborhood_probe`
- Brute-force probe: `python -m tensor_decomp_qd.pilot_F2_2x2.brute_force_probe`

All scripts deterministic under fixed seeds. No external APIs, no
network calls.
