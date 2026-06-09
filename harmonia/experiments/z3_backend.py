"""z3 certification backend for the deterministic verifier lens (EXPERIMENTAL).

Doctrine anchor: this module is part of the *selection side* of the
reasoning-ladder harness. There is NO LLM in this loop — z3 (an SMT solver) and
sympy (for concrete deterministic primality witnesses) are the only oracles, and
both are exact / reproducible. The mutation side is the only place an LLM is
permitted.

What this closes
----------------
`verifier_lens.py` honestly returns ``valid=None`` / ``unverifiable_universal``
for claims of the form "for all integers n, P(n)" because sympy cannot prove a
universal over an infinite domain. z3 *can* decide some of these by the standard
SMT refutation trick: to prove ``forall n. P(n)`` we assert the NEGATION
``exists n. not P(n)`` and check satisfiability:

    * ``unsat``   => no falsifying n exists => P holds for all n  => "proved"
    * ``sat``     => a falsifying n exists   => P is false        => "refuted"
                     (the model gives a concrete counterexample)
    * ``unknown`` => z3 could not decide within the timeout       => "unknown"

The ``unknown`` branch is load-bearing and honest: z3's nonlinear integer
arithmetic (NIA) with quantifiers is *undecidable* in general, so many true
universals over a nonlinear predicate will time out. We report that as
``"unknown"`` and never fabricate a verdict.

Honest boundary (what z3 still cannot do here)
----------------------------------------------
  * Primality is not a first-order arithmetic predicate, so "n^2+n+41 is prime
    for all n" and "every prime is odd" cannot be posed to z3 as universals.
    The *refutation* of each, however, is a concrete deterministic check (a
    single n where the value is composite; the even prime 2) — we verify those
    witnesses with ``sympy.isprime``, which is exact, not an LLM.
  * Genuinely undecidable nonlinear universals (e.g. positive-integer
    a^3+b^3=c^3) come back ``unknown`` — see the self-test in
    ``test_verifier_z3.py``.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import z3

# Default solver budget. SMT over nonlinear integer arithmetic is undecidable in
# general; a short, fixed timeout keeps the lens snappy and turns "can't decide"
# into an honest "unknown" rather than a hang.
_DEFAULT_TIMEOUT_MS = 5000


# --------------------------------------------------------------------------- #
# core: prove/refute a universal by asserting its negation
# --------------------------------------------------------------------------- #
def certify_universal(
    predicate_builder: Callable[[z3.ArithRef], z3.BoolRef],
    domain: Optional[Callable[[z3.ArithRef], z3.BoolRef]] = None,
    *,
    var_name: str = "n",
    timeout_ms: int = _DEFAULT_TIMEOUT_MS,
) -> Dict[str, Any]:
    """Decide ``forall n in domain. predicate(n)`` via SMT refutation.

    Parameters
    ----------
    predicate_builder:
        ``n -> z3 Bool`` building the predicate P(n) over a single integer var.
    domain:
        Optional ``n -> z3 Bool`` constraining the domain (e.g. ``lambda n: n>=0``).
        ``None`` means all integers.
    var_name:
        Name of the z3 integer variable handed to the builders.
    timeout_ms:
        Solver budget in milliseconds. On expiry z3 returns ``unknown`` and we
        report ``"unknown"`` rather than guessing.

    Returns
    -------
    dict with:
        "verdict":       "proved" | "refuted" | "unknown"
        "counterexample": int | None  (only set when refuted and a model exists)
        "z3_result":     the raw z3 check string ("sat"/"unsat"/"unknown")
        "reason":        short human-readable note (esp. for "unknown")
    """
    n = z3.Int(var_name)
    solver = z3.Solver()
    solver.set("timeout", int(timeout_ms))

    # Assert the NEGATION of the universal: exists n (in domain) with not P(n).
    if domain is not None:
        solver.add(domain(n))
    solver.add(z3.Not(predicate_builder(n)))

    result = solver.check()

    if result == z3.unsat:
        # No counterexample to P exists in the domain => P holds for all n.
        return {
            "verdict": "proved",
            "counterexample": None,
            "z3_result": "unsat",
            "reason": "negation unsatisfiable: predicate holds for all n in domain",
        }
    if result == z3.sat:
        model = solver.model()
        cex: Optional[int] = None
        try:
            val = model.eval(n, model_completion=True)
            if z3.is_int_value(val):
                cex = val.as_long()
        except Exception:
            cex = None
        return {
            "verdict": "refuted",
            "counterexample": cex,
            "z3_result": "sat",
            "reason": "negation satisfiable: a falsifying n exists",
        }
    # z3.unknown — undecidable within budget. DO NOT guess.
    return {
        "verdict": "unknown",
        "counterexample": None,
        "z3_result": "unknown",
        "reason": f"z3 returned unknown ({solver.reason_unknown()}); "
        "nonlinear/quantified arithmetic is undecidable in general",
    }


# --------------------------------------------------------------------------- #
# entailment primitive (for future R9 lemma-invention grading)
# --------------------------------------------------------------------------- #
def entails(
    premise: z3.BoolRef,
    conclusion: z3.BoolRef,
    *,
    timeout_ms: int = _DEFAULT_TIMEOUT_MS,
) -> str:
    """Does ``premise`` entail ``conclusion``? (premise => conclusion is valid).

    Standard SMT validity check: ``A => B`` is valid iff ``A and not B`` is
    unsatisfiable. The premise/conclusion are concrete z3 Bool terms (any free
    z3 vars inside are implicitly universally quantified by this test, which is
    exactly what entailment means).

    Returns
    -------
    "valid"   -> entailment holds   (premise & not conclusion is unsat)
    "invalid" -> entailment fails    (a model satisfies premise & not conclusion)
    "unknown" -> z3 could not decide within the timeout
    """
    solver = z3.Solver()
    solver.set("timeout", int(timeout_ms))
    solver.add(premise)
    solver.add(z3.Not(conclusion))
    result = solver.check()
    if result == z3.unsat:
        return "valid"
    if result == z3.sat:
        return "invalid"
    return "unknown"


# --------------------------------------------------------------------------- #
# conjecture registry: cid -> how to decide it
# --------------------------------------------------------------------------- #
# Each entry says HOW the statement is decidable by the selection side:
#   kind="z3_universal": pose forall n. P(n) to z3 (predicate + optional domain).
#   kind="refute_witness": primality is not z3-expressible as a universal, but a
#       concrete counterexample IS deterministically checkable (sympy.isprime on
#       a single witness). We carry the witness and the check.
#   kind="z3_unknown_expected": expressible but z3 is expected to time out
#       (nonlinear/quantified) -> honest "unknown".
#
# NOTE on the harness's stated truths (reasoning_phase0.CONJ):
#   ab_even_then_both_even : FALSE (cex (2,3))   -> z3 refutes
#   n2_plus_n_even         : TRUE                -> z3 proves
#   n2_n_41_prime          : FALSE (cex n=41)    -> primality refutation witness
#   all_primes_odd         : FALSE (cex 2)       -> primality refutation witness
#   sum_two_squares        : "true-ish placeholder" -> NOT a well-specified
#                            predicate; we honestly leave it unknown.

import sympy as _sp  # only for deterministic concrete primality witnesses


def _z3_n2_plus_n_even(n: z3.ArithRef) -> z3.BoolRef:
    # n^2 + n is even, for all integers n.
    return (n * n + n) % 2 == 0


def _z3_ab_even_then_both_even_pair():
    """Two-variable predicate: "a*b even => (a even and b even)" for all ints.

    Returned as (builder2, vars) because this one is over TWO integers, so it
    does not fit the single-var ``certify_universal`` signature. The lens calls
    z3 directly with these.
    """
    a = z3.Int("a")
    b = z3.Int("b")
    pred = z3.Implies((a * b) % 2 == 0, z3.And(a % 2 == 0, b % 2 == 0))
    return a, b, pred


# A registry the lens consults by cid. Values are dicts describing the decision
# procedure; the lens (verifier_lens.verify) dispatches on "kind".
CONJECTURE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "n2_plus_n_even": {
        "kind": "z3_universal",
        "stated_truth": True,
        "predicate": _z3_n2_plus_n_even,
        "domain": None,  # all integers
        "note": "z3 decides: negation is unsat over Z => proved true for all n",
    },
    "ab_even_then_both_even": {
        "kind": "z3_universal_2var",
        "stated_truth": False,
        "note": "z3 decides: 2-var implication; negation sat => refuted with model",
    },
    "n2_n_41_prime": {
        "kind": "refute_witness",
        "stated_truth": False,
        "witness": 41,  # 41^2+41+41 = 41*43, composite; also n=40 works
        "value_at": lambda n: n * n + n + 41,
        "note": "primality not z3-expressible as universal; concrete composite "
        "witness checked with sympy.isprime",
    },
    "all_primes_odd": {
        "kind": "refute_witness_is_prime",
        "stated_truth": False,
        "witness": 2,  # 2 is an even prime
        "note": "refuted by the even prime 2; checked with sympy.isprime",
    },
    "sum_two_squares": {
        "kind": "unknown",
        "stated_truth": True,
        "note": "'true-ish placeholder' in harness: predicate is not concretely "
        "specified, so the selection side cannot pose it. Honest unknown.",
    },
}


def decide_conjecture(cid: str) -> Optional[Dict[str, Any]]:
    """Decide a harness conjecture by `cid` using z3 / deterministic witnesses.

    Returns a dict ``{"valid": True|False|None, "verdict": str,
    "counterexample": <witness or None>, "checks": {...}}`` or ``None`` if the
    cid is not in the registry (caller then falls back to the sympy path).
    """
    spec = CONJECTURE_REGISTRY.get(cid)
    if spec is None:
        return None

    kind = spec["kind"]
    base_checks = {"cid": cid, "decision_kind": kind, "note": spec.get("note")}

    if kind == "z3_universal":
        res = certify_universal(spec["predicate"], spec.get("domain"))
        verdict = res["verdict"]
        valid = {"proved": True, "refuted": False, "unknown": None}[verdict]
        return {
            "valid": valid,
            "verdict": verdict,
            "counterexample": res["counterexample"],
            "checks": {**base_checks, "z3": res},
        }

    if kind == "z3_universal_2var":
        a, b, pred = _z3_ab_even_then_both_even_pair()
        solver = z3.Solver()
        solver.set("timeout", _DEFAULT_TIMEOUT_MS)
        solver.add(z3.Not(pred))
        r = solver.check()
        if r == z3.unsat:
            return {
                "valid": True,
                "verdict": "proved",
                "counterexample": None,
                "checks": {**base_checks, "z3_result": "unsat"},
            }
        if r == z3.sat:
            m = solver.model()
            cex = None
            try:
                av = m.eval(a, model_completion=True)
                bv = m.eval(b, model_completion=True)
                cex = (av.as_long(), bv.as_long())
            except Exception:
                cex = None
            return {
                "valid": False,
                "verdict": "refuted",
                "counterexample": cex,
                "checks": {**base_checks, "z3_result": "sat", "model": str(m)},
            }
        return {
            "valid": None,
            "verdict": "unknown",
            "counterexample": None,
            "checks": {**base_checks, "z3_result": "unknown"},
        }

    if kind == "refute_witness":
        # The statement "f(n) is prime for all n>=0" is refuted by exhibiting one
        # n where f(n) is composite. Deterministic: sympy.isprime on the witness.
        n = spec["witness"]
        val = int(spec["value_at"](n))
        composite = not bool(_sp.isprime(val))
        checks = {
            **base_checks,
            "witness_n": n,
            "value": val,
            "is_composite": composite,
        }
        if composite:
            return {
                "valid": False,
                "verdict": "refuted",
                "counterexample": n,
                "checks": checks,
            }
        # witness did not actually refute -> we cannot certify; honest unknown
        return {
            "valid": None,
            "verdict": "unknown",
            "counterexample": None,
            "checks": {**checks, "warn": "registry witness failed to refute"},
        }

    if kind == "refute_witness_is_prime":
        # "every prime is odd" refuted by an even prime witness.
        w = spec["witness"]
        is_prime = bool(_sp.isprime(w))
        is_even = (w % 2 == 0)
        refutes = is_prime and is_even
        checks = {
            **base_checks,
            "witness": w,
            "is_prime": is_prime,
            "is_even": is_even,
        }
        if refutes:
            return {
                "valid": False,
                "verdict": "refuted",
                "counterexample": w,
                "checks": checks,
            }
        return {
            "valid": None,
            "verdict": "unknown",
            "counterexample": None,
            "checks": {**checks, "warn": "registry witness failed to refute"},
        }

    # kind == "unknown" (or anything unhandled): honest unknown.
    return {
        "valid": None,
        "verdict": "unknown",
        "counterexample": None,
        "checks": base_checks,
    }


__all__ = [
    "certify_universal",
    "entails",
    "decide_conjecture",
    "CONJECTURE_REGISTRY",
]
