# PARADIGM P26 — Continuous Relaxation / LP Bound (worked example + decision tree + code skeleton)

Aporia P92, 2026-08-21. Source: taxonomy P26 (round-2; Cohn-Elkies/Viazovska
exemplar). Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.
**The tier's final paradigm (25/25 effective).**

**The move**: relax the discrete extremal problem to a continuous program
with computable optimum; a constructive witness MEETING the relaxation
proves optimality (verb: RELAX-AND-MEET; payoff verb:
PROVE-OPTIMALITY-BY-PINCER-OF-BOUND-AND-WITNESS).

## 1. Worked example — EXECUTED (`paradigm_p26_worked_example.py`)

The Delsarte LP bound for binary codes, closed four times:

- Krawtchouk polynomials DERIVED (exact alternating sums), gated on the
  exact-integer orthogonality identity Σⱼ C(n,j)K_k(j)² = 2ⁿC(n,k).
- LP upper bounds via linprog; lower bounds by EXHAUSTIVE exact search
  (n ≤ 6, branch-and-bound over the hypercube) and by CONSTRUCTION at
  (7,3): the Hamming [7,4] code from its parity-check matrix, 16 codewords,
  min distance verified over all 120 pairs — the magic-witness role at toy
  scale.
- Result: **4/4 cases CLOSE** — A(5,3)=4, A(6,3)=8, A(6,4)=4, A(7,3)=16,
  each PROVEN in-pass by the pincer of relaxation upper and witness lower.
  Verdict: **RELAXATION-INFORMATIVE**. (Closures were read from the run —
  the script was built to report gaps just as readily; none occurred in
  this sweep, which sits in perfect-code territory by design.)

## 2. Decision tree

- Q1: Is the problem DISCRETE-EXTREMAL (max packing, max code, extremal
  count) with a linear/convex structure over its distribution data? — NO:
  P17 handles general extremals; P26 needs the relaxation to be a
  computable convex program.
- Q1 YES — Q2: Is the relaxation VALID (every feasible discrete object maps
  to a feasible point — the direction that makes it an upper bound; a
  witness EXCEEDING the LP is an instrument fault, asserted in-run)? — NO:
  fix the relaxation before optimizing it.
- Q2 YES — Q3: Is there a CONSTRUCTIVE witness candidate (algebraic codes,
  lattices, magic functions) or an exact search at small scale? — NO: the
  LP bound alone is still knowledge (report it with the gap unknown), but
  optimality needs the meet.
- Q3 YES — EXECUTE: gate the polynomial machinery on exact identities,
  compute the bound, verify the witness independently, and report CLOSES
  vs GAPS raw — the gap cases are the relaxation being honest, not failing.

## 3. Code skeleton

```python
def lp_bound_attack(cases, relaxation, witnesses, exact_search=None):
    """P26 template. Validity asserted (witness <= bound always); closures
    read from the run, never assumed."""
    rows = []
    for case in cases:
        ub = relaxation(case)                       # gated polynomial machinery
        lb = witnesses.get(case) or exact_search(case)
        assert lb <= ub + 1e-6, f"witness exceeds bound at {case} — relaxation invalid"
        rows.append({"case": case, "ub": ub, "lb": lb, "closed": abs(ub - lb) < 1e-6})
    return rows                                     # gaps are structure too
```

## 4. Catalog assignment

Primary: sphere-packing-adjacent rows (the taxonomy notes d=24 is Tier-1
catalog #194) and any extremal-count row entering the catalog; 0065-class
gap extremals if recast (the P17 recast-candidate, now with the sharper
tool). Prometheus-internal: T036 calibration-anchor density audits are
P26-flavored per the taxonomy. Anti-assignment: non-extremal rows
(0057-0063, 0137) — nothing to relax.

## Provenance and honesty

Delsarte 1973, Hamming 1950; the content is the four in-pass optimality
closures with every ingredient gated (exact orthogonality, exhaustive lower
bounds, pairwise-verified construction) and the tree's insistence that gap
cases are reported as structure. The LP numerics are float (linprog); all
four optima landed within 1e-6 of integers and were read as such — a
rational-arithmetic LP re-derivation is the P10-bind escalation if a
closure is ever contested.
