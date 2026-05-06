# Charon 3 — Batch summary (Topology / Geometry)

**Date:** 2026-05-05
**Researcher:** Charon 3 (single batch, fresh instantiation for this task)
**Time spent:** ~3.5 hours total (well under 15 h cap; surface-area-over-depth choice)
**Files written:**
- `charon_3_01_smooth_4d_poincare.md` (~35 min, NO_PROGRESS_DOCUMENTED_OBSTACLES)
- `charon_3_02_hodge_conjecture.md` (~40 min, PARTIAL_RESULT)
- `charon_3_03_novikov.md` (~30 min, NO_PROGRESS_DOCUMENTED_OBSTACLES)
- `charon_3_04_volume_conjecture.md` (~50 min, PARTIAL_RESULT — figure-eight calibration succeeded, 5_2 numerical attempt killed by wrong literature formula)
- `charon_3_05_hadwiger_nelson.md` (~40 min, PARTIAL_RESULT — Moser spindle constructed and χ=4 verified)
- `charon_3_SUMMARY.md` (this file)

## Time-cap discipline

I deliberately stopped each problem at ~30–50 minutes rather than running to the 3-hour cap. Per the brief's "surface area > depth" guidance: a thorough INCONCLUSIVE/PARTIAL with rich kill-data is more valuable than a marginal-progress 3-hour push that wouldn't change any verdict. **None of the five problems is closable by additional hours of literature work; all five require a methodological breakthrough.** The two computational attacks (Volume Conjecture for figure-eight, Hadwiger–Nelson Moser spindle) used most of the per-problem time budget; the three pure literature-survey attacks (Smooth 4D Poincaré, Hodge, Novikov) reached the obstruction map quickly.

## Cross-problem obstruction-class table

| Problem | Primary obstruction | Secondary obstruction | "Insufficient invariant" pattern? |
|---|---|---|---|
| Smooth 4D Poincaré | instrument-vanishes-on-target (Donaldson/SW dim < 0 on S⁴) | candidate-list-vs-universal-claim (Cappell–Shaneson elimination ≠ proof) | **YES — explicit:** the entire gauge-theoretic invariant family vanishes on b₂⁺=0 |
| Hodge / CY3 | case_restriction (cup-product H^{1,1}⊗H^{1,1}→H^{2,2} surjectivity not universal) | requires_unproven_conjecture (standard conjectures equivalent) | **YES:** Lefschetz (1,1) detects codim 1 perfectly, but cup-product structure on H^{1,1} is the insufficient extension to codim 2 |
| Novikov / Burnside, Gromov monster | unknown-property-of-input (Property A, Haagerup, asdim all open for B(m,n)) | entire-tool-family-blind (Gromov monsters fail every standard hypothesis) | **YES:** every available invariant (Higson-Kasparov a-T-menability, Yu coarse BC, Lafforgue, Connes-Moscovici cyclic) is built on a geometric input that the target group lacks |
| Volume Conjecture / 5_2 | stationary-phase-multivalued (Ohtsuki gets consistency, can't pin saddle) | method_complexity (correct J_N formula is double-sum, not single-sum) | **YES:** Kashaev-style computation works for figure-eight but the saddle-point analysis instrument is "insufficient" once the A-polynomial has degree ≥ 2 in L |
| Hadwiger–Nelson | construction-method-limit-reached (no 6-chromatic UDG known) | naive-composition-doesn't-scale | **YES:** Moser spindle gives χ ≥ 4, de Grey gives χ ≥ 5; the construction primitive runs out at exactly the boundary of current knowledge |

## Cross-problem patterns I noticed

### Pattern 1 — The "insufficient invariant" shape is the dominant obstruction class

The brief flagged this pattern explicitly: *invariants that DETECT a lot but cannot DISTINGUISH the specific case*. Across all 5 problems, **every standard tool for the relevant domain has this shape on the open target**:

- Donaldson invariants distinguish many smooth 4-manifolds; vanish on S⁴.
- Lefschetz (1,1) proves Hodge for codim 1; H^{1,1}⊗H^{1,1}→H^{2,2} cup-product is not surjective in general for codim 2.
- Higson-Kasparov, Yu coarse BC, Lafforgue, Connes-Moscovici each prove Novikov for a specific class of groups (a-T-menable, Property A, hyperbolic, …); each FAILS on Burnside groups and Gromov monsters.
- Kashaev's formula for figure-eight succeeds; the analogous single-sum form fails for 5_2 (needs double sum) — and even with the correct formula, the saddle-point analysis runs out at degree-2 A-polynomials.
- Moser spindle gives χ ≥ 4; de Grey's much more elaborate construction reaches χ ≥ 5; **no construction principle is known for χ ≥ 6**.

This is the classic pattern of a problem that has resisted decades of effort: the toolkit gets progressively richer, each new tool proves a stronger result on a wider class, but the **final case** is precisely where every tool's underlying geometric/algebraic input collapses.

### Pattern 2 — Computational verification has a hard ceiling on every conjecture in this batch

- Smooth 4D Poincaré: cannot computationally test (no candidate exotic S⁴ where the gauge invariants are non-trivial).
- Hodge / CY3: numerical period computations on the mirror quintic family produce no Hodge-conjecture counterexample, but absence is not proof.
- Novikov: not a computationally testable conjecture; concerns abstract K-theoretic structure on infinite groups.
- Volume Conjecture: numerical convergence verified for figure-eight at N = 2000 (gap +0.035); for 5_2 the correct formula is harder; even with arbitrary-precision arithmetic, finite N is not a proof. **Convergence at N=10⁶ would still not be a proof.**
- Hadwiger–Nelson: SAT verification works for χ ≥ 5 (de Grey, Heule); **computational search for χ ≥ 6 has been running for 7+ years (Polymath16) without a hit.** The compute-productive direction is now methodological, not brute-force.

The substrate-grade observation: each of these problems sits where the available computational instruments either (a) cannot produce a counterexample/witness because the specific manifold/variety/group has no candidate to test (4D Poincaré, Novikov), or (b) can produce evidence-supporting numerics but cannot close the conjecture (Hodge, Volume Conjecture, Hadwiger–Nelson). **Pure compute-scaling is wasted on this batch.**

### Pattern 3 — At least one computational win per batch is achievable

Per the brief's request for "any computational wins":

- **Hadwiger–Nelson:** verified Moser spindle has χ = 4 by brute-force enumeration with exact unit-distance coordinates. Reproducible <30 sec. Pre-2018 lower bound recovered cleanly.
- **Volume Conjecture:** verified figure-eight VC numerics at N = 10, 20, 50, 100, 200, 500, 1000, 2000 with monotonic convergence; gap +0.035 at N=2000. Confirmed the correct asymptotic shape (2π·log|J_N|/N → Vol). Identified that one published 5_2 colored-Jones formula (single-sum twist-knot form) gives **non-VC-compliant numerics** — kill data on which literature normalization to trust.
- **SnapPy verified hyperbolic volumes** for 10 small knots (4_1, 5_2, 6_1, 6_2, 6_3, 7_2, 7_3, 7_4, 8_18, 10_139). Reproducible inputs for any subsequent VC numerical work.

These are small but clean substrate contributions. The Volume Conjecture single-sum-formula kill is the best individual finding: a published formula that compiles correctly but gives demonstrably wrong asymptotic behavior is exactly the kind of "watch out for this normalization" data that a substrate-grade kill record should preserve.

### Pattern 4 — The "candidate-vs-universal-claim" pattern is structural

Across multiple problems the attack-elimination strategy hits a structural ceiling:

- Smooth 4D Poincaré: ruling out Cappell-Shaneson candidates one family at a time cannot prove SPC4 unless a structure theorem says every homotopy 4-sphere is one of those families. No such structure theorem.
- Volume Conjecture: proving VC for individual knots (figure-eight, (2, 2k+1) torus, Whitehead) does not produce a path to the universal statement; each new knot family requires its own analysis.
- Hadwiger–Nelson: every 5-chromatic unit-distance graph constructed so far is a refinement of de Grey's basic strategy; reaching χ ≥ 6 requires a NEW construction principle, not more refinement.

**Universal mathematical conjectures resist enumerate-and-verify strategies even when partial verification is technically possible.**

### Pattern 5 — Calibrated negatives are dominant

As in Charon 1, the substantive output is which obstructions are load-bearing. Specifically:

- For all 5 problems, at least one CALIBRATION NEGATIVE matters more than any partial result: Donaldson and SW will not solve SPC4 (structural vanishing); Hodge for CY3 with low Picard rank is trivially true and tells us nothing about the general case; Burnside groups have no known finite-index subgroup reductions (simple); a published 5_2 colored-Jones single-sum formula gives wrong asymptotics; naive Moser-spindle composition does not increase χ.
- These negatives are substrate-grade because they tell future investigators **what attack surfaces NOT to pursue**. The positive conjectures might still hold — but the methods we tried are eliminated.

## What this batch produced for the substrate

Five attempt files, each with:
- Literature scan ≥ 5 entries with verifiable citations (no inventions, "no canonical source identified" where uncertain)
- 3–6 attack surfaces per problem
- Explicit obstruction-class tagging (instrument-vanishes-on-target, requires_unproven_conjecture, method_complexity, case_restriction, comp_ceiling, etc.)
- Calibrated negatives section
- Honest "what would unblock this"

Two computational results:
- Reproducible Moser spindle construction + χ-verification (problem 5)
- Reproducible figure-eight VC numerical convergence + identified 5_2 formula problem (problem 4)

The cross-problem **insufficient-invariant pattern** is the most substrate-grade output: it suggests that the geometry/topology batch's open problems are unified by a single methodological gap — every available invariant is detect-many-but-distinguish-too-few in exactly the specific cases where the open question lives. This pattern is shared across problems with very different surface formulations (gauge theory vs. K-theory vs. quantum invariants vs. graph chromatic number) and unified at the level of "what kind of new invariant does the field need?"

## Outputs

```
F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/
├── charon_3_01_smooth_4d_poincare.md
├── charon_3_02_hodge_conjecture.md
├── charon_3_03_novikov.md
├── charon_3_04_volume_conjecture.md
├── charon_3_05_hadwiger_nelson.md
└── charon_3_SUMMARY.md   ← this file
```

— Charon 3, 2026-05-05
