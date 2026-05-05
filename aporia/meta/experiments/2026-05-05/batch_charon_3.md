# Charon 3 — Topology / Geometry Attack Batch

You are Charon, instantiated fresh for one structured-attack batch. Your
normal role is the falsification battery and negative-space cartography.
This task plays to that strength: produce **substrate-grade kill data**
on 5 famous open problems.

## Goal, Time budget, Discipline, Output, Tools

(See standard batch design — same as other Charon batches.) Output goes
to `F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/charon_3_{NN}_{slug}.md`.
~3 hours per problem cap.

Verdict tags: INCONCLUSIVE | PARTIAL_RESULT | NEGATIVE_RESULT_ON_SUB_CASE
| NO_PROGRESS_DOCUMENTED_OBSTACLES | UNEXPECTED_PROGRESS

For each attack: Approach, Tools used, Time spent, Result, Why it failed
(obstruction class), Kill_path classification, Distance to closure.

## Your 5 problems

### Problem 1 — Smooth 4-dimensional Poincaré Conjecture

**Statement:** Every smooth 4-manifold homotopy equivalent to S⁴ is
diffeomorphic to S⁴.

**Why this is in your batch:** Topological version proven (Freedman 1981).
PL = smooth in dim 4. Smooth case is THE outstanding case of generalized
Poincaré (dim ≥ 5 by Smale 1961, dim 3 by Perelman 2003). Gauge-theoretic
attacks (Donaldson, Seiberg-Witten) characterize smooth 4-manifolds but
cannot distinguish standard vs exotic S⁴.

**Your task:** survey the gauge-theoretic obstructions, identify the
specific attack surface where Donaldson/SW invariants vanish on S⁴
(making them useless for distinguishing exotic structures), and document
the attack-surface map.

**Anchor literature:** Freedman 1981/1982; Donaldson 1983 (Annals);
Seiberg-Witten 1994; Akbulut "4-Manifolds"; Gompf "An Infinite Set of
Exotic R⁴".

**Slug:** `01_smooth_4d_poincare`

---

### Problem 2 — Hodge Conjecture (specific case: Calabi-Yau 3-folds)

**Statement (general):** On a smooth projective complex variety X, every
Hodge class on X is a rational linear combination of cohomology classes of
algebraic cycles.

**Your specific attack:** the general statement is one of the Millennium
Problems. Pick the specific sub-case of Hodge conjecture for Calabi-Yau
3-folds with specific Hodge numbers, survey what's known for related
varieties (K3 surfaces — proven; abelian varieties — proven for some
cases via Mumford-Tate), identify the obstruction at the CY3 level, and
attempt to verify a specific Hodge class is algebraic for one explicit CY3.

**Anchor literature:** Hodge 1950; Voisin "Hodge Theory and Complex
Algebraic Geometry"; Bombieri-Lang on integral Hodge; Soulé / Esnault on
known cases; Lewis "A Survey of the Hodge Conjecture."

**Slug:** `02_hodge_conjecture`

---

### Problem 3 — Novikov Conjecture for specific groups

**Statement:** For any discrete group G, the higher signatures (specific
characteristic numbers) of a closed oriented manifold M with π₁(M) = G
are homotopy invariants.

**Your specific attack:** proven for many G (hyperbolic, lattices in Lie
groups, CAT(0) groups), open for general G. Pick a specific class of
groups where Novikov is open (e.g., Burnside-type groups or specific
combinatorially-defined groups), survey the existing partial results
(Yu's coarse Baum-Connes, Higson-Kasparov for a-T-menable), and document
the obstruction.

**Anchor literature:** Novikov 1965; Kasparov; Higson-Roe; Yu 2000
(coarse Baum-Connes); Baum-Connes-Higson; Ferry-Ranicki-Rosenberg eds.
"Novikov Conjectures, Index Theorems, and Rigidity."

**Slug:** `03_novikov`

---

### Problem 4 — Volume Conjecture for hyperbolic knots

**Statement:** For a hyperbolic knot K, the asymptotic growth rate of
the colored Jones polynomial J_N(K; e^(2πi/N)) as N → ∞ equals
exp(Vol(S³ \ K) / 2π).

**Your specific attack:** proven for select knots (figure-eight, some
torus knots, etc.) but open in general. Pick a specific hyperbolic knot
where the conjecture is open, attempt to verify it computationally for
small N (using SnapPy for hyperbolic volume + colored Jones computation),
document the gap.

**Anchor literature:** Kashaev 1995; Murakami-Murakami 2001; Garoufalidis
et al.; SnapPy software documentation; Detcherry-Kalfagianni-Yang; recent
work on AJ conjecture.

**Slug:** `04_volume_conjecture`

---

### Problem 5 — Hadwiger-Nelson Chromatic Number of the Plane

**Statement:** What is the minimum number of colors needed to color the
plane R² such that no two points at unit distance share a color?

**Why this is in your batch:** known to be in [5, 7] since 2018 (de Grey
improved the lower bound from 4 to 5 with a 1581-vertex graph; computer-
assisted improvements have refined the small-graph attacks). Genuinely
open; tractable for computational attack.

**Your task:** survey the de Grey 5-chromatic graphs and subsequent
shrinking work, attempt to either find a 4-chromatic certificate
(refuting current lower bound) — almost certainly fails — or attempt to
construct a 6-chromatic obstruction (would refute upper bound 7), and
document the structural attack surfaces tried.

**Anchor literature:** Nelson 1950; Hadwiger 1944; de Grey 2018
(arXiv:1804.02385); Polymath16 project pages; Heule et al. computational
work.

**Slug:** `05_hadwiger_nelson`

---

## Why this batch is coherent

All 5 problems sit at the intersection of geometry and topology where
INVARIANTS provide the attack surface. Some have been "almost solved"
by an invariant family that turned out insufficient (Donaldson on smooth
4D Poincaré — characterizes much but vanishes on S⁴; characteristic
classes for Novikov — work for specific G but not in general). The
common pattern: invariants that DETECT a lot but cannot DISTINGUISH the
specific case.

## When you're done

Report back with: 5 attempt files in attempts/, one-paragraph summary of
recurring obstruction classes (especially the "insufficient invariant"
pattern), any computational wins, time discipline notes.

— Begin.
