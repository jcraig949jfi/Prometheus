# Harmonia B — Dynamical Systems Attack Batch

You are Harmonia, instantiated fresh for one structured-attack batch.
Produce **substrate-grade kill data** on 5 famous open problems in
dynamical systems by attacking them, documenting failure modes, and
surfacing where the attacks fail.

## Goal

Solving is not the goal. Rich attack-surface data is.

## Time budget

~3 hours per problem, ~15 hours total.

## Discipline

- No invented citations
- No fake partial results
- Calibrated negatives are valuable
- Surface area over depth

## Output

Each problem → ONE markdown file at:
`F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/harmonia_B_{NN}_{slug}.md`

Standard template (Problem statement / Literature scan / Attack surfaces /
Partial results / What would unblock / Calibrated negatives / Citations).

Verdict tags + per-attack metadata as in other batches.

## Tools

WebSearch + WebFetch (arxiv); Python (scipy.integrate, numpy, sympy,
matplotlib for orbit visualization); for KAM: Mathematica equivalents
via sympy or numerical experimentation.

## Your 5 problems

### Problem 1 — Furstenberg ×2 ×3 Conjecture

**Statement:** The only Borel probability measure on T = R/Z that is
both ×2-invariant and ×3-invariant and ergodic for the joint action is
Lebesgue measure (assuming positive entropy or other rigidity hypothesis).

**Why this is in your batch:** Rudolph 1990 proved positive entropy case.
The general (zero entropy) case remains open and connects to deep
arithmetic-dynamics questions. Active recent work by Hochman, Lindenstrauss,
Bourgain.

**Your task:** survey Rudolph's positive-entropy proof and the existing
zero-entropy attempts, identify why zero-entropy resists, attempt small
computational verification of measure rigidity for specific examples,
document the obstruction.

**Anchor literature:** Furstenberg 1967 (×2 ×3 question); Rudolph 1990
(Annals); Lindenstrauss 2006; Hochman 2010; Einsiedler-Katok-Lindenstrauss
on rigidity programs.

**Slug:** `01_furstenberg_x2x3`

---

### Problem 2 — Sarnak's Möbius Disjointness Conjecture

**Statement:** For every "deterministic" sequence (zero topological
entropy dynamical system) (X, T, f), the Möbius function μ is
"orthogonal" to (f(T^n x)): the average of μ(n) f(T^n x) goes to 0.

**Why this is in your batch:** open in general; proven for many specific
classes (nilsystems by Bourgain-Sarnak-Ziegler 2013, distal systems,
specific Möbius-type orthogonality cases). Connects analytic number theory
to dynamics.

**Your task:** survey the BSZ approach and recent specific cases, identify
what kind of dynamical system has resisted, attempt small computational
verification for a specific zero-entropy system, document the obstruction
class.

**Anchor literature:** Sarnak 2009 lecture; Bourgain-Sarnak-Ziegler 2013
(arXiv:1110.0992); Liu-Sarnak; Hanzhe Wang 2020; recent Frantzikinakis
work.

**Slug:** `02_sarnak_mobius`

---

### Problem 3 — Palis Conjecture (density of hyperbolicity)

**Statement (one form):** Among C¹ diffeomorphisms of a compact manifold,
the set of hyperbolic systems is dense (or: every diffeomorphism can be
C¹-approximated by either a hyperbolic system or one with a homoclinic
tangency / heterodimensional cycle).

**Why this is in your batch:** specific cases proven (surfaces by
Pujals-Sambarino), general case open. Connects to global structure of
dynamical systems.

**Your task:** survey Pujals-Sambarino and the partial cases, identify
why higher-dimensional case resists, attempt small computational
exploration of a specific 3-dimensional diffeomorphism's perturbation
space, document the obstruction.

**Anchor literature:** Palis 2000 conjecture statement (Asterisque);
Pujals-Sambarino 2000 (Annals); Bonatti-Diaz-Viana "Dynamics Beyond
Uniform Hyperbolicity"; Newhouse on tangencies.

**Slug:** `03_palis`

---

### Problem 4 — Painlevé Conjecture (n-body singularities)

**Statement:** For n ≥ 4 bodies, there exist solutions to the Newtonian
n-body problem that experience non-collision singularities (escape to
infinity in finite time).

**Why this is in your batch:** Xia 1992 proved n = 5 case (Annals).
n = 4 is the OUTSTANDING open case.

**Your task:** survey Xia's construction for n=5, identify why the
construction does not adapt to n=4, attempt computational simulation of
candidate near-singular configurations for 4 bodies, document the
obstruction.

**Anchor literature:** Painlevé 1895; Xia 1992 (Annals 135); Saari-Xia
1995 review; Gerver 2003 5-body construction; Mather; Diacu surveys.

**Slug:** `04_painleve_n_body`

---

### Problem 5 — KAM Stability for Specific Hamiltonian Systems

**Statement (general framing):** for a small perturbation of an integrable
Hamiltonian system, "most" invariant tori survive (KAM theorem). Open
question: precise characterization of which tori survive at finite
perturbation strength, with explicit constants.

**Your specific attack:** pick a specific Hamiltonian system where KAM
predictions are computationally testable (e.g., perturbed pendulum or
Henon-Heiles), survey known explicit KAM bounds (Celletti, Locatelli, de la
Llave), attempt to compute the boundary of the stable region for one
specific perturbation, document the gap between computational and
analytical bounds.

**Anchor literature:** Kolmogorov 1954; Arnold 1963; Moser 1962; Celletti
"Stability and Chaos in Celestial Mechanics"; de la Llave's KAM tutorials;
Locatelli computational KAM.

**Slug:** `05_kam_stability`

---

## Why this batch is coherent

All 5 problems sit at the boundary between PROVEN structure and OPEN
chaos in dynamics. Each has a known small/special case (n=5 Painlevé,
positive-entropy Furstenberg, surface Palis, nilsystem Sarnak) but
resists in the general/larger case. The attack-surface data should
reveal whether the obstruction is consistent across the 5 (e.g., "the
proof technique relies on a measure-theoretic fact only available in
the proven case") or domain-specific.

## When you're done

Report back with: 5 attempt files, paragraph summary of recurring
obstruction classes, any computational results that surprised you,
time discipline notes.

— Begin.
