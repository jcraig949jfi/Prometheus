"""Capability-gap fixtures: measure whether the FREE path fails before buying or building.

    python -m techne.scripts.capability_gap_fixture --target sdp --out <result.json>

THE RULE THIS IMPLEMENTS. Every paywalled or absent tool on the arsenal roadmap is a roadmap
item with no measured need. A purchase or a build is authorised by a FAILING FIXTURE, never by a
roadmap row — because "we have a roadmap item for MOSEK" and "a problem of ours defeats the free
solvers" are different statements, and only the second costs money.

So a gap fixture is: a problem of the shape our roadmap actually asks for, run through the free
path, with the outcome recorded either way. A passing fixture closes the request. A failing one
is the evidence that justifies the spend, and it also tells you WHICH spend — because the regime
that fails determines whether the answer is a commercial solver, a different free solver, or
something neither of them does.

HONEST STATUS OF THIS FILE: the SDP fixtures below are MINE, hand-built, and have not been
adversarially reviewed. A single hand-built instance where both solvers fail is a CANDIDATE gap,
not a solver verdict — the instance could be badly posed in a way I did not see. Every result
carries that caveat, and the ill-conditioned case is flagged as needing review before it is
quoted as evidence about a solver.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np

FREE_SOLVERS = ("CLARABEL", "SCS")
AUTHORITY_THETA_C5 = 5 ** 0.5     # Lovasz theta of the 5-cycle


def _theta_problem(A: np.ndarray):
    import cvxpy as cp
    n = A.shape[0]
    X = cp.Variable((n, n), symmetric=True)
    cons = [X >> 0, cp.trace(X) == 1]
    cons += [X[i, j] == 0 for i in range(n) for j in range(i + 1, n) if A[i, j]]
    return cp.Problem(cp.Maximize(cp.sum(X)), cons)


def _cycle(n: int) -> np.ndarray:
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i + 1) % n] = A[(i + 1) % n, i] = 1
    return A


def _random_graph(n: int, p: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    A = (rng.random((n, n)) < p).astype(float)
    A = np.triu(A, 1)
    return A + A.T


def _ill_conditioned(m: int, spread_log10: float, seed: int):
    """Minimise trace(C X) over X >> eps I, trace X = 1, with C's spectrum spanning
    10^spread_log10. Feasible by construction: X = I/m satisfies both constraints."""
    import cvxpy as cp
    rng = np.random.default_rng(seed)
    d = np.logspace(0, spread_log10, m)
    Q = np.linalg.qr(rng.standard_normal((m, m)))[0]
    C = Q @ np.diag(d) @ Q.T
    X = cp.Variable((m, m), symmetric=True)
    prob = cp.Problem(cp.Minimize(cp.trace(C @ X)),
                      [X >> np.eye(m) * 1e-6, cp.trace(X) == 1])
    return prob, float(np.trace(C) / m)     # the value at the certified-feasible point X = I/m


def run_sdp(out_path: str | None) -> dict:
    import cvxpy as cp

    cases = []

    # A. AUTHORITY ANCHOR. theta(C_5) = sqrt(5). If the free path misses this, nothing else
    #    measured here means anything.
    prob = _theta_problem(_cycle(5))
    for s in FREE_SOLVERS:
        t = time.perf_counter()
        try:
            v = prob.solve(solver=s)
            cases.append({"case": "A_authority_theta_C5", "solver": s, "status": prob.status,
                          "value": v, "expected": AUTHORITY_THETA_C5,
                          "abs_error": abs(v - AUTHORITY_THETA_C5),
                          "ms": round((time.perf_counter() - t) * 1000, 1), "failed": False})
        except Exception as exc:
            cases.append({"case": "A_authority_theta_C5", "solver": s, "failed": True,
                          "error": f"{type(exc).__name__}: {exc}"})

    # B. SCALE. Where does the free interior-point path stop being affordable?
    for n in (20, 60, 120):
        p = _theta_problem(_random_graph(n, 0.3, seed=0))
        for s in FREE_SOLVERS:
            t = time.perf_counter()
            try:
                v = p.solve(solver=s)
                cases.append({"case": f"B_scale_n{n}", "solver": s, "status": p.status,
                              "value": v, "ms": round((time.perf_counter() - t) * 1000, 0),
                              "failed": p.status not in ("optimal",)})
            except Exception as exc:
                cases.append({"case": f"B_scale_n{n}", "solver": s, "failed": True,
                              "error": f"{type(exc).__name__}: {exc}"})

    # C. CONDITIONING. A feasible problem whose data spans ten orders of magnitude.
    for spread in (4.0, 10.0):
        prob, feasible_value = _ill_conditioned(30, spread, seed=7)
        for s in FREE_SOLVERS:
            t = time.perf_counter()
            try:
                v = prob.solve(solver=s)
                bad = prob.status not in ("optimal",) or not np.isfinite(v)
                cases.append({"case": f"C_illcond_1e{int(spread)}", "solver": s,
                              "status": prob.status, "value": None if not np.isfinite(v) else v,
                              "a_feasible_point_attains": feasible_value,
                              "ms": round((time.perf_counter() - t) * 1000, 0), "failed": bad})
            except Exception as exc:
                cases.append({"case": f"C_illcond_1e{int(spread)}", "solver": s, "failed": True,
                              "error": f"{type(exc).__name__}: {exc}"})

    fails = [c for c in cases if c.get("failed")]
    by_case: dict[str, list] = {}
    for c in cases:
        by_case.setdefault(c["case"], []).append(c)
    all_free_fail = sorted(k for k, v in by_case.items() if all(x.get("failed") for x in v))

    doc = {
        "schema": "techne.capability_gap_fixture/1",
        "target": "sdp",
        "roadmap_claim_under_test": "REQ-029 named MOSEK as the upgrade path from SCS for "
                                   "pm.optimization.solve_sdp. This measures whether the free "
                                   "path actually fails on anything of the shape we ask for.",
        "free_path": {"solvers": list(FREE_SOLVERS),
                      "cvxpy": cp.__version__,
                      "installed_solvers": cp.installed_solvers(),
                      "licences": "CLARABEL Apache-2.0, SCS Apache-2.0 -- both $0",
                      "note": "CLARABEL is an INTERIOR-POINT solver, the same algorithm class as "
                              "MOSEK; SCS is first-order. The roadmap treated SCS as the free "
                              "path and did not account for Clarabel being installed."},
        "cases": cases,
        "n_cases": len(cases),
        "n_failed": len(fails),
        "regimes_where_EVERY_free_solver_failed": all_free_fail,
        "verdict": ("NO GAP MEASURED -- the free path handled every regime tested"
                    if not all_free_fail else
                    f"CANDIDATE GAP in {all_free_fail}"),
        "CAVEAT": ("These instances are hand-built by this seat and have NOT been adversarially "
                   "reviewed. A single instance on which both solvers fail is a CANDIDATE gap, "
                   "not a solver verdict: the instance may be badly posed in a way I did not "
                   "see. Case C declares a certified-feasible point (X = I/m) so that an "
                   "'infeasible' or 'unbounded' status is checkable as wrong rather than taken "
                   "on trust -- but the fixture still needs review before it is quoted as "
                   "evidence about a solver."),
        "what_a_failing_regime_implies": {
            "scale": "a commercial solver may help; so may a better free one. Measure both "
                     "before paying.",
            "conditioning": "a commercial DOUBLE-PRECISION solver may help -- but if the "
                            "requirement is a verifiable certificate rather than a fast float, "
                            "no double-precision solver solves it at any price, and the answer "
                            "is arbitrary-precision (SDPA-GMP, GPL, $0) or rational rounding to "
                            "an exact certificate.",
            "accuracy_on_small_well_conditioned": "no purchase is justified; close the request.",
        },
    }
    if out_path:
        pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(out_path).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="sdp", choices=["sdp"])
    ap.add_argument("--out", default="techne/acquisition/GAP_FIXTURE_SDP.json")
    a = ap.parse_args(argv)

    doc = run_sdp(a.out)
    print(f"=== capability gap fixture: {a.target} ===")
    print(f"free path       {doc['free_path']['solvers']} (both $0); cvxpy "
          f"{doc['free_path']['cvxpy']}")
    print(f"{'case':<24} {'solver':<10} {'status':<22} {'value':>16} {'ms':>8}  failed")
    for c in doc["cases"]:
        val = c.get("value")
        vs = f"{val:16.8f}" if isinstance(val, float) else f"{str(val):>16}"
        print(f"{c['case']:<24} {c['solver']:<10} {str(c.get('status','ERROR')):<22} {vs} "
              f"{str(c.get('ms','')):>8}  {'YES' if c.get('failed') else ''}")
    print(f"\nVERDICT         {doc['verdict']}")
    print(f"                {doc['n_failed']} of {doc['n_cases']} solver-runs failed")
    print(f"CAVEAT          {doc['CAVEAT'][:150]}...")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
