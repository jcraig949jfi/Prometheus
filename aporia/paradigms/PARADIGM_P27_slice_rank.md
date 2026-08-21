# PARADIGM P27 — Slice Rank / Polynomial Method on F_q (worked example + decision tree + code skeleton)

Aporia P95, 2026-08-21. Source: taxonomy P27 (tensor-specific round, James
2026-05-08 directive; catalog refs #13-15, #56, #95-99 in
tensor_open_problems_v1.md). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl. **First of the reopened tier's tensor fifth (25/30 →
26/30).**

**The move**: bound a combinatorial set by the dimension of a polynomial
space via the slice rank of a diagonal tensor (verb: SLICE-THE-TENSOR;
payoff verb: EXPONENTIAL-BOUNDS-FROM-DIMENSION-COUNTS).

## 1. Worked example — EXECUTED (`paradigm_p27_worked_example.py`)

The Croot-Lev-Pach/Ellenberg-Gijswijt engine at honest scale:

- **A. Ground truth arrived from search**: exhaustive branch-and-bound max
  cap sets in F_3^n — 2, 4, 9 for n=1..3 (exact; 262,801 nodes at n=3) and
  best-found **20** at n=4 within a 2M-node budget (the classical value).
- **B. The dimension bound, exact**: |cap| ≤ 3·m_(2n/3)(n) with the monomial
  count by integer DP — 3, 9, 30, 45 at n=1..4, dominating the truth at
  every n (violation asserted as instrument fault).
- **C. The constant, two routes**: DP-counted growth constants at n = 30,
  60, 120, 240 (2.7132 → 2.7390) converge FROM BELOW toward the saddle-point
  minimum of (1+t+t²)/t^(2/3) = **2.755105** at t* = 0.5931 — derived by
  minimization, not memory — with monotone shrinking gaps. The margin below
  the trivial rate 3 IS the Ellenberg-Gijswijt theorem, exhibited.

Instrument-first catch (in-code): the first two-route gate used a fixed 1%
band and read the n=60 constant's expected ~1.3% subexponential deficit as
disagreement — the correct gate is convergence-from-below (increasing,
bounded, gaps shrinking). Finite-n prefactors are part of the comparator.
Verdict: **SLICE-BOUNDS**.

## 2. Decision tree

- Q1: Is the target a SET-SIZE bound for a set avoiding a LINEAR pattern
  over F_q (APs, corners, cap-set-like)? — NO: slice rank bites diagonal
  tensors from linear patterns; other patterns need other ranks (the
  rank-zoo below).
- Q1 YES — Q2: Does the pattern give a DIAGONAL tensor whose slice rank
  bounds the set (the CLP identity: an indicator polynomial of low degree)?
  — NO: check the rank-zoo (partition/analytic/geometric rank) — related
  but distinct detectors; picking the wrong rank gives no bound.
- Q2 YES — Q3: Is the polynomial-space dimension COUNTABLE exactly (DP over
  degree caps)? — YES always for F_q monomials — EXECUTE: count exactly,
  verify domination on exhaustive small cases, and derive the asymptotic
  constant by an independent route (saddle point) with a finite-n-aware
  convergence gate.
- Exit note: the bound is an UPPER bound only — constructions (lower
  bounds) are separate work, and the gap between them (2.218^n vs 2.755^n
  for caps) is an open problem, not a defect.

## 3. Code skeleton

```python
def slice_rank_attack(n_range, pattern_free_search, dim_count, saddle_fn):
    """P27 template. Exhaustive truth on small n, exact DP dimension bound
    with domination asserted, two-route constant with a convergence gate
    that models the finite-n prefactor."""
    for n in n_range.small:
        truth = pattern_free_search(n)
        bound = dim_count(n)
        assert bound >= truth, f"bound violated at {n} — instrument fault"
    limit = minimize(saddle_fn)
    dps = [dim_count(n) ** (1 / n) for n in n_range.large]
    assert increasing(dps) and all(d < limit for d in dps) and gaps_shrink(dps, limit)
    return {"limit": limit, "finite_n_trace": dps}
```

## 4. Catalog assignment

Primary: tensor_open_problems_v1.md rows #13-15, #56, #95-99 (per the
taxonomy's own refs — the tensor catalog is this paradigm's home; the
triage-catalog MATH rows are not, and none are assigned). This is the FIRST
paradigm whose primary targets live in the tensor catalog — the
geometry-awaits-tensor family's wait, ending. Anti-assignment: all
analytic/statistical triage rows.

## Provenance and honesty

EG 2017 is settled; the content is the three-legged executable (search-
arrived truths, asserted domination, two-route constant with the finite-n
lesson) and the tier-correction context: this artifact opens the tensor
fifth that the P92 completion claim missed.
