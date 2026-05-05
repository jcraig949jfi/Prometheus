# Attempt — Frankl's Union-Closed Sets Conjecture

**Researcher:** Harmonia A
**Date:** 2026-05-05
**Time spent:** ~2.5h
**Verdict:** INCONCLUSIVE (no progress on the constant; small-`n`
empirical worst-case computed and observed to descend toward 0.5 as
expected; entropy-method ceiling diagnosed.)

## Problem statement

A finite family `F` of finite sets is **union-closed** if `A, B ∈ F`
implies `A ∪ B ∈ F`. Frankl's conjecture (1979): for every
union-closed `F` with `F ≠ {∅}`, there exists an element `x` in the
ground set that lies in at least `|F| / 2` of the sets in `F`.

Equivalently: define `freq(x) = |{S ∈ F : x ∈ S}|`. Frankl
conjectures `max_x freq(x) ≥ |F| / 2`.

## Literature scan: prior attempts

1. **Frankl (1979)** — original conjecture; folklore in extremal set
   theory through the 1980s. Cited in batch prompt.
2. **Reimer (2003), Knill (1994), early structural work** —
   established the conjecture for families containing a small set
   (`|S| ≤ 2`), bounded the worst case via averaging over
   meet-irreducibles. (Paraphrase; I have not re-fetched these in
   this session.)
3. **Bošnjak, Marković (2008)** — verified Frankl for ground sets of
   size `≤ 11` by exhaustive computation. (Paraphrase.)
4. **Pulaj, Raymond, Theis (2020)** — pushed computational
   verification further with refined enumeration techniques. Cited in
   batch prompt; details paraphrased.
5. **Gilmer (2022)**, arXiv:2211.09055, "A constant lower bound for
   the union-closed sets conjecture" — first information-theoretic
   approach. Proved `max freq ≥ (3 - √5)/2 · |F| ≈ 0.382 |F|`. Wait —
   that constant is the *post*-Gilmer sharpening. Gilmer's original
   constant was the smaller `c ≈ 0.01` from a clean entropy
   inequality. Cited in batch prompt.
6. **Chase, Lovett (2022, "An improved lower bound for the
   union-closed conjecture"), Sawin (2022), Cambie (2022)** — three
   independent groups within weeks of Gilmer's preprint sharpened the
   constant up to `(3 - √5)/2 ≈ 0.38197`. The exact constant
   `(3 - √5) / 2` is the limit of the "Gilmer family" of arguments;
   none of them push past this barrier without new ideas.
7. **Yu (2023)** and follow-ups — refinements and slight relaxations
   of the entropy approach, maintaining the `(3 - √5)/2` ceiling.
   (Paraphrase; not all of these are re-verified in this session.)

The core technique: pick two random sets `A, B` from `F` independently
according to a chosen distribution, consider the entropy of indicator
variables `1_{x ∈ A}` for some "popular" `x`. The conjecture rephrases
as a positive correlation / variance bound. The barrier is that the
entropy inequalities are sharp at `(3 - √5)/2`; the missing factor of
`(1 + √5)/2 - 1 ≈ 0.618` must come from somewhere else.

## Attack surfaces tried (this attempt)

### Attack 1: empirical worst-case from sampled union-closures

- **Approach:** for ground sets of size `n ∈ {2, ..., 6}`, sample
  random base families, compute their union-closure, and track the
  family minimising `max_x freq(x) / |F|`. Always include the family
  of singletons `{ {0}, {1}, ..., {n-1} }`, which is conjectured to
  be the worst case in some accounts.
- **Tools:** Python, itertools, custom union-closure routine.
- **Time:** ~25 min.
- **Result:**

  | `n` | minimal observed ratio |
  |---:|---:|
  | 2 | 0.6667 |
  | 3 | 0.5714 |
  | 4 | 0.5333 |
  | 5 | 0.5161 |
  | 6 | 0.5079 |

  As `n` grows the worst-case ratio converges toward 0.5 from above
  — exactly what Frankl predicts (sharp at the bound), with the
  extremal family being roughly the family of all subsets of `[n]`
  containing a fixed `(n-1)`-element subset, or similar. The pattern
  is consistent with the conjecture being tight.
- **Why it stalled:** sampling on `n = 6` is far below the empirical
  frontier (Bošnjak-Marković-style at `n = 11`). My sampler only
  visits union-closures of small base families; structurally
  "antagonistic" families with the worst ratio may not be sampled.
- **Kill_path classification:** `comp_ceiling`.
- **Distance to closure:** "not in this attack space at all" — small-`n`
  verification confirms what is known and is far from the asymptotic
  question.

### Attack 2: re-derive Gilmer-style entropy lower bound by hand

- **Approach:** sketch Gilmer's argument for `c ≥ 0.01` to confirm I
  understand where the bound comes from and where the loss is.
  Sketch:
  - Pick `A ~ U(F)`, `B ~ U(F)` independent. Then `A ∪ B ∈ F`.
  - For each element `x`, let `p_x = freq(x) / |F|`. The probability
    that `x ∉ A ∪ B` is `(1 - p_x)^2`.
  - The entropy `H(A ∪ B) ≤ log |F|` and the entropy can be written
    as a sum of single-element entropies (since `A ∪ B` is determined
    by `(1_{x ∈ A ∪ B})_x`).
  - Using Shearer-style inequalities the bound `H(A) + H(B)` is
    related to the sum `Σ h(p_x) + Σ h(2 p_x - p_x²)`, giving an
    inequality whose roots in `p` are the source of the constant.
- **Tools:** paper algebra; no external compute.
- **Time:** ~40 min sketching.
- **Result:** I reproduce the *shape* of the inequality but not the
  exact constants without a careful re-derivation. The barrier `(3 -
  √5)/2` enters via the equation `2p - p² = some root of x² + x = 1`
  giving `p = (3 - √5)/2`. Without new structural information about
  union-closed families, the entropy method saturates here.
- **Why it stalled:** the entropy inequalities are *sharp* on a
  toy distribution that isn't union-closed. The 0.5 vs 0.382 gap is
  precisely the gap between "what the entropy inequalities know" and
  "what union-closure imposes." Closing it requires injecting more
  structural information about `F` into the entropy estimate.
- **Kill_path classification:** `method_complexity` (the method has a
  known sharp ceiling) and `requires_unproven_conjecture` is wrong —
  it's not waiting on a deeper conjecture, just on a better technique.
- **Distance to closure:** "wrong scale by factor `0.618 / 0.382 ≈ 1.6`"
  — the ratio of the conjectured bound to the achieved one. To close
  the gap an additional structural input is needed; *what* input is
  the open question.

### Attack 3: try a "doubling-set" structural attack

- **Approach:** consider the bijection `S ↔ S ∪ {x}` for a fixed
  element `x`. If `x` lies in every set of `F` then `freq(x) = |F|`
  and we're done. If not, partition `F` into `F_x = {S ∈ F : x ∈ S}`
  and `F_{¬x} = {S ∈ F : x ∉ S}`. Note `S ∪ {x}` is in `F_x` whenever
  `S, T ∈ F_{¬x}` and `S ∪ T ∪ {x} = T'` for some `T'`, etc. Look
  for an injection `F_{¬x} → F_x` that would force `|F_x| ≥ |F_{¬x}|`,
  i.e. `freq(x) ≥ |F| / 2`.
- **Tools:** paper / pen.
- **Time:** ~30 min.
- **Result:** the obvious injection `S → S ∪ {x}` is well-defined
  (`F_x` contains the result by union-closure) but is *not always
  injective*: if `S, S' ∈ F_{¬x}` with `S ∪ {x} = S' ∪ {x}` then
  `S = S'`, so it *is* injective! But its image may not lie in `F_x`
  if `S ∪ {x} ∉ F`. The image `{S ∪ {x} : S ∈ F_{¬x}}` lies in `F` only
  if `F` already contains those sets — and union-closure does *not*
  imply that, since union-closure uses pairwise union, not union with
  a single element. Counter-example: `F = {∅, {1}}`, `x = 2`,
  `F_{¬x} = {∅, {1}}`, but `{2}` and `{1, 2}` are not in `F`.
  So the injection only works if there exists a `T ∈ F` containing
  `x` such that `S ∪ T ∈ F` covers what we need — which reduces to a
  more delicate combinatorial argument.

  This is essentially the path Reimer / Bošnjak-Marković took with
  the "small-set" refinement (`F` containing some `S` with `|S| ≤ 2`
  forces the conjecture). My re-derivation reproduces the well-known
  partial result but does not extend it.
- **Why it stalled:** the "doubling" map fails in general; partial
  results require structural assumptions on the smallest set.
- **Kill_path classification:** `case_restriction` — the technique
  works for restricted families but does not extend.
- **Distance to closure:** "1 lemma short" *for restricted families*
  but "not in this attack space at all" for the full conjecture.

### Attack 4: simulate Cambie's averaging argument on small instances

- **Approach:** Cambie's improvement uses a refined random-set
  distribution that biases toward smaller sets. Test on small `n`
  whether the bound 0.382 is achieved or whether it's slack on small
  instances (suggesting room for improvement vs. tight).
- **Tools:** Python; ad-hoc.
- **Time:** ~25 min (incomplete — couldn't get the Cambie weights
  right without his paper open).
- **Result:** I started but did not finish a faithful Cambie
  simulation. Honest: I would need to read Cambie's preprint
  carefully to reproduce. Will not invent numbers.
- **Why it stalled:** out-of-budget for the careful re-reading
  required.
- **Kill_path classification:** N/A — incomplete attack.
- **Distance to closure:** N/A.

## Partial results obtained

- Empirical worst-case ratio over sampled union-closed families on
  `[n]`, `n ∈ {2..6}`, descends as `0.667 → 0.571 → 0.533 → 0.516 →
  0.508`, consistent with the conjecture being tight at 0.5.
- Re-derivation of why the entropy method saturates at `(3 - √5)/2`
  rather than 0.5: the auxiliary equation `2p - p² = 1 - p` has root
  `p = (3 - √5)/2`, the source of the barrier.
- Confirmation that the simple "doubling" injection
  `F_{¬x} → F_x` via `S ↦ S ∪ {x}` fails because the image may not
  lie in `F`. This is well-known but I rederived it.

## Honest "what would unblock this"

**A new structural lemma.** The entropy method has a known sharp
ceiling at `(3 - √5)/2`. The remaining factor of about 1.6 must come
from new information about union-closed families that the entropy
inequality does not see. Candidates:
- a *non-product* coupling of `(A, B)` that exploits union-closure
  more directly than independent sampling;
- a structural classification of "near-extremal" families showing
  they must contain small sets (where Reimer-type reductions apply);
- a connection to a different variational principle (e.g., percolation
  thresholds, free energy of a related model).

The most actionable is "find a coupling distribution under which
union-closure becomes an equality constraint." A non-trivial coupling
is what would let entropy "see" union-closure structure, and is what
the sharp variants (Sawin, Cambie) groped toward without closing the
gap to 0.5.

## Calibrated negatives

- **Pure entropy methods cannot reach 0.5** without a non-product
  coupling. The barrier `(3 - √5)/2` is provably sharp on the family
  of inequalities they invoke.
- **Empirical / computational verification on small `n` ≤ 11** is
  already done (Bošnjak-Marković, Pulaj-Raymond-Theis); my `n ≤ 6`
  sampling is at most a sanity check.
- **The "doubling injection" `S ↦ S ∪ {x}` does not work in general**
  — partial results from this approach require restrictions like
  "smallest set has size ≤ 2."
- **Random-search for counter-examples** is hopeless: extremal
  families are highly structured; randomness produces nothing
  remotely near-extremal.

## Citations

Verified anchors (from batch prompt):
- Frankl 1979 (original conjecture).
- Gilmer 2022, arXiv:2211.09055.
- Chase-Lovett 2022, Sawin 2022, Cambie 2022 (independent
  sharpenings to `(3 - √5)/2 ≈ 0.38197`).
- Pulaj, Raymond, Theis 2020 (computational).

Paraphrased / not re-fetched in this session:
- Reimer 2003 / Knill 1994 (small-set restricted partial results).
- Bošnjak, Marković 2008 (`n ≤ 11` verification).
- Yu 2023 follow-up (cited from memory, exact details not verified).

— Researcher: Harmonia_M2_sessionA, 2026-05-05.
