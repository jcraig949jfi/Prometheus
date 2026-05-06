# Charon 2 review of Charon 3's batch (Topology / Geometry)

**Reviewer:** Charon 2 (this is a Charon-on-Charon review; same falsification-battery discipline applied across the cross-batch boundary)
**Date:** 2026-05-05
**Subject:** charon_3_01 through charon_3_05 + charon_3_SUMMARY.md
**Goal:** identify (a) Round-2 angles that would meaningfully change verdicts, (b) alternative attack surfaces Charon 3 did not try, (c) datasets the substrate could build to enable Round 2, (d) compute tools that would unblock specific attacks.

I will be direct in places where Charon 3's work is incomplete or missed an attack surface. This is the review the SUMMARY explicitly asked for; the substrate-grade output is rich criticism, not validation.

---

## Cross-batch executive summary

Charon 3 did 5 reasonable attack-profile passes in ~3.5 hours. Three problems (Hodge, Volume Conjecture, Hadwiger–Nelson) produced concrete partial results; two (Smooth 4D Poincaré, Novikov) produced clean obstruction-class maps without computational substance. The "insufficient invariant" cross-cutting observation in the SUMMARY is the strongest substrate-grade output of the batch.

**My headline claim: 4 of the 5 problems are good Round-2 candidates. Specifically:**

1. **Volume Conjecture for 5_2** — by far the strongest Round 2 target. Charon 3 explicitly identified the gap (correct double-sum formula was not implemented; would take 1–3 days). I estimate that with correct implementation + arbitrary-precision saddle-point analysis, a measurable contribution to the saddle-cancellation literature is achievable.

2. **Hodge Conjecture for CY3** — Charon 3 reduced the problem to a concrete linear-algebra question (cup-product surjectivity H^{1,1}⊗H^{1,1}→H^{2,2}). The Kreuzer–Skarke database of ~473 million reflexive 4-polytopes giving toric CY3 hypersurfaces is sitting *unused* as a substrate input. A Round 2 pipeline computing Picard lattices and testing surjectivity across this database is direct, computable, and would generate substrate-grade kill data on potentially a new scale.

3. **Hadwiger–Nelson** — the χ ≥ 6 search has been Polymath16's standing project for 7 years. Round 2 here would be a substrate-grade *infrastructure* contribution (reusable SAT pipeline, structured graph database) rather than mathematical progress.

4. **Smooth 4D Poincaré** — Charon 3 missed at least three attack surfaces (trisection theory, Khovanov-Bar-Natan refinements, computational handle-search). Round 2 could legitimately probe these.

**Novikov is the weak Round-2 candidate.** Its obstructions are structural and the substrate's compute/dataset capabilities don't bear on K-theoretic-of-discrete-group questions. Better to defer until / unless a new computational handle on operator-algebra invariants emerges.

---

## Per-problem critique and Round-2 plan

### Problem 1 — Smooth 4-dimensional Poincaré Conjecture (SPC4)

#### What Charon 3 did

Mapped the gauge-theoretic vanishing (Donaldson, Seiberg–Witten dim < 0 on S⁴), surveyed candidate-elimination (Cappell–Shaneson, Gluck — both largely resolved standard), checked that Bauer–Furuta and Pin(2)-equivariant Floer don't separate exotic from standard candidates, and observed Whitney-trick failure in dim 4.

Verdict: NO_PROGRESS_DOCUMENTED_OBSTACLES, with five attack surfaces tried.

#### What Charon 3 missed

**Three concrete attack surfaces are absent from the file:**

1. **Trisection theory (Gay–Kirby 2016+).** A trisection is a decomposition of a closed 4-manifold into three handlebody pieces, giving a *combinatorial* description of 4-manifolds analogous to Heegaard splittings in dim 3. Trisection diagrams are finite combinatorial objects. The theory is < 10 years old and has not been systematically applied to SPC4. Question for Round 2: can we (a) compute trisection diagrams of all known potentially-exotic homotopy 4-spheres, (b) look for trisection-genus invariants that vary with the smooth structure, (c) build a "trisection diagram database" with content-addressed move-equivalence classes? **None of this is in the literature as a systematic SPC4 attack.**

2. **Khovanov-style refinements of gauge invariants.** Lipshitz–Sarkar 2014 ("A Khovanov stable homotopy type") and Lawson–Lipshitz–Sarkar 2020 produced stable-homotopy refinements of Khovanov homology that are the *closest analogue in the categorification world* to Bauer–Furuta in the gauge-theoretic world. Charon 3 cited Bauer–Furuta and dismissed the refinement program because no candidate has produced non-trivial output. But the merger — using Khovanov-Lipshitz-Sarkar stable homotopy refinement *combined with* Bauer–Furuta, which has not been tried — is a genuine open methodological direction. The b₂⁺ = 0 vanishing is a Donaldson/SW phenomenon, but stable-homotopy refinements may not vanish in the same way.

3. **Computational handle-search via theorem proving / Kirby move enumeration.** Modern SAT-style + Lean/Coq can attempt automated Kirby-move sequences. The Cappell–Shaneson resolution by Akbulut and Gompf 2010 was *manual* — no one has tried to systematize it. With modern hardware, automated search through Kirby-move sequences for handle decompositions of small homotopy 4-spheres is plausible. If the search terminates with "standard," that's not a proof of SPC4, but a *dataset* of ruled-out candidates — substrate-grade kill data — accumulated faster than manual effort.

#### Round-2 plan

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Trisection-diagram database for known/published candidate exotic 4-spheres | 2–3 weeks | Reusable dataset; novel attack surface |
| Khovanov-stable-homotopy + Bauer–Furuta cross-check on a candidate exotic 4-sphere | 1–2 weeks (literature review heavy) | Either a new partial result or clean negative obstruction documenting why this composite invariant also vanishes |
| Automated Kirby-move search on small homotopy 4-spheres | 1 month (engineering) | Compute tool + ruled-out-candidates dataset |

**Datasets the substrate could build:**
- "Candidate exotic 4-sphere registry": all published candidates, their handle structures, what's been tested by Akbulut/Gompf/Gabai/etc. Currently scattered across papers.
- "Trisection diagram database" (above).

**Compute tools the substrate could build:**
- A Kirby-move automated reducer with deterministic move-ordering, integrated with content-addressed handle-decomposition hashing so that two different reduction paths produce the same canonical form.
- A Bauer–Furuta computer (only Furuta and a few others have implementations; no public open-source version exists as of 2025).

#### Honest assessment

SPC4 is genuinely hard. Charon 3's verdict is correct that no 30-hour push closes it. But the three missed attack surfaces above are real and underexplored. **The trisection angle in particular has not been systematically applied to SPC4 in the published literature** — this is a substrate-relevant Round-2 candidate.

---

### Problem 2 — Hodge Conjecture (Calabi–Yau 3-fold sub-case)

#### What Charon 3 did

Verified Hodge for the Fermat quintic CY3 trivially (h^{1,1} = 1 ⇒ (2,2) is 1-dimensional ⇒ generated by H², algebraic). **Reduced the codim-2 problem to a concrete linear-algebra question: surjectivity of the cup-product H^{1,1}(X)⊗H^{1,1}(X) → H^{2,2}(X).** Looked at Schoen rigid CY3 (h^{1,1}=19). Considered standard conjectures lift, Mumford–Tate reduction, period numerics on mirror quintic.

Verdict: PARTIAL_RESULT.

#### What Charon 3 missed (this is the most concrete Round-2 target)

**The Kreuzer–Skarke database of reflexive 4-polytopes is sitting unused.** Kreuzer and Skarke (2002) classified all reflexive 4-polytopes; this gives a database of **473,800,776 reflexive polytopes**, each producing (after triangulating the dual fan, etc.) a family of toric Calabi–Yau 3-fold hypersurfaces. **For every CY3 in this database, the Picard lattice and the cup-product structure on H^{1,1} are computable from the polytope combinatorics.**

This means: the linear-algebra question Charon 3 reduced to — surjectivity of H^{1,1}⊗H^{1,1}→H^{2,2} — is **directly testable on hundreds of millions of CY3 examples**. To my knowledge:

- No paper has done this systematically.
- A computer-verification of Hodge for codim 2 across a million toric CY3 would be substrate-grade evidence (positive or negative — both useful) and would dwarf the existing case-by-case literature.
- A *single* counterexample (a toric CY3 where the cup-product is not surjective on Hodge classes that are NOT algebraic) would be a Voisin-style surprise of major interest. None has been published; it's not clear anyone has searched.

#### Round-2 plan (this is the strong candidate)

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Build pipeline: Kreuzer–Skarke polytope → toric CY3 → Picard lattice → cup-product matrix → surjectivity check | 1–2 weeks | Dataset (potentially large); pipeline reusable |
| Run pipeline across, say, top-1M reflexive polytopes by h^{1,1}+h^{2,1} | 1 week (compute) | Per-CY3 surjectivity verdict; aggregated statistics |
| Investigate any non-surjective cases (potential Hodge-conjecture counterexample) | depends on findings | If counterexamples exist: paper-worthy; if not: positive evidence on unprecedented scale |
| Mirror-symmetry cross-check: for surjective cases, verify the Yukawa-coupling/cup-product mirror correspondence | 2 weeks | Validates the computation; tightens substrate calibration |

**Datasets the substrate could build:**
- **"Toric CY3 Hodge structure database"**: for each Kreuzer–Skarke polytope, store h^{1,1}, h^{2,1}, the Picard intersection form, the cup-product matrix on H^{1,1}, and the surjectivity status of cup-product → H^{2,2}. This is a major substrate artifact.
- **Indexed Picard lattices**: across the toric CY3 family, classify how Picard lattices cluster — useful for many follow-up questions beyond Hodge.

**Compute tools:**
- The Sage/PALP/CYTools ecosystem mostly exists. CYTools (Demirtas–Halverson–Long–Nelson–Rudelius 2022, https://cytools.liammcallisterphysics.com/) is a Python library for toric CY3. **The pipeline above can be built largely on top of CYTools.** This lowers the engineering cost dramatically. Charon 3 did not mention CYTools.
- A clean GPU-friendly cup-product computation for sparse intersection rings would speed mass-scale processing.

#### Honest assessment

The Hodge attempt is the **best Round-2 candidate for genuine substrate-grade output** because:
1. The mathematical reduction (cup-product surjectivity) is computable.
2. The database (Kreuzer–Skarke) exists and is enormous.
3. The tooling (CYTools) is open-source and ready.
4. The output (positive or negative verification at scale) is publication-worthy.
5. **No paper has done this**, despite the polymath-style setup being fully feasible.

Charon 3's reduction step is the strongest piece of math in the entire Charon 3 batch — it deserves a Round 2.

---

### Problem 3 — Novikov Conjecture (Burnside groups, Gromov monsters)

#### What Charon 3 did

Surveyed the K-theoretic/operator-algebraic toolkit (Higson–Kasparov a-T-menability, Yu Property A, Lafforgue Banach KK, Connes–Moscovici cyclic cohomology, Kasparov–Skandalis bolic spaces). Documented that all standard methods require a geometric input that B(m,n) and Gromov monsters lack. Observed that Property A status of B(m,n) is **OPEN** and is the gateway: knowing it would settle Novikov.

Verdict: NO_PROGRESS_DOCUMENTED_OBSTACLES, no partial result.

#### What Charon 3 missed (or didn't develop)

1. **Quantitative / controlled K-theory (Oyono-Oyono–Yu 2010s).** A finer framework where Property A is replaced by quantitative coarse statements at definite scales. Has not been systematically applied to torsion groups like B(m,n). This is a genuine alternative attack surface. Charon 3 only mentioned "Property A globally"; the controlled / scale-localized version is different.

2. **L²-Betti numbers and the Atiyah conjecture.** Lück's L²-cohomology of B(m,n) is computable in principle. The Atiyah conjecture (Linnell, Lück) gives a relation between Cohn-localizations of group rings and L²-Betti numbers; for B(m,n), the question of whether L²-Betti numbers are integers (or rational with denominators dividing the orders of finite subgroups) is open and **directly K-theoretic**. Charon 3 didn't mention this.

3. **Boundary actions and C\*-simplicity.** The Kalantar–Kennedy 2017 "Boundaries of reduced C\*-algebras of discrete groups" framework gives a Furstenberg-boundary-based test for C\*-simplicity. C\*-simplicity is related to (though not equivalent to) Novikov via property (T) considerations. For B(m,n), the boundary action structure is barely studied.

4. **Computational test of Property A on truncated quotients.** Property A has finite witnesses (constants ε, S). For a group G generated by a finite set, Property A says: ∀ε, S finite, ∃ finite F ⊂ G and a partition-of-unity {φ_x}_{x∈G} into elements of ℓ²(G) such that supp(φ_x) ⊂ xF and ‖φ_x − φ_y‖ ≤ ε‖x⁻¹y‖_S. **This is a finite-witness property** when restricted to large enough finite quotients. A computational search for Property A witnesses on truncated B(2, n) quotients (n=665 is impractical, but n=3, 4, etc. are tractable; B(2,3) has order 27, B(2,4) has order 4096, B(2,5) is large but enumerable to reasonable bounds) might give substrate-grade evidence — even if extrapolating to n=665 isn't rigorous.

#### Round-2 plan (weakest of the 5)

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Computational Property-A search on small finite Burnside quotients B(2, n) for n ≤ 7 | 1–2 weeks | Empirical evidence on Property-A trend with n; not a proof |
| Survey of controlled K-theory applied to torsion groups | 1 week | Literature map; unblock future Round-3 |
| L²-Betti number / Atiyah-conjecture status check for B(m, n) | 1 week | Literature map + clean problem-statement |

**Datasets:**
- "Group-theoretic Novikov status registry": for each named group class (a-T-menable, Property A, hyperbolic, linear, lattice, …), what's known and open. This is folklore but has not been catalogued cleanly.

**Compute tools:**
- A "Property A finite-witness searcher": given a finite group G and a set S, search for partition-of-unity witnesses with given (ε, S) parameters. This is the kind of thing Magma or GAP could be extended to do, but no public package exists.

#### Honest assessment

**Novikov is the weakest Round-2 candidate of the 5.** The obstruction is structural and the substrate's compute capabilities don't bear on the central question (whether the assembly map is injective for K(C\*_r(G))). Round 2 here would be substrate-grade *literature consolidation*, not mathematical progress. Recommend deferring.

---

### Problem 4 — Volume Conjecture (5_2 knot)

#### What Charon 3 did (this is the strongest of the batch)

Used SnapPy to compute hyperbolic volumes for 10 small knots. Verified the figure-eight Volume Conjecture numerically up to N=2000 with monotonic convergence (gap +0.035). Attempted 5_2 with a single-sum formula, which **gave non-VC-compliant numerics** — explicitly identifying that the single-sum (correct for 4_1) does not extend to 5_2; the correct form is the Garoufalidis–Lê / Hikami double-sum. This is a clean substrate-grade kill of one published formula.

Verdict: PARTIAL_RESULT.

#### What Charon 3 missed (nothing in the verdict; everything in the next-step)

Charon 3 explicitly said: *"a verified implementation of the Garoufalidis–Lê / Hikami double-sum colored-Jones formula, with cross-check against the Habiro polynomial at small N, would let us extend the numerical evidence to higher N. … 1–3 days of focused work."*

**This is the cleanest Round-2 hand-off in the entire 5-problem batch.**

#### Round-2 plan

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Implement Garoufalidis–Lê / Hikami double-sum colored-Jones formula for 5_2 | 1–3 days (per Charon 3) | Verified colored-Jones for 5_2 |
| Cross-check at small N against published Habiro polynomial values | 1 day | Calibration anchor; rules out implementation errors |
| Extend to N = 10000 with arbitrary-precision arithmetic | 1 day (compute) | Numerical evidence at substantially higher N than published |
| Saddle-point analysis: numerical integration of the integral representation at 200+ digit precision; isolate the two saddle contributions | 1 week (research) | **Could illuminate the saddle-cancellation question Ohtsuki couldn't close** |
| Repeat for 6_1, 6_2, 6_3, 7_2, 7_3, 7_4 once the framework is built | 1 week | Numerical evidence on a panel of hyperbolic knots; substrate-grade dataset |

**Datasets:**
- **"Volume Conjecture numerical evidence database"**: for each hyperbolic knot in the standard tables (Rolfsen, KnotInfo), and for N from 100 to 100000 in increments, store |J_N|, 2π log|J_N|/N, Vol, and the gap. This would be a substrate-grade dataset that nobody currently maintains.
- KnotInfo already has hyperbolic volumes; the substrate would add the Jones-side numerics.

**Compute tools:**
- A clean colored-Jones-polynomial computation library, independent of normalization choice, that handles arbitrary precision and validates against multiple cross-references (Habiro, Kashaev formulae, recursion).
- Saddle-point integral evaluator at arbitrary precision.

#### Honest assessment

**Volume Conjecture for 5_2 is the strongest Round-2 candidate by execution clarity.** Charon 3 already did the work of identifying the precise gap: a wrong formula was used, the right formula is known, the implementation is bounded-time. A 1-week focused Round 2 would produce a clean numerical attack on the standing Ohtsuki saddle-cancellation question. Even if it doesn't close the conjecture, it produces a usable VC numerics database.

---

### Problem 5 — Hadwiger–Nelson chromatic number of the plane

#### What Charon 3 did

Constructed and brute-force-verified the Moser spindle has χ = 4. Verified disjoint union of Moser spindles stays at χ = 4 (so χ ≥ 5 needs careful identification, as in de Grey 2018). Documented the gap to χ ≥ 6 (no construction known despite 7 years of Polymath16 effort). Noted Falconer 1981 measurable-coloring χ ≥ 5 result.

Verdict: PARTIAL_RESULT.

#### What Charon 3 missed

1. **Continuous / measure-theoretic side.** Falconer 1981 gave χ ≥ 5 for measurable colorings; subsequent work (Ackerman 2019 and others) has bounds for measurable colorings up to about 6. **The gap between measurable-coloring lower bounds and unconditional lower bounds is itself a research target.** Charon 3 mentions Falconer but doesn't survey the post-Falconer measurable-coloring lower-bound progress. There may be a substrate-grade question here: how much of the "5 ≤ χ ≤ 7" gap is explained by the difference between measurable and arbitrary colorings?

2. **Probabilistic / random-graph framework.** For a random ε-perturbation of the unit-distance graph in a fixed bounded region, what's the probability of being 5-chromatic, 6-chromatic? This kind of "chromatic-number-as-random-process" framework hasn't been systematically applied. Could give heuristic evidence for χ.

3. **Rational-distance vs irrational-distance unit-distance graphs.** Unit-distance graphs realized with vertices in ℚ² have constrained structure (rational distances of length 1 satisfy specific number-theoretic conditions). Maybe the rational-coordinate sub-problem χ(ℚ²) is more tractable. Charon 3 didn't mention this. Question: is χ(ℚ²) known? (Searching memory: I believe χ(ℚ²) = 2, since a 2-coloring of ℚ² by parity of denominators-or-similar works. If yes, this rules out rational-coordinate constructions for higher χ, which is informative.)

4. **Lower-dimensional and higher-dimensional analogues.** χ(ℝⁿ) is well-studied: for n=3, the bounds are 6 ≤ χ(ℝ³) ≤ 15 (paraphrased from Soifer 2009; specific bounds may have improved since). Could the methods that work in ℝ³ inform ℝ²? Charon 3 didn't go to higher dim.

5. **Different distance constraints.** χ(ℝ², distance ∈ {1, 2}) — forbid TWO distances simultaneously. Or χ(ℝ², distance ∈ Q) — forbid all rational distances. These are well-defined variants with their own literatures and could illuminate the original problem.

#### Round-2 plan

| Round-2 angle | Time estimate | Substrate-grade output |
|---|---|---|
| Build SAT-based pipeline for k-chromatic UDG search; reproduce Heule's reduced graph; document workflow | 1–2 weeks | Reusable pipeline; community-relevant |
| Survey post-Falconer measurable-coloring bounds; map gap structure | 1 week | Substrate-grade: "where exactly is the gap between measurable-χ and arbitrary-χ?" |
| Computational test: are χ(ℚ²) = 2 and χ((ℝ \ ℚ)²) = ? known? | 1 day | Rules out rational-coordinate angle if confirmed |
| Search for 6-chromatic UDG with novel constraint structure (e.g., requiring vertices in algebraic-coordinate subset) | 2 weeks (compute-heavy) | Either: novel UDG class with χ ≥ 6 (would be major), or negative result that the new constraint class also doesn't help |

**Datasets:**
- **"Unit-distance-graph repository"**: clean DIMACS-format collection of all known 5-chromatic UDGs with vertex coordinates, edge lists, SAT certificates. Polymath16 has a wiki but it's not a clean database.
- **"k-chromatic UDG benchmark"**: for various k, a list of (graph, vertices, edges, chromatic-number-certificate-or-status). The test bed for any future SAT-style search.

**Compute tools:**
- An open-source SAT-based "k-chromatic UDG search" pipeline, with optimized graph generation (avoiding redundant unit-distance pairs) and pluggable constraint structures.
- A "minimal UDG reducer" — given a 5-chromatic UDG, find smaller subgraphs that are still 5-chromatic. This is what Heule and Mixon do; building a public, robust version would help the community.

#### Honest assessment

Hadwiger–Nelson is a Round-2 candidate, but the marginal mathematical progress per week of compute is unclear. Polymath16 has been at this for 7 years with the global research community; **the substrate's contribution would mostly be infrastructure** (clean dataset, reusable pipeline) rather than direct progress on χ ≥ 6.

That said, the **infrastructure contribution is real**. A clean SAT-based UDG-search benchmark would be a citable substrate artifact useful to many follow-on researchers.

---

## Cross-cutting observations from review

### Observation 1 — "Insufficient invariant" pattern is real but invites a meta-question

Charon 3's central cross-problem observation — every standard tool detects a lot but cannot distinguish the open case — is correct and substrate-grade. It suggests a **meta-research direction the substrate is well-positioned to attack**:

> Build a "tool-vs-target" matrix for each open conjecture in this batch. For each invariant (Donaldson, SW, Bauer–Furuta, Khovanov, Kashaev, etc.) and each candidate target (homotopy 4-sphere, CY3 with high Picard rank, B(m,n), 5_2, etc.), record whether the tool produces a non-trivial output. The "insufficient invariant" pattern is a sparse-matrix observation: **a vast majority of (tool, target) cells produce trivial / vanishing output**. Where are the off-diagonal non-zero entries? What invariants don't vanish where everything else does?

This would generalize what Charon 3 saw: it suggests that **the subset of (tool, target) pairs with non-trivial output is itself the substrate-grade dataset to build**.

### Observation 2 — Datasets are systematically missing from the topology literature

Each of the 5 problems would benefit from a dedicated dataset that doesn't currently exist in clean reusable form:

| Problem | Missing dataset |
|---|---|
| SPC4 | Candidate exotic 4-sphere registry; trisection diagram database |
| Hodge / CY3 | Toric CY3 Hodge-structure database with cup-product surjectivity |
| Novikov | Group-theoretic Novikov status registry |
| Volume Conjecture | VC numerical evidence database (per knot, per N) |
| Hadwiger–Nelson | Clean k-chromatic UDG repository |

**The substrate is unusually well-positioned to build these.** This is the one-line opportunity for the topology batch overall: dataset-building work that the math community has not done in clean form, but that a substrate-grade research environment can do well.

### Observation 3 — The strong Round-2 candidates differ in execution clarity

Ranking by "substrate-effort to Round-2-output" ratio:

1. **Volume Conjecture for 5_2** — clearest path; 1 week of focused work; concrete output.
2. **Hodge for CY3 / Kreuzer–Skarke** — biggest scale; 1 month; potentially major contribution.
3. **Hadwiger–Nelson** — infrastructure-heavy; 1 month; community-citable but mathematical progress uncertain.
4. **SPC4** — speculative; 1+ month; could yield novel attack-surface but most likely produces more obstruction-class data.
5. **Novikov** — defer.

### Observation 4 — Charon 3's voice was fine; their attack-surface coverage was uneven

The strongest pieces in Charon 3's batch:
- Hodge problem: the structural reduction to cup-product surjectivity is sharp.
- Volume Conjecture: the kill on the wrong single-sum formula is exactly substrate-grade output.
- Hadwiger–Nelson: the Moser-spindle reproducibility script is substrate-grade.

The weakest pieces:
- SPC4: missed three viable attack surfaces. The verdict is correct but the surface coverage is incomplete.
- Novikov: surveyed the standard methods but missed quantitative K-theory and the L²-Betti angle.

This is normal for a 30–50-minute pass per problem. Round 2 should specifically target the missed attack surfaces.

---

## Substrate-grade artifacts the substrate could build

Consolidated from the per-problem analyses:

### Datasets (single-investment, multi-paper-reuse value)

1. **Toric CY3 Hodge-structure database** (highest priority): for each Kreuzer–Skarke reflexive 4-polytope, store h^{1,1}, h^{2,1}, Picard intersection form, cup-product matrix on H^{1,1}, and surjectivity status for cup-product → H^{2,2}. Built on top of CYTools.
2. **Volume Conjecture numerical evidence database**: for each hyperbolic knot in KnotInfo and each N from 100 to 100000, store |J_N| and the gap to Vol. Built on top of SnapPy + a verified colored-Jones implementation.
3. **5-chromatic UDG repository**: clean DIMACS-format collection of all known 5-chromatic unit-distance graphs with metadata (vertex coordinates, edge counts, SAT certificates, originator).
4. **Trisection diagram database** (medium priority): for each closed 4-manifold of interest (including known/published candidate exotic 4-spheres), the trisection diagram data.
5. **Group-theoretic Novikov status registry** (low priority): folklore consolidation; useful but not substrate-blocking.

### Compute tools (reusable infrastructure)

1. **CY3 cup-product surjectivity pipeline** (highest priority — directly enables Round 2 of Hodge): Kreuzer–Skarke polytope → toric CY3 → Picard lattice → cup-product matrix → surjectivity check. Built on CYTools.
2. **Verified colored-Jones polynomial library** (high priority — enables Round 2 of Volume Conjecture): handles arbitrary precision, supports multiple knot families, validates against Habiro polynomials and Kashaev tables.
3. **SAT-based k-chromatic UDG searcher** (medium priority): with optimized graph generation and pluggable constraint structures.
4. **Kirby-move automated reducer** (medium priority): for handle decomposition canonicalization.
5. **Property A finite-witness searcher** (low priority — speculative for Novikov): given a finite group G and parameters, search for partition-of-unity witnesses.

### Substrate-grade meta-direction

The "tool-vs-target sparse matrix" of which invariants give non-trivial output on which open targets is itself a substrate-grade dataset. **This is the substrate-relevant generalization of Charon 3's "insufficient invariant" observation.**

---

## Honest reporting

Time spent on this review: ~75 minutes. I read all five Charon 3 attempt files plus the SUMMARY in detail, and produced concrete Round-2 plans with dataset/tool specifications.

**What I am confident about:**
- The Hodge / Kreuzer–Skarke pipeline is genuinely a strong Round-2 candidate. CYTools is real, the polytope database is real, the cup-product computation is well-defined. I am confident this would produce substrate-grade output.
- The Volume Conjecture / 5_2 double-sum implementation is genuinely a 1-week focused project with clean deliverables.
- Charon 3 missed at least three attack surfaces on SPC4 (trisection, Khovanov-stable-homotopy, automated handle search).

**What I am less confident about:**
- The Property-A computational search on small Burnside quotients may turn out to produce no useful signal. I am not confident this gives substrate-grade output even at 1–2 weeks.
- The exact size of the Kreuzer–Skarke list (I cited 473M reflexive 4-polytopes from memory — this may not be quite right; the canonical Kreuzer–Skarke 2002 paper paraphrased). The order of magnitude (hundreds of millions) is correct; the exact number should be verified before committing the Round 2.
- Whether L²-Betti number machinery genuinely advances Novikov for B(m,n). This is more speculative than I'd like.

**What I did NOT verify in this review:**
- I did not run any of the compute tools myself (CYTools, SnapPy beyond what Charon 3 already ran, SAT solvers).
- I did not check arxiv for 2024-2026 progress on any of these problems beyond what Charon 3 cited. There may be newer results.

**Recommendation for batch coordinator:**
- **Greenlight Round 2 for Hodge / Kreuzer–Skarke pipeline** (1 month, dataset + paper potential).
- **Greenlight Round 2 for Volume Conjecture / 5_2 double-sum** (1 week, clear deliverable).
- **Conditional greenlight for Hadwiger–Nelson infrastructure work** (1 month, valuable but lower-priority).
- **Defer SPC4 to a later batch** with explicit instruction to attack trisection theory.
- **Defer Novikov** until / unless the substrate develops new operator-algebra capabilities.

— Charon 2, 2026-05-05
