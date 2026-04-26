"""Smoke tests for prometheus_math.optimization.

Each function is exercised on a small, easily verifiable problem. Tests
gracefully skip when no backend is available for a category.
"""
from __future__ import annotations

import math

import pytest

from prometheus_math import optimization as opt
from prometheus_math.registry import is_available


# ---------------------------------------------------------------------------
# installed_solvers
# ---------------------------------------------------------------------------

def test_installed_solvers_shape():
    s = opt.installed_solvers()
    assert set(s.keys()) == {"lp", "mip", "cp", "sat", "smt", "convex"}
    for cat, lst in s.items():
        assert isinstance(lst, list)
        for name in lst:
            assert is_available(name), f"{cat}: {name} reported but not available"


# ---------------------------------------------------------------------------
# LP
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not opt.installed_solvers()["lp"], reason="no LP backend")
def test_lp_default_dispatch():
    """min -x - y s.t. x+y <= 4, x,y >= 0  →  fun = -4 at (4,0) or (0,4) or interior."""
    res = opt.solve_lp(
        c=[-1, -1], A_ub=[[1, 1]], b_ub=[4],
        bounds=[(0, None), (0, None)],
    )
    assert res["success"], res
    assert math.isclose(res["fun"], -4.0, abs_tol=1e-7)
    assert res["backend_used"] == opt.installed_solvers()["lp"][0]
    # x+y == 4
    assert math.isclose(res["x"][0] + res["x"][1], 4.0, abs_tol=1e-7)


@pytest.mark.skipif(not is_available("scipy"), reason="scipy not installed")
def test_lp_force_scipy():
    res = opt.solve_lp(
        c=[1.0, 1.0], A_eq=[[1, 1]], b_eq=[3],
        bounds=[(0, None), (0, None)],
        backend="scipy",
    )
    assert res["backend_used"] == "scipy"
    assert math.isclose(res["fun"], 3.0, abs_tol=1e-7)


def test_lp_unknown_backend_raises():
    with pytest.raises(ValueError):
        opt.solve_lp(c=[1.0], backend="not-a-real-solver")


def test_lp_unavailable_backend_raises():
    # Use a name that's in the preference list but unlikely uninstalled.
    # Pick whichever LP backend is *not* available; if all are, skip.
    missing = [b for b in ("highspy", "scipy", "pulp") if not is_available(b)]
    if not missing:
        pytest.skip("all LP backends installed")
    with pytest.raises(ValueError):
        opt.solve_lp(c=[1.0], backend=missing[0])


# ---------------------------------------------------------------------------
# MIP
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not opt.installed_solvers()["mip"], reason="no MIP backend")
def test_mip_default_dispatch():
    """min -x - y s.t. 2x + y <= 5, x + 2y <= 5, x,y in {0,1,2,3}; integer.
    Optimum at x=y=1.66 LP relaxation, but integer optimum is x=y=1 or
    x=2,y=1 or x=1,y=2 depending — actually max of x+y is 3 at e.g. (2,1).
    """
    res = opt.solve_mip(
        c=[-1, -1],
        A_ub=[[2, 1], [1, 2]], b_ub=[5, 5],
        integrality=[1, 1],
        bounds=[(0, 3), (0, 3)],
    )
    assert res["success"], res
    # Expected integer optimum: x+y = 3, so fun = -3
    assert math.isclose(res["fun"], -3.0, abs_tol=1e-7)
    # both should be integers
    for v in res["x"]:
        assert math.isclose(v, round(v), abs_tol=1e-6)
    assert res["backend_used"] == opt.installed_solvers()["mip"][0]


@pytest.mark.skipif(not is_available("pulp"), reason="pulp not installed")
def test_mip_force_pulp():
    res = opt.solve_mip(
        c=[-1.0, -1.0],
        A_ub=[[1, 1]], b_ub=[2.5],
        integrality=[1, 1],
        bounds=[(0, None), (0, None)],
        backend="pulp",
    )
    assert res["backend_used"] == "pulp"
    assert res["success"]
    # Best is x+y = 2 (integer), fun = -2
    assert math.isclose(res["fun"], -2.0, abs_tol=1e-7)


# ---------------------------------------------------------------------------
# CP
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not is_available("ortools"), reason="ortools not installed")
def test_cp_simple():
    """Find x,y in [0,10] with x+y == 7, x-y == 1 → x=4, y=3."""
    def build(m):
        x = m.NewIntVar(0, 10, "x")
        y = m.NewIntVar(0, 10, "y")
        m.Add(x + y == 7)
        m.Add(x - y == 1)
        return {"x": x, "y": y}

    res = opt.solve_cp(build)
    assert res["backend_used"] == "ortools"
    assert res["solution_dict"] == {"x": 4, "y": 3}


@pytest.mark.skipif(not is_available("ortools"), reason="ortools not installed")
def test_cp_with_objective():
    """Maximize x+y subject to 2x+y <= 5 and x,y in [0,5] (integer)."""
    def build(m):
        x = m.NewIntVar(0, 5, "x")
        y = m.NewIntVar(0, 5, "y")
        m.Add(2 * x + y <= 5)
        m.Maximize(x + y)
        return {"x": x, "y": y}

    res = opt.solve_cp(build)
    assert res["backend_used"] == "ortools"
    assert res["objective_value"] == 5.0
    # Best is x=0,y=5 (sum=5) since 2*0+5=5 <= 5
    sol = res["solution_dict"]
    assert sol["x"] + sol["y"] == 5


# ---------------------------------------------------------------------------
# SAT
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not opt.installed_solvers()["sat"], reason="no SAT backend")
def test_sat_satisfiable():
    """(x1 ∨ x2) ∧ (¬x1) ∧ (¬x2 ∨ x3)  → SAT, x1=False."""
    clauses = [[1, 2], [-1], [-2, 3]]
    res = opt.solve_sat(clauses)
    assert res["sat"] is True
    assert res["backend_used"] == opt.installed_solvers()["sat"][0]
    # Verify model satisfies clauses
    assignment = {abs(lit): (lit > 0) for lit in res["model"]}
    for cl in clauses:
        assert any(
            (assignment.get(abs(lit), True) if lit > 0
             else not assignment.get(abs(lit), False))
            for lit in cl
        ), f"clause {cl} not satisfied"


@pytest.mark.skipif(not opt.installed_solvers()["sat"], reason="no SAT backend")
def test_sat_unsatisfiable():
    """(x1) ∧ (¬x1)  → UNSAT."""
    res = opt.solve_sat([[1], [-1]])
    assert res["sat"] is False
    assert res["model"] is None


@pytest.mark.skipif(not is_available("z3"), reason="z3 not installed")
def test_sat_force_z3():
    res = opt.solve_sat([[1, 2], [-1, -2]], backend="z3")
    assert res["backend_used"] == "z3"
    assert res["sat"] is True


# ---------------------------------------------------------------------------
# SMT
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not is_available("z3"), reason="z3 not installed")
def test_smt_integer_system():
    import z3
    x = z3.Int("x")
    y = z3.Int("y")
    res = opt.solve_smt([x + y == 10, x - y == 4])
    assert res["sat"] is True
    assert res["model_dict"] == {"x": 7, "y": 3}
    assert res["backend_used"] == "z3"


@pytest.mark.skipif(not is_available("z3"), reason="z3 not installed")
def test_smt_unsat():
    import z3
    x = z3.Int("x")
    res = opt.solve_smt([x > 0, x < 0])
    assert res["sat"] is False
    assert res["model_dict"] is None


# ---------------------------------------------------------------------------
# Convex
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not is_available("cvxpy"), reason="cvxpy not installed")
def test_convex_prebuilt():
    import cvxpy as cp
    import numpy as np
    x = cp.Variable(2)
    obj = cp.Minimize(cp.sum_squares(x - np.array([1.0, 2.0])))
    res = opt.solve_convex(obj, constraints=[x >= 0], variables={"x": x})
    assert res["status"] == "optimal"
    assert res["value"] is not None and abs(res["value"]) < 1e-6
    sol = res["solution"]["x"]
    assert abs(sol[0] - 1.0) < 1e-5
    assert abs(sol[1] - 2.0) < 1e-5
    assert res["backend_used"] == "cvxpy"


@pytest.mark.skipif(not is_available("cvxpy"), reason="cvxpy not installed")
def test_convex_builder_mode():
    import cvxpy as cp

    def build(vars):
        x = vars["x"]
        obj = cp.Minimize(cp.square(x - 3.0))
        return obj, [x >= 0]

    res = opt.solve_convex(build, variables={"x": None})
    assert res["status"] == "optimal"
    assert abs(res["solution"]["x"] - 3.0) < 1e-5
    assert res["backend_used"] == "cvxpy"
