# Attempt — Erdős-Faber-Lovász Conjecture

**Researcher:** Harmonia A
**Date:** 2026-05-05
**Time spent:** ~2.5h (lit recall, code, runs, writeup)
**Verdict:** PARTIAL_RESULT (small-n verified by direct chromatic search; gap to "complete coverage" not closed because the asymptotic proof gives no explicit threshold)

## Problem statement

Let `G` be the union of `n` complete graphs `K_1, ..., K_n`, each on
`n` vertices, with the property that any two of these cliques share at
most one vertex. The **Erdős-Faber-Lovász (EFL) conjecture** (1972)
states that the chromatic number of `G` satisfies `χ(G) = n`.

Equivalently (and historically more commonly stated): every linear
hypergraph with `n` edges on `n` vertices has chromatic index `n`. The
graph form above is the line-graph reformulation.

The lower bound `χ(G) ≥ n` is immediate: any single `K_n` requires `n`
colors. The conjecture is the matching upper bound.

## Literature scan: prior attempts

1. **Erdős, Faber, Lovász (1972)** — original conjecture, posed at a
   conference. Erdős offered a $500 prize. Cited in batch prompt.
2. **Hindman (1981)** "On a conjecture of Erdős, Faber, and Lovász
   about n-colorings", Canad. J. Math. — verified the conjecture for
   `n ≤ 10` by ad-hoc combinatorial reasoning. Cited in batch prompt
   (paraphrased — exact bound on `n` cited from memory; Hindman's
   paper is real but I have not re-fetched the precise threshold for
   this writeup).
3. **Klein, Margraf (2005)** — incremental improvements on small-`n`
   cases. Cited in batch prompt; details not verified here.
4. **Kahn (1992)** "Coloring nearly-disjoint hypergraphs with `n + o(n)`
   colors", J. Combin. Theory Ser. A — proved a *weakening* with
   `χ(G) ≤ n + o(n)`. The leading constant `1` is what EFL claims; Kahn
   proves it asymptotically but with an additive error.
5. **Romero, Sánchez Arroyo (2007), survey** — comprehensive treatment
   of bounds and related conjectures (paraphrase; I have not refetched
   to verify the exact citation).
6. **Kang, Kelly, Kühn, Methuku, Osthus (2021)**, arXiv:2101.04698 —
   proved EFL for all sufficiently large `n`. Headline of the program;
   the gap is that "sufficiently large" is not explicit.

The KKKMO 2021 result is the dominant prior. Its method is absorbing /
nibble + iterative refinement of partial colorings — a high-tech
extension of Kahn-style probabilistic colouring. The proof gives
`χ(G) = n` for `n ≥ N_0` for some unspecified large `N_0`. Closing the
small-`n` gap therefore reduces to:
  - either extracting an explicit `N_0` from the proof (which the
    authors note in their paper they do not pursue);
  - or computational verification up to whatever threshold suffices.

## Attack surfaces tried (this attempt)

### Attack 1: direct chromatic-number computation for small `n`

- **Approach:** Construct the "maximum-overlap" EFL graph for each `n`:
  every pair of cliques shares exactly one vertex. This minimises
  vertex count (`n + C(n,2)` vertices) and maximises edge density,
  giving the *hardest* instance in some senses (more shared structure
  → more coupling between clique colourings). Compute `χ(G)` exactly
  via backtracking with symmetry-breaking on first-color use.
- **Tools:** Python, networkx, custom backtracking; DSATUR greedy as
  upper bound.
- **Time:** ~30 min including code.
- **Result:** verified `χ(G) = n` for `n ∈ {2, 3, 4, 5, 6}` on the
  max-overlap instance. DSATUR greedy gave the optimum for
  `n ∈ {2, 3, 4, 6}` and was off by 1 (returned 6 when χ=5) for `n=5`.

  | `n` | `|V|` | `|E|` | `χ(G)` | DSATUR upper bound |
  |---:|---:|---:|---:|---:|
  | 2 | 3 | 2 | 2 | 2 |
  | 3 | 6 | 9 | 3 | 3 |
  | 4 | 10 | 24 | 4 | 4 |
  | 5 | 15 | 50 | 5 | 6 |
  | 6 | 21 | 90 | 6 | 6 |

- **Why it stalled (extending to `n=7`):** the backtracking search blew
  up on `n=7` (28 vertices, 168 edges) within my budget. Better
  encoding (via SAT or ILP) would handle this comfortably but I lack
  a SAT solver in environment (z3 not installed).
- **Kill_path classification:** N/A — attack succeeded for the chosen
  range. Failure to reach `n=7` is `comp_ceiling` (search algorithm
  too naive), not a substantive obstruction.
- **Distance to closure:** small-`n` verification is *not* what closes
  the conjecture; closure requires either an explicit bound `N_0` from
  KKKMO + small-`n` exhaust up to `N_0`, or a structural proof. My
  attack confirms what is already known (Hindman-style). It is at
  best calibration that my code is right.

### Attack 2: structural reduction to "linear hypergraph chromatic index"

- **Approach:** EFL is equivalent to: every linear `n`-uniform
  hypergraph with `n` edges has chromatic index ≤ `n`. (Linear =
  pairwise edge intersection ≤ 1.) Try to attack the chromatic-index
  formulation directly — does König-type matching theory bite?
- **Tools:** paper / pen / mental.
- **Time:** ~30 min.
- **Result:** the chromatic-index formulation makes the lower bound
  obvious (each vertex of degree `d` needs ≥ `d` colors at edges
  incident to it; max degree is at most `n`). The upper bound `n` is
  what's hard. König's theorem gives χ' = Δ for bipartite multigraphs;
  this is not bipartite in general. Vizing-type bounds give `χ' ≤ Δ + 1`
  but not the integer = Δ in our setting.
- **Why it stalled:** the chromatic-index reformulation is not new —
  this *is* how Kahn 1992 attacked it, and his argument needed a fully
  probabilistic (nibble + concentration) machinery to close the
  asymptotic gap. There is no clean structural reduction available
  here that I can see; the difficulty is genuinely combinatorial.
- **Kill_path classification:** `requires_unproven_conjecture` is the
  wrong tag — this is not gated on a deeper conjecture. Better tag:
  `method_complexity` — known clean tools (König, Vizing, list-coloring
  via Galvin) don't directly give χ' = Δ here, so the route requires
  more delicate machinery.
- **Distance to closure:** "wrong tool entirely" — anything but the
  probabilistic / nibble approach is unlikely to bite, and that
  approach does close it (asymptotically) per KKKMO.

### Attack 3: extract or estimate the implicit `N_0` from KKKMO's proof

- **Approach:** read KKKMO 2021 with an eye for the smallest constant
  in their tower-of-lemmas. Each "sufficiently large" step compounds.
  Estimate `N_0` from the looseness of constants.
- **Tools:** abstract recall of nibble-style proofs; I do **not** have
  the paper open in this session and I will not invent numbers.
- **Time:** ~10 min thought.
- **Result:** I cannot give a number without re-reading the paper.
  Nibble-style proofs commonly compound to `N_0` at the level of
  10^{(10^k)} for small `k` — high enough that direct verification is
  impossible; low enough that "compute up to `N_0`" is not a closure
  path even in principle.
- **Why it stalled:** I refused to invent a value. The output of this
  attack is the honest negative: extracting `N_0` is doable in
  principle but is a paper-reading effort, not a search effort, and
  in a small-time budget the expected `N_0` is computationally
  unreachable anyway.
- **Kill_path classification:** `asymptotic_only` — the proof is
  asymptotic by design and explicifying `N_0` does not close the gap
  to "complete coverage" because the resulting threshold is
  computationally inaccessible.
- **Distance to closure:** complete coverage via this route is "not
  in this attack space at all" — explicifying `N_0` extracted from a
  nibble proof yields a `N_0` so large that exhaustive verification
  remains hopeless. Closure requires a different (presumably
  algebraic / structural) argument.

### Attack 4: random instances → sanity-check the worst case

- **Approach:** randomly perturb the max-overlap EFL graph (drop edges,
  add isolated cliques, vary the intersection pattern), compute χ, see
  if any instance has χ > n.
- **Tools:** Python, networkx.
- **Time:** ~15 min.
- **Result:** all 50 random EFL-compatible instances I generated for
  `n ∈ {3, 4, 5}` had χ ∈ {n - 1, n} depending on whether all `n`
  cliques are "active" (some random instances reduce to a smaller `n'`
  if some cliques become absorbable into others). No instance I
  produced violated the conjecture. (This is calibration, not
  evidence, since 50 random instances is nothing on the scale of
  EFL's combinatorial space.)
- **Why it stalled:** random sampling cannot find a *worst case* in a
  domain whose conjectured bound is sharp at the maximum-overlap
  configuration. Sampling around max-overlap also produced no
  violation, again as expected.
- **Kill_path classification:** `comp_ceiling` if read as "looking
  for a counter-example"; more accurately, `not in this attack space`
  — random search is not a useful tool for attacking EFL.
- **Distance to closure:** "wrong tool entirely."

## Partial results obtained

- `χ(G) = n` confirmed by direct chromatic search on max-overlap EFL
  graphs for `n ∈ {2, 3, 4, 5, 6}`.
- DSATUR greedy is loose by 1 at `n = 5` and tight at `n ∈ {2, 3, 4, 6}`
  on max-overlap instances. (Anecdotal; not a useful general fact.)
- Confirmed (by re-derivation) that the chromatic-index reformulation
  makes the conjecture equivalent to `χ'(H) = Δ(H)` for the linear
  `n`-uniform `n`-edge hypergraph derived from `G`.

## Honest "what would unblock this"

Two distinct unblockings:
1. **For an explicit `N_0`**, the right move is a careful audit of
   KKKMO 2021 to track the worst constant through their nibble +
   absorbing iterations. Output: a numerical `N_0` (almost certainly
   far too large to verify computationally, but explicit).
2. **For full closure (small-`n` verified up to wherever needed)**, an
   exact-coloring oracle — say, a high-performance SAT/ILP encoding
   that handles `n ≤ ~30` or so — would let a determined effort push
   the verified range up. Combined with (1), if `N_0` from the proof
   were ever pushed below such a verified range, the conjecture would
   close. As of 2026 this gap is enormous.

A genuine novel attack would be a structural argument that bypasses
the probabilistic machinery — for instance, an algebraic invariant of
linear hypergraphs that forces a perfect matching of "color classes"
to cliques. None such is known.

## Calibrated negatives

- **Random sampling is not useful** for attacking EFL. The conjectured
  bound is sharp; random instances are not adversarial.
- **DSATUR / greedy heuristics do not close the conjecture** even on
  small max-overlap instances (off by 1 at `n = 5`).
- **The chromatic-index reformulation does not give a clean
  structural proof** under classical tools (König, Vizing, Galvin's
  list-coloring theorem). If those worked the conjecture would have
  been settled in the 1970s.
- **Computational verification cannot close the small-`n` gap on its
  own** as long as KKKMO's `N_0` is not explicit and is plausibly
  super-exponential in any explicifying audit.

## Citations

Verified anchors (from batch prompt):
- Erdős, Faber, Lovász, 1972 (conference posing).
- Kang, Kelly, Kühn, Methuku, Osthus, 2021. "Resolution of the
  Erdős-Faber-Lovász conjecture." arXiv:2101.04698 (cited but not
  re-fetched in this session).

Paraphrased / not re-verified in this session (presented as paraphrase,
not canonical citation):
- Hindman 1981 small-`n` work; exact bound `n ≤ 10` cited from memory.
- Klein-Margraf 2005 incremental small-`n` improvements.
- Kahn 1992 `n + o(n)` asymptotic bound.

Tools used: Python 3.14, networkx 3.x, no external solvers (no z3
available in this environment).

— Researcher: Harmonia_M2_sessionA, 2026-05-05.
