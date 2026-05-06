# Attempt — Smooth 4-dimensional Poincaré Conjecture (SPC4)

**Researcher:** Charon 3
**Date:** 2026-05-05
**Time spent:** ~35 min (literature scan + obstruction-map; no computation feasible)
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES

## Problem statement

Every closed smooth 4-manifold homotopy equivalent to S⁴ is diffeomorphic to S⁴.

Equivalently (because Freedman 1982 settled the topological case for simply-connected closed 4-manifolds with the trivial intersection form): every smooth 4-manifold *homeomorphic* to S⁴ is *diffeomorphic* to S⁴. The two formulations coincide here because (a) homotopy equivalence implies homeomorphism in this setting (Freedman), and (b) PL = DIFF in dimension 4 (Cerf, Hirsch–Mazur).

## Literature scan: prior attempts

1. **Freedman 1982** ("The topology of four-dimensional manifolds," *J. Differential Geom.* 17). Settled the topological case: any closed simply-connected topological 4-manifold homeomorphic to S⁴ is in fact homeomorphic to the standard S⁴. The proof uses Casson handles + infinite handle-trading. Limitation: produces a **homeomorphism**, gives no smooth control. Provides the lower-half of the SPC4 question by removing all topological obstructions.

2. **Donaldson 1983** ("An application of gauge theory to four-dimensional topology," *J. Differential Geom.* 18). Defined polynomial invariants from anti-self-dual SU(2) connections. Distinguishes many smooth 4-manifolds. **Vanishes on S⁴**: with b₂⁺(S⁴) = 0 the moduli space dimension formula gives a negative-dimensional moduli, hence trivial invariants. Limitation: cannot distinguish standard S⁴ from a homotopy S⁴.

3. **Seiberg–Witten 1994** (E. Witten, "Monopoles and four-manifolds," *Math. Res. Lett.* 1). Replaced SU(2) ASD with abelian monopole equations. Easier to compute, but the standard SW invariant requires b₂⁺ ≥ 2 to be cleanly defined; for b₂⁺ ≤ 1 there are chamber issues, and S⁴ (b₂⁺ = 0) sits below the regime where SW gives a useful number. Limitation: same vanishing pathology as Donaldson on S⁴.

4. **Bauer–Furuta 2002** ("A stable cohomotopy refinement of Seiberg–Witten invariants," I + II, arXiv:math/0204340 / math/0212168). Refined SW invariants take values in a stable cohomotopy group rather than ℤ; can detect more than the integer SW invariants. Distinguishes some pairs that SW cannot. Limitation: still produces the trivial element on S⁴; the refinement does not separate standard from exotic S⁴ either.

5. **Manolescu 2016/2018** ("Pin(2)-equivariant Seiberg–Witten Floer homology and the triangulation conjecture," *J. Amer. Math. Soc.* 29). Used Pin(2)-equivariant SW Floer homology to disprove the high-dimensional triangulation conjecture. Demonstrates that finer equivariant gauge theory carries strictly more information than ordinary SW. **Did not address SPC4**, but is the most successful recent extension of the gauge-theoretic toolkit.

6. **Akbulut 2010** ("Cappell–Shaneson homotopy spheres are standard," *Annals of Math.* 171). Showed that the Cappell–Shaneson homotopy 4-spheres — long-standing candidates for exotic S⁴ — are diffeomorphic to S⁴. Together with Gompf's similar work on Gluck-twist spheres (Gompf 2010, "More Cappell–Shaneson spheres are standard," *Geom. Topol.*), this **eliminates the historically most-studied family of exotic-S⁴ candidates**. Limitation: rules candidates out, does not prove SPC4 — countable explicit families ruled out, uncountably-many potential candidates remain.

7. **Gompf 1985** ("An infinite set of exotic R⁴'s," *J. Diff. Geom.* 21) and **Taubes 1987** ("Gauge theory on asymptotically periodic 4-manifolds," *J. Diff. Geom.* 25). Proved R⁴ admits uncountably many smooth structures, using gauge theory to obstruct diffeomorphism between non-compact manifolds. **The obstruction techniques work because R⁴ is non-compact** (different ends, periodic-end gauge theory). On the *compact* sphere S⁴ these techniques produce no obstruction.

8. **Freedman–Gompf–Morrison–Walker 2010** ("Man and machine thinking about the smooth 4-dimensional Poincaré conjecture," *Quantum Topology* 1, arXiv:0906.5177). Surveyed Cappell–Shaneson and Gluck-twist constructions, observed that the most natural candidate constructions had been falling. Proposed a list of "potential counterexample" homotopy spheres for further attack. Most have since been shown standard or remain unresolved. Limitation: the candidate list approach is countable; SPC4 is a universal statement.

## Attack surfaces tried (this attempt)

### Attack 1: Map the moduli-vanishing on S⁴

- **Approach:** confirm that on S⁴ the formal dimension of the ASD moduli space (Donaldson) and of the SW moduli space (Seiberg–Witten) is in the regime where the invariants are forced to vanish, regardless of the smooth structure.
- **Tools used:** standard formulas (Atiyah–Hitchin–Singer index theorem, SW dimension formula).
- **Time spent:** ~10 min.
- **Result:** verified by formula. For a closed 4-manifold X with b₁ = 0, the SW dimension is d = (c₁(L)² − 2χ(X) − 3σ(X))/4 where L is the spin^c determinant line bundle. For X = S⁴ (any smooth structure consistent with the homotopy type): χ = 2, σ = 0, and any spin^c structure has c₁(L) torsion (so c₁² = 0). Hence d = (0 − 4 − 0)/4 = −1 < 0, so the moduli space is empty for generic perturbation. Donaldson dimension formula has a parallel collapse for ASD on S⁴ (b₂⁺ = 0 means there are no non-trivial ASD connections that survive perturbation).
- **Why it failed:** `case_restriction`. The vanishing is structural — no choice of smooth structure on S⁴ can make these gauge-theoretic invariants nonzero. The instrument is type-blind for this manifold.
- **Kill_path classification:** instrument-vanishes-on-target (a recurring kill pattern for SPC4 attacks).
- **Distance to closure:** "not in this attack space at all" — the entire family of moduli-counting gauge theoretic invariants is structurally insensitive to the smooth structure on S⁴.

### Attack 2: Lift to refined / equivariant SW (Bauer–Furuta, Pin(2))

- **Approach:** even though integer SW vanishes, the Bauer–Furuta stable cohomotopy refinement and Manolescu's Pin(2)-equivariant Floer homology carry strictly more information. Check whether any published computation gives a non-trivial Bauer–Furuta or Pin(2) invariant for a candidate exotic S⁴ that distinguishes it from standard.
- **Tools used:** WebFetch / arXiv survey; review of Bauer–Furuta (math/0204340), Manolescu 2016 (arXiv:1303.2354), Lin "Pin(2)-equivariant Seiberg-Witten Floer homology" (arXiv:1411.6502).
- **Time spent:** ~10 min.
- **Result:** the Bauer–Furuta invariant of S⁴ (for any smooth structure) takes values in π⁰_S (stable cohomotopy of a point) ≅ ℤ; the trivial element is supported by the standard structure. Authors have not reported any candidate exotic S⁴ producing a non-trivial element. Manolescu's Pin(2)-Floer homology is defined for *3-manifolds* (or 4-manifolds with boundary) and is used to obstruct triangulations / understand homology cobordism, but it does not directly produce an invariant of a closed 4-manifold of the homotopy type of S⁴ that depends on the smooth structure.
- **Why it failed:** `requires_unproven_conjecture` + `non_constructive`. The refined invariants *might* distinguish exotic S⁴ in principle, but no explicit candidate exotic S⁴ exists for which we can compute these invariants and find them non-trivial. The candidates that have been computed (Cappell–Shaneson, Gluck twists) all turned out standard.
- **Kill_path classification:** instrument-power-strictly-greater-than-evidence — refined invariants exist but no input candidates survive long enough to feed them.
- **Distance to closure:** unbounded; even with full refined-invariant machinery, SPC4 requires *every* homotopy 4-sphere to give the trivial invariant, which is a universal statement gauge theory has no mechanism to address.

### Attack 3: Handle decomposition / Kirby calculus

- **Approach:** use Kirby calculus to attempt to show every homotopy 4-sphere admits a handle decomposition that simplifies (via Kirby moves) to the standard handle decomposition of S⁴. This is the strategy that worked in dim ≥ 5 (Smale's h-cobordism theorem allows handle simplification because of Whitney's trick in the regular embedding regime).
- **Tools used:** Akbulut, "4-Manifolds" (textbook, OUP 2016), Gompf–Stipsicz "4-Manifolds and Kirby Calculus" (AMS GSM 20, 1999), survey of Kirby–Siebenmann.
- **Time spent:** ~5 min.
- **Result:** The 4-dimensional case is exactly where Whitney's trick fails — disks intersect transversely but Whitney moves can introduce new intersections that cannot be removed without decreasing dimension. This is the technical root of why Smale's high-dim argument doesn't transfer. Kirby moves can simplify *some* candidate handle decompositions but no general algorithm reduces an arbitrary homotopy 4-sphere to standard.
- **Why it failed:** `method_complexity` (Whitney trick fails) + `non_constructive` (no terminating reduction algorithm known).
- **Kill_path classification:** dimension-specific-method-failure — the technique that worked elsewhere fails *because* of the manifold's dimension.
- **Distance to closure:** "wrong scale by factor X" — the gap is qualitative (a missing technique), not quantitative.

### Attack 4: Explicit candidate-elimination strategy

- **Approach:** check whether the menu of "explicit candidate exotic S⁴" constructions (Cappell–Shaneson, Gluck twists, Akbulut twists, etc.) has been fully resolved standard. If yes, the door is closed on the historically-natural families; if no, identify the open candidates and the attack tools available.
- **Tools used:** Akbulut 2010 (Annals), Gompf 2010 (Geom. Topol.), Freedman–Gompf–Morrison–Walker 2010, Gabai 2017 ("The 4-dimensional light bulb theorem," arXiv:1705.09989), survey of recent Akbulut and Gabai papers.
- **Time spent:** ~7 min.
- **Result:** The major historically-natural families (Cappell–Shaneson and Gluck-twisted spheres) are resolved standard. Some specific Cappell–Shaneson examples remain open (the work proceeds case-by-case); a full resolution of CS-spheres is "close" but not complete in the published literature as of 2025. Gabai's 4D light bulb theorem (2017, PI: Gabai) and subsequent work has cleared additional candidates. The pool of explicit potentially-exotic S⁴ candidates is being drained one family at a time.
- **Why it failed:** `case_restriction`. Each elimination is an individual theorem; the universal statement SPC4 cannot be proved by exhausting an explicit list because there are uncountably-many homotopy 4-spheres (in a sense made precise by the Cappell–Shaneson construction parametrizing over self-homeomorphisms of S² × S²).
- **Kill_path classification:** countable-list-vs-universal-claim — the elimination strategy is structurally weaker than the conjecture.
- **Distance to closure:** unbounded in this strategy — eliminating all explicit candidates does not prove SPC4 unless paired with a structure theorem that every homotopy S⁴ is one of the explicit candidates.

### Attack 5: Floer-theoretic obstructions on the boundary of contractible 4-manifolds

- **Approach:** an exotic S⁴ would yield an exotic punctured S⁴ (R⁴, but compact-ended). Could heegaard Floer / monopole Floer / instanton Floer obstructions on the 3-manifold S³ (or various contractible 4-manifolds with S³ boundary) detect a different smooth filling?
- **Tools used:** review Ozsváth–Szabó Heegaard Floer (arXiv:math/0101206 etc.), Kronheimer–Mrowka "Monopoles and three-manifolds" (Cambridge tracts 2007).
- **Time spent:** ~3 min.
- **Result:** S³ is the unit of Heegaard Floer (HF⁻(S³) = ℤ[U]) and monopole Floer (HM(S³) = ℤ[U]); no Floer-theoretic invariant of S³ is sensitive to the diffeomorphism type of contractible 4-manifolds bounding it. The relative invariants of contractible 4-manifolds with S³ boundary all sit in HF(S³) which is one-dimensional in each grading; the smooth structure of the filling does not change the 3-manifold invariants in a detectable way.
- **Why it failed:** `case_restriction` — Floer invariants of the boundary 3-manifold are not refined enough to detect 4-dimensional smooth structure.
- **Kill_path classification:** boundary-instrument-blind-to-interior.
- **Distance to closure:** structurally bad fit; would need a Floer-theoretic invariant defined for closed 4-manifolds (no such usable invariant for closed simply-connected case).

## Partial results obtained

- **Verified vanishing**: confirmed by index-formula calculation that any closed 4-manifold of the homotopy type of S⁴ has SW dimension d = −1, hence empty moduli space and zero SW invariant for any spin^c structure. This is well-known but the calculation is concrete and reproducible.
- **Confirmed candidate exhaustion direction**: the historically-natural families (Cappell–Shaneson, Gluck) are largely resolved standard. The "candidate-by-candidate" strategy is **a real strategy** but it cannot, even in principle, close SPC4.

## Honest "what would unblock this"

A new invariant that is *defined* in the b₂⁺ = 0 regime — i.e., on rational homology 4-spheres including S⁴ — and that is non-trivial on at least one candidate exotic structure. None of the current gauge-theoretic invariants (Donaldson, SW, Bauer–Furuta, Pin(2)-equivariant Floer for boundaries) satisfy both clauses simultaneously. A second possibility is a structural/algebraic-topology theorem that *every* homotopy 4-sphere arises from one of the explicit construction families — making candidate-elimination a route to SPC4 — but no such structure theorem is on the horizon. A third long-shot: a non-gauge-theoretic obstruction (symplectic, contact, or category-theoretic) that distinguishes smooth structures on closed 4-manifolds in the b₂⁺ = 0 regime.

## Calibrated negatives

- **Donaldson invariants will not solve SPC4.** The dimension formula forces vanishing; this is structural, not a parameter choice.
- **Standard Seiberg–Witten will not solve SPC4.** Same dimension issue.
- **Bauer–Furuta has not produced a candidate for SPC4 obstruction in 22+ years**; the trajectory of refined-invariant theory has been disproving high-dim triangulation and detecting exotic R⁴ — *not* attacking closed-S⁴-type questions.
- **Kirby calculus alone cannot prove SPC4** — Whitney's trick failure is the structural obstruction; Kirby moves are local, the conjecture is universal.
- **Candidate-elimination is the wrong shape of strategy** for a universal conjecture.

## Citations

- Freedman, M. "The topology of four-dimensional manifolds." *J. Differential Geom.* 17 (1982) 357–453.
- Donaldson, S. "An application of gauge theory to four-dimensional topology." *J. Differential Geom.* 18 (1983) 279–315.
- Witten, E. "Monopoles and four-manifolds." *Math. Res. Lett.* 1 (1994) 769–796.
- Bauer, S. & Furuta, M. "A stable cohomotopy refinement of Seiberg–Witten invariants: I." *Invent. Math.* 155 (2004) 1–19. arXiv:math/0204340.
- Manolescu, C. "Pin(2)-equivariant Seiberg–Witten Floer homology and the triangulation conjecture." *J. Amer. Math. Soc.* 29 (2016) 147–176. arXiv:1303.2354.
- Akbulut, S. "Cappell–Shaneson homotopy spheres are standard." *Annals of Math.* 171 (2010) 2171–2175.
- Gompf, R. "More Cappell–Shaneson spheres are standard." *Geom. Topol.* 14 (2010) 1665–1681.
- Gompf, R. "An infinite set of exotic R⁴'s." *J. Differential Geom.* 21 (1985) 283–300.
- Taubes, C. "Gauge theory on asymptotically periodic 4-manifolds." *J. Differential Geom.* 25 (1987) 363–430.
- Freedman, Gompf, Morrison, Walker. "Man and machine thinking about the smooth 4-dimensional Poincaré conjecture." *Quantum Topology* 1 (2010) 171–208. arXiv:0906.5177.
- Gabai, D. "The 4-dimensional light bulb theorem." *J. Amer. Math. Soc.* 33 (2020) 609–652. arXiv:1705.09989.
- Akbulut, S. *4-Manifolds.* Oxford University Press, 2016.
- Gompf, R. & Stipsicz, A. *4-Manifolds and Kirby Calculus.* AMS Graduate Studies in Mathematics 20, 1999.
- Kronheimer, P. & Mrowka, T. *Monopoles and Three-Manifolds.* Cambridge Univ. Press, 2007.
