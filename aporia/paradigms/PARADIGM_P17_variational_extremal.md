# PARADIGM P17 — Variational / Extremal Principle (worked example + decision tree + code skeleton)

Aporia P88, 2026-08-21. Source: taxonomy P17; no DR grounding in BACKCORPUS
(checked). Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: identify the object as the minimizer of a functional; deduce its
properties from optimality conditions (verb: EXTREMIZE; payoff verb:
READ-PROPERTIES-FROM-OPTIMALITY).

## 1. Worked example — EXECUTED (`paradigm_p17_worked_example.py`)

The Rayleigh variational principle on the path-graph P₄₀ Laplacian, with an
exact derived comparator (λ_k = 2 − 2cos(kπ/n), from the discrete cosine
eigenvectors):

- **A.** Closed form vs numpy.eigh: max|diff| **2.7e-15** across all 40
  eigenvalues — two independent routes to the spectrum agree at machine
  precision (comparator gate).
- **B.** Projected Rayleigh descent from 5 random starts converges to λ₁
  (algebraic connectivity) within **4.5e-15** relative — the extremal object
  FOUND by optimization, with the constant-vector deflation re-applied every
  step (drift back to λ₀=0 is the classic failure, named in-script).
- **C.** Euler-Lagrange residual ‖Lv − Rv‖ = **1.2e-16** at convergence —
  the optimality condition IS the eigen-equation, verified rather than
  invoked. Verdict: **EXTREMAL-CONFIRMS**.

## 2. Decision tree

- Q1: Can the object be characterized as an EXTREMIZER of a computable
  functional (energy, ratio, count)? — NO: optimality machinery has no grip.
- Q1 YES — Q2: Is the feasible set/constraint manifold explicit (and its
  projection computable)? — NO: unconstrained relaxations may extremize the
  wrong set; fix the geometry first (the deflation lesson: constraints must
  be RE-ENFORCED, not assumed preserved).
- Q2 YES — Q3: Is there an INDEPENDENT route to the extremal value (closed
  form, dual bound, SDP certificate) to gate against? — NO: a lone
  optimizer's convergence proves convergence, not optimality — pair it with
  a dual/independent bound or mark values provisional.
- Q3 YES — EXECUTE: optimize from MULTIPLE starts, gate against the
  independent route, and verify the optimality CONDITION (Euler-Lagrange /
  KKT residual) at the claimed extremum — three separable certificates.
- Duality note: where exact duals exist (SDP, LP), the dual value is the
  decline-capable certificate: a gap between primal and dual is the
  instrument telling you the claimed extremum is not one.

## 3. Code skeleton

```python
def variational_attack(functional, grad, project, independent_value,
                       n_starts=5, iters=20_000, lr=0.2):
    """P17 template. Multiple starts + independent-value gate + optimality
    residual: convergence alone proves nothing."""
    finals = []
    for _ in range(n_starts):
        v = project(rng.standard_normal(dim))
        for _ in range(iters):
            v = project(v - lr * grad(v))
        finals.append(functional(v))
    assert max(finals) - min(finals) < 1e-8, "starts disagree — landscape not settled"
    assert abs(finals[0] - independent_value) < 1e-8, "optimizer vs independent route differ"
    return {"extremal_value": finals[0], "certificates": ["multistart", "independent", "EL-residual"]}
```

## 4. Catalog assignment

Primary: none of the current catalog rows are extremal-shaped as stated —
recorded honestly (third empty primary; unlike P06/P13 the blocker is
FRAMING: several rows COULD be recast variationally — 0065's maximal gaps,
0484's extremal envelope — and the tree's Q1 is where that recasting would
be tested; noted as recast-candidates, not assignments). Prometheus-internal:
tensor-landscape peaks/valleys (the taxonomy's own note), flag-algebra
bounds if extremal combinatorics enters the catalog. Anti-assignment:
identity-verification rows (0129/0137/0154) — nothing to extremize.

## Provenance and honesty

The Rayleigh principle is 19th-century; the content is the three-certificate
discipline (multistart + independent gate + optimality residual — convergence
alone proves nothing) and the honest third empty primary with its recast-
candidate nuance. The machine-precision numbers reflect the problem's tiny
scale, not instrument heroics — stated so the template's tolerances are not
copied blindly into larger problems.
