---
catalog_name: P vs NP
problem_id: p-vs-np
version: 1
version_timestamp: 2026-04-21T01:00:00Z
status: sketch
surface_statement: Is the complexity class P (decision problems solvable in polynomial time) equal to the class NP (decision problems verifiable in polynomial time), or strictly contained in it?
---

## What the problem is really asking

1. **Is verification fundamentally easier than discovery?** If P ≠ NP,
   there exist problems we can check quickly but not solve quickly —
   an asymmetry between reading proofs and finding them.
2. **Is there a general-purpose structural shortcut for NP-hard
   problems?** The conjecture P ≠ NP says no.
3. **Does the universe permit efficient simulation of all polynomial-
   time verifiable processes?** If P = NP, many currently-intractable
   optimization problems (SAT, TSP, protein folding) become tractable.
4. **Is cryptographic hardness (as currently deployed) fundamental or
   contingent?** Modern cryptography assumes P ≠ NP (plus stronger
   hardness assumptions). P = NP would collapse much of practical
   cryptography.
5. **Where are the computational "phase transitions" of SAT-like
   problems in real computing practice?** Empirical hardness of
   random-k-SAT shows a sharp threshold; theoretical understanding
   is incomplete.

This is a sketch-status catalog. Template demonstration, not
exhaustive population.

## Data provenance

**The problem (1971).** Cook-Levin theorem established NP-completeness
of SAT. The P vs NP question was formally posed in Cook 1971 and
Levin 1973 (independently). Prior informal versions: Gödel's 1956
letter to von Neumann anticipated the essence.

**Millennium Prize (2000).** Clay Mathematics Institute — $1M for a
proof or disproof.

**The empirical record:** decades of algorithm-design and hardness-
reduction have produced vast landscapes of polynomial-time algorithms
on one side and NP-complete reductions on the other. No progress
toward collapse.

## Motivations

- **Theoretical computer science** — central question of complexity
  theory.
- **Cryptographic practice** — security assumptions ultimately rest
  on P ≠ NP (and stronger).
- **Optimization practice** — if P = NP, many practical problems
  become tractable.
- **Philosophical** — asks whether "proof" and "search" are
  fundamentally different computational activities.

## Lens catalog (sketch, 12 entries)

### Lens 1 — Diagonalization / relativization (Baker-Gill-Solovay)

- **Discipline:** Computability theory
- **Status:** PUBLIC_KNOWN
- **Prior result:** Baker-Gill-Solovay 1975: no relativizing proof
  of P vs NP in either direction — existing diagonalization methods
  are insufficient.
- **Tier contribution:** Yes (surfaces a barrier rather than a
  result).

### Lens 2 — Circuit complexity lower bounds

- **Discipline:** Boolean complexity theory
- **Status:** PUBLIC_KNOWN
- **Prior result:** Strong lower bounds for specific circuit classes
  (monotone, AC⁰, ACC⁰) but not for general polynomial-size Boolean
  circuits; would imply NP ⊄ P/poly ⇒ P ≠ NP if proven.
- **Tier contribution:** Yes.

### Lens 3 — Natural-proofs barrier (Razborov-Rudich)

- **Discipline:** Complexity theory
- **Status:** PUBLIC_KNOWN (barrier result)
- **Prior result:** Razborov-Rudich 1994: any "natural" proof of
  strong circuit lower bounds would break cryptographic primitives
  assumed secure. Rules out a broad class of lower-bound techniques.
- **Tier contribution:** Yes.

### Lens 4 — Algebrization barrier (Aaronson-Wigderson)

- **Discipline:** Complexity theory
- **Status:** PUBLIC_KNOWN
- **Prior result:** Aaronson-Wigderson 2008: extends relativization
  barrier to include arithmetization-based techniques. Further
  narrows the solution space.
- **Tier contribution:** Yes.

### Lens 5 — Geometric complexity theory (Mulmuley)

- **Discipline:** Algebraic geometry / representation theory
- **Status:** PUBLIC_KNOWN (ongoing research program)
- **Prior result:** Mulmuley 2000s+: attempt to prove P ≠ NP via
  invariant-theoretic obstructions. No resolution; program's
  expected timeline is "decades to centuries."
- **Tier contribution:** Yes.

### Lens 6 — Proof complexity / SAT solver analysis

- **Discipline:** Proof theory
- **Status:** PUBLIC_KNOWN
- **Prior result:** Lower bounds on proof length in specific proof
  systems (resolution, Frege, etc.). Does not directly settle P vs
  NP but illuminates structure.
- **Tier contribution:** Yes.

### Lens 7 — Average-case vs worst-case (Levin)

- **Discipline:** Complexity theory
- **Status:** PUBLIC_KNOWN
- **Prior result:** Levin 1986: distributional NP; asks whether NP is
  hard on natural distributions. Partial reductions known; complete
  resolution open.
- **Tier contribution:** Yes.

### Lens 8 — Derandomization / pseudorandomness

- **Discipline:** Complexity theory
- **Status:** PUBLIC_KNOWN
- **Prior result:** Impagliazzo-Wigderson: BPP ⊆ P under certain
  hardness assumptions; connects derandomization to circuit lower
  bounds.
- **Tier contribution:** Yes.

### Lens 9 — Physics / adiabatic quantum computing

- **Discipline:** Mathematical physics
- **Status:** PUBLIC_KNOWN (analog)
- **Prior result:** BQP (bounded-error quantum polynomial time) is
  believed to strictly contain P but not contain NP. Related but
  distinct questions.
- **Tier contribution:** Yes.

### Lens 10 — Information-theoretic / communication complexity

- **Discipline:** Information theory
- **Status:** PUBLIC_KNOWN
- **Prior result:** Strong lower bounds in communication complexity
  models; some connections to circuit lower bounds.
- **Tier contribution:** Yes.

### Lens 11 — Formal verification of proof attempts

- **Discipline:** Formal methods
- **Status:** UNAPPLIED systematically
- **Expected yield:** Could provide certainty on attempted proofs
  (many P vs NP "proofs" have been posted; most rapidly disproved).

### Lens 12 — Empirical phase-transition analysis of SAT

- **Discipline:** Statistical mechanics / combinatorial optimization
- **Status:** PUBLIC_KNOWN (partial)
- **Prior result:** k-SAT shows sharp threshold at specific clause-
  to-variable ratios; does not directly address P vs NP but
  illuminates typical-case hardness.
- **Tier contribution:** Yes.

## Cross-lens summary

- **Total lenses cataloged:** 12
- **APPLIED (Prometheus):** 0 — this is a sketch; no Prometheus
  attack has been run.
- **PUBLIC_KNOWN:** 10
- **UNAPPLIED:** 2

**Current `SHADOWS_ON_WALL@v1` tier:** `coordinate_invariant` on the
stance level (near-universal community belief: P ≠ NP) via
public-known lenses only. BUT: this consensus rests entirely on
"no counterexample found + several barrier results" rather than on
convergence from radically different disciplinary priors. A
Prometheus multi-perspective attack might surface genuine
disagreement that community consensus has smoothed over.

**Priority unapplied lenses:**

No immediate Prometheus work is planned for P vs NP. This catalog
exists to demonstrate the template handles problems outside number
theory / dynamics.

## Connections

**To other open problems:** NP-hard optimization problems (TSP, SAT,
graph coloring) all inherit their hardness from P vs NP. If resolved,
downstream effects on practical computing.

**To Prometheus symbols:**
- `SHADOWS_ON_WALL@v1` — an instructive case: community consensus is
  `coordinate_invariant` but the lenses are largely correlated via
  shared complexity-theoretic vocabulary. A genuinely orthogonal
  lens (e.g., geometric complexity theory's algebraic-geometry
  approach) is the exception that tests the tier.
