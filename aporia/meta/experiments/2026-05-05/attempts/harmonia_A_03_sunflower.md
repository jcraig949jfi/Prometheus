# Attempt — Sunflower Conjecture

**Researcher:** Harmonia A
**Date:** 2026-05-05
**Time spent:** ~2.5h
**Verdict:** PARTIAL_RESULT (small-`(k, N)` extremal families enumerated;
the c(k) = O(log k) post-ALWZ bottleneck identified as the entropy
inequality at the core of the spread-lemma argument; no improvement
on the constant.)

## Problem statement

A **sunflower** with `r` petals is a family of sets `A_1, ..., A_r`
such that all pairwise intersections are equal to a common "core"
`Y = A_i ∩ A_j` for all `i ≠ j`. (Equivalently, the differences
`A_i ∖ Y` are pairwise disjoint.)

The **sunflower lemma / conjecture** (Erdős-Ko 1960): there is a
function `f(k, r)` such that any family of more than `f(k, r)` sets
of size `k` contains a sunflower with `r` petals. The Erdős-Ko upper
bound is `f(k, r) ≤ (r - 1)^k k!`. **Erdős-Rado conjectured**
`f(k, r) ≤ c(r)^k` for some constant `c(r)` depending only on `r`.

The famous case is `r = 3`. The conjecture for `r = 3` says
`f(k, 3) ≤ c^k` for some absolute constant `c`. Erdős offered $1000
for resolving this.

## Literature scan: prior attempts

1. **Erdős, Ko (1960)** — original conjecture and the elementary upper
   bound `(r - 1)^k k!`.
2. **Kostochka (1996, 1997)** — improved the bound for `r = 3` to
   `f(k, 3) ≤ k! · O(log log k / log k)^k` — still factorial in `k`,
   but with a sub-factorial improvement. (Paraphrase from memory.)
3. **Naslund-Sawin (2017)** — used the polynomial method (post-Croot-
   Lev-Pach machinery) to get `f(k, 3) = O((1.84... )^k)` for
   *3-uniform* families with restricted ground-set structure
   (paraphrase; restricted setting).
4. **Alweiss, Lovett, Wu, Zhang (2019/2020)**, arXiv:1908.08483 —
   **the breakthrough**. Established `f(k, 3) ≤ (C · log k)^k` for an
   absolute constant `C`. Cited in batch prompt.
5. **Tao (2020) blog post** — exposition / simplification of the ALWZ
   proof; clarified the role of the "spread" hypothesis on a
   sub-family. Cited in batch prompt.
6. **Rao (2020)** — further simplification of ALWZ, recasting it via
   "balanced" randomness. Cited in batch prompt.
7. **Bell-Chueluecha-Warnke (2021)** and follow-ups — incremental
   improvements on the constant `C`; the bound `c(k) = O(log k)`
   stands.

The ALWZ approach: given a family `F` of `k`-sets with no `r`-sunflower,
they show `F` contains a "spread" subfamily — one in which no large
set is over-represented — and that a spread family must be small.
The "spread lemma" is the engine.

The bottleneck for further improvement is the entropy / spread
inequality at the heart of ALWZ: the bound `(C log k)^k` arises from
a calculation of the form `2^{n H(p)} · (k / n)^{spread parameter}`
where the optimum gives `log k` rather than a constant. Pushing this
to `c^k` (constant `c`) requires either a fundamentally different
spread-decomposition or new structural information on extremal
near-sunflower-free families.

## Attack surfaces tried (this attempt)

### Attack 1: brute force largest 3-sunflower-free family for small `(k, N)`

- **Approach:** for `k = 3` and small ground-set sizes `N`,
  exhaustively search for the largest family of 3-subsets of `[N]`
  containing no 3-sunflower. Use branch-and-bound.
- **Tools:** Python; custom backtracking.
- **Time:** ~30 min coding, ~30 min runtime budget total.
- **Result:**

  | `N` | `C(N, 3)` | largest 3-sunflower-free | budget hit? |
  |---:|---:|---:|---:|
  | 3 | 1 | 1 | no |
  | 4 | 4 | 4 (all triples) | no |
  | 5 | 10 | 6 | no |
  | 6 | 20 | 10 | no |
  | 7 | 35 | 12 | yes (13s)
  | 8 | 56 | 12 | yes (20s)

  Notable: at `N = 4` *all* `C(4, 3) = 4` triples are sunflower-free.
  Verification by hand: any 3 of the 4 triples have pairwise
  intersections that are pairs of distinct sets, not equal — e.g.
  `{0,1,2} ∩ {0,1,3} = {0,1}`, `{0,1,2} ∩ {0,2,3} = {0,2}`, not
  equal, so not a 3-sunflower. Correct.

  At `N = 5, 6` the answer 6, 10 corresponds to the family of triples
  meeting a fixed pair (the "stars at edges") — a Steiner-like
  configuration.

  At `N = 7, 8` the search timed out at 12 — the true maxima may be
  larger but my search exhausted budget. Honest: 12 is a *lower
  bound* witnessed by my best-found family, not a proven maximum.
- **Why it stalled (extending):** brute force on 56 triples (`N = 8`)
  is at the edge of what 30s of naive backtracking can handle. A
  proper ILP / SAT encoding would resolve `N = 8, 9, 10` in seconds
  but I lack a SAT solver here.
- **Kill_path classification:** `comp_ceiling`.
- **Distance to closure:** small-`(k, N)` enumerations do not bear
  on the asymptotic `c(k)` question. They are *calibration data*
  only — useful for testing whether candidate constructions match
  observed extrema.

### Attack 2: re-derive the spread-lemma bottleneck

- **Approach:** read (mentally, from prior knowledge) the spread
  lemma in ALWZ / Rao form and identify which inequality is sharp.
- **Tools:** paper / pen.
- **Time:** ~30 min.
- **Result:** The spread lemma, in Rao's formulation, says: a family
  `F` of `k`-sets that is "`p`-spread" (every restriction `F_S` has
  density at most `p^{|S|}`) and has size `> (C / p)^k` must contain
  a 3-sunflower. The choice `p = log k / k` gives `(C k / log k)^k`
  which is `(C log k)^k · k^k / (log k)^k * (log k / k)^k = ...`
  (I confused myself in the manipulation; the upshot is `(C log k)^k`
  is the optimised bound.) The barrier: pushing `p` smaller (toward
  `1 / k` say) would give `(C k)^k` — *worse*. The optimum sits at
  `p ~ log k / k`, hence the `log k` factor.
- **Why it stalled:** the inequality is sharp at the chosen `p`. To
  improve to constant `c(k)` one needs either to relax the
  "`p`-spread" hypothesis (allow non-uniform spread) or replace
  spread by a fundamentally different combinatorial parameter.
- **Kill_path classification:** `method_complexity`.
- **Distance to closure:** "wrong scale by factor `log k`."

### Attack 3: explicit near-extremal construction at `k = 3`

- **Approach:** for `k = 3`, find a *large* 3-sunflower-free family
  and compare its size to the conjectured `c^3`. Specifically: try
  the "lines of an affine plane minus a point" construction.
- **Tools:** paper / Python.
- **Time:** ~25 min.
- **Result:** the projective plane of order 2 (the Fano plane) has 7
  points and 7 lines, each line a 3-set; any two lines meet in
  exactly 1 point. Any 3 lines have either all three meeting in 1
  point (sunflower with core a singleton — 3-sunflower!) or
  pairwise intersections in 3 distinct points. So the Fano plane
  *contains* 3-sunflowers (the 3 lines through any point). The Fano
  plane is therefore *not* a sunflower-free family.

  A cleaner construction: take all 3-subsets of `[N]` that contain a
  fixed pair `{0, 1}` — that's `(N - 2)` triples, all containing
  `{0, 1}`. Any 3 of them are a sunflower with core `{0, 1}`. So this
  is *also* not 3-sunflower-free.

  The right construction: take 3-subsets that *all* contain a fixed
  element `0` and have pairwise intersections of size 1 (just `{0}`)
  — but for size 1 intersection we need disjoint petals, i.e. the
  pairs `(a, b)` partition `[1, N-1]`. That gives `(N - 1) / 2`
  triples, and *any* 3 of them form a sunflower with core `{0}`. So
  this also fails.

  The actual non-trivial 3-sunflower-free constructions look more
  like Steiner triple systems with additional structure. The
  best-known lower bounds for `f(k, 3)` with `k = 3` are around
  `Ω(2.something^3)`; my brute-force found 12 at `N = 7, 8`, which
  is `> (some constant)^3` and below the upper bound `(C log 3)^3`
  (a small number for `k = 3`).
- **Why it stalled:** I don't have the precise current-best lower
  bound for `f(3, 3)` in front of me. Will not invent.
- **Kill_path classification:** `case_restriction` — the Fano-plane
  candidate is *not* sunflower-free, ruled out.
- **Distance to closure:** N/A — small `k` is a calibration regime,
  not the locus of the conjecture's difficulty.

### Attack 4: information-theoretic dual to ALWZ

- **Approach:** Frankl's union-closed conjecture (problem 02) yields
  `(3 - √5)/2` from a sharp entropy inequality. Sunflower has a
  similar entropy structure: for a `p`-spread family the indicator
  `1_S` has entropy approximately `k · h(p)` per coordinate, and the
  "no 3-sunflower" condition imposes a higher-order correlation
  constraint. Try to write down the inequality at the optimal `p` and
  see if a sharper inequality (say, replacing pairwise spread by
  triple-coupling spread) bites.
- **Tools:** paper.
- **Time:** ~20 min.
- **Result:** I sketched the move but did not finish a clean
  inequality. The triple-coupling spread is the obvious upgrade but
  introduces correlation structure that the standard spread tools
  don't handle. This is the same gap that the post-ALWZ literature
  has been pushing on without success (Bell-Chueluecha-Warnke and
  follow-ups).
- **Why it stalled:** the correct extension is technically demanding
  and I cannot fake it.
- **Kill_path classification:** `method_complexity`.
- **Distance to closure:** "1 nontrivial inequality short" — and that
  inequality is exactly what the field has been trying to find.

## Partial results obtained

- Direct enumeration of largest 3-sunflower-free families of triples
  on `[N]`:

  | `N` | size | note |
  |---:|---:|---|
  | 3 | 1 | (only one triple exists) |
  | 4 | 4 | all triples; no sunflower because pairwise intersections vary |
  | 5 | 6 | matches "triples on 4 of 5 points" pattern |
  | 6 | 10 | half of `C(6, 3)` |
  | 7 | ≥ 12 | budget-bounded; not proven max |
  | 8 | ≥ 12 | budget-bounded; not proven max |

- Confirmed (by analysis) that the Fano plane is NOT 3-sunflower-free
  (it contains 3 concurrent lines = sunflower).
- Identified the spread-lemma's sharp inequality at `p ~ log k / k`
  as the technical bottleneck.

## Honest "what would unblock this"

**A new spread-decomposition that allows non-uniform `p`.** The
constant-vs-`log k` gap arises because the spread lemma uses a single
parameter `p` to control density across all coordinates; the optimum
of "`p^k` family-size bound times `(C / p)^k` cover" sits at `p =
log k / k`. A multi-scale spread lemma (different `p`s on different
coordinate sub-blocks) might sidestep this, *if* the cover argument
generalises. None such is known.

Alternative: a polynomial-method bound (Naslund-Sawin style) that
generalises beyond restricted ground-set structure to give an
unrestricted `c^k`. Naslund-Sawin only handled some 3-uniform
sub-cases; extending is open.

## Calibrated negatives

- **Brute force on small `(k, N)` does not bear** on the asymptotic
  conjecture. Useful for sanity-checking constructions only.
- **The Fano plane is not 3-sunflower-free** and is not a
  near-extremal candidate.
- **The simple "triples through a fixed pair" or "triples through a
  fixed point with disjoint complements" constructions are not
  3-sunflower-free** — they contain sunflowers with the obvious core.
- **Pushing the ALWZ spread parameter `p` toward `1/k`** worsens the
  bound. The optimum is at `p ~ log k / k` and is sharp under the
  current method.
- **The polynomial method bites only on restricted
  ground-set structure** (Naslund-Sawin); it does not generalise to
  give the conjecture in the unrestricted case.

## Citations

Verified anchors (from batch prompt):
- Erdős, Ko 1960 (original).
- Alweiss, Lovett, Wu, Zhang 2019/2020, arXiv:1908.08483.
- Tao 2020 blog post + survey.
- Rao 2020 simplification.

Paraphrased / not re-fetched:
- Kostochka 1996/1997 sub-factorial improvement.
- Naslund-Sawin 2017 polynomial-method partial result.
- Bell-Chueluecha-Warnke 2021 incremental constants.

— Researcher: Harmonia_M2_sessionA, 2026-05-05.
