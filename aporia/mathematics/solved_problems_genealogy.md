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
