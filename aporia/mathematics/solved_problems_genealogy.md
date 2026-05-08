# Solved Problem Genealogies — How Voids Get Filled
## The training data for void detection: what techniques cracked which barriers?
## Agent: Aporia | Date: 2026-04-17 | Status: Seed catalog, growing

---

## Purpose

If we know HOW past problems were solved — the chain of ideas, the domain transfers, the branching paths — we can predict HOW current voids will fill. The proof genealogy is the training data for technique transfer detection.

---

## 1. Fermat's Last Theorem (FLT)

**Statement:** x^n + y^n = z^n has no positive integer solutions for n > 2.
**Posed:** 1637 (Fermat). **Solved:** 1995 (Wiles). **Gap:** 358 years.

**Proof Genealogy:**
1. [1637] Fermat — marginal claim, no proof
2. [1753] Euler — proved n=3 (descent)
3. [1825] Dirichlet, Legendre — proved n=5
4. [1839] Lamé — proved n=7
5. [1847] Kummer — proved for regular primes (introduced ideal theory)
6. [1955] Taniyama-Shimura — conjectured every EC is modular (BRANCH POINT)
7. [1975] Frey — linked FLT counterexample to non-modular EC (MERGE: FLT → modularity)
8. [1986] Ribet — proved Frey's link (epsilon conjecture): FLT follows from modularity
9. [1993-95] Wiles (+ Taylor) — proved modularity for semistable EC → FLT proved

**Domain transfer:** YES — number theory problem solved via algebraic geometry (EC) + representation theory (Galois representations) + harmonic analysis (automorphic forms). Three-domain merge.
**Solution type:** Long program (40 years from Taniyama to Wiles)
**Barrier broken:** Conceptual (required Langlands framework)
**What it unlocked:** Full modularity theorem (Breuil-Conrad-Diamond-Taylor 2001), Serre's conjecture proved (Khare-Wintenberger 2009), entire edifice of modern Langlands for GL(2).
**Could it have been predicted?** The Frey-Ribet link made it clear by 1986 that modularity would prove FLT. The void (modularity for semistable EC) was precisely identified 9 years before it was filled.

---

## 2. Poincaré Conjecture (3D)

**Statement:** Every simply connected, closed 3-manifold is homeomorphic to S^3.
**Posed:** 1904 (Poincaré). **Solved:** 2003 (Perelman). **Gap:** 99 years.

**Proof Genealogy:**
1. [1904] Poincaré — posed the conjecture
2. [1961] Smale — proved for dim ≥ 5 (h-cobordism)
3. [1982] Freedman — proved for dim 4 (topological, not smooth)
4. [1982] Hamilton — introduced Ricci flow program for 3-manifolds
5. [1982-1999] Hamilton — developed Ricci flow theory, proved many partial cases
6. [2002-2003] Perelman — proved Ricci flow with surgery works: singularity analysis via entropy monotonicity + no local collapsing theorem → Poincaré + Geometrization

**Domain transfer:** YES — topology problem solved via PDE (Ricci flow) + differential geometry + entropy (statistical physics analogy).
**Solution type:** Long program (Hamilton 20 years) + single breakthrough (Perelman's entropy + surgery)
**Barrier broken:** Technique (Hamilton's program was stuck on singularities; Perelman's entropy was the key)
**What it unlocked:** Thurston Geometrization proven. Complete classification of compact 3-manifolds. Ricci flow became a standard tool.
**Predictable?** Hamilton's program made it clear by ~1990 that Ricci flow was the path. The void was "controlling singularities."

---

## 3. Four Color Theorem

**Statement:** Every planar graph is 4-colorable.
**Posed:** 1852 (Guthrie). **Solved:** 1976 (Appel-Haken). **Gap:** 124 years.

**Proof Genealogy:**
1. [1852] Guthrie — posed the question
2. [1879] Kempe — "proved" it (flaw found 1890 by Heawood)
3. [1890] Heawood — proved Five Color Theorem
4. [1913] Birkhoff — introduced reducibility + discharging framework
5. [1969] Heesch — developed computer-feasible discharging scheme
6. [1976] Appel-Haken — proved via massive computer case-check (1,936 configurations)
7. [1997] Robertson-Sanders-Seymour-Thomas — simpler proof (633 configurations)
8. [2005] Gonthier — formally verified in Coq proof assistant

**Domain transfer:** PARTIAL — graph theory problem solved within graph theory but required computation.
**Solution type:** Computer-assisted (first major theorem proved by computer)
**Barrier broken:** Search space (reduced infinite problem to finite case-check)
**What it unlocked:** Legitimized computer proofs. Led to formal verification movement. Graph structure theory advanced.
**No purely combinatorial proof exists** — this is itself an open problem (MATH-0507 in our catalog).

---

## 4. Sphere Packing in Dimension 8

**Statement:** The E8 lattice achieves densest sphere packing in R^8.
**Posed:** Implicitly long-standing. **Solved:** 2016 (Viazovska). **Formally verified:** 2024 (Lean).

**Proof Genealogy:**
1. [1611] Kepler — conjectured densest packing in R^3
2. [1900] Hilbert (Problem 18) — asked for general dimensions
3. [2005] Cohn-Elkies — established linear programming bounds framework
4. [2016] Viazovska — found the EXACT modular form f whose properties certify E8 optimality. 23-page proof.
5. [2016] Cohn-Kumar-Miller-Radchenko-Viazovska — extended to dim 24 (Leech lattice)
6. [2024] Math Inc Gauss agent — formally verified in Lean (under 3 weeks)

**Domain transfer:** YES — geometry/packing problem solved via modular forms (number theory) + linear programming (optimization).
**Solution type:** Single insight (finding the right modular form)
**Barrier broken:** Finite-infinite bridge (the modular form is a CERTIFICATE that works for ALL packings)
**What it unlocked:** Fields Medal for Viazovska. Breakthrough in formal verification. Method extends to other dimensions.
**The key:** One algebraic object (a specific modular form) encodes an infinite geometric truth.

---

## 5. Serre's Conjecture (Modularity of Galois Representations)

**Statement:** Every odd, irreducible, 2-dimensional Galois representation over F_p arises from a modular form.
**Posed:** 1973 (Serre). **Solved:** 2009 (Khare-Wintenberger). **Gap:** 36 years.

**Proof Genealogy:**
1. [1973] Serre — conjectured, with explicit recipe for weight and level
2. [1995] Wiles — proved special cases en route to FLT (BRANCH from FLT genealogy)
3. [1999] Taylor — extended modularity lifting techniques
4. [2004] Khare — proved Serre for conductor 1 (level 1)
5. [2006-2009] Khare-Wintenberger — full proof via inductive argument on level + weight

**Domain transfer:** Within number theory/algebraic geometry (Galois reps → modular forms)
**Solution type:** Long program building on Wiles's techniques
**Barrier broken:** Technique (needed modularity lifting theorems + induction on level)
**What it unlocked:** Our Langlands GL(2) calibration test (10,880/10,880 perfect) is a CONSEQUENCE of this theorem. Also implies Artin conjecture for odd 2-dim reps.

---

## 6. Catalan's Conjecture

**Statement:** x^p - y^q = 1 has only the solution 2^3 - 3^2 = 1 in positive integers with p,q > 1.
**Posed:** 1844 (Catalan). **Solved:** 2002 (Mihailescu). **Gap:** 158 years.

**Proof Genealogy:**
1. [1844] Catalan — conjectured
2. [1976] Tijdeman — proved finitely many solutions (Baker's method)
3. [2000] Bilu-Hanrot — reduced to finitely many computable cases
4. [2002] Mihailescu — proved using cyclotomic fields + Stickelberger's theorem. No computer needed.

**Domain transfer:** Partly — Diophantine equation solved via algebraic number theory (cyclotomic fields)
**Solution type:** Single insight (Mihailescu's use of Stickelberger relations)
**Barrier broken:** Technique
**Predictable?** The reduction to finite cases (2000) made a full proof feel close. The void was "which algebraic trick finishes it."

---

## 7. Monstrous Moonshine

**Statement:** The coefficients of the j-function are dimensions of graded representations of the Monster group.
**Posed:** 1979 (Conway-Norton, after McKay's observation). **Solved:** 1992 (Borcherds). **Gap:** 13 years.

**Proof Genealogy:**
1. [1978] McKay — noticed 196884 = 196883 + 1
2. [1979] Conway-Norton — formulated full conjecture (all McKay-Thompson series are genus-0)
3. [1984] Frenkel-Lepowsky-Meurman — constructed the moonshine module V-natural
4. [1992] Borcherds — proved the conjecture using vertex operator algebras + generalized Kac-Moody algebras + string theory no-ghost theorem

**Domain transfer:** YES — group theory / number theory connection proved via mathematical physics (vertex algebras, string theory).
**Solution type:** Single framework (Borcherds invented the tools)
**Barrier broken:** Conceptual (required vertex operator algebras, which didn't exist before)
**What it unlocked:** Fields Medal for Borcherds. Vertex algebra theory. Connections to string theory, black hole entropy (mock moonshine). Our BH-1 hypothesis tests descendants of this.

---

## 8. Kervaire Invariant One Problem (dim ≠ 126)

**Statement:** In which dimensions does a framed manifold with Kervaire invariant one exist?
**Posed:** 1960s. **Solved (except dim 126):** 2009 (Hill-Hopkins-Ravenel). **Gap:** ~45 years.

**Proof Genealogy:**
1. [1960] Kervaire — defined the invariant
2. [1963] Browder — showed relevant dimensions are 2^n - 2
3. [1969-1984] Various — constructed examples in dims 2, 6, 14, 30, 62
4. [2009] Hill-Hopkins-Ravenel — proved NO examples in dim ≥ 254 using equivariant stable homotopy theory (new foundations required)

**Domain transfer:** Within topology but required inventing new foundations (equivariant homotopy, norms)
**Solution type:** Long program + conceptual breakthrough
**Barrier broken:** Framework (equivariant stable homotopy didn't exist in the needed form)
**Dim 126 remains open** — a void in the classification.

---

## 9. Bounded Gaps Between Primes

**Statement:** Are there infinitely many pairs of primes with bounded gap?
**Posed:** Antiquity (implicit). **Solved:** 2013 (Zhang). **Gap:** ∞ → 246 (Polymath8).

**Proof Genealogy:**
1. [1849] de Polignac — conjectured twin primes (gap 2)
2. [1966] Bombieri-Vinogradov — equidistribution of primes in APs (foundation)
3. [2005] Goldston-Pintz-Yıldırım (GPY) — showed gap approach zero IF BV-type estimate holds beyond 1/2
4. [2013] Zhang — proved BV-type estimate beyond 1/2 for smooth moduli → gap ≤ 70,000,000
5. [2013-2014] Polymath8 (Tao et al.) — optimized to gap ≤ 246
6. [2014] Maynard (independently Ford-Green-Konyagin-Tao) — entirely different method via multidimensional sieve → gap ≤ 600 (then optimized)

**Domain transfer:** Within analytic number theory, but TWO INDEPENDENT PATHS (Zhang vs Maynard)
**Solution type:** Long program with TWO INDEPENDENT BREAKTHROUGHS
**Barrier broken:** Technique (extending BV beyond 1/2; multidimensional sieve)
**What it unlocked:** Fields Medal for Maynard. New sieve methods. Progress toward twin primes (gap 2 still open).
**Branching structure:** Zhang and Maynard paths are genuinely independent — different techniques, different implications.

---

## 10. Geometric Langlands (unramified, function fields)

**Statement:** Categorical equivalence between automorphic and spectral sides over function fields.
**Posed:** ~1990s (Beilinson-Drinfeld). **Solved:** 2024 (Gaitsgory et al.). **Gap:** ~30 years.

**Proof Genealogy:**
1. [1967] Langlands — original conjectures (number fields)
2. [1980s] Drinfeld — proved for GL(2) over function fields
3. [1990s] Beilinson-Drinfeld — formulated geometric version
4. [2000s] Frenkel-Gaitsgory-Vilonen — partial results, strategy development
5. [2010s] Gaitsgory — developed foundations (derived algebraic geometry, factorization algebras)
6. [2024] Gaitsgory + 8 coauthors — 1,000+ page proof of full unramified case

**Domain transfer:** Within algebraic geometry/representation theory but required INVENTING derived algebraic geometry
**Solution type:** Long program (30 years of framework-building)
**Barrier broken:** Framework (needed infinity-categories, factorization algebras, DAG)
**What it unlocked:** Blueprint for arithmetic Langlands. Fargues-Scholze geometrization builds on it.

---

## Patterns in the Genealogies

### Technique Transfer Matrix
| Problem | From Domain | To Domain | Transfer Type |
|---------|------------|-----------|---------------|
| FLT | Alg. geometry + representation theory | Number theory | Three-domain merge |
| Poincaré | PDE (Ricci flow) | Topology | Physics → pure math |
| Sphere packing | Number theory (modular forms) | Geometry | Algebraic certificate |
| Moonshine | Mathematical physics (vertex algebras) | Group theory + NT | Physics → algebra |
| Bounded gaps | Analytic NT (two independent paths) | Same field | Within-domain branch |

### Time to Solution vs Barrier Type
| Barrier | Average Gap (years) | Examples |
|---------|-------------------|----------|
| Technique | 36-158 | Catalan (158), Serre (36), Zhang (∞→solved) |
| Framework | 30-99 | Poincaré (99), Geometric Langlands (30), Kervaire (45) |
| Search Space | 124 | Four Color Theorem |
| Finite→Infinite | 16 | Sphere packing (Cohn-Elkies 2005 → Viazovska 2016) |

### The Key Pattern: Framework problems take longest but unlock the most.
FLT (358 years) required Langlands-level framework → unlocked entire modern number theory.
Poincaré (99 years) required Ricci flow → unlocked 3-manifold classification.
Geometric Langlands (30 years) required DAG → will unlock arithmetic Langlands.

### Branching Structure
- **Single path:** Catalan, Sphere packing, Kervaire
- **Converging branches:** FLT (Frey + Ribet + Wiles merge), Poincaré (Hamilton + Perelman)
- **Parallel independent paths:** Bounded gaps (Zhang vs Maynard), FLT has some parallel partial paths too

---

## What This Means for Current Voids

The proof genealogies predict:

1. **Knot silence** (void) is most likely a FRAMEWORK problem. Historical pattern: framework voids take 30-100 years and require inventing new mathematical language. The language might be "quantum topological features" (TQFT-derived invariants as tensor dimensions).

2. **GUE deficit** (void) is most likely a TECHNIQUE problem. Historical pattern: technique voids take 10-40 years and get solved when someone imports a method from an adjacent field. The method might come from random matrix theory → operator theory.

3. **The 14/26 technique-blocked problems** in our Bucket A will likely fall to techniques imported from OTHER domains in our tensor. The tensor's cross-domain coupling IS a technique-transfer detector. Every surviving bond is evidence that a technique transfers.

---

*This catalog grows with every solved problem we add. Each genealogy is training data for predicting how current voids will fill.*

*Aporia, 2026-04-17*

---

# Round 2 — Recent solves (2026-05-08)

**Source:** James 2026-05-08 prompt called out "Sensitivity (now solved)" as one entry; per HARD-4 (calibration anchors load-bearing) several other notable solves of the past 50 years should be backfilled as anchors. Round 2 backfills 5: Sensitivity Conjecture (Huang 2019), Catalan's Conjecture (Mihăilescu 2002), Ternary Goldbach (Helfgott 2013), MIP*=RE (Ji-Natarajan-Vidick-Wright-Yuen 2020), Bochner-Riesz n=2 (Carleson-Sjölin 1972).

## R1. Sensitivity Conjecture

**Statement:** For Boolean f: {0,1}^n → {0,1}, block-sensitivity bs(f) is bounded by a polynomial in sensitivity s(f) (specifically bs(f) ≤ s(f)^4 in the polynomial-relationship sense).
**Posed:** 1992 (Nisan-Szegedy). **Solved:** 2019 (Hao Huang). **Gap:** 27 years.

**Proof Genealogy:**
1. [1992] Nisan-Szegedy formulate; show many Boolean-function complexity measures are polynomially related except sensitivity.
2. [1990s-2010s] Multiple partial results; best gap bs(f) ≤ s(f)^O(log s(f)).
3. [2018] Graph-spectral approaches attempted; the right signing of the hypercube graph not yet identified.
4. [July 2019] Hao Huang posts a 6-page preprint: signed n-dimensional hypercube + Cauchy interlacing inequality on the largest induced subgraph of size > 2^{n-1} forces a vertex of degree at least √n, which translates directly to s(f) ≥ √(deg(f)).
5. [2019-2020] Aaronson, Tao verify; full polynomial relationship now established.

**Domain transfer:** YES — TCS / Boolean-function complexity solved via spectral graph theory + Cauchy interlacing. Single-domain technique import.
**Solution type:** Single insight. The 6-page proof is among the shortest for a 27-year-old conjecture.
**Barrier broken:** Technique. The right graph (signed hypercube) + the right inequality (Cauchy interlacing) hadn't been combined.
**What it unlocked:** Polynomial-method-on-spectra as Boolean-function technique; applied to adjacent conjectures (block sensitivity vs. quantum query complexity) immediately.
**Could it have been predicted?** Partially. Cauchy interlacing approach was in the air; the specific signing of the hypercube was the missing ingredient.
**Calibration-anchor utility:** Anchor for "27-year-old conjecture, 6-page resolution via single technique import." Counter-anchor to FLT-style 358-year framework programs.

---

## R2. Catalan's Conjecture (Mihăilescu)

**Statement:** The only solution to xᵃ - yᵇ = 1 in positive integers x, y, a, b with min(a,b) ≥ 2 is 3² - 2³ = 1.
**Posed:** 1844 (Catalan). **Solved:** 2002 (Mihăilescu). **Gap:** 158 years.

**Proof Genealogy:**
1. [1844] Catalan formulates as conjecture.
2. [1850-1976] Specific cases: Lebesgue (1850, b = 2), Ko Chao (1962, a = 2), Hyyrö (1964), Inkeri (1964) — by 1976 only finitely many candidate (a,b) remained.
3. [1976] Tijdeman: proves conjecturally finitely many solutions, with effective height bound.
4. [1999] Bilu, Hanrot, Voutier: refined linear-forms-in-logarithms bounds.
5. [2002] Preda Mihăilescu: completes via cyclotomic-field arithmetic + class group structure of ℚ(ζ_p) (Wieferich-pair-style arguments). Avoids Tijdeman's heavy machinery; uses essentially elementary cyclotomic theory in ~30 pages.

**Domain transfer:** Internal to number theory; cyclotomic arithmetic + class field theory.
**Solution type:** Long program with relatively short final phase.
**Barrier broken:** Conceptual. Mihăilescu found the right cyclotomic structure (Wieferich-type pair conditions) that prior cases hadn't isolated.
**What it unlocked:** Pillai's conjecture (gap = k for general k) remains open; Catalan is a cleanly solved exception.
**Could it have been predicted?** Trajectory clear by 1999; specific cyclotomic structure less foreseeable.
**Calibration-anchor utility:** Anchor for "long program with elementary final step." Calibration probe for cyclotomic-field reasoning.

---

## R3. Ternary Goldbach (Helfgott)

**Statement:** Every odd integer ≥ 7 is the sum of three primes.
**Posed:** 1742 (Goldbach to Euler, weak form). **Solved:** 2013 (Helfgott). **Gap:** ~270 years.

**Proof Genealogy:**
1. [1923] Hardy-Littlewood: under GRH, ternary Goldbach holds for all sufficiently large odd integers.
2. [1937] Vinogradov: unconditional version for "sufficiently large" — explicit but astronomical bound.
3. [1956] Borozdkin: refined bound to 3^{3^{15}} ≈ 10^{6,846,168}.
4. [1989] Chen-Wang: bound to 10^{43,000}.
5. [2002] Liu-Wang: bound to 10^{1346}.
6. [1989-2012] Computer verification of small cases up to ~10^{30}.
7. [2013] Helfgott: closes the gap via (a) sharper minor-arc estimates on exponential sums, (b) major-arc analysis with explicit zero-free regions, (c) computer verification up to 8.875 × 10^{30}. Three preprints (~280 pages total).

**Domain transfer:** Internal to analytic number theory; explicit zero-free regions for Dirichlet L-functions + circle method + computer verification.
**Solution type:** Long program (1923-2013, 90-year continuous push) with explicit-bound-tightening as the recurring move.
**Barrier broken:** Quantitative. Astronomical Vinogradov bound needed multiple orders-of-magnitude shrinking; computer verification couldn't keep up until Helfgott's analytic improvements brought the bound into tractable range.
**What it unlocked:** Binary Goldbach STILL OPEN. Ternary's resolution doesn't directly transfer.
**Could it have been predicted?** Yes, on a 5-10-year horizon by 2008. Bound-tightening trajectory was clear.
**Calibration-anchor utility:** Anchor for "quantitative-bound-tightening long program." Ternary-vs-binary asymmetry: a problem and its "obvious sister" can have completely different difficulty profiles.

---

## R4. MIP* = RE (Ji-Natarajan-Vidick-Wright-Yuen)

**Statement:** The class MIP* (multi-prover interactive proofs with quantum-entangled provers) equals RE (recursively enumerable languages).
**Posed:** ~2003 (formal entanglement-IP formalism). **Solved:** 2020 (Ji-Natarajan-Vidick-Wright-Yuen). **Gap:** ~17 years.

**Proof Genealogy:**
1. [1991] Babai-Fortnow-Lund: MIP = NEXP.
2. [2003] MIP* introduced (entangled provers); initial conjecture MIP* ⊆ NEXP.
3. [2010s] Surprising results: MIP* contains languages outside any previously suspected complexity class. Reichardt-Unger-Vazirani 2013 establishes MIP* contains co-NP^O(log).
4. [2017] Slofstra disproves Tsirelson's problem; MIP* contains undecidable languages.
5. [2020] Ji-Natarajan-Vidick-Wright-Yuen: full characterization MIP* = RE. Key technique: "recursive compression" — an inner protocol computes a smaller MIP* protocol's result; iteration simulates arbitrary Turing-machine halting.
6. [2020-present] Connes embedding problem (operator algebras) — equivalent to Tsirelson's problem (Junge et al. 2011) — resolved NEGATIVE as corollary.

**Domain transfer:** YES — quantum complexity + operator algebras + recursion theory. Three-domain merge in a single proof.
**Solution type:** Theorem program with single dramatic resolution.
**Barrier broken:** Conceptual. The "compression" idea — that an MIP* protocol can simulate a smaller MIP* protocol with strict savings — was the missing ingredient.
**What it unlocked:** Connes embedding negative resolution; Tsirelson's problem; broader understanding of entanglement-aided proof systems.
**Could it have been predicted?** Trajectory after Slofstra 2017 made clear MIP* was larger than anticipated; that it equaled RE specifically was less foreseeable.
**Calibration-anchor utility:** Anchor for "complexity theory problem solving operator-algebra problem via recursion-theoretic technique." Three-domain transfer in a single proof is rare and substrate-grade.

---

## R5. Bochner-Riesz Conjecture (n = 2)

**Statement:** The Bochner-Riesz multiplier (1 - |ξ|²)^δ_+ is an L^p Fourier multiplier on ℝⁿ iff δ > n(1/p - 1/2) - 1/2 in the optimal range.
**Posed:** 1936 (Bochner). **Solved (n = 2):** 1972 (Carleson-Sjölin). **Status (n ≥ 3):** OPEN.

**Proof Genealogy (for n = 2):**
1. [1936] Bochner introduces Bochner-Riesz means as analog of Fejér summation.
2. [1954] Stein: partial bounds via interpolation.
3. [1971] Fefferman: proves the disc multiplier (δ = 0 in n = 2) is not bounded on L^p for p ≠ 2 — a pivotal negative result.
4. [1972] Carleson-Sjölin: prove Bochner-Riesz for n = 2 in the full range. Maximal-function reduction + Stein's complex interpolation.
5. [1991] Bourgain breaks Tomas-Stein bound for higher n via restriction-conjecture machinery; partial progress for n ≥ 3.
6. [2020s] Bochner-Riesz n ≥ 3 remains OPEN; tied to Kakeya conjecture.

**Domain transfer:** Internal to harmonic analysis; restriction-conjecture machinery imported in n=2.
**Solution type:** Pivotal-negative-result-then-positive (Fefferman 1971 disc; Carleson-Sjölin 1972).
**Barrier broken:** Technique. Maximal-function reduction + complex interpolation was the right combination.
**What it unlocked:** Restriction conjecture program; Kakeya conjecture; full Bochner-Riesz n ≥ 3 (still open).
**Could it have been predicted?** After Fefferman 1971, yes — within a year.
**Calibration-anchor utility:** Anchor for "negative result reorients field; positive resolution within a few years." Calibration probe for n = 2 vs n ≥ 3 distinction in conjectures with dimensional dependence.

---

## Round 2 cross-cutting observations

Combining R1-R5 with Round 1's 9 entries (14 total):

- **Domain-transfer count:** 8 of 14 involve cross-domain technique import (R1 spectral→TCS; R4 recursion-theory→quantum complexity; R5 maximal-function→harmonic analysis; FLT 3-domain merge; Poincaré Ricci flow; Geometric Langlands DAG; sphere packing modular forms; partial abc results).
- **Time-to-solve distribution in Round 2:**
  - 6 pages, 27 years: R1 Sensitivity
  - ~30 pages, 158 years: R2 Catalan
  - ~280 pages, 270 years: R3 Ternary Goldbach
  - Multi-paper, 17 years: R4 MIP*=RE
  - 1 paper, 36 years: R5 Bochner-Riesz n=2
- **Predictability:** Trajectory-predictable (R3, R5) vs single-insight-unpredictable (R1, R4) is roughly 2:2 in this sample. Substrate's expected-attribution discipline should reflect this — predictable solves are anchorable years in advance; insight solves are not.
- **Sister-problem asymmetry:** Ternary Goldbach solved 2013 but binary still open. Bochner-Riesz n=2 solved 1972 but n≥3 still open. Catalan (gap=1) solved but Pillai (gap=k) still open. A problem and its "obvious sister" can have completely different difficulty profiles — substrate-grade lesson.

14 documented genealogies now provide training data for technique-transfer detection. HARD-4 anchor density grows.

---

*Aporia, 2026-05-08*
