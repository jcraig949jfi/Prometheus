"""Tests for the Verifier Lens — proves it ACCEPTS correct artifacts and REJECTS
wrong ones. Deterministic, no LLM.

Run:  python -m pytest harmonia/experiments/test_verifier_lens.py -q
 or:  python harmonia/experiments/test_verifier_lens.py     (runs + prints demo)

The rejection cases are the product: each asserts BOTH valid==False AND the
specific kill_pattern (the failure SHAPE), per failure-signature doctrine —
a bare pass/fail line would destroy the gradient.
"""
from __future__ import annotations

import os
import random
import sys

# Allow `python harmonia/experiments/test_verifier_lens.py` (bare-script mode)
# in addition to `python -m harmonia.experiments.test_verifier_lens` and pytest:
# ensure the repo root (three levels up) is importable.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import sympy as sp

from harmonia.experiments import reasoning_phase0 as rp0
from harmonia.experiments.verifier_lens import verify

X = rp0.x


# --------------------------------------------------------------------------- #
# probe fixtures (built directly so the tests are hermetic and readable)
# --------------------------------------------------------------------------- #
def linear_probe():
    # 2x + 3 - 7 = 0  -> x = 2
    return rp0.Probe("R0", "clean", "linear", {"expr": 2 * X + 3 - 7}, sp.Integer(2))


def linear_probe_renamed():
    # adversarial R0 uses var y: 3y + 1 - 10 = 0 -> y = 3
    y = rp0.y
    return rp0.Probe("R0", "adversarial", "linear", {"expr": 3 * y + 1 - 10, "var": y}, sp.Integer(3))


def quadratic_probe():
    # (x+1)(x-6) = 0  -> {-1, 6}
    return rp0.Probe("R1", "clean", "quadratic", {"expr": sp.expand((X + 1) * (X - 6))}, [-1, 6])


def quadratic_no_real_roots():
    # x^2 + 1 = 0 -> no real roots
    return rp0.Probe("R1", "adversarial", "quadratic", {"expr": X ** 2 + 1}, [])


def sqrt_probe(a=0, b=4):
    # sqrt(x+a) = x - b
    eq = sp.Eq(sp.sqrt(X + a), X - b)
    true_sols = [s for s in sp.solve(eq, X) if s.is_real]
    return rp0.Probe("R2", "clean", "sqrt", {"a": a, "b": b, "eq": eq}, true_sols)


def rational_probe(r=5):
    return rp0.Probe(
        "R3", "clean", "rational",
        {"num": X ** 2 - r ** 2, "den": X - r, "rhs": X + r, "excluded": r},
        {"identity_except": r},
    )


def conjecture_false_probe():
    # "if a*b even then both even" — FALSE, cex (2,3)
    return rp0.Probe("R6", "clean", "conjecture",
                     {"cid": "ab_even_then_both_even", "truth": False, "cex": (2, 3), "delayed": False},
                     False)


def conjecture_true_probe():
    # "n^2 + n is even for all n" — TRUE
    return rp0.Probe("R6", "clean", "conjecture",
                     {"cid": "n2_plus_n_even", "truth": True, "cex": None, "delayed": False},
                     True)


def conjecture_delayed_probe():
    # "n^2+n+41 prime for all n" — FALSE, cex n=41
    return rp0.Probe("R6", "clean", "conjecture",
                     {"cid": "n2_n_41_prime", "truth": False, "cex": 41, "delayed": True},
                     False)


# --------------------------------------------------------------------------- #
# ACCEPT correct artifacts
# --------------------------------------------------------------------------- #
def test_accept_correct_linear_root():
    r = verify(linear_probe(), 2)
    assert r["valid"] is True, r
    assert r["kill_pattern"] is None


def test_accept_correct_linear_renamed_var():
    # substitution must hit the renamed variable y, not x
    r = verify(linear_probe_renamed(), 3)
    assert r["valid"] is True, r
    assert r["kill_pattern"] is None


def test_accept_correct_quadratic_root_set():
    r = verify(quadratic_probe(), [-1, 6])
    assert r["valid"] is True, r
    assert r["kill_pattern"] is None


def test_accept_empty_set_when_no_real_roots():
    r = verify(quadratic_no_real_roots(), [])
    assert r["valid"] is True, r
    assert r["kill_pattern"] is None


def test_accept_correct_sqrt_root():
    p = sqrt_probe(a=0, b=4)
    r = verify(p, p.ground_truth)
    assert r["valid"] is True, r
    assert r["kill_pattern"] is None


def test_accept_correct_rational_claim():
    r = verify(rational_probe(), "all_x_except_excluded")
    assert r["valid"] is True, r
    assert r["kill_pattern"] is None


def test_accept_correct_counterexample():
    r = verify(conjecture_false_probe(), (False, (2, 3)))
    assert r["valid"] is True, r
    assert r["kill_pattern"] is None


def test_accept_correct_delayed_counterexample():
    r = verify(conjecture_delayed_probe(), (False, 41))
    assert r["valid"] is True, r
    assert r["kill_pattern"] is None


# --------------------------------------------------------------------------- #
# REJECT wrong artifacts (the kill_pattern is the load-bearing assertion)
# --------------------------------------------------------------------------- #
def test_reject_hallucinated_linear_root():
    r = verify(linear_probe(), 5)  # truth is 2
    assert r["valid"] is False, r
    assert r["kill_pattern"] == "claimed_root_not_a_root", r


def test_reject_missed_quadratic_root():
    r = verify(quadratic_probe(), [-1])  # dropped the root x=6
    assert r["valid"] is False, r
    assert r["kill_pattern"] == "missed_root", r


def test_reject_hallucinated_roots_when_none_exist():
    r = verify(quadratic_no_real_roots(), [3])  # claims a real root where there is none
    assert r["valid"] is False, r
    assert r["kill_pattern"] == "claimed_root_not_a_root", r


def test_reject_unrejected_extraneous_sqrt_root():
    # sqrt(x+0) = x - 4 ; squared form admits 9/2 - sqrt(17)/2 (the conjugate
    # branch). A reasoner that squares-and-keeps-all returns BOTH; the verifier
    # must catch the extraneous one and name the shape.
    p = sqrt_probe(a=0, b=4)
    extraneous = sp.Rational(9, 2) - sp.sqrt(17) / 2
    r = verify(p, [p.ground_truth[0], extraneous])
    assert r["valid"] is False, r
    assert r["kill_pattern"] == "extraneous_root_admitted", r


def test_reject_excluded_value_missed_in_rational():
    # the naive-cancel failure: claims "all_x", forgetting x != excluded
    r = verify(rational_probe(), "all_x")
    assert r["valid"] is False, r
    assert r["kill_pattern"] == "excluded_value_missed", r


def test_reject_bogus_counterexample():
    # (4, 6): 4*6=24 even AND both 4,6 even -> does NOT break the statement
    r = verify(conjecture_false_probe(), (False, (4, 6)))
    assert r["valid"] is False, r
    assert r["kill_pattern"] == "bogus_counterexample", r


def test_reject_bogus_delayed_counterexample():
    # n=3: 3^2+3+41 = 53, which IS prime -> not a counterexample
    r = verify(conjecture_delayed_probe(), (False, 3))
    assert r["valid"] is False, r
    assert r["kill_pattern"] == "bogus_counterexample", r


# --------------------------------------------------------------------------- #
# HONEST LIMITS: refuse to certify true universals
# --------------------------------------------------------------------------- #
def test_true_universal_decided_by_z3_when_posable():
    # P38 update of the stale "not rubber-stamped" expectation: since Harmonia
    # B's z3 backend (494ee2e2, battery-verified by soak HARMA-P7), the
    # n2_plus_n_even universal is DECIDED (negation unsat over Z) — valid=True
    # here is an execution-certified proof, not a rubber stamp, and the z3
    # verdict must be recorded in checks.
    r = verify(conjecture_true_probe(), True)
    assert r["valid"] is True, r
    assert r["checks"].get("z3", {}).get("decision_kind") == "z3_universal", r


def test_true_universal_not_rubber_stamped_when_z3_cannot_pose():
    # The not-rubber-stamped property lives where z3 CANNOT decide: a
    # non-posable universal must abstain (valid None), never certify.
    import copy
    p = copy.deepcopy(conjecture_true_probe())
    p.data["cid"] = "sum_two_squares"
    r = verify(p, True)
    assert r["valid"] is None, r
    assert r["kill_pattern"] == "unverifiable_universal", r


def test_verifier_fails_closed_on_garbage():
    # a structurally broken claim on a KNOWN kind is a REJECTION, not an
    # abstention — pinned exactly (HARMA-P12: the old `in (False, None)` guard
    # would stay green through a rejection->abstention regression too).
    r = verify(conjecture_false_probe(), "definitely")
    assert r["valid"] is False, r
    assert r["kill_pattern"] == "unparsable_conjecture_claim", r


def test_unknown_kind_abstains_exactly():
    # an UNREGISTERED kind must abstain (valid None + unknown_kind), never
    # certify in either direction. Pinned per HARMA-P12: a regression from
    # abstention back to mis-certification must turn the suite red.
    from collections import namedtuple
    P = namedtuple("P", "tier version kind data ground_truth")
    r = verify(P("X", "clean", "totally_unknown_kind", {"stmt": "a true claim"}, None), True)
    assert r["valid"] is None, r
    assert r["kill_pattern"] == "unknown_kind", r


# --------------------------------------------------------------------------- #
# integration: run against the actual harness probes + reasoners.
# The verifier's verdict must AGREE with the harness's own _ans_correct on the
# cases the harness can grade (a cross-check that the lens is not inventing a
# different notion of correctness), and must FLAG the careful-vs-procedural sqrt
# split (procedural admits extraneous roots; careful does not).
# --------------------------------------------------------------------------- #
def test_integration_agrees_with_harness_on_gradeable_cases():
    rng = random.Random(rp0.SEED)
    probes = []
    for g in (rp0.gen_R0, rp0.gen_R1, rp0.gen_R2, rp0.gen_R3):
        probes += g(rng)
    mismatches = []
    for p in probes:
        ans, tr = rp0.reasoner_careful(p)
        harness_ok = rp0._ans_correct(p, ans)
        # translate the harness's symbolic answer into a claim the lens can read
        claim = _harness_answer_to_claim(p, ans)
        if claim is _SKIP:
            continue
        v = verify(p, claim)
        if v["valid"] is None:
            continue
        if bool(v["valid"]) != bool(harness_ok):
            mismatches.append((p.tier, p.version, p.kind, ans, harness_ok, v))
    assert not mismatches, f"{len(mismatches)} verifier/harness disagreements: {mismatches[:3]}"


def test_integration_catches_procedural_extraneous_on_sqrt():
    # the careful reasoner rejects extraneous roots; the procedural one does not.
    # On at least one sqrt probe the procedural answer must be killed by the lens
    # with the extraneous_root_admitted shape.
    rng = random.Random(rp0.SEED)
    sqrt_probes = [p for p in rp0.gen_R2(rng) if p.kind == "sqrt"]
    shapes = set()
    for p in sqrt_probes:
        ans, _ = rp0.reasoner_procedural(p)
        if not isinstance(ans, list):
            continue
        v = verify(p, ans)
        if v["valid"] is False and v["kill_pattern"]:
            shapes.add(v["kill_pattern"])
    assert "extraneous_root_admitted" in shapes, shapes


_SKIP = object()


def _harness_answer_to_claim(p, ans):
    """Map a harness reasoner answer onto a claim the lens accepts."""
    if p.kind in ("linear", "quadratic", "sqrt"):
        return ans  # list / scalar of roots, or None
    if p.kind == "rational":
        if ans == "all_x_except_excluded":
            return "all_x_except_excluded"
        if ans == "all_x":
            return "all_x"
        return _SKIP
    if p.kind == "conjecture":
        if ans is False:
            return (False, p.data.get("cex"))
        if ans is True:
            return True
        return _SKIP
    return _SKIP


# --------------------------------------------------------------------------- #
# demo
# --------------------------------------------------------------------------- #
def _demo():
    print("=" * 72)
    print("VERIFIER LENS DEMO — deterministic, no-LLM selector")
    print("=" * 72)
    cases = [
        ("linear, correct root x=2", linear_probe(), 2),
        ("linear, hallucinated root x=5", linear_probe(), 5),
        ("quadratic, correct {-1,6}", quadratic_probe(), [-1, 6]),
        ("quadratic, missed root [-1]", quadratic_probe(), [-1]),
        ("quadratic adversarial (no real roots), correct []", quadratic_no_real_roots(), []),
        ("quadratic adversarial, hallucinated real root [3]", quadratic_no_real_roots(), [3]),
        ("sqrt, correct principal root", sqrt_probe(0, 4), sqrt_probe(0, 4).ground_truth),
        ("sqrt, UNREJECTED extraneous root", sqrt_probe(0, 4),
         [sqrt_probe(0, 4).ground_truth[0], sp.Rational(9, 2) - sp.sqrt(17) / 2]),
        ("rational, correct (excludes x=5)", rational_probe(), "all_x_except_excluded"),
        ("rational, naive 'all_x' (misses exclusion)", rational_probe(), "all_x"),
        ("conjecture FALSE, correct cex (2,3)", conjecture_false_probe(), (False, (2, 3))),
        ("conjecture FALSE, BOGUS cex (4,6)", conjecture_false_probe(), (False, (4, 6))),
        ("conjecture FALSE delayed, correct cex n=41", conjecture_delayed_probe(), (False, 41)),
        ("conjecture FALSE delayed, BOGUS cex n=3", conjecture_delayed_probe(), (False, 3)),
        ("conjecture TRUE universal (UNVERIFIABLE)", conjecture_true_probe(), True),
    ]
    for label, probe, claim in cases:
        r = verify(probe, claim)
        verdict = {True: "ACCEPT", False: "REJECT", None: "UNVERIFIABLE"}[r["valid"]]
        kp = f"  kill={r['kill_pattern']}" if r["kill_pattern"] else ""
        print(f"  [{verdict:12s}] {label}{kp}")
    print("=" * 72)


if __name__ == "__main__":
    _demo()
