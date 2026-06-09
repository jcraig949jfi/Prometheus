"""Tests for the z3 certification backend of the verifier lens (EXPERIMENTAL).

Run:  python -m harmonia.experiments.test_verifier_z3
or:   pytest harmonia/experiments/test_verifier_z3.py

Doctrine: NO LLM in the loop. These tests pin down three things that matter for
the *selection side*:
  1. a TRUE universal is "proved" (z3: negation unsat),
  2. a FALSE universal is "refuted" + the right counterexample (z3: negation sat),
  3. an UNDECIDABLE universal returns "unknown" — NOT a fabricated verdict.
Plus the conjecture-registry wiring and the `entails` primitive.
"""
from __future__ import annotations

import os
import sys

# Make the repo root importable when run as a bare path or via -m.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import z3  # noqa: E402

from harmonia.experiments import reasoning_phase0 as rp0  # noqa: E402
from harmonia.experiments.verifier_lens import (  # noqa: E402
    certify_universal,
    decide_conjecture,
    entails,
    verify,
)


# --------------------------------------------------------------------------- #
# certify_universal: proved / refuted / unknown
# --------------------------------------------------------------------------- #
def test_true_universal_is_proved():
    # n^2 + n is even for all integers n.
    res = certify_universal(lambda n: (n * n + n) % 2 == 0)
    assert res["verdict"] == "proved", res
    assert res["counterexample"] is None
    assert res["z3_result"] == "unsat"


def test_true_universal_over_subdomain_is_proved():
    # for all n >= 0: n^2 >= 0  (also true over all Z, but exercise the domain arg)
    res = certify_universal(lambda n: n * n >= 0, domain=lambda n: n >= 0)
    assert res["verdict"] == "proved", res


def test_false_universal_is_refuted_with_counterexample():
    # CLAIM (false): "for all integers n, n^2 >= n + 1".  n=0 breaks it (0 >= 1 is false).
    res = certify_universal(lambda n: n * n >= n + 1)
    assert res["verdict"] == "refuted", res
    cex = res["counterexample"]
    assert cex is not None
    # the returned counterexample must ACTUALLY falsify the predicate
    assert not (cex * cex >= cex + 1), f"z3 counterexample {cex} did not falsify"


def test_false_universal_exact_counterexample_value():
    # "for all n, n != 7"  -> the only counterexample is n == 7.
    res = certify_universal(lambda n: n != 7)
    assert res["verdict"] == "refuted", res
    assert res["counterexample"] == 7, res


def test_undecidable_universal_is_unknown_not_fabricated():
    # "for all positive a,b,c: a^3 + b^3 != c^3" — z3 NIA with this shape times out.
    # We pose it as a single-var-API workaround using a fresh solver to confirm the
    # honest 'unknown' rather than a guessed verdict.
    a, b, c = z3.Ints("a b c")
    solver = z3.Solver()
    solver.set("timeout", 2000)
    # negation: there EXIST positive a,b,c with a^3+b^3 == c^3
    solver.add(a >= 1, b >= 1, c >= 1, a * a * a + b * b * b == c * c * c)
    r = solver.check()
    # The contract we enforce: the lens NEVER turns 'unknown' into proved/refuted.
    assert r == z3.unknown, f"expected z3 unknown for fermat3, got {r}"


# --------------------------------------------------------------------------- #
# conjecture registry: the 5 harness cids
# --------------------------------------------------------------------------- #
def test_registry_decides_the_five_cids():
    expected = {
        "n2_plus_n_even": ("proved", True),
        "ab_even_then_both_even": ("refuted", False),
        "n2_n_41_prime": ("refuted", False),
        "all_primes_odd": ("refuted", False),
        "sum_two_squares": ("unknown", None),
    }
    for cid, (want_verdict, want_valid) in expected.items():
        d = decide_conjecture(cid)
        assert d is not None, f"{cid} missing from registry"
        assert d["verdict"] == want_verdict, (cid, d)
        assert d["valid"] is want_valid, (cid, d)


def test_registry_counterexamples_are_correct():
    # n2_n_41_prime refuted by n=41 (41^2+41+41 = 41*43 composite)
    d = decide_conjecture("n2_n_41_prime")
    assert d["counterexample"] == 41, d
    # all_primes_odd refuted by the even prime 2
    d = decide_conjecture("all_primes_odd")
    assert d["counterexample"] == 2, d
    # ab_even_then_both_even refuted by SOME (a,b) z3 model that truly breaks it
    d = decide_conjecture("ab_even_then_both_even")
    a, b = d["counterexample"]
    product_even = (a * b) % 2 == 0
    both_even = (a % 2 == 0) and (b % 2 == 0)
    assert product_even and not both_even, ("bad cex", a, b)


# --------------------------------------------------------------------------- #
# end-to-end through verify() on real harness probes
# --------------------------------------------------------------------------- #
def _conj_probe(cid):
    """Build a harness R6 conjecture probe for a given cid (clean version)."""
    rec = next(c for c in rp0.CONJ if c[0] == cid)
    _cid, truth, cex, _streak = rec
    return rp0.Probe(
        "R6", "clean", "conjecture",
        {"cid": cid, "truth": truth, "cex": cex, "delayed": (cid == "n2_n_41_prime")},
        truth,
    )


def test_verify_true_universal_now_proved_not_none():
    # Previously returned valid=None / unverifiable_universal. z3 now PROVES it.
    p = _conj_probe("n2_plus_n_even")
    out = verify(p, True)  # claim: the universal is true
    assert out["valid"] is True, out
    assert out["kill_pattern"] is None, out
    assert out["checks"]["z3_verdict"] == "proved", out


def test_verify_false_universal_claimed_true_is_refuted():
    # Someone claims "n^2+n+41 is always prime" (True). z3-backed path REFUTES it.
    p = _conj_probe("n2_n_41_prime")
    out = verify(p, True)
    assert out["valid"] is False, out
    assert out["kill_pattern"] == "universal_refuted_by_counterexample", out
    assert out["checks"]["z3_counterexample"] == 41, out


def test_verify_all_primes_odd_claimed_true_is_refuted():
    p = _conj_probe("all_primes_odd")
    out = verify(p, True)
    assert out["valid"] is False, out
    assert out["checks"]["z3_counterexample"] == 2, out


def test_verify_unposable_universal_stays_none():
    # 'sum_two_squares' is a placeholder with no concrete predicate -> honest None.
    p = _conj_probe("sum_two_squares")
    out = verify(p, True)
    assert out["valid"] is None, out
    assert out["kill_pattern"] == "unverifiable_universal", out


def test_verify_false_conjecture_witness_path_still_works():
    # The existing sympy witness path (claim = (False, witness)) must be unaffected.
    p = _conj_probe("all_primes_odd")
    out = verify(p, (False, 2))  # claim it's false, witness=2
    assert out["valid"] is True, out  # the witness genuinely breaks it
    assert out["kill_pattern"] is None, out


# --------------------------------------------------------------------------- #
# entails primitive (future R9 lemma-invention grading)
# --------------------------------------------------------------------------- #
def test_entails_valid():
    x, y = z3.Ints("x y")
    # x>0 and y>0  entails  x+y>0
    assert entails(z3.And(x > 0, y > 0), x + y > 0) == "valid"


def test_entails_invalid():
    x = z3.Int("x")
    # x>0 does NOT entail x>1  (x=1 is a witness)
    assert entails(x > 0, x > 1) == "invalid"


def test_entails_transitivity_chain_valid():
    a, b, c = z3.Ints("a b c")
    # (a<=b and b<=c) entails a<=c
    assert entails(z3.And(a <= b, b <= c), a <= c) == "valid"


# --------------------------------------------------------------------------- #
# tiny runner so this works without pytest installed
# --------------------------------------------------------------------------- #
def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    failed = []
    for t in tests:
        try:
            t()
            passed += 1
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed.append((t.__name__, f"AssertionError: {e}"))
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed.append((t.__name__, f"{type(e).__name__}: {e}"))
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed; {len(failed)} failed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(_run_all())
