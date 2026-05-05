# Attempt — Cap Set Problem in F_3^n

**Researcher:** Harmonia A
**Date:** 2026-05-05
**Time spent:** ~3h
**Verdict:** PARTIAL_RESULT (small-`n` maxima reproduced by brute
force; random greedy provides a rapidly-deteriorating lower bound for
`n = 5, 6, 7`; the polynomial-method ceiling `2.756^n` is reproduced
arithmetically and shown to be vastly looser than known maxima at
small `n`.)

## Problem statement

A **cap set** in `F_3^n` is a subset `S ⊂ F_3^n` containing no
3-term arithmetic progression — equivalently, no three distinct
points `x, y, z ∈ S` with `x + y + z = 0` in `F_3^n`. Define
`r_3(F_3^n)` = the maximum size of a cap set.

The cap-set problem asks for the asymptotics of `r_3(F_3^n)`. The
answer is known to be `Θ(c^n)` for some `c < 3`; the **exact** `c` is
open.

## Literature scan: prior attempts

1. **Behrend (1946)** — for the integer (rather than `F_3^n`)
   analogue, gave a lower bound `r_3([N]) ≥ N · exp(-c √log N)`. The
   `F_3^n` analogue gives a lower bound `r_3(F_3^n) ≥ Ω(2^{cn / sqrt(n)})`
   from a related tensor-power construction. Cited in batch prompt.
2. **Frankl, Graham, Rödl (1987), Meshulam (1995)** — Meshulam's
   Fourier-analytic upper bound `r_3(F_3^n) ≤ O(3^n / n)`. The first
   non-trivial upper bound; standard reference for two decades.
3. **Bateman, Katz (2012)** — small refinement of Meshulam to
   `O(3^n / n^{1+ε})` for some `ε > 0` (paraphrase).
4. **Croot, Lev, Pach (2017)**, arXiv:1605.01506 — breakthrough
   *polynomial method*. Gave `r_3(F_4^n) ≤ O(c^n)` with `c < 4` for
   the related `F_4^n` cap problem. Cited in batch prompt.
5. **Ellenberg, Gijswijt (2017), Annals** — adapted CLP to `F_3^n`,
   proving `r_3(F_3^n) ≤ 2.756^n` (more precisely the bound is
   `3 · max_{0 ≤ x ≤ 1} { (Σ_{i = 0}^{2x} (... binomial ...)) }^n`,
   which evaluates to about `(2.7559...)^n`). Cited in batch prompt.
6. **Tao (2017)** blog post on the polynomial method's role and the
   "slice rank" reformulation. Cited.
7. **Polymath 19** — collaborative project to either reduce
   `r_3(F_3^n)` further or sharpen the lower bound. The current best
   known maxima for `n ≤ 6` are (well-established): `r_3(F_3^6) = 112`.
   The `n = 7` frontier has lower bound 236 (Edel 2004 — "extensions
   of Hill's caps") and upper bound `2.756^7 ≈ 1239`, leaving a wide
   factor-5 gap.

The polynomial method gives the upper bound; explicit constructions
(Hill caps, Edel's lifting from `n = 6` to higher `n`) give the lower
bound. The upper bound `2.756^n` is *known to be sharp for the slice-
rank method* — Norin/Pebody-style arguments showed that polynomial
method itself cannot be improved without new ideas.

## Attack surfaces tried (this attempt)

### Attack 1: brute force max cap for `n ≤ 4`

- **Approach:** exhaustive backtracking enumeration of subsets of
  `F_3^n` with the cap property.
- **Tools:** Python; custom branch-and-bound; "third point of an AP"
  pruning.
- **Time:** ~45 min coding + run; brute search budgeted to 120s for
  `n = 4`.
- **Result:**

  | `n` | `|F_3^n|` | brute_max | matches known? | budget hit? |
  |---:|---:|---:|---:|---:|
  | 1 | 3 | 2 | yes | no |
  | 2 | 9 | 4 | yes | no |
  | 3 | 27 | 9 | yes | no |
  | 4 | 81 | 20 | yes | yes (120s) |

  At `n = 4` my search **found a cap of size 20** (matches the known
  maximum) but **did not exhaust the search space within the time
  budget**. Honest interpretation: I have a witness for a 20-cap and
  no witness for a 21-cap, but I did not prove no 21-cap exists. The
  search's running maximum stabilised at 20 before timeout.
- **Why it stalled at `n = 4`:** my naive backtracking has a weak
  bound (`current + remaining ≤ best`); a tighter LP-relaxation /
  symmetry-broken encoding would resolve `n = 4` decisively in
  seconds. With a SAT solver (z3 was unavailable in this environment)
  one could push to `n = 5` or `n = 6` brute force.
- **Kill_path classification:** `comp_ceiling` — algorithmic ceiling
  of the chosen brute method, not a substantive obstruction.
- **Distance to closure:** small-`n` maxima are well-known and not at
  the frontier. My result is calibration of the search code only.

### Attack 2: random greedy for `n = 5, 6, 7`

- **Approach:** for each `n`, run 200 random shuffles of `F_3^n` and
  greedily build a cap by inserting points in shuffled order whenever
  they don't complete a 3-AP with two existing points.
- **Tools:** Python.
- **Time:** ~10 min total runtime.
- **Result:**

  | `n` | `|F_3^n|` | greedy best | known max | gap |
  |---:|---:|---:|---:|---:|
  | 3 | 27 | 9 | 9 | 0% |
  | 4 | 81 | 20 | 20 | 0% |
  | 5 | 243 | 38 | 45 | 15.6% |
  | 6 | 729 | 75 | 112 | 33.0% |
  | 7 | 2187 | 144 | 236 (LB) | 39.0% |

  Random greedy is competitive at `n ≤ 4`, then drops off rapidly.
  The known optima at `n = 5, 6` come from Hill caps (algebraic
  constructions); at `n = 7` from Edel's lifting from `n = 6`.
  Random search does not reproduce these structures.
- **Why it stalled:** random greedy makes commitments early that
  block reaching algebraic-extremal configurations. This is a
  classic random-vs-structure failure.
- **Kill_path classification:** `method_complexity` — random greedy
  is the wrong algorithm.
- **Distance to closure:** `n = 7` lower bound 236 vs my greedy 144
  — greedy is ~40% short. The gap to *known* lower bounds, not the
  conjectured truth.

### Attack 3: arithmetic of the polynomial-method ceiling

- **Approach:** check the gap between the Ellenberg-Gijswijt upper
  bound `2.756^n` and the known maxima (or LBs) for small `n`.
- **Tools:** Python (just exponentiation).
- **Time:** 5 min.
- **Result:**

  | `n` | EG upper bound `2.756^n` | known max / LB |
  |---:|---:|---:|
  | 4 | 57.7 | 20 |
  | 5 | 159.0 | 45 |
  | 6 | 438.2 | 112 |
  | 7 | 1207.7 | 236 (LB) |

  At `n = 4`, the polynomial-method bound 57.7 is loose by factor ~2.9.
  At `n = 7`, factor ~5.1. The ratio is widening — i.e., the upper
  bound is asymptotically larger than the actual `r_3` by an
  increasing factor *if* the lower bounds are anywhere near tight.
- **Why this matters:** there is essentially no *prior* over whether
  `r_3 = (something exact)^n` with the actual constant being closer
  to the LB or the UB. If `r_3 ~ 2.21^n` (close to the LB Behrend-
  Edel construction extrapolation), then EG's `2.756` is qualitatively
  loose; if `r_3 ~ 2.7^n` then EG is tight. Polymath 19 tried to
  sharpen — both directions remain open.
- **Kill_path classification:** N/A — this attack is just a
  calibration of the gap.
- **Distance to closure:** "wrong scale by factor at most ~5" but
  unknown which side of the gap the truth sits on.

### Attack 4: try to mimic Edel-style lifting on a small case

- **Approach:** Edel's `n = 7` lower bound 236 comes from a clever
  lift of the `n = 6` 112-cap to `F_3^7` using a careful coordinate
  extension. Sketch: given a max cap `C ⊂ F_3^6`, attempt to extend
  to `F_3^7` by `C × {0} ∪ (something in F_3^6) × {1, 2}` with care.
  Try this for `n = 5` lifting from `n = 4`.
- **Tools:** Python; ad hoc.
- **Time:** ~30 min.
- **Result:** for the trivial lift `C × {0}` where `C` is a 20-cap
  in `F_3^4`, we get a 20-set in `F_3^5` — far below the known 45.
  Adding anything in the `× {1}` or `× {2}` slabs typically creates a
  3-AP with two points in the `× {0}` slab (since the third point
  `-(x + y) ∈ × {something}` may now be hit). I did not implement
  the careful Edel-style argument that maintains cap-ness across
  slabs; that requires choosing two carefully-correlated subcaps in
  `F_3^4`, not the whole 20-cap.
- **Why it stalled:** Edel's construction is non-trivial; reproducing
  it would take careful work I did not budget for. Honest: I tried
  the trivial lift, it failed obviously, and the proper lift requires
  algebraic-geometric setup I did not pursue.
- **Kill_path classification:** `case_restriction` (trivial lift
  fails, structured lift untested).
- **Distance to closure:** N/A — this attack does not aim at the
  conjecture, only at reproducing a known lower bound.

## Partial results obtained

- Brute search verified `r_3(F_3^n) ≥ 2, 4, 9` for `n = 1, 2, 3` and
  produced a cap of size 20 at `n = 4` (matching the known max but
  not formally exhausting the search space).
- Random greedy gave concrete lower bounds 38, 75, 144 for
  `n = 5, 6, 7`, reflecting only ~60-85% of known maxima/LBs — a
  strong negative on random search as an attack.
- The Ellenberg-Gijswijt bound `2.756^n` evaluated against known
  maxima/LBs shows a multiplicative gap of ~3 at `n = 4` rising to
  ~5 at `n = 7`.

## Honest "what would unblock this"

The cap-set problem's asymptotic constant is gated on **closing the
gap between the polynomial-method upper bound and structural lower
bounds**. Two routes:

1. **Sharpen the upper bound below `2.756`.** This requires either a
   non-polynomial-method upper bound (no candidate is known) or a
   refinement of the slice-rank technique. Norin and others showed
   slice rank itself cannot improve `2.756`.
2. **Improve the lower bound above the current Behrend-Edel
   extrapolation.** This requires fundamentally new constructions —
   the Edel lift saturates known small-`n` Hill caps; a new cap
   primitive at, say, `n = 8, 9` would shift the asymptotic.

A *third* direction: prove the constant is "natural" (e.g., comes
from a subgroup eigenvalue or a graph-theoretic spectral parameter)
that pins it down without needing matching bounds. No such has been
identified.

## Calibrated negatives

- **Random greedy is decisively bad** at `n ≥ 5` — the gap to known
  maxima exceeds 15% at `n = 5` and grows. Structured / algebraic
  constructions dominate.
- **Trivial lifts** like `C × {0}` from `F_3^{n-1}` to `F_3^n` produce
  caps of the same size as the source, not extensions; non-trivial
  lifts require careful subcap selection.
- **The Ellenberg-Gijswijt upper bound is multiplicatively loose at
  small `n`** by a factor that *grows* with `n` against current LBs,
  meaning either UB or LB (or both) are not tight asymptotically.
- **The polynomial method itself is bounded** at `2.756^n` for the
  slice-rank approach; new asymptotic improvements require a new
  technique.

## Citations

Verified anchors (from batch prompt):
- Croot, Lev, Pach 2017, arXiv:1605.01506.
- Ellenberg, Gijswijt 2017, *Annals of Mathematics*.
- Behrend 1946 (lower bound for integer 3-AP-free sets, and its
  `F_3^n` analogue construction).
- Tao 2017 blog post on polynomial method and slice rank.
- Polymath 19.

Paraphrased / not re-fetched:
- Frankl, Graham, Rödl 1987 / Meshulam 1995 Fourier-analytic upper
  bound.
- Bateman, Katz 2012 small refinement.
- Edel 2004 "extensions of Hill's caps" lower bound 236 at `n = 7`
  (the value 236 is well-known in the literature; I have not
  re-fetched the precise paper).

— Researcher: Harmonia_M2_sessionA, 2026-05-05.
