"""Tests for the R12 conjecture-generation-under-falsification grader (EXPERIMENTAL).

Run:  python harmonia/experiments/test_r12.py
or:   pytest harmonia/experiments/test_r12.py

Doctrine: NO LLM in these tests -- they pin the DETERMINISTIC machinery:

  A. SAFETY -- the AST sandbox must REJECT unsafe emissions (imports, attribute
     access, arbitrary calls, loops, comprehensions, lambdas, dunders, walrus,
     assignment, multi-statement bodies, f-strings) and ACCEPT the legal grammar
     (bool ops, comparisons, arithmetic, obj[...] reads, whitelisted helpers).
     Also: the sandbox must NEVER execute a side effect, even when handed code
     that *would* mutate global state if run unsandboxed.

  B. CONJECTURE GRADING -- a known-good (exact-target) conjecture scores high and
     exact_partition=True; an OVERFIT (memorize-revealed-positives) conjecture
     and a NAIVE-MIMIC (const-true / single-literal) conjecture both collapse
     toward 0 via the baseline penalty, EVEN IF their raw Jaccard is non-trivial.

  C. TEST GRADING -- a maximally-splitting probe earns near-optimal info gain;
     a useless probe (all hypotheses agree on it, or an off-universe object)
     earns ~0; the two scores are returned SEPARATELY (never fused).
"""
from __future__ import annotations

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from r12_universe import (  # noqa: E402
    build_bits_universe,
    build_tuples_universe,
    enumerate_hypothesis_class,
    make_trial,
    pred_to_python,
    pred_signature,
    _atoms,
)
from r12_grader import (  # noqa: E402
    UnsafeConjecture,
    compile_safe_conjecture,
    consistent_version_space,
    grade_conjecture,
    grade_emission,
    grade_test_object,
)


# --------------------------------------------------------------------------- #
# shared fixtures (deterministic)
# --------------------------------------------------------------------------- #
_U = build_bits_universe(5)
_H = enumerate_hypothesis_class(_U, max_terms=2)
_T = make_trial(seed=7, universe=_U, H=_H, n_reveal=8)

_UT = build_tuples_universe(0, 7)
_HT = enumerate_hypothesis_class(_UT, max_terms=2)
_TT = make_trial(seed=1, universe=_UT, H=_HT, n_reveal=8)


# ======================================================================== #
# A. SAFETY -- the sandbox must reject unsafe code
# ======================================================================== #
_UNSAFE_SAMPLES = {
    "import": "def conjecture(obj):\n    import os\n    return True",
    "import_inline_call": "__import__('os').system('echo x')",
    "attr_dunder": "obj.__class__",
    "attr_globals": "(lambda: 0).__globals__",
    "attr_general": "obj.keys()",
    "arbitrary_call": "open('x')",
    "builtins_open": "def conjecture(obj):\n    return open('/etc/passwd')",
    "lambda": "def conjecture(obj):\n    return (lambda x: x)(obj['x'])",
    "comprehension": "def conjecture(obj):\n    return any(v for v in [1,2,3])",
    "for_loop": "def conjecture(obj):\n    s=0\n    for i in range(3): s+=i\n    return s>0",
    "while_loop": "def conjecture(obj):\n    while True: pass",
    "assignment": "def conjecture(obj):\n    x = obj['x']\n    return x > 0",
    "walrus": "def conjecture(obj):\n    return (y := obj['x']) > 0",
    "fstring": "def conjecture(obj):\n    return f'{obj}' == 'x'",
    "two_args": "def conjecture(obj, evil):\n    return True",
    "subscript_other": "def conjecture(obj):\n    return [1,2,3][0] == 1",  # subscript not on obj
    "name_leak": "def conjecture(obj):\n    return __builtins__",
    "huge_pow": "def conjecture(obj):\n    return 9999 ** 99 > 0",
    "decorator": "@staticmethod\ndef conjecture(obj):\n    return True",
    "multi_statement": "def conjecture(obj):\n    print(1)\n    return True",
    "nested_def": "def conjecture(obj):\n    def g(): return 1\n    return g()==1",
}


def test_sandbox_rejects_all_unsafe_samples():
    for name, src in _UNSAFE_SAMPLES.items():
        try:
            compile_safe_conjecture(src)
        except UnsafeConjecture:
            continue
        raise AssertionError(f"UNSAFE sample {name!r} was NOT rejected: {src!r}")


def test_sandbox_never_executes_side_effects():
    # Code that, if run unsandboxed, would mutate a module-global sentinel.
    import builtins
    builtins._R12_SIDE_EFFECT = 0  # type: ignore[attr-defined]
    evil = ("def conjecture(obj):\n"
            "    import builtins\n"
            "    builtins._R12_SIDE_EFFECT = 1\n"
            "    return True")
    try:
        compile_safe_conjecture(evil)
    except UnsafeConjecture:
        pass
    # Even attempting to *grade* it must not run it.
    res = grade_emission(_T, evil, None)
    assert res.safe is False, res
    assert builtins._R12_SIDE_EFFECT == 0, "sandbox EXECUTED the side effect!"  # type: ignore[attr-defined]
    del builtins._R12_SIDE_EFFECT  # type: ignore[attr-defined]


_SAFE_SAMPLES = [
    "def conjecture(obj):\n    return obj['f0'] == 1",
    "def conjecture(obj):\n    return obj['f0'] == 1 and obj['f1'] == 0",
    "def conjecture(obj):\n    return obj['popcount'] >= 2 or obj['f3'] == 1",
    "def conjecture(obj):\n    return not (obj['f2'] == 1)",
    "def conjecture(obj):\n    return (obj['f0'] + obj['f1']) % 2 == 0",
    "def conjecture(obj):\n    return abs(obj['f0'] - obj['f1']) <= 1",
    "def conjecture(obj):\n    return max(obj['f0'], obj['f1']) == 1",
    "def conjecture(obj):\n    '''a docstring is tolerated'''\n    return obj['f4'] == 0",
    "obj['popcount'] <= 3",  # bare expression form is allowed
]


def test_sandbox_accepts_legal_grammar():
    for src in _SAFE_SAMPLES:
        p = compile_safe_conjecture(src)   # must not raise
        # and it must actually evaluate to a bool on a real object
        v = p(_U.objects[0])
        assert isinstance(v, bool), (src, v)


def test_sandbox_records_feature_keys():
    p = compile_safe_conjecture(
        "def conjecture(obj):\n    return obj['f0'] == 1 and obj['popcount'] >= 2")
    assert set(p.feature_keys) == {"f0", "popcount"}, p.feature_keys


def test_sandbox_extension_handles_missing_feature_gracefully():
    # references a feature that doesn't exist -> KeyError per object -> rejected,
    # never a crash; extension should be empty, not an exception.
    p = compile_safe_conjecture("def conjecture(obj):\n    return obj['nope'] == 1")
    ext = p.extension(_U)
    assert ext == frozenset(), ext


def test_pow_bound_blocks_resource_exhaustion():
    # exponent within range is fine.
    ok = compile_safe_conjecture("def conjecture(obj):\n    return obj['f0'] ** 2 == 1")
    _ = ok.extension(_U)  # evaluates without error
    # constant exponent out of band -> rejected at PARSE time (defence in depth)
    try:
        compile_safe_conjecture("def conjecture(obj):\n    return obj['f0'] ** 9 == 0")
        raise AssertionError("constant out-of-band exponent should be rejected at parse")
    except UnsafeConjecture:
        pass
    # DYNAMIC exponent (feature-valued) escapes parse-time const check but is
    # caught by the eval-time bound -> per-object rejection, no crash. popcount
    # ranges 0..5, so popcount as an exponent exceeds the [0,8] band only some
    # of the time; the guard fires without raising out of extension().
    dyn = compile_safe_conjecture(
        "def conjecture(obj):\n    return 2 ** (obj['popcount'] + 7) > 0")
    ext = dyn.extension(_U)        # must not crash; offending objs are dropped
    assert isinstance(ext, frozenset)


# ======================================================================== #
# B. CONJECTURE GRADING -- good vs overfit vs naive-mimic
# ======================================================================== #
def test_exact_target_scores_high_and_exact():
    src = "def conjecture(obj):\n    return " + pred_to_python(_T.target)
    res = grade_emission(_T, src, None)
    assert res.safe, res
    cq = res.conjecture
    assert cq.exact_partition is True, cq
    assert cq.raw_jaccard_full == 1.0, cq
    assert cq.raw_holdout_acc == 1.0, cq
    # quality is the highest achievable for THIS target (== 1 - intrinsic
    # baseline similarity of the true rule); must beat both overfit and mimic.
    assert cq.quality > 0.0, cq


def test_overfit_memorize_revealed_collapses_to_zero():
    # Build a conjecture that accepts EXACTLY the revealed positives (overfit):
    # an explicit OR of equality-on-all-features for each revealed-positive obj.
    pos = [i for i in _T.revealed_idx if _T.labels[i]]
    feats = _U.features
    clauses = []
    for i in pos:
        o = _U.objects[i]
        conj = " and ".join(f"obj['{f}'] == {o[f]}" for f in feats)
        clauses.append(f"({conj})")
    body = " or ".join(clauses) if clauses else "False"
    src = "def conjecture(obj):\n    return " + body
    res = grade_emission(_T, src, None)
    assert res.safe, res
    cq = res.conjecture
    # raw held-out accuracy of pure memorization is poor; quality must be ~0
    assert cq.quality < 0.05, cq
    assert cq.most_similar_baseline == "memorize_pos", cq


def test_naive_const_true_mimic_scores_zero():
    res = grade_emission(_T, "def conjecture(obj):\n    return True", None)
    cq = res.conjecture
    assert cq.quality == 0.0, cq           # identical to const_true baseline
    assert cq.most_similar_baseline in ("const_true", "majority"), cq


def test_single_literal_mimic_scores_low():
    # the single best literal on revealed data is a naive baseline -> penalized
    bl_atom = max(_atoms(_U),
                  key=lambda a: sum(1 for i in _T.revealed_idx
                                    if (i in pred_signature(a, _U)) == _T.labels[i]))
    src = "def conjecture(obj):\n    return " + pred_to_python(bl_atom)
    res = grade_emission(_T, src, None)
    cq = res.conjecture
    assert cq.quality < 0.10, (cq, pred_to_python(bl_atom))


def test_good_conjecture_beats_overfit_and_mimic_strictly():
    # the three conjectures graded on the SAME trial; ordering must hold.
    good = grade_emission(
        _T, "def conjecture(obj):\n    return " + pred_to_python(_T.target), None
    ).conjecture.quality
    mimic = grade_emission(_T, "def conjecture(obj):\n    return True", None).conjecture.quality
    pos = [i for i in _T.revealed_idx if _T.labels[i]]
    feats = _U.features
    body = " or ".join("(" + " and ".join(f"obj['{f}'] == {_U.objects[i][f]}"
                                          for f in feats) + ")" for i in pos) or "False"
    overfit = grade_emission(_T, "def conjecture(obj):\n    return " + body, None).conjecture.quality
    assert good > overfit, (good, overfit)
    assert good > mimic, (good, mimic)


# ======================================================================== #
# C. TEST GRADING -- version-space entropy reduction
# ======================================================================== #
def test_version_space_consistent_with_revealed():
    V = consistent_version_space(_TT)
    assert len(V) >= 1
    # every surviving hypothesis MUST match all revealed labels (definition)
    for _hi, sig in V:
        for i in _TT.revealed_idx:
            assert (i in sig) == _TT.labels[i], (i, _hi)
    # the TRUE target is always in the version space
    assert any(sig == _TT.target_sig for _hi, sig in V), "target fell out of V"


def test_optimal_probe_earns_near_optimal_info_gain():
    V = consistent_version_space(_TT)
    assert len(V) > 2, f"need a non-trivial version space, |V|={len(V)}"
    # find the universe object with the best split, propose it -> efficiency ~1
    best_idx, best_gain = None, -1.0
    m = len(V)
    prior = math.log2(m)
    for j in range(len(_UT)):
        t = sum(1 for _hi, sig in V if j in sig)
        f = m - t
        ep = 0.0
        if t: ep += (t/m)*math.log2(t)
        if f: ep += (f/m)*math.log2(f)
        g = prior - ep
        if g > best_gain:
            best_gain, best_idx = g, j
    ts = grade_test_object(_TT, dict(_UT.objects[best_idx]), V=V)
    assert ts.is_in_universe
    assert ts.efficiency > 0.99, ts
    assert ts.info_gain_bits > 0.0, ts


def test_useless_probe_earns_zero_info_gain():
    V = consistent_version_space(_TT)
    # an object on which ALL surviving hypotheses agree -> zero split -> 0 gain.
    m = len(V)
    useless = None
    for j in range(len(_UT)):
        t = sum(1 for _hi, sig in V if j in sig)
        if t == 0 or t == m:
            useless = j
            break
    if useless is not None:
        ts = grade_test_object(_TT, dict(_UT.objects[useless]), V=V)
        assert abs(ts.info_gain_bits) < 1e-9, ts


def test_off_universe_probe_earns_zero():
    # an object that is not in the finite universe distinguishes nothing.
    bogus = {"x": 999, "y": -999, "s": 0, "d": 0, "mx": 0}
    ts = grade_test_object(_TT, bogus)
    assert ts.is_in_universe is False, ts
    assert abs(ts.info_gain_bits) < 1e-9, ts
    assert ts.efficiency == 0.0 or ts.info_gain_bits == 0.0, ts


def test_worst_case_never_exceeds_expected():
    V = consistent_version_space(_TT)
    for j in (0, 5, 17, 33):
        ts = grade_test_object(_TT, dict(_UT.objects[j]), V=V)
        # worst-case (guaranteed) reduction <= expected reduction, always
        assert ts.worst_case_gain_bits <= ts.info_gain_bits + 1e-9, (j, ts)


def test_scores_are_separate_objects():
    # the two graders return DISTINCT score objects; grade_emission keeps them
    # in separate fields (never a fused scalar).
    src = "def conjecture(obj):\n    return " + pred_to_python(_TT.target)
    probe = dict(_UT.objects[_TT.holdout_idx[0]])
    res = grade_emission(_TT, src, probe)
    assert res.conjecture is not None and res.test is not None
    assert type(res.conjecture).__name__ == "ConjectureScore"
    assert type(res.test).__name__ == "TestScore"
    # no attribute fuses them
    assert not hasattr(res, "combined_score")


# --------------------------------------------------------------------------- #
# tiny runner (works without pytest)
# --------------------------------------------------------------------------- #
def _run_all():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    passed, failed = 0, []
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
