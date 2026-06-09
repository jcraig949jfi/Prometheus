"""Verifier Lens (EXPERIMENTAL) — a deterministic, non-LLM *selector* for the
reasoning-ladder Phase-0 harness.

Doctrine anchor: `harmonia/memory/architecture/topological_falsification_engine.md`,
Invariant §1.1 — **LLM on the mutation side only; never on the selection side.**
This lens is the selection side. There is no model in the loop here: it is a pure
sympy verifier that certifies whether a *claimed* reasoning artifact actually holds.

Design stance — VERIFY, do not RE-DERIVE
----------------------------------------
The cheap, hard-to-fool direction is verification, not re-solving:
  * a claimed root is checked by SUBSTITUTION into the original equation
    (and, for sqrt, by checking the principal-branch domain);
  * a claimed rational identity is checked by EVALUATION at sampled points
    plus a check that the excluded value is correctly excluded;
  * a claimed counterexample is checked by EVALUATING the predicate at it.
Re-deriving with `sp.solve` and string-comparing answers re-introduces the
solver as an oracle and is exactly as fool-able as the thing being graded; it
also inherits every solver bug as a grading bug. We use `solve` ONLY where a
*completeness* certificate (a degree count) is needed to claim `missed_root`,
never to decide whether a claimed root is genuine.

Public interface
----------------
    verify(probe, claimed_answer) -> {
        "valid":  bool | None,   # None == honestly unverifiable (see limits)
        "checks": {...},         # per-root / per-sample evidence
        "kill_pattern": str|None # the failure SHAPE, in the shared kill vocabulary
    }

`valid` semantics:
    True   -> the claim is certified to hold by deterministic substitution/eval.
    False  -> the claim is certified WRONG (a kill_pattern names the shape).
    None   -> the claim is of a form sympy cannot certify (e.g. a true
              universal over an infinite domain). We refuse to rubber-stamp.

Honest limits (where a real SMT/proof backend is required)
----------------------------------------------------------
sympy can VERIFY a concrete witness (a root, a counterexample, an identity on a
sampled cofinite set) but it cannot, in general, PROVE a universally-quantified
statement over an infinite domain. So a conjecture claimed *true* used to return
`valid=None` with kill_pattern="unverifiable_universal".

z3 backend (NEW)
----------------
z3-solver is now installed, and `z3_backend.py` closes part of that gap for the
fragments z3 can DECIDE. To prove `forall n. P(n)` we assert the NEGATION and
check satisfiability: `unsat` => proved; `sat` => refuted (with a concrete
counterexample model); `unknown`/timeout => honestly "unknown" (we never guess).
The conjecture path consults a small cid->predicate registry and:
  * PROVES   `n2_plus_n_even`      (z3: negation unsat over Z)
  * REFUTES  `ab_even_then_both_even` (z3: 2-var negation sat, model counterexample)
  * REFUTES  `n2_n_41_prime`       (primality not z3-posable as a universal, but
             the concrete composite witness n=41 is checked with sympy.isprime)
  * REFUTES  `all_primes_odd`      (the even prime 2, checked with sympy.isprime)
  * leaves   `sum_two_squares`     UNKNOWN (a "true-ish placeholder" in the
             harness: the predicate is not concretely specified, so the
             selection side cannot pose it — honest unknown).

Honest boundary that REMAINS
----------------------------
z3 nonlinear integer arithmetic (NIA) with quantifiers is undecidable in
general, so a genuinely hard nonlinear universal (e.g. positive-integer
a^3+b^3=c^3) returns `unknown` — that is correct behaviour, not a failure.
Primality is not a first-order arithmetic predicate, so the *universal* "all
primes odd" / "n^2+n+41 always prime" cannot be posed to z3 at all; only their
concrete refutations are deterministically checkable. Genuine inductive
universals beyond z3's decidable reach still need a proof assistant (Lean/Coq).
The boundary is marked inline as `# >>> SMT/Lean boundary`.

`certify_universal` and `entails` are re-exported here for use as standalone
primitives (the latter for future R9 lemma-invention grading).
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional

import sympy as sp

# Make the harness importable whether this file is loaded as a package module,
# via `-m`, or as a bare path: ensure the repo root is on sys.path.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Re-use the harness symbols so substitution targets line up exactly with how
# the probes were generated. We import the module (not just symbols) to keep the
# dependency direction explicit: this lens reads FROM the harness, never edits it.
from harmonia.experiments import reasoning_phase0 as rp0

# z3 certification backend (SMT selection-side, NO LLM). Re-export its two
# primitives so callers can use the lens as the single entry point.
from harmonia.experiments.z3_backend import (
    certify_universal,
    decide_conjecture,
    entails,
)

X = rp0.x
Y = rp0.y

# Number of sampled points used to verify a rational identity. Verification (not
# proof): a rational function of bounded degree that agrees with a target at more
# points than its degree is the target on the cofinite domain. We sample well
# past that bound and over rationals to avoid accidental cancellation.
_RATIONAL_SAMPLES = 25


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _probe_var(probe) -> sp.Symbol:
    """The free variable the probe's expression lives in.

    R0 adversarial renames the variable to ``y`` and records it as
    ``data['var']``; everything else uses ``x``. We honour the recorded var and
    otherwise read it off the expression so substitution never silently no-ops.
    """
    if "var" in probe.data:
        return probe.data["var"]
    expr = probe.data.get("expr")
    if expr is not None:
        syms = list(getattr(expr, "free_symbols", []))
        if syms:
            return syms[0]
    return X


def _to_root_list(claimed) -> Optional[list]:
    """Normalise a claimed root set into a list of sympy values, or None."""
    if claimed is None:
        return None
    if isinstance(claimed, (list, tuple, set)):
        items = list(claimed)
    else:
        items = [claimed]
    out = []
    for it in items:
        try:
            out.append(sp.nsimplify(it) if not isinstance(it, sp.Basic) else it)
        except Exception:
            out.append(sp.sympify(it))
    return out


def _is_zero(expr) -> Optional[bool]:
    """Deterministic exact zero-test. Returns True/False, or None if undecided.

    We simplify symbolically (exact, no floats) and ask sympy whether the result
    is identically zero. ``expr.is_zero`` can be None for hard forms; we then fall
    back to a radical-aware simplify before giving up.
    """
    try:
        simplified = sp.simplify(expr)
    except Exception:
        simplified = expr
    z = simplified.is_zero
    if z is not None:
        return bool(z)
    # radical-heavy residuals (sqrt branches) — push harder, still exact
    try:
        z2 = sp.simplify(sp.nsimplify(sp.radsimp(simplified))).is_zero
        if z2 is not None:
            return bool(z2)
    except Exception:
        pass
    return None


# --------------------------------------------------------------------------- #
# per-kind verifiers
# --------------------------------------------------------------------------- #
def _verify_polynomial(probe, claimed) -> Dict[str, Any]:
    """linear / quadratic: substitute each claimed root into expr == 0.

    Certifies each claimed root by substitution (claimed_root_not_a_root if a
    substitution leaves a nonzero residual). Certifies completeness via a degree
    count (the ONE place we trust the solver structurally, not as an oracle):
    a degree-d polynomial has at most d distinct roots, so if the claim has fewer
    *genuine* distinct roots than the count of real roots that exist, flag
    missed_root.
    """
    expr = probe.data["expr"]
    var = _probe_var(probe)
    roots = _to_root_list(claimed)
    checks: Dict[str, Any] = {"substitutions": []}
    kill: Optional[str] = None

    if roots is None:
        roots = []

    genuine = []
    for r in roots:
        residual = sp.expand(expr.subs(var, r))
        z = _is_zero(residual)
        checks["substitutions"].append(
            {"root": str(r), "residual": str(residual), "is_root": z}
        )
        if z is True:
            genuine.append(r)
        elif z is False:
            kill = "claimed_root_not_a_root"
        else:  # z is None — could not certify either way
            checks.setdefault("undecided", []).append(str(r))

    # completeness: how many real roots SHOULD there be?
    poly = sp.Poly(sp.expand(expr), var)
    degree = poly.degree()
    checks["degree"] = degree
    try:
        real_roots = [s for s in sp.solve(expr, var) if s.is_real]
    except Exception:
        real_roots = None

    if kill is None and real_roots is not None:
        n_distinct_real = len({sp.nsimplify(s) for s in real_roots})
        n_claimed_genuine = len({sp.nsimplify(g) for g in genuine})
        checks["real_roots_expected"] = n_distinct_real
        checks["claimed_genuine"] = n_claimed_genuine
        if n_claimed_genuine < n_distinct_real:
            kill = "missed_root"
        elif n_claimed_genuine > n_distinct_real:
            # more "genuine" roots than the polynomial admits — only possible if
            # substitution mis-certified; treat as a hallucination.
            kill = "claimed_root_not_a_root"

    valid = kill is None and (
        checks.get("real_roots_expected", len(genuine)) == len(genuine)
        or not roots
    )
    # an empty claim is only valid if no real roots exist
    if not roots:
        valid = (real_roots is not None and len(real_roots) == 0)
        if not valid and real_roots:
            kill = "missed_root"
    return {"valid": bool(valid), "checks": checks, "kill_pattern": kill}


def _verify_sqrt(probe, claimed) -> Dict[str, Any]:
    """R2 sqrt(x+a) = x - b : substitute into the ORIGINAL equation.

    The principal square root is non-negative, so a genuine root must satisfy
    x - b >= 0 AND x + a >= 0. Squaring introduces roots of the *conjugate*
    branch sqrt(x+a) = -(x-b); those satisfy the squared equation but fail the
    original because x - b < 0. We catch them by substituting into the original
    (sqrt stays the principal branch in sympy), and we additionally report the
    domain check explicitly so the kill is named precisely:
        - claimed value fails substitution  -> claimed_root_not_a_root
        - claimed value passes squared form but x-b<0 -> extraneous_root_admitted
    """
    a, b = probe.data["a"], probe.data["b"]
    # NB: `probe.data.get("eq")` returns a sympy Eq; using `... or sp.Eq(...)`
    # would evaluate the Eq in a boolean context and raise. Guard explicitly.
    eq = probe.data.get("eq")
    if eq is None:
        eq = sp.Eq(sp.sqrt(X + a), X - b)
    lhs, rhs = eq.lhs, eq.rhs
    roots = _to_root_list(claimed)
    if roots is None:
        roots = []
    checks: Dict[str, Any] = {"substitutions": []}
    kill: Optional[str] = None

    genuine = []
    for r in roots:
        # principal-branch substitution into the ORIGINAL equation
        residual = sp.simplify(lhs.subs(X, r) - rhs.subs(X, r))
        passes_original = _is_zero(residual)
        # domain facts (exact, radical-aware; .is_nonnegative avoids the
        # symbolic-Relational truth-value trap that >= / Max fall into).
        dom_radicand = sp.simplify(r + a).is_nonnegative   # True iff x+a >= 0
        dom_rhs_bool = sp.simplify(r - b).is_nonnegative    # True iff x-b >= 0
        # squared form, to distinguish "not a root at all" from "extraneous branch"
        squared_residual = sp.simplify((r + a) - (r - b) ** 2)
        passes_squared = _is_zero(squared_residual)
        rec = {
            "root": str(r),
            "original_residual": str(residual),
            "passes_original": passes_original,
            "x_plus_a_nonneg": dom_radicand,
            "x_minus_b_nonneg": dom_rhs_bool,
            "passes_squared": passes_squared,
        }
        checks["substitutions"].append(rec)
        if passes_original is True:
            genuine.append(r)
        elif passes_squared is True and dom_rhs_bool is False:
            # solved the squared equation but lies on the rejected branch
            kill = "extraneous_root_admitted"
        else:
            kill = "claimed_root_not_a_root"

    # completeness over the original equation
    try:
        true_sols = [s for s in sp.solve(eq, X) if s.is_real]
    except Exception:
        true_sols = None
    if true_sols is not None:
        checks["true_solution_count"] = len(true_sols)
        if kill is None:
            n_true = len({sp.nsimplify(s) for s in true_sols})
            n_gen = len({sp.nsimplify(g) for g in genuine})
            if n_gen < n_true:
                kill = "missed_root"

    valid = kill is None
    if valid and true_sols is not None:
        valid = len({sp.nsimplify(g) for g in genuine}) == len({sp.nsimplify(s) for s in true_sols})
    return {"valid": bool(valid), "checks": checks, "kill_pattern": kill}


def _verify_rational(probe, claimed) -> Dict[str, Any]:
    """R3 (num/den) = rhs, with one excluded value.

    Verify the identity num/den == rhs by EVALUATION at sampled rationals (all
    != excluded), and verify that the claim correctly EXCLUDES the singular point
    (den == 0 there). The expected correct claim string is
    'all_x_except_excluded'.
    """
    num, den, rhs, excluded = (
        probe.data["num"],
        probe.data["den"],
        probe.data["rhs"],
        probe.data["excluded"],
    )
    checks: Dict[str, Any] = {"samples": [], "excluded": int(excluded)}
    kill: Optional[str] = None

    # 1) the identity holds at sampled points != excluded
    samples = []
    v = -_RATIONAL_SAMPLES // 2
    while len(samples) < _RATIONAL_SAMPLES:
        if v != excluded:
            samples.append(sp.Rational(v))
        v += 1
    identity_ok = True
    for s in samples:
        lhs_val = sp.simplify(num.subs(X, s) / den.subs(X, s))
        rhs_val = sp.simplify(rhs.subs(X, s))
        diff = _is_zero(lhs_val - rhs_val)
        checks["samples"].append({"x": int(s), "lhs": str(lhs_val), "rhs": str(rhs_val), "equal": diff})
        if diff is not True:
            identity_ok = False
    checks["identity_holds_off_excluded"] = identity_ok

    # 2) the excluded value really is singular (denominator zero there)
    den_at_excluded = sp.simplify(den.subs(X, excluded))
    den_singular = _is_zero(den_at_excluded)
    checks["denominator_zero_at_excluded"] = den_singular

    # 3) does the CLAIM correctly exclude it?
    claim_excludes = claimed == "all_x_except_excluded"
    claim_overreaches = claimed == "all_x"  # the naive-cancel failure shape
    checks["claim"] = str(claimed)

    if not identity_ok:
        kill = "identity_fails_off_excluded"
    elif not den_singular:
        kill = "excluded_value_not_singular"
    elif claim_overreaches or not claim_excludes:
        kill = "excluded_value_missed"

    valid = kill is None and claim_excludes and identity_ok and bool(den_singular)
    return {"valid": bool(valid), "checks": checks, "kill_pattern": kill}


# --- conjecture predicates: deterministic, witness-checkable -------------------
# Each predicate maps a counterexample witness -> bool "does the witness BREAK
# the statement?". This is the only thing sympy can certify about a conjecture:
# a concrete falsifying witness. Universals get no rubber stamp (see limits).
def _pred_breaks(cid: str, witness) -> Optional[bool]:
    """Return True if `witness` deterministically falsifies statement `cid`.

    Returns None if we have no encoded predicate for `cid` (honest: we will not
    pretend to evaluate a statement we cannot represent).
    """
    if cid == "ab_even_then_both_even":
        # "if a*b is even then a and b are both even"  (witness: a 2-tuple)
        if not (isinstance(witness, (tuple, list)) and len(witness) == 2):
            return None
        a, b = int(witness[0]), int(witness[1])
        product_even = (a * b) % 2 == 0
        both_even = (a % 2 == 0) and (b % 2 == 0)
        # breaks iff antecedent true but consequent false
        return product_even and not both_even
    if cid == "n2_n_41_prime":
        # "n^2 + n + 41 is prime for all n>=0"  (witness: an int n)
        if not isinstance(witness, int):
            return None
        val = witness * witness + witness + 41
        return not sp.isprime(val)
    if cid == "all_primes_odd":
        # "every prime is odd"  (witness: a prime that is even)
        if not isinstance(witness, int):
            return None
        return bool(sp.isprime(witness)) and (witness % 2 == 0)
    if cid in ("n2_plus_n_even", "sum_two_squares"):
        # stated TRUE in the harness; no finite witness can break a true universal
        return None
    return None


def _verify_conjecture(probe, claimed) -> Dict[str, Any]:
    """R6: a claim is either ('false', counterexample) or 'true'.

    claimed may be:
      * (False, witness)               -> verify the witness really breaks it
      * False  with probe.data['cex'] -> use the harness-provided witness
      * True                          -> UNVERIFIABLE universal (valid=None)
    """
    cid = probe.data["cid"]
    checks: Dict[str, Any] = {"cid": cid}
    kill: Optional[str] = None

    # unpack the claim
    if isinstance(claimed, (tuple, list)) and len(claimed) == 2:
        claim_truth, witness = claimed[0], claimed[1]
    elif claimed is False:
        claim_truth, witness = False, probe.data.get("cex")
    elif claimed is True:
        claim_truth, witness = True, None
    else:
        return {
            "valid": False,
            "checks": {**checks, "claim": str(claimed)},
            "kill_pattern": "unparsable_conjecture_claim",
        }

    checks["claim_truth"] = bool(claim_truth)
    checks["witness"] = repr(witness)

    if claim_truth is False:
        # the verifiable direction: a concrete falsifying witness
        breaks = _pred_breaks(cid, witness)
        checks["witness_breaks_statement"] = breaks
        if breaks is True:
            return {"valid": True, "checks": checks, "kill_pattern": None}
        if breaks is False:
            return {"valid": False, "checks": checks, "kill_pattern": "bogus_counterexample"}
        # breaks is None: no encoded predicate / unrepresentable witness
        return {"valid": None, "checks": checks, "kill_pattern": "unverifiable_counterexample"}

    # claim_truth is True:
    # >>> SMT/Lean boundary <<<
    # A universally-quantified statement over an infinite domain cannot be
    # certified by substitution. Before falling back, consult the z3 backend:
    # it DECIDES some of these (proves true universals via an unsat negation,
    # or refutes them with a concrete counterexample). Primality universals are
    # not z3-posable, but their refutations are deterministic (sympy.isprime on
    # a concrete witness). z3 returning "unknown" is preserved honestly.
    z3_decision = decide_conjecture(cid)
    if z3_decision is not None:
        checks["z3"] = z3_decision["checks"]
        checks["z3_verdict"] = z3_decision["verdict"]
        if z3_decision["counterexample"] is not None:
            checks["z3_counterexample"] = z3_decision["counterexample"]
        valid = z3_decision["valid"]
        if valid is True:
            # z3 proved the universal: the "claimed true" matches.
            return {"valid": True, "checks": checks, "kill_pattern": None}
        if valid is False:
            # z3 (or a deterministic primality witness) REFUTED the universal:
            # the claim that it is true is therefore WRONG.
            checks["refuting_counterexample"] = z3_decision["counterexample"]
            return {
                "valid": False,
                "checks": checks,
                "kill_pattern": "universal_refuted_by_counterexample",
            }
        # valid is None -> z3 returned unknown / unposable. Stay honest.
        checks["note"] = (
            "z3 could not decide this universal (nonlinear/quantified arithmetic "
            "is undecidable in general, or the predicate is not concretely posable); "
            "an inductive universal beyond z3's reach needs a proof assistant (Lean/Coq)"
        )
        return {"valid": None, "checks": checks, "kill_pattern": "unverifiable_universal"}

    # No registry entry at all -> sympy still cannot certify a true universal.
    checks["note"] = (
        "true-universal: sympy cannot certify and no z3 predicate is registered; "
        "needs SMT (z3/CVC5) for decidable fragments or Lean/Coq for inductive universals"
    )
    return {"valid": None, "checks": checks, "kill_pattern": "unverifiable_universal"}


# --------------------------------------------------------------------------- #
# public entry point
# --------------------------------------------------------------------------- #
_DISPATCH = {
    "linear": _verify_polynomial,
    "quadratic": _verify_polynomial,
    "sqrt": _verify_sqrt,
    "rational": _verify_rational,
    "conjecture": _verify_conjecture,
}


def verify(probe, claimed_answer) -> Dict[str, Any]:
    """Deterministically certify whether `claimed_answer` holds for `probe`.

    NO LLM in the loop. Returns {"valid": bool|None, "checks": {...},
    "kill_pattern": str|None}. See module docstring for `valid` semantics and
    the honest limits (true universals -> valid=None).
    """
    fn = _DISPATCH.get(probe.kind)
    if fn is None:
        return {
            "valid": False,
            "checks": {"kind": probe.kind},
            "kill_pattern": "unknown_kind",
        }
    try:
        return fn(probe, claimed_answer)
    except Exception as exc:  # a verifier that crashes must FAIL CLOSED, never pass
        return {
            "valid": False,
            "checks": {"exception": f"{type(exc).__name__}: {exc}"},
            "kill_pattern": "verifier_error",
        }


__all__ = ["verify", "certify_universal", "entails", "decide_conjecture"]
