# Deep Research Report #168: Maximum k for k-MOLS at Order n=10

**Target Agent:** Ergon
**Date:** 2026-04-26
**Front:** Combinatorial design (Batch 9 Tier 1)
**Structural region:** orthogonality-of-square-pairs (per `feedback_domains_are_docstrings`; "combinatorial design" is the bibliography label, not the operator)

## 1. Problem Statement

A Latin square of order n is an n × n array on n symbols with each symbol appearing exactly once per row and column. Two Latin squares L_1, L_2 are **orthogonal** if the n^2 ordered pairs (L_1(i,j), L_2(i,j)) are all distinct. A set {L_1, ..., L_k} is k-MOLS if pairwise orthogonal. The trivial upper bound is k ≤ n−1, attained iff a projective plane of order n exists.

State of n=10:
- k=2: known since Bose-Shrikhande-Parker 1960 (refuted Euler's broader conjecture).
- k=3: **OPEN for 65 years.** No 3-MOLS has been exhibited and no impossibility proved.
- k≥4: open; widely believed false (would imply substantial substructure of a projective plane of order 10, ruled out by Lam-Thiel-Swiercz 1989).
- n=10 is the smallest non-prime-power order after the resolved n=6.

The specific falsifiable question for Ergon: **does a 3-MOLS configuration exist at n=10, and if not, what structural property of order-10 Latin squares obstructs orthogonal extension of a 2-MOLS pair?**

## 2. Literature

- **Euler 1782** — 36 officers; conjectured no MOLS pair for n ≡ 2 (mod 4).
- **Tarry 1900** — exhaustive proof n=6 has no MOLS pair.
- **Bose-Shrikhande-Parker 1959-60** — constructed MOLS pairs for all n ≡ 2 (mod 4) with n ≥ 10; killed Euler conjecture.
- **Lam-Thiel-Swiercz 1989** — no projective plane of order 10 (rules out k=9 at n=10, and bounds k ≤ 8 information-theoretically).
- **McKay-Meynert-Myrvold 2007** — main-class enumeration of order-10 Latin squares; established quotient size ~34M main classes.
- **Soicher (2000s+), Kokkala-Östergård 2018+** — SAT/CP attacks on orthogonal-mate completion at small order; no k=3 at n=10 found despite years of CPU.
- **Egan-Wanless 2016** — autotopism / intercalate constraints on extendability.

The 65-year absence of 3-MOLS at n=10 across millions of CPU-hours is itself empirical evidence of non-existence per `feedback_assume_wrong` — but **no proof**, so the question remains live.

## 3. Computational Handle

Total Latin squares of order 10 ~ 7.6 × 10^24 — full enumeration infeasible.

Tractable surface:
- Main-class quotient (row/column/symbol perm + transpose + conjugacy) reduces to ~34M classes.
- Within each main class, 2-MOLS extendability is invariant; orthogonal-mate search is a constraint-propagation problem.
- Encoding 3-MOLS-completion as SAT/CP at fixed L_1 has ~3 × 10^4 boolean variables, solvable per main class in seconds-to-minutes with modern solvers.

The Techne SDP/SAT line per Batch 4 #79 evaluation is directly applicable. **`F:\Prometheus\techne\inventory.json` does not yet contain `TOOL_SAT_SOLVER`** — needs forging (PySAT + Glucose/Kissat wrapper, ~2h Techne work). Symmetry reduction via autotopism group should use `nauty`/`Traces` bindings.

## 4. Test Design

**Step 1 — Canonical enumeration.** Generate main-class representatives of order-10 Latin squares within reach (~10^6-10^7) by streaming the McKay-Meynert-Myrvold catalog or regenerating via `nauty`. Filter to those admitting at least one orthogonal mate (i.e., the 2-MOLS-extendable subset).

**Step 2 — 3-MOLS completion attempt.** For each (L_1, L_2) pair in the 2-MOLS-extendable subset, encode "exists L_3 orthogonal to both" as SAT with unit-propagation on each cell. Time-bound per instance (e.g., 600 CPU-seconds). Record SAT/UNSAT/TIMEOUT.

**Step 3 — Failure-mode clustering.** For each UNSAT instance, extract structural signature: (a) autotopism group order |Aut(L_1)|, (b) intercalate count, (c) transversal count of L_1 (an order-10 Latin square has between 0 and ~5000 transversals), (d) cycle structure of row-permutation orbits.

**Step 4 — Operator extraction.** Cluster signatures into "extendable to k=3" vs "obstructed". Test operator-natural predicates: e.g., does transversal-count modulo small primes separate the classes? Does autotopism-order > k correlate with non-extendability?

## 5. Falsification

Quantitative outcomes (each independently publishable):
- **(a) Discovery of 3-MOLS at n=10** — extraordinary; settles a 65-year open problem. Verification trivial (check 3 pairwise orthogonality conditions on 100 cells each).
- **(b) Structural impossibility lemma** — e.g., "no main class with autotopism order > k or transversal-count < t can extend to 3-MOLS" reduces remaining search by a measurable factor F. Publishable if F > 10.
- **(c) Negative result at scale** — confirmation that no 3-MOLS exists in the searched ~10^7 main-class subset. Concrete empirical reinforcement; sets a new lower bar for any future existence claim.
- **(d) Null sanity** — completion rate at n=9 (k=8 known via GF(9)) and n=11 (k=10 via GF(11)) must hit 100% on the same SAT pipeline; if not, encoding is buggy.

## 6. Budget

- Ergon ~8h: SAT/CP encoding + symmetry-reduction harness (~4h), structural-signature clustering pipeline (~1h), writeup (~1h), Techne handoff for `TOOL_SAT_SOLVER` forge request (~1h), initial result triage (~1h).
- Compute: ~4-12 CPU-hours per 10^5-class subset on Skullport; full ~10^7 sweep is 400-1200 CPU-hours, parallelizable.
- Techne dependency: forge `TOOL_SAT_SOLVER` (PySAT + Kissat) and `TOOL_LATIN_AUTOTOPISM` (nauty wrapper). Queue request via `F:\Prometheus\techne\queue\requests.jsonl`.

## 7. Expected Outcome

The combinatorial-design region of the unified tensor is currently very thin (per `project_silent_islands` — knots, NF, genus-2, fungrim are isolated islands; combinatorial design is even more isolated). Per `feedback_tensor_first`, this brief's empirical results feed directly into that region.

Realistic high-value outcome: **structural narrowing** — a measurable obstruction predicate, contributing the first operator-natural signature distinguishing extendable from non-extendable Latin squares at n=10. This becomes a new column in the structural-region tensor, immediately usable for cross-island bridges (e.g., does autotopism-order obstruction correlate with the symmetry-rank operator already extracted from `project_padic_symmetry_signal`?).

Long-shot: actual 3-MOLS construction. Probability low (Bayesian prior from 65 years of search), but the SAT-completion approach has not been run at the main-class scale Ergon can now attempt, and a single hit is order-of-magnitude.

**Word count: 798**
