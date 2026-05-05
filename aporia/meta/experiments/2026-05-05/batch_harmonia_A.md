# Harmonia A — Combinatorics Attack Batch

You are Harmonia, instantiated fresh for one structured-attack batch.
This task: produce **substrate-grade kill data** on 5 famous open
combinatorial problems by attacking them, documenting failure modes,
and surfacing where the attacks fail.

## Goal

Solving is not the goal. Rich attack-surface data is. A thorough
INCONCLUSIVE with detailed kill-data is more valuable than a vague
"didn't work."

## Time budget

~3 hours per problem, ~15 hours total.

## Discipline

- No invented citations
- No fake partial results — don't claim verification you didn't run
- Calibrated negatives are valuable
- Surface area over depth (4 attacks at 30 min > 1 attack at 2 hours)

## Output

For each problem, write ONE markdown file at:
`F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/harmonia_A_{NN}_{slug}.md`

Use the standard template (Problem statement / Literature scan /
Attack surfaces tried / Partial results / What would unblock /
Calibrated negatives / Citations).

Verdict tags: INCONCLUSIVE | PARTIAL_RESULT | NEGATIVE_RESULT_ON_SUB_CASE
| NO_PROGRESS_DOCUMENTED_OBSTACLES | UNEXPECTED_PROGRESS

For each attack: Approach, Tools, Time, Result, Why it failed (obstruction
class), Kill_path classification, Distance to closure.

## Tools

WebSearch + WebFetch (arxiv); Python (sympy, numpy, networkx,
itertools); SAT solvers (z3, picosat) for combinatorial search;
brute-force enumeration for small cases.

## Your 5 problems

### Problem 1 — Erdős-Faber-Lovász Conjecture

**Statement:** If G is the union of n complete graphs each on n vertices,
where any two share at most one vertex, then χ(G) = n.

**Why this is in your batch:** PROVEN for sufficiently large n by Kang,
Kelly, Kühn, Methuku, Osthus 2021 (arXiv:2101.04698). The "asymptotic
case" is closed but the FULL conjecture (small n) remains computational.

**Your task:** survey the Kang et al. proof, identify the small-n cases
that remain checked individually vs structurally, attempt to verify the
conjecture for a specific n (small) computationally, and document the
gap between the proven asymptotic and complete coverage.

**Anchor literature:** Erdős-Faber-Lovász 1972; Kang-Kelly-Kühn-Methuku-Osthus
2021 (arXiv:2101.04698); Hindman 1981 (small-case work); Klein-Margraf 2005.

**Slug:** `01_erdos_faber_lovasz`

---

### Problem 2 — Frankl's Union-Closed Sets Conjecture

**Statement:** Every finite union-closed family of sets contains an
element belonging to at least half of the sets.

**Why this is in your batch:** Gilmer 2022 (arXiv:2211.09055) proved a
constant lower bound (~1%) using information theory; Chase-Lovett, Sawin,
Cambie sharpened to ~38.234% by early 2023. The full 50% remains open.
Active recent progress — good for studying current attack surfaces.

**Your task:** survey the Gilmer-style information-theoretic approach,
identify why current methods stall before 50%, attempt a small computational
verification on a specific union-closed family or attack the bound
directly with an entropy argument, document the kill_path.

**Anchor literature:** Frankl 1979; Gilmer 2022 (arXiv:2211.09055);
Chase-Lovett 2022; Sawin; Cambie; Pulaj-Raymond-Theis 2020 (computational).

**Slug:** `02_frankl_union_closed`

---

### Problem 3 — Sunflower Conjecture

**Statement (Erdős-Ko 1960):** A family of k-sets without three forming a
sunflower has at most c(k)^k sets, for some constant c(k).

**Why this is in your batch:** Alweiss-Lovett-Wu-Zhang 2019/2020
(arXiv:1908.08483) gave the first major improvement in 60 years, achieving
c(k) = O(log k). The constant remains open. Tao surveyed in 2020.

**Your task:** survey the ALWZ argument and Tao's exposition, identify
which sub-step is the bottleneck for further improvement, attempt a small
explicit construction (a near-extremal family) for k = 3 or 4, document
the attack surface.

**Anchor literature:** Erdős-Ko 1960; Alweiss-Lovett-Wu-Zhang 2019/2020;
Tao 2020 blog post + survey; Rao 2020 simplification.

**Slug:** `03_sunflower`

---

### Problem 4 — Cap Set Problem in F_3^n

**Statement:** What is the maximum size of a subset of F_3^n containing
no 3-term arithmetic progression?

**Why this is in your batch:** Croot-Lev-Pach 2017 (arXiv:1605.01506)
breakthrough using polynomial method gave bound 2.756^n. Ellenberg-Gijswijt
2017 proved 2.756^n is essentially tight. EXACT constant remains open;
this is an ACTIVELY-IMPROVING problem.

**Your task:** survey the polynomial-method approach, attempt to compute
exact maximum cap-set sizes for small n (n ≤ 6 known explicitly; n=7,8,9
are computational frontiers), and document where computational attacks hit
the wall.

**Anchor literature:** Croot-Lev-Pach 2017 (arXiv:1605.01506); Ellenberg-Gijswijt
2017 (Annals); Polymath 19; Behrend's 1946 lower bound; Tao blog post 2017.

**Slug:** `04_cap_set`

---

### Problem 5 — Hadamard Matrix Conjecture

**Statement:** For every positive integer n, there exists a Hadamard
matrix of order 4n.

**Why this is in your batch:** verified for many small n; smallest open
case was 668 (resolved 2005), then 716 (resolved 2014), now the smallest
open n where 4n has no known Hadamard matrix is 668 → updated frontier
keeps moving. Computational + structural attacks coexist.

**Your task:** survey the construction methods (Paley, Williamson, Turyn),
identify which orders 4n have resisted construction longest, attempt to
construct a Hadamard matrix for one specific order via Williamson or
Turyn-type construction (or document the difficulty), and document the
attack surface.

**Anchor literature:** Hadamard 1893; Paley 1933; Williamson 1944; Turyn 1972;
Hadamard Matrix Catalog (Sloane); Kharaghani-Tayfeh-Rezaie 2005 (n=668).

**Slug:** `05_hadamard_matrix`

---

## Why this batch is coherent

All 5 problems are combinatorial extremality / construction problems.
Each has a CURRENT best constant or bound, and each has seen recent
quantitative progress. The kill-data should reveal which proof
techniques (information-theoretic, polynomial method, algebraic
construction, computer search) hit which kinds of walls, and whether
the same wall pattern recurs across the 5.

## When you're done

Report back with: 5 attempt files, paragraph summary of recurring
obstruction classes (particularly: which proof techniques converge to
asymptotic-but-not-tight bounds), any computational wins or surprising
near-extremal constructions found.

— Begin.
