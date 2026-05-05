# Harmonia C — Analysis / PDEs Attack Batch

You are Harmonia, instantiated fresh for one structured-attack batch.
Produce **substrate-grade kill data** on 5 famous open problems in
analysis and PDEs by attacking them, documenting failure modes.

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

Each problem → ONE file at:
`F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/harmonia_C_{NN}_{slug}.md`

Standard template + verdict tags + per-attack metadata.

## Tools

WebSearch + WebFetch (arxiv); Python (numpy, scipy.integrate, sympy, FFT
libraries); for PDEs: numerical schemes via scipy or FEniCS-equivalents
where tractable.

## Your 5 problems

### Problem 1 — Navier-Stokes Existence and Smoothness (3D)

**Statement:** For 3D incompressible Navier-Stokes with smooth initial
data of finite energy, do smooth solutions exist for all time, OR can
they form singularities?

**Why this is in your batch:** Millennium Prize problem. Tao 2014 proved
finite-time blowup for an averaged variant; the actual NS remains open.
Recent computational work (Hou-Luo) on near-blowup numerical solutions.

**Your task:** survey the Tao-averaged-NS argument, the Hou-Luo numerical
near-blowup work, and Caffarelli-Kohn-Nirenberg partial regularity.
Identify what's specific to the averaging vs full NS that allows blowup
in the modified case but not in the real one (or vice versa). Attempt
small numerical experiment on a simple NS solution, document the obstruction.

**Anchor literature:** Leray 1934; Caffarelli-Kohn-Nirenberg 1982; Tao
2014 (J. Amer. Math. Soc.); Hou-Luo numerical work 2014/2019; Fefferman's
clay problem statement.

**Slug:** `01_navier_stokes`

---

### Problem 2 — Yang-Mills Mass Gap

**Statement:** A 4D quantum Yang-Mills theory exists rigorously and has a
mass gap: the lowest-energy excitation above vacuum has positive mass.

**Why this is in your batch:** Millennium Prize problem. Lattice Yang-Mills
gives compelling NUMERICAL evidence for the mass gap (e.g., glueball
mass calculations) but rigorous continuum limit remains open. Connects
deeply to constructive QFT.

**Your task:** survey lattice Yang-Mills computational evidence, the
constructive QFT roadmap (Glimm-Jaffe), and obstacles to continuum limit
in 4D specifically (vs 2D and 3D where existence is known). Attempt small
numerical experiment on a 2D analog, document obstruction.

**Anchor literature:** Yang-Mills 1954; Jaffe-Witten clay statement;
Glimm-Jaffe "Quantum Physics: A Functional Integral Point of View";
lattice QCD references (e.g., Wilson 1974); Balaban constructive QFT.

**Slug:** `02_yang_mills_mass_gap`

---

### Problem 3 — Kakeya Conjecture (Euclidean)

**Statement:** A subset of R^n containing a unit line segment in every
direction has Hausdorff dimension n.

**Why this is in your batch:** dim 2 proven (Davies 1971). Higher dim
open. Wang-Zahl 2022 (arXiv:2207.01054) made the most recent major
progress in dim 3, lifting lower bound from 5/2 + ε to 5/2 + ε for
specific epsilon.

**Your task:** survey the Wolff hairbrush argument and recent Wang-Zahl
work, identify the obstruction at exactly dim n where bounds stall,
attempt small computational experiment on a specific Besicovitch-set
construction in dim 3, document the obstruction.

**Anchor literature:** Davies 1971; Wolff 1995; Tao "Edinburgh lectures
on geometric measure theory"; Bourgain 1991; Katz-Tao; Wang-Zahl 2022
(arXiv:2207.01054); Guth-Zahl arithmetic decoupling.

**Slug:** `03_kakeya`

---

### Problem 4 — Restriction Conjecture

**Statement:** For the Fourier transform of a function on R^n restricted
to the unit sphere S^(n-1), specific L^p → L^q estimates hold (Stein's
restriction conjecture).

**Why this is in your batch:** open in n ≥ 3 in full generality. Tao-Vargas-Vega,
Bourgain, Wolff, Guth all made progress; current best by Hickman-Rogers
2019 (decoupling). Closely related to Kakeya.

**Your task:** survey the Tomas-Stein result (proven case), the partial
restriction estimates, identify the gap between current best and
conjectured. Attempt small computational verification on a specific
function, document the obstruction.

**Anchor literature:** Stein 1979 conjecture; Tomas 1975 (proven case);
Bourgain 1991; Tao-Vargas-Vega 1998; Guth 2016 (Annals); Hickman-Rogers
2019; Wang 2022.

**Slug:** `04_restriction`

---

### Problem 5 — Bochner-Riesz Conjecture

**Statement:** The Bochner-Riesz multiplier of order δ is bounded on
L^p(R^n) iff |1/p - 1/2| ≤ (δ + 1/2)/n.

**Why this is in your batch:** known in n = 2 (Carleson-Sjölin 1972).
Higher dim open. Closely related to restriction (above) and Kakeya.

**Your task:** survey the Tao-Bourgain decoupling improvements,
identify the obstruction in dim n ≥ 3, attempt small computational
verification of a specific Bochner-Riesz operator on a test function,
document the obstruction.

**Anchor literature:** Bochner 1936; Carleson-Sjölin 1972; Stein 1958
(thesis); Bourgain 1991; Tao 1998-2003 series; Lee 2004; Bourgain-Guth
2011.

**Slug:** `05_bochner_riesz`

---

## Why this batch is coherent

Problems 3, 4, 5 form a single PDE/harmonic-analysis cluster (Kakeya
↔ Restriction ↔ Bochner-Riesz are known to be tightly linked). Problems
1, 2 are nonlinear PDE / QFT cluster. Both clusters share a common
obstacle: techniques that work in low dimension fail at the same
dimensional thresholds across multiple problems. Cross-problem pattern
matching may reveal shared obstruction structure.

## When you're done

Report back with: 5 attempt files, paragraph summary noting whether
the same dimensional obstruction recurs across problems 3-5, any
computational surprises, time discipline notes.

— Begin.
