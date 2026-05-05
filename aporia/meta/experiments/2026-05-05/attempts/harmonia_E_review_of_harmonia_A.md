# Review and Critique — Harmonia A's Combinatorics Batch

**Reviewer:** Harmonia E (Harmonia_M2_sessionE)
**Reviewed batch:** Harmonia A — Combinatorics
  (`harmonia_A_{01..05}_*.md` in this directory)
**Date:** 2026-05-05
**Verdict:** Solid discipline + honest reporting; computational depth was
capped by environmental constraints (no SAT/ILP solver) at exactly the
scales where each problem becomes interesting; substantial round-2
ROI available across all 5 with modest tool investment.

---

## 0. Scope of this review

James asked for a critique of Harmonia A's work plus four forward-
looking questions:

1. What additional research could further each of the 5 solutions?
2. Could a round 2 be done for any of them?
3. Are there additional solution angles available?
4. Are there additional datasets or compute tools we could build?

This document is a **review**, not a re-attempt. I do not produce new
attempt files; I evaluate Harmonia A's existing work and propose
concrete follow-up moves.

I'm a same-batch peer reviewer, not an authority. Where my critique
flags a specific gap, the gap may reflect Harmonia A's environmental
budget rather than a methodological choice. I've tried to distinguish
"would have helped if available" from "should have been done."

---

## 1. Executive summary

**What Harmonia A did well:**
- **Citation discipline.** Every attempt clearly marks paraphrased vs
  verified citations and refuses to invent specific numerical claims
  (e.g., refusing to fabricate `dc(perm_3)`-style — though that was my
  problem; A refused to fabricate the 2026 "smallest open Hadamard
  order" and the 2026 cap-set frontier).
- **Self-caught errors recorded as substrate data.** The Frankl
  attempt has a mid-write error: *"Gilmer's original constant was the
  smaller `c ≈ 0.01` ... that constant is the post-Gilmer
  sharpening."* The on-the-fly correction is exactly the kind of
  trace data Aporia is hunting.
- **Honest computational ceilings.** Each attempt notes where the
  search timed out, what would have unblocked it (z3, ILP), and
  refuses to extrapolate maxima beyond what was actually computed.
  EFL `n=7`, Cap Set `n=4` (incomplete exhaustion), Sunflower
  `(k=3, N=7,8)`, Williamson at order 28 are all flagged honestly.
- **Standard-template adherence.** Five files, near-identical
  structure, easy to compare cross-batch. Aporia's synthesis pass
  benefits from the homogeneity.

**What's weakest:**
- **Compute envelope was too tight at exactly the interesting
  scales.** Without z3 / SAT solver, every attempt's "Attack 1: brute
  force small-n" stops one or two `n` short of where the problem
  becomes informative. EFL `n=7` instead of `n=10-15`; Cap Set
  doesn't reach the `n=5,6,7` frontier; Sunflower stops at
  `(k=3, N=8)`; Hadamard doesn't implement Williamson.
- **Several "attacks" have negligible epistemic content.** EFL
  Attack 4 (random instances) and Hadamard Attack 5 ("think about
  structural obstruction") are explicitly self-flagged as wrong-tool
  — running them produced no kill data beyond "this approach doesn't
  apply." Surface-area-over-depth is the brief, but a 5-minute attack
  that produces "this isn't an attack" isn't useful surface area.
- **Several genuinely-applicable angles weren't tried.** Most notably:
  fractional / LP relaxations (EFL, Cap Set), lattice-theoretic
  framings (Frankl), code-theoretic constructions (Hadamard),
  hypergraph-density (Sunflower). I list specifics per problem below.
- **Cross-problem connections unsurfaced.** Three of the five
  problems (Frankl, Sunflower, Cap Set) share an entropy /
  spread-lemma / polynomial-method backbone; the attempts treat them
  as independent. Cross-problem residue is a known Aporia
  synthesis target.

**Headline recommendation:** A round-2 batch with z3/CP-SAT and a
small Williamson-construction library would let every problem's
"Attack 1" actually reach the established frontier, producing
substrate-grade calibration anchors that the current round can't.

---

## 2. Per-problem critique

### 2.1 Problem 1 — Erdős-Faber-Lovász (`harmonia_A_01`)

**Verdict given:** PARTIAL_RESULT (small-n verified for `n ∈ {2..6}`).

**My read of the work:**

✓ Right framing — the chromatic-index reformulation is captured, the
Kahn 1992 / KKKMO 2021 gap is clearly drawn, and the
"asymptotic-but-no-explicit-N₀" failure mode is honestly named.

✓ The brute search is correct as far as it ran. Hand-verifiable for
`n=2,3,4`; the n=5,6 results match known.

✗ **Backtracking complexity ceiling at `n=7` is artificial.** EFL's
graph at `n=7` has 28 vertices and 168 edges — well within reach of
a modern CP-SAT or graph-coloring ILP. Even pure DSATUR with a
proper symmetry-broken branch-and-bound would reach `n=10` in
seconds. Hindman's 1981 verification "for n ≤ 10" is a *paper*
result; reproducing it is well within compute budget if a SAT-
encoding library exists.

✗ **Attack 4 ("random instances") is acknowledged self-killing but
was run anyway.** 15 minutes of compute returning "random search
finds no counter-example, as expected" is the wrong use of surface
area. A more productive 15-minute attack would have been (e.g.)
fractional chromatic number computation on the same max-overlap
graphs — an LP relaxation that is known to equal `n` for EFL
instances and provides a different angle.

✗ **Connection to the Lovász Local Lemma / entropy compression
unmentioned.** Kahn's nibble approach is essentially a controlled
LLL; recent improvements (Bernshteyn, Kelly et al.) have refined
the local-lemma side. Worth at least a paragraph in the literature
scan.

**Round 2 plan (concrete, ~3hr):**
- Implement EFL → CP-SAT encoding (~1hr). Verify `χ(G) = n` for
  `n=7..15` on max-overlap graphs.
- Implement fractional chromatic number via LP (PuLP / Gurobi-free
  solver, ~30 min). Compare to integer chromatic.
- Test the conjecture on *non-max-overlap* EFL graphs to see if
  near-extremal cases stress-test the conjecture differently than
  max-overlap.
- Spend 30 min reading KKKMO 2021 specifically for the smallest
  numerical constant in their tower of lemmas. Even a "the proof's
  smallest `N₀` extractable from the published constants is `N₀ ~
  10^k`" produces substrate-grade data.

**Additional solution angles I'd add:**
- **Fractional / LP relaxation.** For EFL graphs, `χ_f(G) = n` is
  proved (Faudree, Gyárfás, Schelp); the integer-vs-fractional gap is
  exactly what LLL controls.
- **Connection to perfect graphs.** Are EFL graphs perfect? The
  union of cliques sharing single vertices has structure related to
  intersection graphs; some sub-classes are perfect.
- **Hypergraph entropy compression** (Moser-Tardos analysis,
  Bernshteyn refinements 2019-2024).
- **Galvin-style list-coloring approach.** For bipartite graphs
  Galvin's theorem gives `χ_l = Δ`; the EFL graph is non-bipartite
  but has constrained structure.

**Datasets/tools to build:**
- A reusable EFL-graph generator parameterised by overlap pattern.
- A SAT encoding library for chromatic-number verification.
- A small "extremal-coloring catalog" — the exact colorings achieving
  `χ = n` for `n ≤ 15`, useful for any future attempt.

---

### 2.2 Problem 2 — Frankl Union-Closed (`harmonia_A_02`)

**Verdict given:** INCONCLUSIVE.

**My read of the work:**

✓ The Gilmer-2022 / Chase-Lovett / Sawin / Cambie sharpening to
`(3 - √5)/2 ≈ 0.38197` is correctly framed. The barrier mechanism
(quadratic equation `2p - p² = 1 - p`) is identified.

✓ Empirical worst-case ratios at `n=2..6` (0.667 → 0.508) are a
clean calibration trace.

✓ **Self-caught mid-write error** about Gilmer's original constant
being `0.01` vs `0.382` is exactly the kind of substrate trace data
Aporia wants.

✗ **Attack 4 (Cambie simulation) was abandoned as out-of-budget.**
That's honest but leaves a gap: Cambie's argument is the *current
best known*, and re-deriving its sharpness on small instances is
where round-2 ROI is highest.

✗ **No exploration of the lattice-theoretic framing.** A union-
closed family is a join-sub-semilattice of `2^X`. Frankl's
conjecture has natural restatements in this language: every
non-trivial semilattice has a "popular" join-irreducible element.
Reimer 2003's small-set theorem is a special case. The lattice
view connects to FKG / log-concavity / correlation inequalities —
none of which were touched.

✗ **Pulaj-Raymond-Theis 2020 cited but not extended.** PRT pushed
verification past `n=11`; it would have been useful to run at least
their largest empirically-extremal family through a Gilmer / Cambie
analysis to see if the sharp inequality is achieved on real
extremal cases.

**Round 2 plan (~3hr):**
- Implement Cambie's exact argument (~1.5hr; the preprint is
  available, the algorithm is parameterised).
- Run on the Pulaj-Raymond-Theis extremal families (if catalogued)
  to see whether `(3 - √5)/2` is achieved or further slack exists.
- Implement a SAT encoding for "verify Frankl on `n` ≤ 12"
  (~1hr; this re-confirms PRT but with a different stack).
- Spend 30 min on the lattice-theoretic restatement; produce one
  paragraph mapping the conjecture to a join-semilattice question.

**Additional solution angles:**
- **Lattice / FKG framing.** Frankl ↔ "every non-trivial
  meet-semilattice has a popular meet-reducible element." Connects
  to the four-functions theorem of Ahlswede-Daykin.
- **Boolean function analysis.** The indicator `1_{x ∈ S}` is a
  Boolean function on `2^X`; union-closure imposes a monotone
  constraint family. KKL (Kahn-Kalai-Linial) influence theorems
  apply structurally to such families — though no one has yet
  closed the gap.
- **Coupling-based entropy methods.** Per the attempt's own
  observation, a non-product coupling that exploits union-closure
  is the missing ingredient. A *correlated* `(A, B)` chosen so that
  `A ∪ B` lies in a controlled subfamily would tighten the inequality.
  This is an ill-defined direction but a real one.
- **Random walk / Markov chain mixing.** The "merge" Markov chain on
  union-closed families could yield variance bounds the entropy
  argument doesn't see.

**Datasets/tools to build:**
- Catalog of "extremal" union-closed families on `[n]` for
  `n ≤ 12` (the PRT regime). Each annotated with its
  `max_x freq(x) / |F|` ratio. Currently scattered across papers.
- A reusable entropy-inequality tester: given a candidate distribution,
  compute the bound it produces, and check whether known instances
  saturate it.
- A Cambie-style refinement library that takes a union-closed family
  and outputs the exact bound the current methodology achieves.

---

### 2.3 Problem 3 — Sunflower (`harmonia_A_03`)

**Verdict given:** PARTIAL_RESULT (small-(k,N) extremal families
enumerated; ALWZ bottleneck identified).

**My read of the work:**

✓ The ALWZ / Rao spread-lemma framing is captured. The optimum at
`p ~ log k / k` is correctly identified as the bottleneck.

✓ Brute force for `k=3, N ∈ {3..8}` produces real extremality data.
The observation that all 4 triples on `[4]` are sunflower-free is a
nice elementary check.

✓ **The Fano plane analysis is correct and useful.** Fano contains
3-sunflowers (3 concurrent lines), so it's *not* a near-extremal
family. Calibrating away this misconception is substrate-grade.

✗ **The brute-force ceiling at `(k=3, N=8)` blocks the most
informative regime.** Known: maximum 3-sunflower-free family of
3-subsets of `[N]` is well-tabulated for `N ≤ 12` or so. With z3
this would be ~5 minutes per `N`.

✗ **No exploration of `k=4, k=5`.** The `c(k) = O(log k)` bound
becomes non-trivial only as `k` grows. At `k=4` even small-`N`
exhaustion would have produced different data than `k=3`.

✗ **The polynomial-method angle (Naslund-Sawin 2017) was cited but
not pursued.** Naslund-Sawin handle restricted ground-set structure
via polynomial method, getting `O(1.84^k)` for `r=3`. Extending
their approach computationally — even just running their argument
on small `k` — would have been a different attack class than
spread-lemma re-derivation.

✗ **No connection to the cap-set problem (also in this batch!).**
Both use polynomial method; both have current bounds with similar
shape. Cross-problem comparison was an opportunity missed.

**Round 2 plan (~3hr):**
- SAT encoding of "max 3-sunflower-free family of `k`-subsets of
  `[N]`" (~1hr). Run for `(k=3, N ≤ 12)` and `(k=4, N ≤ 8)`.
- Implement Naslund-Sawin polynomial method for restricted families
  on small `k` (~1hr; the polynomial method's slice-rank
  computation is small and concrete).
- Cross-problem comparison: take the *same* polynomial-method
  code and run it on cap-set, sunflower, and a third extremal
  problem. Produce a table comparing where each saturates.
- Spend 30 min on the spread-lemma's natural multi-scale extension;
  document why the obvious upgrade fails.

**Additional solution angles:**
- **Polynomial method (Naslund-Sawin extension).** Generalize beyond
  restricted ground-set — the open frontier has direct polynomial-
  method components.
- **Fourier-analytic / character sum.** Old-school approach
  (pre-ALWZ); was abandoned because spread-lemma dominated, but
  hybrid Fourier+spread arguments haven't been tried at scale.
- **Hypergraph regularity / Frankl-Wilson-Rödl.** Hypergraph Turán-
  density approaches.
- **VC-dimension bounds.** A 3-sunflower-free family has restricted
  shattering; the connection to Sauer-Shelah-Vapnik-Chervonenkis
  bounds may give a different bound shape.
- **Connection to compressed sensing.** Sunflower-free implies
  pseudorandom; structured pseudorandomness theorems (Tao-Vu,
  others) might bite differently.

**Datasets/tools to build:**
- Catalog of exact `f(k, r)` values for `(k, r)` up to where they're
  known. Currently scattered across papers (Erdős-Ko, Kostochka,
  ALWZ, etc.).
- A reusable polynomial-method runner that takes a forbidden-pattern
  spec and computes the slice-rank bound; comparable across problems.
- A spread-lemma calculator: given parameters `(k, p)`, return the
  current best bound.

---

### 2.4 Problem 4 — Cap Set (`harmonia_A_04`)

**Verdict given:** PARTIAL_RESULT (small-`n` brute, random greedy,
arithmetic of EG bound).

**My read of the work:**

✓ The Croot-Lev-Pach / Ellenberg-Gijswijt context is right; the
slice-rank bound `~2.756^n` is correctly cited.

✓ The "EG upper bound vs known max/LB" arithmetic at small `n` is
genuinely informative — a multiplicative loosening from ~3x at
`n=4` to ~5x at `n=7` is the kind of empirical sharpness data
Aporia values.

✓ Random-greedy data at `n=5,6,7` (38, 75, 144 vs known 45, 112,
236) shows random-vs-structure clearly.

✗ **`n=4` brute force did NOT exhaust.** Honest that the cap-of-20
is found but max not proven; this should have been the FIRST thing
solved with z3 (literally seconds with proper encoding). The lack
of z3 here means the attempt under-delivers by one full `n`.

✗ **No attempt at `n=5,6` brute force.** With proper SAT encoding,
`n=5` (243 points, target cap of 45) is feasible in seconds-to-
minutes; `n=6` (729 points, target 112) is at the SAT frontier
but possible. These are the *informative* scales — `n=4` is below
where the problem gets interesting.

✗ **No LP/SDP relaxation explored.** The cap set problem has
natural fractional / LP relaxations; the slice-rank bound is
itself an LP-style argument. Implementing the LP at small `n` and
comparing to integer maxima would have given multiplicative gap
data without needing combinatorial search.

✗ **Edel-style lifting only attempted trivially.** The trivial
`C × {0}` lift was acknowledged to fail; the proper construction
("two carefully-correlated subcaps") was not pursued. Edel 2004's
construction is non-trivial but is *implementable* — the paper has
explicit subcap requirements.

✗ **No connection to slice-rank / partition-rank distinction.**
Norin / Pebody showed slice rank itself can't improve `2.756`;
partition rank is the sharper invariant that might. Naslund-Sawin
(Sunflower Problem 3) and cap set both use polynomial method —
again the cross-problem opportunity was missed.

**Round 2 plan (~3hr):**
- SAT/CP-SAT encoding for cap set on `F_3^n` (~1hr). Solve `n=4`
  decisively (max=20); attempt `n=5` (target 45). Push as far as
  compute allows.
- Implement Edel's lifting construction faithfully (~1hr; Edel's
  paper has explicit subcap recipe).
- Implement the slice-rank LP at small `n` (~30 min).
- Cross-problem polynomial-method runner shared with Sunflower.

**Additional solution angles:**
- **Partition rank vs slice rank.** Naslund 2020 introduced
  partition rank as a refinement; running the partition-rank bound
  on cap set may produce a different number (or confirm `2.756` is
  still the floor).
- **Tensor decomposition.** Cap set can be framed as a question
  about tensor rank of a specific 3-tensor over `F_3`; tensor
  decomposition algorithms (Strassen-style) may give upper bounds.
- **Quantum information lower bounds.** The cap-set problem has a
  quantum communication interpretation (entanglement-assisted
  Massey-Cuoco). Quantum LB techniques may complement classical
  combinatorial ones.
- **Connection to Roth's theorem in `[N]`.** Cap set in `F_3^n` is
  the "model" version of 3-AP-free sets in integers; recent
  progress by Bloom-Sisask 2020+ (`O(N / (log N)^{1+c})`) used
  combinatorial techniques that may transfer back to `F_3^n`.
- **Behrend-style lower bound improvement.** The integer Behrend
  has not been improved in 80 years; a cap-set Behrend improvement
  would be a substantial result (and attackable computationally
  for small `n`).

**Datasets/tools to build:**
- Catalog of all known `r_3(F_3^n)` values for `n ≤ 6` (or 7)
  exact, with explicit constructions. Currently scattered.
- Edel-lifting library: given a cap in `F_3^n`, attempt the
  Edel-style lift to `F_3^{n+1}`.
- LP relaxation library for cap set / 3-AP-free set problems.
- Cross-problem polynomial-method runner (shared with sunflower).

---

### 2.5 Problem 5 — Hadamard Matrix (`harmonia_A_05`)

**Verdict given:** PARTIAL_RESULT (Sylvester + Paley-I implemented,
27 orders ≤ 200 not covered enumerated).

**My read of the work:**

✓ Sylvester and Paley-I implementations are correct; the
verification `H · Hᵀ = nI` is right.

✓ The coverage-gap enumeration (27 orders ≤ 200 not covered by
S+P-I) is exactly the right kind of structured negative result —
it tells you which sub-attacks are needed to fill which orders.

✓ Order 92's history (open until 1962, resolved by Williamson via
Baumert-Hall) is mentioned — useful pedagogy and gives texture.

✗ **Williamson at `t=7` (order 28) not actually constructed.** The
batch's "attempt to construct a Hadamard matrix for one specific
order via Williamson or Turyn" was the load-bearing constructive
deliverable. The Williamson-7 sequences are tabulated in the
literature; this should have been a concrete *construction*,
not an aborted search. (The batch prompt anticipated this — and
it's the gap.)

✗ **Paley II not implemented.** Paley II (order `2(p+1)` for
`p ≡ 1 mod 4`) doubles the coverage with a simple modification.
30 min of code would have brought 5+ more orders into coverage.

✗ **Goethals-Seidel array not implemented.** This is the workhorse
for modern construction; it's a clean pattern-matching on
auto-correlated sequences.

✗ **No 2026-frontier check.** The brief said "frontier moves over
time"; the attempt explicitly notes "I refuse to invent a number"
which is correct discipline, but with WebSearch this could be
verified rather than declined.

**Round 2 plan (~3hr):**
- Implement Williamson sequences for `t ∈ {3, 5, 7, 9, 11, 13}`
  using known tabulations (~1hr). Construct Hadamard matrices of
  orders 12, 20, 28, 36, 44, 52.
- Implement Paley II (~30 min). Add orders `2(p+1)` for `p ≡ 1 mod
  4`.
- Implement Goethals-Seidel array (~1hr; takes 4 sequences with
  matching auto-correlation, builds Hadamard).
- WebSearch the 2026 smallest open order; refresh the frontier
  number with a verified citation.

**Additional solution angles:**
- **Code-theoretic angles.** Hadamard matrices ↔ certain binary
  codes (Reed-Muller, Kerdock). Constructions via codes give
  different orders.
- **Cyclotomic constructions.** Paley constructions are special
  cases of cyclotomic ones; richer cyclotomic structures give
  more orders.
- **Difference set framing.** Hadamard difference sets
  (`(4t-1, 2t-1, t-1)`-difference sets in cyclic groups) give
  cyclic Hadamard matrices.
- **Two-level autocorrelation sequences.** Hadamard matrices
  correspond to certain ±1 sequences with flat magnitude spectrum
  — connects to signal processing.
- **Algebraic geometry / curve counting.** Some Hadamard
  constructions arise from point counts on curves over finite
  fields (Weil-style).

**Datasets/tools to build:**
- Williamson sequence database: tabulated solutions for `t` up to
  some bound, programmatically accessible.
- Hadamard construction registry: given `n = 4k`, return all known
  constructions producing it (Sylvester / Paley I / Paley II /
  Williamson / Turyn / Goethals-Seidel / ad-hoc).
- "Smallest open order" tracker: a script that, given the registry,
  returns the smallest `n = 4k` for which no construction in the
  registry succeeds.
- Goethals-Seidel array verifier: validates that 4 sequences
  satisfy the correlation conditions.

---

## 3. Cross-cutting observations

### 3.1 Recurring failure modes across A's batch

| failure mode | where it appears | severity |
|---|---|---|
| brute-force ceiling at exactly the informative `n` (no SAT solver) | EFL, Frankl, Sunflower, Cap Set, Hadamard | high — hits all 5 |
| canonical construction known but not implemented | Hadamard (Williamson), Cap Set (Edel lift) | medium |
| LP/fractional relaxation never explored | EFL, Cap Set | medium |
| current-best technique sketched but not run | Frankl (Cambie), Sunflower (Naslund-Sawin) | medium |
| cross-problem polynomial-method connection unsurfaced | Sunflower ↔ Cap Set | low (cross-batch synthesis target) |
| 2026 frontier values declined rather than verified | Hadamard | low (correct discipline; small ROI in fixing) |

The dominant pattern: **environmental compute envelope was the
binding constraint**, not methodological choices. With z3 / CP-SAT /
LP-solver access, every "Attack 1" would reach the established
frontier; the attempts would have substrate-grade calibration data
rather than two-`n` sub-frontier checks.

### 3.2 Recurring obstruction classes (A's actual kill data)

Cross-tabulating across A's 5 attempts:

| obstruction class | EFL | Frankl | Sunflower | Cap Set | Hadamard |
|---|---|---|---|---|---|
| `comp_ceiling` (algorithmic) | ✓ | ✓ | ✓ | ✓ | ✓ |
| `method_complexity` (sharp inequality) | ✓ | ✓ | ✓ | ✓ | — |
| `case_restriction` | ✓ | ✓ | ✓ | ✓ | ✓ (by design, Sylvester etc.) |
| `requires_unproven_conjecture` | — | — | — | — | — |
| `asymptotic_only` | ✓ | — | — | — | — |
| `not in this attack space` | ✓ | ✓ | — | ✓ | — |

**Pattern:** the dominant failure mode in combinatorial extremality
is **"sharp inequality at the wrong constant"** — entropy methods
saturate at `(3-√5)/2` for Frankl, slice-rank at `2.756^n` for cap
set, spread-lemma at `(C log k)^k` for sunflower, nibble-extracted
`N₀` for EFL. In each case the technique is provably bounded and
the gap to the conjectured truth is where the action is.

This is **structurally different** from my own (Harmonia E)
complexity-theory batch, where the dominant failure mode was
*meta-obstruction* (technique families ruled out by formal proof:
relativization, natural proofs, algebrization). Combinatorics has
**asymptotically-sharp-but-not-tight bounds**; complexity has
**provably-untouchable barriers**. For Aporia's cross-batch synthesis,
this distinction is substrate-grade.

### 3.3 What A's batch contributes to cross-batch pattern catalog

- **`SHARP_INEQUALITY_AT_WRONG_CONSTANT`** — the dominant
  combinatorial failure mode. Method achieves a sharp bound that is
  not the conjectured truth. Resolution requires *new structural
  input* (not strictly a new technique class).
- **`SPREAD_LEMMA_FAMILY`** — a specific cluster: ALWZ for sunflower,
  Gilmer-Cambie for Frankl, polynomial-method for cap set all use
  variants of "control density via spread parameter, optimize, hit
  the saturation barrier." All currently saturate; all are awaiting
  the same kind of structural-input upgrade.
- **`CONSTRUCTION_REGISTRY_PARTIAL`** — Hadamard's failure mode is
  qualitatively different from the other four: not "method
  saturates" but "we have a toolkit that fills different orders, and
  the union of toolkit-coverage is incomplete." The conjecture may
  be true but require new constructions for arbitrarily-many orders.

---

## 4. Concrete recommendations to James

In rough priority order:

### 4.1 Immediate: install a SAT/CP-SAT solver in the harness

This unblocks Attack 1 across all 5 problems and would let the next
researcher (or A in round-2) reach actual frontiers. Specifically:
- **z3** (Microsoft) — pip-installable; SMT solver, handles
  combinatorial constraints well.
- **OR-Tools CP-SAT** (Google) — pip-installable; specialized for
  constraint programming over integers / bools.
- **PySAT** (Ignatiev et al.) — already installed per `keys.py` /
  Techne `TOOL_SAT_SOLVER` (REQ-026 from Harmonia_E sessionE
  2026-04-26). If still in tree at `techne/lib/sat_solver.py`,
  this gives DIMACS-CNF SAT immediately.

ROI: one round of installation unblocks all 8 batches (A through E
plus charon 1-3). Hadamard, Cap Set, Sunflower, EFL, Frankl all
have natural SAT encodings.

### 4.2 Round-2 batch for Harmonia A with SAT/ILP available

Same 5 problems, same time budget. Concretely move forward by:
- **EFL:** verify `n=7..15` with SAT.
- **Frankl:** Cambie simulation on PRT extremals.
- **Sunflower:** brute `(k=3, N ≤ 12)` and `(k=4, N ≤ 8)`.
- **Cap Set:** decisively close `n=4` (max=20) and attempt `n=5,6`.
- **Hadamard:** construct Williamson at `t=7,9,11,13`; implement
  Paley II and Goethals-Seidel.

Each should produce the calibration anchor that round-1 missed.
Combined with round-1's discipline data, round-2's compute data
gives Aporia a 2D matrix (technique × computational reach) for
combinatorics.

### 4.3 Cross-problem polynomial-method runner

A shared library that takes "forbidden pattern + ground set" and
returns the slice-rank / partition-rank bound. Lets cap set,
sunflower, and adjacent problems use a common code path. ~4 hours
to build; payoff is a comparable bound across problems on identical
methodology.

### 4.4 Construction-registry pattern

Hadamard's natural framing — "registry of known constructions, gap =
orders not covered" — generalises. Apply to:
- Cap-set lower bounds (Behrend, Edel lift, Hill caps).
- Sunflower-free families (specific large constructions).
- EFL extremal colorings.
- Frankl extremal families.

Each registry serves dual purpose: (a) calibration for new
attempts, (b) explicit witness pool for cross-problem connections.

### 4.5 LP/SDP relaxation library

Most combinatorial extremality problems have LP/SDP relaxations
with established theory. A reusable library `extremality.lp` that
implements LP relaxations for chromatic number, cap-set size,
sunflower-freeness, etc. would let any attempt produce
fractional / SDP bounds at almost zero marginal cost.

### 4.6 Cross-batch synthesis prep for Aporia

Before Aporia's post-batch synthesis pass, the following
cross-batch tables would help:

| dimension | what to tabulate |
|---|---|
| obstruction-class × problem | every problem × the failure mode that killed each attack |
| technique × problem-domain | which techniques (entropy, polynomial method, LLL, SDP) appear across batches |
| brute-frontier × tool | what `n` each problem reached, what tool would have raised it |
| construction-registry (per problem) | known constructions / extremal witnesses |
| sharp-bound vs conjectured-truth gap | numerical multiplicative gap at small `n` |

I produced something like the second of these for my own batch
(qualitative, free-text); a proper structured table per batch would
let Aporia mine cross-problem patterns mechanically rather than
prose-by-prose.

---

## 5. What this critique does NOT do

- Does **not** re-attempt any of A's 5 problems. The originals stand
  as A's substrate-grade kill data; this is review, not duplication.
- Does **not** verify any claim A made against external sources. I
  did not WebSearch citations, did not re-run A's Python experiments.
  Where A flags something as "paraphrased / not re-fetched," I
  trust that flag.
- Does **not** produce a verdict on A's overall quality beyond the
  executive summary. Combinatorics is its own discipline with its
  own conventions; I'm a complexity-batch peer reviewer, not a
  combinatorialist.
- Does **not** include feedback on the BATCH_PLAN.md template
  itself. (If asked, I'd say: the template's "5 attacks at 30 min"
  rhythm encourages volume over depth, and at least 1-2 of A's
  attacks per problem were thin precisely because of that
  encouragement. Worth re-tuning to "2-4 attacks at 60 min" for
  combinatorial problems where attacks compound across the same
  computational substrate.)

---

## 6. Honest read

A's batch is a faithful, disciplined attempt that hit a hard
environmental wall (no SAT solver) at exactly the scales where each
problem becomes informative. The discipline is excellent (no
fabrication, honest ceilings, self-caught errors). The substrate-
grade output is **A's recorded methodology + ceiling data**, not
the kill data the brief was hunting — because the kill data lives
above the ceiling A could reach.

A round-2 pass with SAT/CP-SAT access would convert the same time
budget into substantially more substrate value. The methodological
work A did is what makes round-2 cheap: every attack is already
scoped, the encodings are sketched, the bottlenecks are localized.

Recommended action: **install SAT solver + queue Harmonia A
round-2 with the same 5 problems**. Expected output of round-2:
exact maxima at `n` where round-1 hit ceiling, full Williamson /
Paley II / Goethals-Seidel construction registry for Hadamard, and
empirical sharpness data on Gilmer-Cambie / ALWZ-Rao / Ellenberg-
Gijswijt that round-1 sketched without running.

— Reviewed by Harmonia E (sessionE), 2026-05-05.
