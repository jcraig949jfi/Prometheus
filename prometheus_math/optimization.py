"""prometheus_math.optimization — unified facade for LP/MIP/CP/SAT/SMT/convex.

Each operation tries available backends in a sensible default order and
returns a plain dict so callers don't depend on backend object types.
Pass `backend=` to force a specific solver; if not available, ValueError
is raised naming the alternatives.

Backends (probed via prometheus_math.registry):
    LP      : highspy, scipy (linprog method='highs'), pulp
    MIP     : pyscipopt, ortools (CP-SAT for pure-int), highspy, pulp
    CP      : ortools (CP-SAT)
    SAT     : pysat (Glucose3), z3 (Boolean fragment)
    SMT     : z3
    Convex  : cvxpy

All return shapes are dicts with at minimum {status, backend_used}; LP/MIP
also have {fun, x, success}. SAT returns {sat, model}. SMT returns
{sat, model_dict}. Convex returns {status, value, solution}.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Sequence, Union

from .registry import is_available


# ---------------------------------------------------------------------------
# Backend selection helper
# ---------------------------------------------------------------------------

def _pick_backend(category: str, requested: Optional[str],
                  preference: Sequence[str]) -> str:
    """Choose backend: explicit request if available, else first available
    from preference. Raises ValueError if none available."""
    avail = [b for b in preference if is_available(b)]
    if requested is not None:
        if requested not in preference:
            raise ValueError(
                f"Unknown {category} backend {requested!r}; "
                f"known: {list(preference)}")
        if not is_available(requested):
            raise ValueError(
                f"Backend {requested!r} not installed; "
                f"available {category} backends: {avail}")
        return requested
    if not avail:
        raise ValueError(
            f"No {category} backend available; install one of {list(preference)}")
    return avail[0]


# ---------------------------------------------------------------------------
# 1. Linear programming
# ---------------------------------------------------------------------------

_LP_PREFERENCE = ("highspy", "scipy", "pulp")


def solve_lp(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
             bounds=None, backend: Optional[str] = None) -> dict:
    """Solve a linear program: minimize c.x s.t. A_ub x <= b_ub, A_eq x = b_eq.

    Parameters
    ----------
    c        : sequence of floats, objective coefficients (length n).
    A_ub,b_ub: optional inequality matrix and rhs.
    A_eq,b_eq: optional equality matrix and rhs.
    bounds   : list of (lo, hi) per variable; None for +/-inf.
    backend  : 'highspy' | 'scipy' | 'pulp' (forces choice).

    Returns
    -------
    dict with keys: status, fun, x, backend_used, success.

    Example
    -------
    >>> solve_lp([-1, -1], A_ub=[[1, 1]], b_ub=[4],
    ...          bounds=[(0, None), (0, None)])['fun']
    -4.0
    """
    chosen = _pick_backend("LP", backend, _LP_PREFERENCE)
    if chosen == "highspy":
        return _lp_highspy(c, A_ub, b_ub, A_eq, b_eq, bounds)
    if chosen == "scipy":
        return _lp_scipy(c, A_ub, b_ub, A_eq, b_eq, bounds)
    if chosen == "pulp":
        return _lp_pulp(c, A_ub, b_ub, A_eq, b_eq, bounds)
    raise ValueError(f"Unhandled LP backend {chosen}")


def _lp_scipy(c, A_ub, b_ub, A_eq, b_eq, bounds) -> dict:
    from scipy.optimize import linprog
    res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")
    return {
        "status": int(res.status),
        "fun": float(res.fun) if res.fun is not None else None,
        "x": list(res.x) if res.x is not None else None,
        "success": bool(res.success),
        "backend_used": "scipy",
        "message": str(res.message),
    }


def _lp_highspy(c, A_ub, b_ub, A_eq, b_eq, bounds) -> dict:
    # Use scipy's linprog(method='highs') as a thin bridge to HiGHS — same
    # underlying solver, but stable input shape. Fall back to scipy if scipy
    # absent (rare but possible).
    if is_available("scipy"):
        out = _lp_scipy(c, A_ub, b_ub, A_eq, b_eq, bounds)
        out["backend_used"] = "highspy"
        return out
    # Direct highspy path (no scipy): use the model-style API.
    import highspy
    import numpy as np
    h = highspy.Highs()
    h.silent()
    n = len(c)
    lb = np.full(n, -np.inf)
    ub = np.full(n, np.inf)
    if bounds is not None:
        for i, b in enumerate(bounds):
            lo, hi = (b if b is not None else (None, None))
            if lo is not None:
                lb[i] = lo
            if hi is not None:
                ub[i] = hi
    # Add variables
    for i in range(n):
        h.addCol(float(c[i]), float(lb[i]), float(ub[i]), 0, [], [])
    # Inequality rows: -inf <= a.x <= b
    if A_ub is not None:
        for row, rhs in zip(A_ub, b_ub):
            idxs = [i for i, v in enumerate(row) if v != 0]
            vals = [float(row[i]) for i in idxs]
            h.addRow(-highspy.kHighsInf, float(rhs), len(idxs), idxs, vals)
    if A_eq is not None:
        for row, rhs in zip(A_eq, b_eq):
            idxs = [i for i, v in enumerate(row) if v != 0]
            vals = [float(row[i]) for i in idxs]
            h.addRow(float(rhs), float(rhs), len(idxs), idxs, vals)
    h.run()
    sol = h.getSolution()
    info = h.getInfo()
    success = (h.getModelStatus() == highspy.HighsModelStatus.kOptimal)
    return {
        "status": int(h.getModelStatus()),
        "fun": float(info.objective_function_value) if success else None,
        "x": list(sol.col_value) if success else None,
        "success": success,
        "backend_used": "highspy",
        "message": str(h.getModelStatus()),
    }


def _lp_pulp(c, A_ub, b_ub, A_eq, b_eq, bounds) -> dict:
    import pulp
    n = len(c)
    prob = pulp.LpProblem("lp", pulp.LpMinimize)
    xs = []
    for i in range(n):
        lo = hi = None
        if bounds is not None and bounds[i] is not None:
            lo, hi = bounds[i]
        xs.append(pulp.LpVariable(f"x{i}", lowBound=lo, upBound=hi))
    prob += pulp.lpSum(float(c[i]) * xs[i] for i in range(n))
    if A_ub is not None:
        for row, rhs in zip(A_ub, b_ub):
            prob += pulp.lpSum(float(row[i]) * xs[i] for i in range(n)) <= float(rhs)
    if A_eq is not None:
        for row, rhs in zip(A_eq, b_eq):
            prob += pulp.lpSum(float(row[i]) * xs[i] for i in range(n)) == float(rhs)
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    success = pulp.LpStatus[status] == "Optimal"
    return {
        "status": int(status),
        "fun": float(pulp.value(prob.objective)) if success else None,
        "x": [float(v.value()) for v in xs] if success else None,
        "success": success,
        "backend_used": "pulp",
        "message": pulp.LpStatus[status],
    }


# ---------------------------------------------------------------------------
# 2. Mixed-integer programming
# ---------------------------------------------------------------------------

_MIP_PREFERENCE = ("pyscipopt", "ortools", "highspy", "pulp")


def solve_mip(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
              integrality=None, bounds=None,
              backend: Optional[str] = None) -> dict:
    """Solve a mixed-integer program: minimize c.x with integrality mask.

    Parameters
    ----------
    integrality : 0/1 vector of length n; 1 means variable is integer.
                  None => all-continuous (equivalent to LP).
    Other args  : same as solve_lp.

    Returns
    -------
    dict with keys: status, fun, x, success, backend_used.
    """
    chosen = _pick_backend("MIP", backend, _MIP_PREFERENCE)
    if integrality is None:
        integrality = [0] * len(c)
    if chosen == "pyscipopt":
        return _mip_scip(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds)
    if chosen == "ortools":
        return _mip_ortools(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds)
    if chosen == "highspy":
        return _mip_highspy(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds)
    if chosen == "pulp":
        return _mip_pulp(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds)
    raise ValueError(f"Unhandled MIP backend {chosen}")


def _mip_scip(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds) -> dict:
    from pyscipopt import Model
    m = Model("mip")
    m.hideOutput()
    n = len(c)
    xs = []
    for i in range(n):
        lo, hi = (None, None)
        if bounds is not None and bounds[i] is not None:
            lo, hi = bounds[i]
        kwargs = {"name": f"x{i}", "vtype": "I" if integrality[i] else "C"}
        if lo is not None:
            kwargs["lb"] = lo
        if hi is not None:
            kwargs["ub"] = hi
        xs.append(m.addVar(**kwargs))
    m.setObjective(sum(float(c[i]) * xs[i] for i in range(n)), "minimize")
    if A_ub is not None:
        for row, rhs in zip(A_ub, b_ub):
            m.addCons(sum(float(row[i]) * xs[i] for i in range(n)) <= float(rhs))
    if A_eq is not None:
        for row, rhs in zip(A_eq, b_eq):
            m.addCons(sum(float(row[i]) * xs[i] for i in range(n)) == float(rhs))
    m.optimize()
    success = m.getStatus() == "optimal"
    return {
        "status": m.getStatus(),
        "fun": float(m.getObjVal()) if success else None,
        "x": [float(m.getVal(v)) for v in xs] if success else None,
        "success": success,
        "backend_used": "pyscipopt",
        "message": m.getStatus(),
    }


def _mip_ortools(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds) -> dict:
    # CP-SAT only handles integer vars; for mixed problems use linear solver.
    if all(integrality):
        return _mip_ortools_cpsat(c, A_ub, b_ub, A_eq, b_eq, bounds)
    return _mip_ortools_linear(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds)


def _mip_ortools_cpsat(c, A_ub, b_ub, A_eq, b_eq, bounds) -> dict:
    from ortools.sat.python import cp_model
    n = len(c)
    m = cp_model.CpModel()
    xs = []
    for i in range(n):
        lo, hi = (-(10**9), 10**9)
        if bounds is not None and bounds[i] is not None:
            blo, bhi = bounds[i]
            if blo is not None:
                lo = int(blo)
            if bhi is not None:
                hi = int(bhi)
        xs.append(m.NewIntVar(lo, hi, f"x{i}"))
    # CP-SAT needs integer coefficients; scale if needed.
    coeffs = [int(round(v)) for v in c]
    m.Minimize(sum(coeffs[i] * xs[i] for i in range(n)))
    if A_ub is not None:
        for row, rhs in zip(A_ub, b_ub):
            m.Add(sum(int(round(row[i])) * xs[i] for i in range(n)) <= int(round(rhs)))
    if A_eq is not None:
        for row, rhs in zip(A_eq, b_eq):
            m.Add(sum(int(round(row[i])) * xs[i] for i in range(n)) == int(round(rhs)))
    s = cp_model.CpSolver()
    status = s.Solve(m)
    success = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    return {
        "status": int(status),
        "fun": float(s.ObjectiveValue()) if success else None,
        "x": [float(s.Value(v)) for v in xs] if success else None,
        "success": success,
        "backend_used": "ortools",
        "message": s.StatusName(status),
    }


def _mip_ortools_linear(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds) -> dict:
    from ortools.linear_solver import pywraplp
    s = pywraplp.Solver.CreateSolver("CBC_MIXED_INTEGER_PROGRAMMING")
    if s is None:
        raise ValueError("OR-Tools CBC backend unavailable")
    inf = s.infinity()
    n = len(c)
    xs = []
    for i in range(n):
        lo, hi = -inf, inf
        if bounds is not None and bounds[i] is not None:
            blo, bhi = bounds[i]
            if blo is not None:
                lo = float(blo)
            if bhi is not None:
                hi = float(bhi)
        v = s.IntVar(lo, hi, f"x{i}") if integrality[i] else s.NumVar(lo, hi, f"x{i}")
        xs.append(v)
    obj = s.Objective()
    for i in range(n):
        obj.SetCoefficient(xs[i], float(c[i]))
    obj.SetMinimization()
    if A_ub is not None:
        for row, rhs in zip(A_ub, b_ub):
            ct = s.Constraint(-inf, float(rhs))
            for i in range(n):
                ct.SetCoefficient(xs[i], float(row[i]))
    if A_eq is not None:
        for row, rhs in zip(A_eq, b_eq):
            ct = s.Constraint(float(rhs), float(rhs))
            for i in range(n):
                ct.SetCoefficient(xs[i], float(row[i]))
    status = s.Solve()
    success = status == pywraplp.Solver.OPTIMAL
    return {
        "status": int(status),
        "fun": float(s.Objective().Value()) if success else None,
        "x": [float(v.solution_value()) for v in xs] if success else None,
        "success": success,
        "backend_used": "ortools",
        "message": "OPTIMAL" if success else f"status={status}",
    }


def _mip_highspy(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds) -> dict:
    # Use scipy.optimize.milp if available — it bridges to HiGHS and accepts
    # an integrality mask directly.
    if not is_available("scipy"):
        raise ValueError("highspy MIP path requires scipy.optimize.milp")
    from scipy.optimize import milp, LinearConstraint, Bounds
    import numpy as np
    n = len(c)
    constraints = []
    if A_ub is not None and len(A_ub) > 0:
        constraints.append(LinearConstraint(A_ub, -np.inf, b_ub))
    if A_eq is not None and len(A_eq) > 0:
        constraints.append(LinearConstraint(A_eq, b_eq, b_eq))
    if bounds is None:
        b_obj = Bounds(-np.inf, np.inf)
    else:
        lo = [b[0] if b and b[0] is not None else -np.inf for b in bounds]
        hi = [b[1] if b and b[1] is not None else np.inf for b in bounds]
        b_obj = Bounds(lo, hi)
    res = milp(c=c, constraints=constraints if constraints else None,
               integrality=integrality, bounds=b_obj)
    return {
        "status": int(res.status),
        "fun": float(res.fun) if res.fun is not None else None,
        "x": list(res.x) if res.x is not None else None,
        "success": bool(res.success),
        "backend_used": "highspy",
        "message": str(res.message),
    }


def _mip_pulp(c, A_ub, b_ub, A_eq, b_eq, integrality, bounds) -> dict:
    import pulp
    n = len(c)
    prob = pulp.LpProblem("mip", pulp.LpMinimize)
    xs = []
    for i in range(n):
        lo = hi = None
        if bounds is not None and bounds[i] is not None:
            lo, hi = bounds[i]
        cat = "Integer" if integrality[i] else "Continuous"
        xs.append(pulp.LpVariable(f"x{i}", lowBound=lo, upBound=hi, cat=cat))
    prob += pulp.lpSum(float(c[i]) * xs[i] for i in range(n))
    if A_ub is not None:
        for row, rhs in zip(A_ub, b_ub):
            prob += pulp.lpSum(float(row[i]) * xs[i] for i in range(n)) <= float(rhs)
    if A_eq is not None:
        for row, rhs in zip(A_eq, b_eq):
            prob += pulp.lpSum(float(row[i]) * xs[i] for i in range(n)) == float(rhs)
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    success = pulp.LpStatus[status] == "Optimal"
    return {
        "status": int(status),
        "fun": float(pulp.value(prob.objective)) if success else None,
        "x": [float(v.value()) for v in xs] if success else None,
        "success": success,
        "backend_used": "pulp",
        "message": pulp.LpStatus[status],
    }


# ---------------------------------------------------------------------------
# 3. Constraint programming (CP-SAT)
# ---------------------------------------------------------------------------

_CP_PREFERENCE = ("ortools",)


def solve_cp(model_fn: Callable[[Any], None],
             backend: Optional[str] = None) -> dict:
    """Solve a CP-SAT model built by `model_fn(model)`.

    Parameters
    ----------
    model_fn : callable receiving an `ortools.sat.python.cp_model.CpModel`.
               Must add variables and constraints; may set an objective.
               Should return a dict {var_name: var} OR set them as
               attributes — the solver returns whatever the callback
               yielded as `solution_dict` if it returned a mapping.

    Returns
    -------
    dict with keys: status, objective_value, solution_dict, backend_used.

    Example
    -------
    >>> def build(m):
    ...     x = m.NewIntVar(0, 10, 'x'); y = m.NewIntVar(0, 10, 'y')
    ...     m.Add(x + y == 7); m.Add(x - y == 1)
    ...     return {'x': x, 'y': y}
    >>> solve_cp(build)['solution_dict']
    {'x': 4, 'y': 3}
    """
    chosen = _pick_backend("CP", backend, _CP_PREFERENCE)
    if chosen != "ortools":
        raise ValueError(f"Unsupported CP backend {chosen}")
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    var_map = model_fn(m)
    s = cp_model.CpSolver()
    status = s.Solve(m)
    success = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    sol_dict = None
    if success and isinstance(var_map, dict):
        sol_dict = {k: int(s.Value(v)) for k, v in var_map.items()}
    obj_val = None
    try:
        obj_val = float(s.ObjectiveValue())
    except Exception:
        pass
    return {
        "status": s.StatusName(status),
        "objective_value": obj_val,
        "solution_dict": sol_dict,
        "backend_used": "ortools",
    }


# ---------------------------------------------------------------------------
# 4. SAT
# ---------------------------------------------------------------------------

_SAT_PREFERENCE = ("pysat", "z3")


def solve_sat(clauses: Sequence[Sequence[int]],
              backend: Optional[str] = None) -> dict:
    """Solve a CNF SAT problem given DIMACS-style clauses.

    Parameters
    ----------
    clauses : list of lists of nonzero ints. Positive int = positive literal
              for variable abs(int); negative int = negated literal.

    Returns
    -------
    dict with keys: sat (bool), model (list[int] or None), backend_used.
    Each entry in `model` is signed: +k means var k true, -k means false.

    Example
    -------
    >>> solve_sat([[1, 2], [-1], [-2, 3]])['sat']
    True
    """
    chosen = _pick_backend("SAT", backend, _SAT_PREFERENCE)
    if chosen == "pysat":
        from pysat.solvers import Glucose3
        g = Glucose3()
        try:
            for cl in clauses:
                g.add_clause(list(cl))
            sat = g.solve()
            model = list(g.get_model()) if sat else None
        finally:
            g.delete()
        return {"sat": bool(sat), "model": model, "backend_used": "pysat"}
    if chosen == "z3":
        import z3
        s = z3.Solver()
        # Variable id k -> z3 Bool 'v{k}'
        var_ids = sorted({abs(lit) for cl in clauses for lit in cl})
        bools = {k: z3.Bool(f"v{k}") for k in var_ids}
        for cl in clauses:
            terms = []
            for lit in cl:
                if lit > 0:
                    terms.append(bools[lit])
                else:
                    terms.append(z3.Not(bools[-lit]))
            s.add(z3.Or(*terms))
        result = s.check()
        sat = (result == z3.sat)
        model = None
        if sat:
            mdl = s.model()
            model = []
            for k in var_ids:
                v = mdl[bools[k]]
                # Unassigned vars default to True (arbitrary).
                signed = k if (v is None or bool(v)) else -k
                model.append(signed)
        return {"sat": sat, "model": model, "backend_used": "z3"}
    raise ValueError(f"Unhandled SAT backend {chosen}")


# ---------------------------------------------------------------------------
# 5. SMT (Z3)
# ---------------------------------------------------------------------------

_SMT_PREFERENCE = ("z3",)


def solve_smt(formula_or_assertions,
              backend: Optional[str] = None) -> dict:
    """Solve an SMT problem via Z3.

    Parameters
    ----------
    formula_or_assertions : single Z3 formula, or list/tuple of formulas.

    Returns
    -------
    dict with keys: sat (bool), model_dict (or None), backend_used.

    Example
    -------
    >>> import z3
    >>> x = z3.Int('x'); y = z3.Int('y')
    >>> solve_smt([x + y == 10, x - y == 4])['model_dict']
    {'x': 7, 'y': 3}
    """
    chosen = _pick_backend("SMT", backend, _SMT_PREFERENCE)
    if chosen != "z3":
        raise ValueError(f"Unsupported SMT backend {chosen}")
    import z3
    s = z3.Solver()
    if isinstance(formula_or_assertions, (list, tuple)):
        for f in formula_or_assertions:
            s.add(f)
    else:
        s.add(formula_or_assertions)
    result = s.check()
    sat = (result == z3.sat)
    model_dict = None
    if sat:
        mdl = s.model()
        model_dict = {}
        for d in mdl.decls():
            v = mdl[d]
            try:
                if v.is_int():
                    model_dict[d.name()] = v.as_long()
                elif z3.is_rational_value(v):
                    num = v.numerator_as_long()
                    den = v.denominator_as_long()
                    model_dict[d.name()] = num / den if den != 1 else num
                elif z3.is_bool(v):
                    model_dict[d.name()] = bool(v)
                else:
                    model_dict[d.name()] = str(v)
            except Exception:
                model_dict[d.name()] = str(v)
    return {"sat": sat, "model_dict": model_dict, "backend_used": "z3"}


# ---------------------------------------------------------------------------
# 6. Convex (CVXPY)
# ---------------------------------------------------------------------------

_CVX_PREFERENCE = ("cvxpy",)


def solve_convex(objective_fn, constraints=None, variables=None,
                 backend: Optional[str] = None) -> dict:
    """Solve a convex optimization problem via CVXPY.

    Two calling modes:

    1) Pre-built mode: pass a `cvxpy.Minimize`/`cvxpy.Maximize` objective
       and a list of constraints. `variables` is then a dict
       {name: cvxpy.Variable} whose values are reported in `solution`.

    2) Builder mode: pass `variables` as a dict {name: shape_or_int}, and
       `objective_fn(vars_dict)` returns (cvxpy_objective, [constraints]).

    Returns
    -------
    dict with keys: status, value, solution, backend_used.
    `solution` is {name: numpy.ndarray or float}.

    Example (pre-built)
    -------
    >>> import cvxpy as cp, numpy as np
    >>> x = cp.Variable(2)
    >>> obj = cp.Minimize(cp.sum_squares(x - np.array([1.0, 2.0])))
    >>> solve_convex(obj, constraints=[x >= 0],
    ...              variables={'x': x})['value']
    0.0
    """
    chosen = _pick_backend("Convex", backend, _CVX_PREFERENCE)
    if chosen != "cvxpy":
        raise ValueError(f"Unsupported convex backend {chosen}")
    import cvxpy as cp

    # Mode 2: builder
    if callable(objective_fn) and not isinstance(objective_fn, (cp.Minimize, cp.Maximize)):
        if variables is None:
            raise ValueError(
                "Builder mode requires variables={name: shape_or_int}")
        var_dict = {}
        for name, shape in variables.items():
            if isinstance(shape, int):
                var_dict[name] = cp.Variable(shape) if shape > 1 else cp.Variable()
            elif shape is None or shape == ():
                var_dict[name] = cp.Variable()
            else:
                var_dict[name] = cp.Variable(shape)
        obj, cons = objective_fn(var_dict)
        prob = cp.Problem(obj, list(cons) if cons is not None else [])
    else:
        # Mode 1: pre-built objective
        if not isinstance(objective_fn, (cp.Minimize, cp.Maximize)):
            raise ValueError(
                "objective_fn must be a cvxpy.Minimize/Maximize or a callable")
        var_dict = variables or {}
        prob = cp.Problem(objective_fn, list(constraints or []))

    prob.solve()
    sol = {}
    for name, v in var_dict.items():
        try:
            val = v.value
            if val is None:
                sol[name] = None
            else:
                # Scalar collapse for shape ()
                try:
                    if hasattr(val, "shape") and val.shape == ():
                        sol[name] = float(val)
                    else:
                        sol[name] = val
                except Exception:
                    sol[name] = val
        except Exception:
            sol[name] = None
    return {
        "status": str(prob.status),
        "value": float(prob.value) if prob.value is not None else None,
        "solution": sol,
        "backend_used": "cvxpy",
    }


# ---------------------------------------------------------------------------
# 7. Capability listing
# ---------------------------------------------------------------------------

def installed_solvers() -> dict:
    """Return available backends per category.

    Example
    -------
    >>> installed_solvers()
    {'lp': ['highspy', 'scipy', 'pulp'],
     'mip': ['pyscipopt', 'ortools', 'highspy', 'pulp'],
     'cp': ['ortools'], 'sat': ['pysat', 'z3'],
     'smt': ['z3'], 'convex': ['cvxpy']}
    """
    return {
        "lp": [b for b in _LP_PREFERENCE if is_available(b)],
        "mip": [b for b in _MIP_PREFERENCE if is_available(b)],
        "cp": [b for b in _CP_PREFERENCE if is_available(b)],
        "sat": [b for b in _SAT_PREFERENCE if is_available(b)],
        "smt": [b for b in _SMT_PREFERENCE if is_available(b)],
        "convex": [b for b in _CVX_PREFERENCE if is_available(b)],
    }


__all__ = [
    "solve_lp", "solve_mip", "solve_cp",
    "solve_sat", "solve_smt", "solve_convex",
    "installed_solvers",
]
