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

STATUS: the ill-conditioned case was REVIEWED AND INVALIDATED (ELEN-TECHNE-38, METHOD-FLAW,
invalidates-claim; Elenchus, 1912d823e). Version 1 reported a candidate gap that was an
unnormalised objective — a missing preprocessing step in my own call, worth $0 to fix. Three
further defects are now repaired, and the worst of them was not the one the review was filed
about: the failure criterion was STATUS-ONLY, so a solver returning a confidently wrong number
while reporting `optimal` would have scored a PASS. SCS does exactly that.

WHAT I TAKE FROM IT, since version 1 did carry a caveat saying it might be badly posed. The
caveat was correct and insufficient. Three of the four defects were computable before the fixture
was ever run — a closed-form optimum, a correctness check, a seed sweep — and labelling the
output provisional did not cause any of them to happen. A caveat buys time, not truth; the fix
for "this might be wrong in a way I cannot see" is an instrument that would notice, not a
sentence saying so.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np

FREE_SOLVERS = ("CLARABEL", "SCS")
AUTHORITY_THETA_C5 = 5 ** 0.5     # Lovasz theta of the 5-cycle

#: A relative error above this is WRONG under any requirement anyone would set --
#: it is worse than two significant digits. It is NOT an accuracy requirement and
#: must not be read as one: nobody has declared one (see ACCURACY_REQUIREMENT
#: below). It exists only to separate "solver returned the answer" from "solver
#: returned a confident wrong number", and `threshold_robustness` in the output
#: measures how far it could move without changing a single classification.
#: One bar governs every arm (A, B and C) since TECHNE-45; a fixture with a different
#: bar per arm would be choosing its thresholds after seeing what each arm achieves.
SILENTLY_WRONG_REL = 1e-2


class _ThetaProblem:
    """The Lovasz theta SDP for adjacency A, keeping hold of the pieces the
    CERTIFICATE needs afterwards: the variable, the edge list, and the edge
    constraint whose duals seed the upper bound.

    The edge constraints are one vectorised equality `X[ei, ej] == 0` rather than
    one constraint per edge (the 2026-09-10 form). Same problem; the dual comes
    back as one vector aligned with (ei, ej), which is what `certificate` reads.
    """

    def __init__(self, A: np.ndarray):
        import cvxpy as cp
        n = A.shape[0]
        self.n = n
        self.ei, self.ej = np.where(np.triu(A, 1) > 0)
        self.X = cp.Variable((n, n), symmetric=True)
        self.edge_con = self.X[self.ei, self.ej] == 0
        self.prob = cp.Problem(cp.Maximize(cp.sum(self.X)),
                               [self.X >> 0, cp.trace(self.X) == 1, self.edge_con])

    def solve(self, solver: str, **kw):
        v = self.prob.solve(solver=solver, **kw)
        return v, self.prob.status

    def certificate(self) -> dict | None:
        """[lb, ub] bracketing theta, computed by numpy from what the solver RETURNED
        and never from what it REPORTED.

        lb: the returned X made exactly feasible -- edge entries zeroed, then
            |lambda_min| * I added if lambda_min < 0 (a shift keeps the edges at
            zero; a clip does not), trace rescaled to 1. sum(X') <= theta whatever
            the solver said.
        ub: Lovasz's theta_3 form -- for ANY symmetric Y supported on the edge set,
            theta <= lambda_max(J + Y). The direction of Y is the solver's dual
            vector for the edge constraints; the scalar in front of it is chosen by a
            1-D minimisation of lambda_max, which is convex in that scalar. The
            bound is valid at every scalar, so a dual-scaling convention (cvxpy
            reports 2y for a symmetric-variable equality) cannot make it wrong,
            only loose.
        Returns None when the solver handed back no X or no duals; the caller
        records UNCERTIFIED rather than inventing a bracket.
        """
        Xv = self.X.value
        y = self.edge_con.dual_value
        if Xv is None or y is None:
            return None
        Xv = np.asarray(Xv, dtype=float)
        if not np.all(np.isfinite(Xv)):
            return None
        n = self.n
        Xp = (Xv + Xv.T) / 2
        Xp[self.ei, self.ej] = 0.0
        Xp[self.ej, self.ei] = 0.0
        # Make it PSD by SHIFTING, never by eigen-clipping. The first version
        # clipped negative eigenvalues and reconstructed; the reconstruction puts
        # small nonzeros back on the edges, so "feasible by construction" was
        # false, and on Petersen with SCS the "lower bound" came out ABOVE the
        # literature value 4 (4.000018). The bound control caught it. Adding
        # |lambda_min| * I keeps every off-diagonal entry, hence every edge, exactly
        # zero, and the result is PSD to the accuracy of eigvalsh.
        lam_min = float(np.linalg.eigvalsh(Xp)[0])
        if lam_min < 0:
            Xp = Xp + (-lam_min) * np.eye(n)
        tr = float(np.trace(Xp))
        if not tr > 0:
            return None
        Xp /= tr
        lb = float(Xp.sum())

        y = np.asarray(y, dtype=float).ravel()
        if not np.all(np.isfinite(y)) or y.shape[0] != self.ei.shape[0]:
            return None
        Y0 = np.zeros((n, n))
        Y0[self.ei, self.ej] = y
        Y0 = Y0 + Y0.T
        J = np.ones((n, n))

        def lam_max(t: float) -> float:
            return float(np.linalg.eigvalsh(J + t * Y0)[-1])

        from scipy.optimize import minimize_scalar
        cands = [(-1.0, lam_max(-1.0)), (-0.5, lam_max(-0.5)), (0.0, lam_max(0.0)),
                 (0.5, lam_max(0.5)), (1.0, lam_max(1.0))]
        t_best, ub = min(cands, key=lambda c: c[1])
        try:
            r = minimize_scalar(lam_max, bounds=(t_best - 1.0, t_best + 1.0),
                                method="bounded", options={"xatol": 1e-10})
            if np.isfinite(r.fun) and r.fun < ub:
                t_best, ub = float(r.x), float(r.fun)
        except Exception:                                        # noqa: BLE001
            pass
        return {"lb": lb, "ub": ub, "dual_scale": t_best,
                "width_rel": (ub - lb) / abs(ub) if ub else None,
                "primal_projection_moved": float(np.abs(Xp - (Xv + Xv.T) / 2).max())}


def _theta_problem(A: np.ndarray) -> _ThetaProblem:
    return _ThetaProblem(A)


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


# ---------------------------------------------------------------------------
# Graph families with a CLOSED-FORM theta, so the scale arm has a ground truth
# the solver under test did not supply. All three are vertex-transitive, where
# Lovasz's bound theta(G) = -n*lambda_min(A) / (lambda_max(A) - lambda_min(A))
# is attained for edge-transitive graphs; the values below are the standard
# ones (Lovasz 1979 for cycles and Kneser; Paley by self-complementarity,
# theta(G)*theta(complement G) = n for vertex-transitive G).
# ---------------------------------------------------------------------------

def _odd_cycle_theta(n: int) -> float:
    if n % 2 == 0:
        raise ValueError("closed form is for ODD cycles")
    c = float(np.cos(np.pi / n))
    return n * c / (1 + c)


def _paley(p: int) -> np.ndarray:
    """Paley graph on GF(p), p prime, p = 1 mod 4: i ~ j iff i - j is a nonzero square."""
    if p % 4 != 1 or any(p % q == 0 for q in range(2, int(p ** 0.5) + 1)):
        raise ValueError("Paley needs a prime p = 1 (mod 4)")
    squares = {(x * x) % p for x in range(1, p)}
    A = np.zeros((p, p))
    for i in range(p):
        for j in range(i + 1, p):
            if (i - j) % p in squares:
                A[i, j] = A[j, i] = 1
    return A


def _paley_theta(p: int) -> float:
    return float(p) ** 0.5


def _kneser(m: int, k: int) -> np.ndarray:
    """Kneser K(m, k): vertices are the k-subsets of an m-set, adjacent iff disjoint."""
    from itertools import combinations
    verts = list(combinations(range(m), k))
    sets = [frozenset(v) for v in verts]
    n = len(verts)
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if not (sets[i] & sets[j]):
                A[i, j] = A[j, i] = 1
    return A


def _kneser_theta(m: int, k: int) -> float:
    from math import comb
    return float(comb(m - 1, k - 1))


#: The scale arm's closed-form families, sized beside the existing random graphs.
CLOSED_FORM_FAMILIES = (
    ("odd_cycle", 21, lambda: _cycle(21), _odd_cycle_theta(21)),
    ("odd_cycle", 61, lambda: _cycle(61), _odd_cycle_theta(61)),
    ("odd_cycle", 121, lambda: _cycle(121), _odd_cycle_theta(121)),
    ("paley", 29, lambda: _paley(29), _paley_theta(29)),
    ("paley", 61, lambda: _paley(61), _paley_theta(61)),
    ("paley", 113, lambda: _paley(113), _paley_theta(113)),
    ("kneser", (7, 2), lambda: _kneser(7, 2), _kneser_theta(7, 2)),
    ("kneser", (9, 3), lambda: _kneser(9, 3), _kneser_theta(9, 3)),
    ("kneser", (10, 3), lambda: _kneser(10, 3), _kneser_theta(10, 3)),
)

#: Tolerance, relative to ub, for "value lies inside its own certificate" under
#: the PREREGISTERED rule (roles/Techne/journal/2026-09-11.md). Kept, and every row
#: still reports its class under it, because the rule was AMENDED after a control
#: fired -- see _classify_certified.
CERT_INSIDE_TOL = 1e-6


def _classify_certified_prereg(status, value, cert, bar=SILENTLY_WRONG_REL):
    """The rule exactly as preregistered: inside [lb - 1e-6 ub, ub + 1e-6 ub] and
    width <= bar is CERTIFIED; outside is SILENTLY_WRONG; inside-but-loose is
    INDETERMINATE. Retained verbatim so the amendment below is auditable."""
    if value is None or not np.isfinite(value):
        return "DECLARED_FAILURE" if status != "optimal" else "OPTIMAL_BUT_NO_VALUE"
    if status != "optimal":
        return "DECLARED_FAILURE"
    if cert is None:
        return "UNCERTIFIED"
    lb, ub = cert["lb"], cert["ub"]
    tol = CERT_INSIDE_TOL * abs(ub)
    if not (lb - tol <= value <= ub + tol):
        return "SILENTLY_WRONG"
    if cert["width_rel"] is None or cert["width_rel"] > bar:
        return "INDETERMINATE"
    return "CERTIFIED"


CERTIFICATE_RULE_AMENDMENT = (
    "AMENDED 2026-09-11 AFTER A CONTROL FIRED, before the fixture was run. The "
    "preregistered rule held a certificate-scored row to a 1e-6 'inside' tolerance "
    "while holding a closed-form row to the 1e-2 bar -- two standards, contradicting "
    "the same preregistration's 'one bar governs every arm'. The control that exposed "
    "it: SCS on a 14-vertex random graph reported 6.0000632 against a certified "
    "bracket [5.99989, 6.00000001]; the preregistered rule called that SILENTLY_WRONG "
    "(1.05e-5 above ub) while the closed-form rule would call the identical error "
    "CORRECT. The amended rule judges the WORST-CASE error of the value against every "
    "theta in the bracket, at the one bar. Both classes are recorded on every row "
    "(certificate_class, certificate_class_prereg); the preregistered class is not "
    "deleted, and the fact it was pointing at -- a reported objective that no feasible "
    "X can attain -- is kept as reported_value_outside_certificate_rel.")


def _classify_certified(status, value, cert, bar=SILENTLY_WRONG_REL):
    """The certificate classes (amended rule; CERTIFICATE_RULE_AMENDMENT says why).

        err_bound = max(|value - lb|, |value - ub|) / |ub|   worst case over theta in [lb, ub]
        outside   = max(lb - value, value - ub, 0) / |ub|   how far the value leaves the bracket

        CERTIFIED       err_bound <= bar    (the value is within the bar of EVERY theta the
                                             certificate allows)
        SILENTLY_WRONG  outside  >  bar     (status optimal, value farther than the bar from
                                             any theta the certificate allows)
        INDETERMINATE   otherwise           (the bracket is too loose to certify at the bar,
                                             or the value sits within the bar of the bracket
                                             but not of every point in it)

    The two INSTRUMENT branches stay distinct from the solver branches: INDETERMINATE
    and UNCERTIFIED are never counted as passes."""
    if value is None or not np.isfinite(value):
        return "DECLARED_FAILURE" if status != "optimal" else "OPTIMAL_BUT_NO_VALUE"
    if status != "optimal":
        return "DECLARED_FAILURE"
    if cert is None:
        return "UNCERTIFIED"
    lb, ub = cert["lb"], cert["ub"]
    if not ub:
        return "INDETERMINATE"
    err_bound = max(abs(value - lb), abs(value - ub)) / abs(ub)
    outside = max(lb - value, value - ub, 0.0) / abs(ub)
    if err_bound <= bar:
        return "CERTIFIED"
    if outside > bar:
        return "SILENTLY_WRONG"
    return "INDETERMINATE"


def _certificate_error_fields(value, cert) -> dict:
    """The numbers the amended rule reads, recorded on the row so a reader can
    re-derive the class without trusting it."""
    if value is None or cert is None or not cert.get("ub"):
        return {}
    lb, ub = cert["lb"], cert["ub"]
    return {"certified_error_bound_rel": max(abs(value - lb), abs(value - ub)) / abs(ub),
            "reported_value_outside_certificate_rel": max(lb - value, value - ub, 0.0) / abs(ub)}


def _old_criterion_failed(status) -> bool:
    """The criterion arms A and B used before TECHNE-45, kept so the receipt can say
    which rows it would have scored differently. It reads only the status string."""
    return status not in ("optimal",)


#: The eps in X >> eps I. Part of the problem statement, so the closed form below
#: depends on it and it is named rather than inlined twice.
ILLCOND_EPS = 1e-6



def _illcond_data(m: int, spread_log10: float, seed: int):
    """C with spectrum spanning 10^spread_log10, and the problem's EXACT optimum.

    THE CLOSED FORM, and why this fixture now carries one. Minimise tr(CX) over
    X >> eps*I, tr X = 1. Substitute X = eps*I + Y with Y >> 0 and tr Y = 1 - m*eps:

        tr(CX) = eps*tr(C) + tr(CY),  and  min{tr(CY) : Y >> 0, tr Y = t} = t*lambda_min(C)

    so  p* = eps*tr(C) + (1 - m*eps)*lambda_min(C),  attained at eps*I plus
    (1 - m*eps) times the projector onto a minimal eigenvector.

    WHAT WAS HERE BEFORE WAS THE WRONG KIND OF OBJECT. This function used to return
    tr(C)/m -- the objective value AT the Slater point X = I/m. That is an UPPER
    BOUND, and at spread 1e10 it is 33,332x the true optimum. Comparing a solver's
    answer against it cannot distinguish a correct answer from a wrong one, which
    is exactly what the fixture needed to do. Elenchus (ELEN-TECHNE-38) found this;
    the derivation above is theirs, re-derived and verified here.
    """
    rng = np.random.default_rng(seed)
    d = np.logspace(0, spread_log10, m)
    Q = np.linalg.qr(rng.standard_normal((m, m)))[0]
    C = Q @ np.diag(d) @ Q.T
    ev = np.linalg.eigvalsh(C)
    p_star = ILLCOND_EPS * float(np.trace(C)) + (1 - m * ILLCOND_EPS) * float(ev[0])
    return C, p_star, float(ev[0]), float(ev[-1])


def _illcond_problem(C: np.ndarray, scale: float):
    """The problem with its objective divided by `scale`. Dividing the cost by a
    positive constant is ARGMIN-PRESERVING, so this is the same problem; the
    solution value is recovered by multiplying back."""
    import cvxpy as cp
    m = C.shape[0]
    X = cp.Variable((m, m), symmetric=True)
    return cp.Problem(cp.Minimize(cp.trace((C / scale) @ X)),
                      [X >> np.eye(m) * ILLCOND_EPS, cp.trace(X) == 1]), X


def _normalisers(C: np.ndarray, lam_max: float) -> dict:
    """Candidate cost normalisers. More than one, because a fix that works under
    exactly one choice of normaliser is a coincidence and not a preprocessing
    step."""
    return {"none": 1.0, "lambda_max": lam_max, "frobenius": float(np.linalg.norm(C)),
            "max_abs_entry": float(np.abs(C).max()), "trace": float(np.trace(C))}


def _classify(status, value, p_star, bar=SILENTLY_WRONG_REL):
    """Four outcomes, and the third is the one the old criterion could not see."""
    if value is None or not np.isfinite(value):
        return ("DECLARED_FAILURE" if status not in ("optimal",) else "OPTIMAL_BUT_NO_VALUE"), None
    rel = abs(value - p_star) / abs(p_star)
    if status not in ("optimal",):
        return "DECLARED_FAILURE", rel
    return ("CORRECT" if rel <= bar else "SILENTLY_WRONG"), rel


#: Swept, not picked. Ten seeds is enough to show the first version's seed=7 was a
#: selection artifact; three spreads span the regime the roadmap row cared about.
ILLCOND_SEEDS = tuple(range(10))
ILLCOND_SPREADS = (4.0, 10.0, 14.0)

#: NOBODY HAS DECLARED ONE, and this fixture must not invent one.
ACCURACY_REQUIREMENT = {
    "declared": False,
    "owner": "Harmonia (scopes the requirement) with Aporia (names the consuming problem)",
    "why_it_matters": (
        "'failure' is undefined without it. After normalisation CLARABEL attains roughly 7 "
        "significant digits at low conditioning and roughly 3 from 1e6 upward. Whether 3.5 "
        "digits at 1e10 is a FAILURE is a requirements question, not a solver question, and it "
        "is the only thread here that could still bear on a spend."),
    "and_if_the_requirement_is_a_certificate": (
        "no double-precision solver satisfies it at any price -- MOSEK is float64 -- and the "
        "route is arbitrary precision at $0. That is TECHNE-39, not a purchase."),
}


def _run_illcond(*, spreads, seeds, m: int) -> dict:
    """The ill-conditioned regime, swept over seeds and normalisers, and scored
    against the CLOSED FORM rather than against a status string.

    THREE THINGS THIS DOES THAT THE FIRST VERSION DID NOT, each a defect Elenchus
    found in ELEN-TECHNE-38:

      * SCORES CORRECTNESS. The old criterion was `status not in ("optimal",)`,
        structurally blind to a solver returning a confidently wrong number. SCS
        does exactly that here: after normalisation it reports `optimal` and
        returns 52618 against a true optimum of 18250 -- 188% wrong -- and the old
        fixture would have scored it a PASS. That silent error is the most serious
        thing in the regime, and it was invisible to the instrument that found it.
      * NORMALISES THE COST. C spans 1e0-1e10 while the constraint data is O(1),
        and neither CVXPY nor either solver auto-scales the objective. Dividing C
        by a norm is argmin-preserving and one line. The unscaled arm is KEPT,
        because the contrast is the finding -- but it is labelled a missing
        preprocessing step rather than a capability boundary.
      * SWEEPS SEEDS and reports every one.
    """
    rows = []
    cases = []
    for spread in spreads:
        for seed in seeds:
            C, p_star, _lam_min, lam_max = _illcond_data(m, spread, seed)
            for nname, scale in _normalisers(C, lam_max).items():
                for s in FREE_SOLVERS:
                    prob, _X = _illcond_problem(C, scale)
                    t0 = time.perf_counter()
                    err = None
                    try:
                        prob.solve(solver=s)
                        raw = prob.value
                        value = None if raw is None else float(raw) * scale
                        status = prob.status
                    except Exception as exc:                     # noqa: BLE001
                        value, status = None, "RAISED"
                        err = "%s: %s" % (type(exc).__name__, exc)
                    ms = round((time.perf_counter() - t0) * 1000, 0)
                    klass, rel = _classify(status, value, p_star)
                    if err:
                        klass = "RAISED"
                    digits = None
                    if rel is not None:
                        digits = 16.0 if rel <= 0 else round(float(-np.log10(rel)), 2)
                    row = {"spread_log10": spread, "seed": seed, "normaliser": nname,
                           "solver": s, "status": status, "value": value, "p_star": p_star,
                           "rel_error": rel, "class": klass, "significant_digits": digits,
                           "ms": ms}
                    if err:
                        row["error"] = err
                    rows.append(row)
                    # Only the headline arms reach `cases`, so the top-level table
                    # stays readable; `rows` carries every run.
                    if nname in ("none", "lambda_max"):
                        cases.append(dict(row,
                                          case="C_illcond_1e%d_%s" % (int(spread), nname),
                                          failed=klass != "CORRECT"))
    return {"cases": cases, "rows": rows}


def _scs_tolerance_arm(*, spreads, seeds, m: int) -> dict:
    """IS SCS SILENTLY WRONG, OR IS CVXPY'S DEFAULT TOLERANCE SILENTLY LOOSE?

    The sweep above found SCS reporting `optimal` with a 2%-200% error on almost
    every normalised run, and my first draft of this file wrote that up as a
    finding about SCS. It is not. At eps=1e-9 SCS returns the closed-form optimum,
    so the hazard is the DEFAULT, not the solver -- and the difference decides what
    the fix is: configure the call, rather than replace or buy a solver.

    Keeping the arm because the hazard is real either way: the default is what a
    caller gets, and a caller who checks `status == "optimal"` is told the answer
    is good when it is 188% wrong.

    AND ONE THING WORTH MORE THAN THE REST. At eps=1e-12 SCS says
    `optimal_inaccurate` while being MORE accurate than when it says `optimal`.
    The status string is anti-correlated with accuracy across these settings. That
    is the strongest possible argument against a status-only criterion, and it
    comes from the solver's own reporting rather than from my opinion of it.
    """
    rows = []
    settings = (("default", {}), ("eps_1e-9", {"eps": 1e-9}),
                ("eps_1e-12_200k_iters", {"eps": 1e-12, "max_iters": 200000}))
    for spread in spreads:
        for seed in seeds:
            C, p_star, _lmin, lam_max = _illcond_data(m, spread, seed)
            for label, kw in settings:
                prob, _X = _illcond_problem(C, lam_max)
                t0 = time.perf_counter()
                err = None
                try:
                    prob.solve(solver="SCS", **kw)
                    raw = prob.value
                    value = None if raw is None else float(raw) * lam_max
                    status = prob.status
                except Exception as exc:                         # noqa: BLE001
                    value, status = None, "RAISED"
                    err = "%s: %s" % (type(exc).__name__, exc)
                klass, rel = _classify(status, value, p_star)
                if err:
                    klass = "RAISED"
                row = {"spread_log10": spread, "seed": seed, "setting": label,
                       "status": status, "value": value, "p_star": p_star,
                       "rel_error": rel, "class": klass,
                       "ms": round((time.perf_counter() - t0) * 1000, 0)}
                if err:
                    row["error"] = err
                rows.append(row)

    def rels(label):
        return [r["rel_error"] for r in rows
                if r["setting"] == label and r["rel_error"] is not None]

    summary = {}
    for label, _kw in settings:
        sel = [r for r in rows if r["setting"] == label]
        rr = rels(label)
        summary[label] = {
            "n": len(sel),
            "correct": sum(1 for r in sel if r["class"] == "CORRECT"),
            "silently_wrong": sum(1 for r in sel if r["class"] == "SILENTLY_WRONG"),
            "statuses": sorted({r["status"] for r in sel}),
            "rel_error_min": min(rr) if rr else None,
            "rel_error_max": max(rr) if rr else None,
        }

    worst_default = max(rels("default") or [0])
    best_tight = min(rels("eps_1e-9") or [0])
    return {
        "rows": rows,
        "summary": summary,
        "finding": (
            "SCS's silent error is a DEFAULT-TOLERANCE hazard, not a solver capability limit. "
            "At CVXPY's default settings it reports `optimal` with relative error up to %.3g; at "
            "eps=1e-9 its worst case drops to %.3g or better. So the remedy is to configure the "
            "call, and neither a different solver nor a purchase is implied." % (worst_default,
                                                                                best_tight)),
        "the_status_string_is_anti_correlated_with_accuracy": (
            "at eps=1e-12 SCS reports `optimal_inaccurate` while being MORE accurate than when "
            "it reports `optimal` at the default. A criterion reading the status would prefer "
            "the worse answer. This is the argument against status-only scoring, made by the "
            "solver's own reporting rather than by my opinion of it."),
        "why_this_arm_exists": (
            "my first write-up of the sweep said SCS was silently wrong on 119 of 120 runs, as a "
            "finding about SCS. This arm is the check that stopped it shipping in that form -- "
            "the same class of over-claim the review had just caught me in, one file later."),
    }


def _illcond_summary(rows) -> dict:
    """What the sweep says, computed rather than narrated."""
    def sel(**kw):
        return [r for r in rows if all(r[k] == v for k, v in kw.items())]

    per_norm = {}
    for nname in sorted({r["normaliser"] for r in rows}):
        per_norm[nname] = {
            s: {k: sum(1 for r in sel(normaliser=nname, solver=s) if r["class"] == k)
                for k in ("CORRECT", "SILENTLY_WRONG", "DECLARED_FAILURE", "RAISED")}
            for s in FREE_SOLVERS}

    unscaled = sel(normaliser="none", solver="CLARABEL")
    solved_unscaled = sorted({(r["spread_log10"], r["seed"]) for r in unscaled
                              if r["class"] == "CORRECT"})
    modes = sorted({r["status"] for r in unscaled if r["class"] != "CORRECT"})

    scaled = [r for r in rows if r["normaliser"] != "none"]
    silent = [r for r in scaled if r["class"] == "SILENTLY_WRONG"]
    correct_rels = [r["rel_error"] for r in scaled
                    if r["class"] == "CORRECT" and r["rel_error"]]
    wrong_rels = [r["rel_error"] for r in silent if r["rel_error"]]

    digits_by_spread = {}
    for spread in sorted({r["spread_log10"] for r in rows}):
        d = [r["significant_digits"] for r in sel(spread_log10=spread, solver="CLARABEL")
             if r["normaliser"] != "none" and r["class"] == "CORRECT"
             and r["significant_digits"] is not None]
        if d:
            digits_by_spread["1e%d" % int(spread)] = {"min": round(min(d), 2),
                                                      "max": round(max(d), 2), "n": len(d)}

    return {
        "n_runs": len(rows),
        "per_normaliser_class_counts": per_norm,
        "unscaled_CLARABEL_correct_on": ["spread 1e%d seed %d" % (int(s), d)
                                         for s, d in solved_unscaled],
        "unscaled_CLARABEL_failure_modes": modes,
        "seed_selection_artifact": (
            "the first version hardcoded seed=7 and never reported it. CLARABEL solves the "
            "UNSCALED problem correctly on %d of %d runs, so another seed would have made the "
            "case a PASS and no candidate gap would have been filed. %d distinct non-correct "
            "statuses for one problem shape is a scaling heuristic tipping, not a capability "
            "boundary." % (len(solved_unscaled), len(unscaled), len(modes))),
        "n_silently_wrong_after_normalisation": len(silent),
        "silently_wrong_examples": [
            {"solver": r["solver"], "spread_log10": r["spread_log10"], "seed": r["seed"],
             "normaliser": r["normaliser"], "status": r["status"], "value": r["value"],
             "p_star": r["p_star"], "rel_error": r["rel_error"]} for r in silent[:6]],
        "threshold_robustness": {
            "threshold_used": SILENTLY_WRONG_REL,
            "worst_rel_among_CORRECT": max(correct_rels) if correct_rels else None,
            "best_rel_among_SILENTLY_WRONG": min(wrong_rels) if wrong_rels else None,
            "factor_of_slack_below": (round(SILENTLY_WRONG_REL / max(correct_rels), 1)
                                      if correct_rels else None),
            "factor_of_slack_above": (round(min(wrong_rels) / SILENTLY_WRONG_REL, 1)
                                      if wrong_rels else None),
            "claim": ("a classification is only robust if its threshold sits in a GAP. Both "
                      "edges are reported so a reader can see how far the line could move "
                      "without changing a single classification, instead of taking the choice "
                      "on trust. This is a reporting threshold and NOT an accuracy "
                      "requirement -- see accuracy_requirement."),
        },
        "CLARABEL_significant_digits_after_normalisation": digits_by_spread,
    }


INSTRUMENT_CLASSES = ("INDETERMINATE", "UNCERTIFIED", "OPTIMAL_BUT_NO_VALUE")


def _ab_reclassification(cases: list, previous: dict | None) -> dict:
    """TECHNE-45's receipt: what the correctness criterion says about arms A and B
    beside what the status criterion said, row by row; plus a value-by-value
    comparison against the previously COMMITTED result so any drift from the
    vectorised edge constraint is visible rather than assumed away.
    """
    ab = [c for c in cases if c["case"].startswith(("A_", "B_"))]
    changed = [c for c in ab if bool(c.get("failed")) != bool(c.get("old_criterion_failed"))]
    instr = [c for c in ab if c.get("class") in INSTRUMENT_CLASSES]
    closed = [c for c in ab if "expected" in c]
    certd = [c for c in ab if c.get("certificate") is not None]
    bracket_fail = [c for c in closed if c.get("certificate_brackets_truth") is False]
    prev_rows = {}
    if previous:
        for c in previous.get("cases", []):
            if c["case"].startswith(("A_", "B_")):
                prev_rows[(c["case"], c["solver"])] = c
    drift = []
    for c in ab:
        pc = prev_rows.get((c["case"], c["solver"]))
        if pc is None or pc.get("value") is None or c.get("value") is None:
            continue
        drift.append({"case": c["case"], "solver": c["solver"],
                      "value_previous": pc["value"], "value_now": c["value"],
                      "rel_change": abs(c["value"] - pc["value"]) / max(abs(pc["value"]), 1e-300),
                      "status_previous": pc.get("status"), "status_now": c.get("status"),
                      "failed_previous": pc.get("failed"), "failed_now": c.get("failed")})
    widths = [c["certificate"]["width_rel"] for c in certd
              if c["certificate"].get("width_rel") is not None]
    prereg_diff = [c for c in ab if c.get("certificate_class") is not None
                   and c.get("certificate_class") != c.get("certificate_class_prereg")]
    exceed = [c for c in ab if c.get("reported_value_outside_certificate_rel")]
    return {
        "certificate_rule_amendment": CERTIFICATE_RULE_AMENDMENT,
        "rows_where_prereg_and_amended_certificate_rules_DISAGREE": [
            {"case": c["case"], "solver": c["solver"],
             "certificate_class_prereg": c["certificate_class_prereg"],
             "certificate_class": c["certificate_class"],
             "reported_value_outside_certificate_rel":
                 c.get("reported_value_outside_certificate_rel")} for c in prereg_diff],
        "rows_whose_reported_value_no_feasible_X_attains": [
            {"case": c["case"], "solver": c["solver"], "value": c["value"],
             "ub": c["certificate"]["ub"],
             "outside_rel": c["reported_value_outside_certificate_rel"]} for c in exceed],
        "rule": ("a row FAILS iff its class is not CORRECT (closed form known) or CERTIFIED "
                 "(bracket computed by numpy from the returned matrices). INDETERMINATE and "
                 "UNCERTIFIED are failures of the INSTRUMENT, listed apart, and never a "
                 "candidate gap."),
        "eligible_rows": len(ab),
        "rows_where_old_and_new_criteria_DISAGREE": [
            {"case": c["case"], "solver": c["solver"], "status": c.get("status"),
             "class": c.get("class"), "old_criterion_failed": c.get("old_criterion_failed"),
             "failed_now": c.get("failed")} for c in changed],
        "n_disagree": len(changed),
        "class_counts": {k: sum(1 for c in ab if c.get("class") == k)
                         for k in sorted({c.get("class") for c in ab}, key=str)},
        "instrument_could_not_decide": [
            {"case": c["case"], "solver": c["solver"], "class": c["class"],
             "certificate": c.get("certificate")} for c in instr],
        "certificate_validation_on_closed_forms": {
            "n_closed_form_rows": len(closed),
            "n_with_certificate": sum(1 for c in closed if c.get("certificate") is not None),
            "n_bracket_truth": sum(1 for c in closed if c.get("certificate_brackets_truth")),
            "n_bracket_FAIL": len(bracket_fail),
            "failures": [{"case": c["case"], "solver": c["solver"],
                          "expected": c["expected"], "certificate": c["certificate"]}
                         for c in bracket_fail],
            "reading": ("every closed-form row's certificate must bracket the literature "
                        "value; one that does not voids every certificate-scored row"),
        },
        "certificate_width_rel": {"min": min(widths) if widths else None,
                                  "max": max(widths) if widths else None,
                                  "n": len(widths)},
        "value_drift_vs_previous_committed_result": {
            "n_compared": len(drift),
            "max_rel_change": max((d["rel_change"] for d in drift), default=None),
            "rows": drift,
            "note": ("the edge constraints are now one vectorised equality instead of one "
                     "constraint per edge, so the values are re-measured rather than carried; "
                     "any change is shown here, not assumed to be nil"),
        },
    }


def run_sdp(out_path: str | None, previous_path: str | None = None) -> dict:
    import cvxpy as cp

    previous = None
    for cand in (previous_path, out_path):
        if cand and pathlib.Path(cand).exists():
            try:
                previous = json.loads(pathlib.Path(cand).read_text(encoding="utf-8"))
            except Exception:                                        # noqa: BLE001
                previous = None
            break

    cases = []

    def _theta_case(case: str, A: np.ndarray, truth: float | None, meta: dict) -> None:
        """One theta instance through both free solvers, scored on CORRECTNESS.

        TECHNE-45. Before this, arm A wrote `failed: False` unconditionally (it
        recorded abs_error and then ignored it) and arm B wrote `failed = status
        not in ("optimal",)` with no ground truth at all -- the same blindness
        ELEN-TECHNE-38 found in arm C, unmeasured. Now every row carries a class
        from `_classify` (closed form known) or `_classify_certified` (closed form
        unknown; a numpy-computed bracket instead), a `failed` derived from that
        class, and `old_criterion_failed` so the receipt can show the two side by
        side. The certificate is computed for every row, known truth or not: on
        the closed-form families it is the CHECK that the certificate code brackets
        a value nobody here computed.
        """
        for s in FREE_SOLVERS:
            p = _theta_problem(A)
            t = time.perf_counter()
            row = {"case": case, "solver": s, **meta, "n": int(A.shape[0]),
                   "n_edges": int(p.ei.shape[0])}
            try:
                v, status = p.solve(s)
                row.update({"status": status,
                            "value": None if v is None else float(v),
                            "ms": round((time.perf_counter() - t) * 1000, 1)})
            except Exception as exc:                                  # noqa: BLE001
                row.update({"status": "RAISED", "value": None,
                            "ms": round((time.perf_counter() - t) * 1000, 1),
                            "error": f"{type(exc).__name__}: {exc}", "class": "RAISED",
                            "failed": True, "old_criterion_failed": True})
                cases.append(row)
                continue
            cert = p.certificate()
            row["certificate"] = cert
            row.update(_certificate_error_fields(row["value"], cert))
            row["certificate_class"] = _classify_certified(status, row["value"], cert)
            row["certificate_class_prereg"] = _classify_certified_prereg(status, row["value"],
                                                                         cert)
            if truth is not None:
                row["expected"] = truth
                klass, rel = _classify(status, row["value"], truth)
                row["rel_error"] = rel
                row["abs_error"] = (None if row["value"] is None
                                    else abs(row["value"] - truth))
                row["significant_digits"] = (None if rel is None else
                                             (16.0 if rel <= 0 else
                                              round(float(-np.log10(rel)), 2)))
                # The certificate must bracket the KNOWN value; if it does not, the
                # certificate code is wrong and every certificate-scored row is void.
                row["certificate_brackets_truth"] = (
                    None if cert is None else
                    bool(cert["lb"] - CERT_INSIDE_TOL * abs(cert["ub"]) <= truth
                         <= cert["ub"] + CERT_INSIDE_TOL * abs(cert["ub"])))
                row["class"] = klass
            else:
                row["class"] = row["certificate_class"]
            row["failed"] = row["class"] not in ("CORRECT", "CERTIFIED")
            row["old_criterion_failed"] = _old_criterion_failed(status)
            cases.append(row)

    # A. AUTHORITY ANCHOR. theta(C_5) = sqrt(5). If the free path misses this, nothing else
    #    measured here means anything. Scored against sqrt(5), not against `optimal`.
    _theta_case("A_authority_theta_C5", _cycle(5), AUTHORITY_THETA_C5,
                {"family": "odd_cycle", "param": 5, "truth_source": "Lovasz 1979, closed form"})

    # B. SCALE. Where does the free interior-point path stop being affordable -- and
    #    is what it returns there CORRECT? Two kinds of row:
    #      B_scale_n*      the roadmap's shape (random G(n, 0.3), seed 0), no closed
    #                      form, scored by the numpy certificate;
    #      B_closed_*      vertex-transitive families at comparable n with a closed-form
    #                      theta the solver never saw, scored against it AND certified.
    for n in (20, 60, 120):
        _theta_case(f"B_scale_n{n}", _random_graph(n, 0.3, seed=0), None,
                    {"family": "random_gnp", "param": {"n": n, "p": 0.3, "seed": 0},
                     "truth_source": "none -- certificate only"})
    for fam, param, build, truth in CLOSED_FORM_FAMILIES:
        tag = param if isinstance(param, int) else "%dc%d" % param
        _theta_case(f"B_closed_{fam}_{tag}", build(), truth,
                    {"family": fam, "param": param,
                     "truth_source": {"odd_cycle": "n cos(pi/n)/(1+cos(pi/n)), Lovasz 1979",
                                      "paley": "sqrt(p): self-complementary + vertex-transitive",
                                      "kneser": "C(m-1,k-1), Lovasz 1979"}[fam]})

    # C. CONDITIONING. Rebuilt after ELEN-TECHNE-38 invalidated the first version.
    #    SEEDS ARE SWEPT, NOT PICKED. The old case hardcoded seed=7 and never
    #    reported it; on 2 of 10 seeds of the identical family CLARABEL solves the
    #    unscaled problem and says optimal, so the single instance was a selection
    #    artifact before it was anything else.
    illcond = _run_illcond(spreads=ILLCOND_SPREADS, seeds=ILLCOND_SEEDS, m=30)
    cases.extend(illcond["cases"])

    # D. Is the silent error SCS's, or CVXPY's default tolerance? Three seeds is
    #    enough to separate a solver limit from a settings hazard.
    scs_tol = _scs_tolerance_arm(spreads=ILLCOND_SPREADS, seeds=(0, 3, 7), m=30)

    fails = [c for c in cases if c.get("failed")]
    by_case: dict[str, list] = {}
    for c in cases:
        by_case.setdefault(c["case"], []).append(c)
    # A SOLVER failure on every free solver is a candidate gap. An INSTRUMENT
    # failure (the certificate could not decide) is not: it is listed under
    # techne45.instrument_could_not_decide and counts against the fixture, not
    # against the free path.
    all_free_fail = sorted(k for k, v in by_case.items()
                           if all(x.get("failed") and x.get("class") not in INSTRUMENT_CLASSES
                                  for x in v))
    ab_reclass = _ab_reclassification(cases, previous)

    # A CANDIDATE GAP REQUIRES THE NORMALISED ARM TO FAIL. The unscaled arm failing
    # is a missing preprocessing step in our own call, worth $0 to fix, and the
    # first version of this fixture reported exactly that as a candidate gap.
    illcond_summary = _illcond_summary(illcond["rows"])
    normalised_rows = [r for r in illcond["rows"] if r["normaliser"] != "none"]
    illcond_candidate = sorted({
        "1e%d/seed%d" % (int(s), d)
        for s, d in {(r["spread_log10"], r["seed"]) for r in normalised_rows}
        if all(x["class"] != "CORRECT" for x in normalised_rows
               if x["spread_log10"] == s and x["seed"] == d)})
    all_free_fail = [k for k in all_free_fail if not k.startswith("C_illcond")]
    if illcond_candidate:
        all_free_fail.append("C_illcond(normalised): " + ", ".join(illcond_candidate))

    doc = {
        "schema": "techne.capability_gap_fixture/2",
        "schema_change": ("/2 (TECHNE-45): arms A and B carry class / failed derived from "
                          "correctness (closed form or numpy certificate), old_criterion_failed "
                          "beside it, and nine closed-form scale rows; see techne45"),
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
                    "CANDIDATE GAP in %s" % all_free_fail),
        "techne45": ab_reclass,
        "illcond": illcond_summary,
        "scs_tolerance_arm": {k: v for k, v in scs_tol.items() if k != "rows"},
        "accuracy_requirement": ACCURACY_REQUIREMENT,
        "review": {
            "finding": "ELEN-TECHNE-38, METHOD-FLAW, severity invalidates-claim",
            "by": "Elenchus, commit 1912d823e on elenchus/review-2026-09-11",
            "verdict_on_version_1": "BADLY POSED. Not a capability gap. A purchase may not "
                                    "cite it.",
            "accepted": True,
            "what_survived": (
                "the feasibility claim. X = I/m is STRICTLY feasible -- min eig(I/30 - 1e-6 I) "
                "= 0.0333 > 0, a Slater point -- and trace X = 1 with X >> 1e-6 I makes the "
                "feasible set compact, so the optimum exists and is attained. CLARABEL's "
                "'infeasible_inaccurate' and SCS's 'unbounded' are therefore provably wrong "
                "answers, not hard instances."),
            "four_defects_and_where_each_is_now_fixed": {
                "objective_unnormalised": (
                    "THE ONE THAT INVALIDATES THE CLAIM. C spans 1e0-1e10 while the constraint "
                    "data is O(1), and nothing auto-scales the cost. Dividing C by any norm is "
                    "argmin-preserving and makes CLARABEL return the closed-form optimum. What "
                    "the fixture measured was a missing preprocessing step in MY OWN call, "
                    "worth $0 to fix. FIXED: _normalisers() sweeps five choices and the "
                    "unscaled arm is labelled as the preprocessing contrast."),
                "failure_criterion_was_status_only": (
                    "WORSE THAN THE ONE IT FILED. `status not in ('optimal',)` is structurally "
                    "blind to a confidently wrong number, and SCS returns one: after "
                    "normalisation it says 'optimal' and gives 52618 against a true 18250. The "
                    "old fixture would have scored that a PASS. FIXED: _classify() scores "
                    "against the closed form and SILENTLY_WRONG is its own class."),
                "ground_truth_was_the_wrong_kind_of_object": (
                    "tr(C)/m is the value AT the Slater point -- an upper bound 33,332x the "
                    "true optimum at 1e10. A bound cannot separate a right answer from a wrong "
                    "one. FIXED: _illcond_data() returns the exact optimum "
                    "eps*tr(C) + (1 - m*eps)*lambda_min(C), re-derived and verified here."),
                "seed_selection_artifact": (
                    "seed=7 was hardcoded and never reported, and CLARABEL solves the unscaled "
                    "problem on some seeds of the identical family. FIXED: ILLCOND_SEEDS "
                    "sweeps ten and every run is reported."),
            },
            "my_own_reading": (
                "the caveat on version 1 was correct and insufficient. I wrote that a single "
                "hand-built instance is a CANDIDATE gap and may be badly posed in a way I did "
                "not see -- and that is exactly what happened. But a caveat is not an "
                "instrument: three of the four defects were computable before the fixture was "
                "ever run (a closed form, a correctness check, a seed sweep), and labelling the "
                "result provisional did not make any of them happen. The caveat bought time "
                "rather than truth."),
        },
        "CAVEAT": ("Version 1 of the ill-conditioned case was reviewed and INVALIDATED "
                   "(ELEN-TECHNE-38). This version scores correctness against a closed form, "
                   "normalises the cost, and sweeps seeds. The remaining open question is not "
                   "about solvers: no accuracy requirement has been declared by anyone, so "
                   "'failure' in the high-conditioning regime is still undefined -- see "
                   "accuracy_requirement, which names its owner."),
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
    ap.add_argument("--previous", default=None,
                    help="previously committed result to diff arms A/B against (default: --out)")
    a = ap.parse_args(argv)

    doc = run_sdp(a.out, a.previous)
    print(f"=== capability gap fixture: {a.target} ===")
    print(f"free path       {doc['free_path']['solvers']} (both $0); cvxpy "
          f"{doc['free_path']['cvxpy']}")
    print(f"{'case':<28} {'solver':<9} {'status':<20} {'value':>14} {'ms':>8} "
          f"{'class':<16} failed old")
    for c in doc["cases"]:
        val = c.get("value")
        vs = f"{val:14.6f}" if isinstance(val, float) else f"{str(val):>14}"
        print(f"{c['case']:<28} {c['solver']:<9} {str(c.get('status','ERROR')):<20} {vs} "
              f"{str(c.get('ms','')):>8} {str(c.get('class','')):<16} "
              f"{'YES' if c.get('failed') else '-':<6} "
              f"{'YES' if c.get('old_criterion_failed') else '-'}")
    t45 = doc["techne45"]
    print(f"\nTECHNE-45       {t45['eligible_rows']} A/B rows; old and new criteria disagree on "
          f"{t45['n_disagree']}; classes {t45['class_counts']}")
    cv = t45["certificate_validation_on_closed_forms"]
    print(f"                certificate brackets the literature value on "
          f"{cv['n_bracket_truth']} of {cv['n_closed_form_rows']} closed-form rows "
          f"({cv['n_bracket_FAIL']} FAIL)")
    print(f"\nVERDICT         {doc['verdict']}")
    print(f"                {doc['n_failed']} of {doc['n_cases']} solver-runs failed")
    print(f"CAVEAT          {doc['CAVEAT'][:150]}...")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
