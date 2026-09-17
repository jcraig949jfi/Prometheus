"""D25 (r8 conditional C2): signflip_p is a function of the MULTISET of paired diffs, not their order.

The defect lived only in the Monte Carlo branch (n > SIGNFLIP_EXACT_MAX): one seeded sign matrix, column j paired with
diff j, so permuting the diffs changed p. The exact branch enumerates all 2^n flips and was order-invariant already,
so every test here asserts it actually REACHED the MC branch before it asserts invariance.
"""
from __future__ import annotations

import random

import numpy as np

from primordial.cohorts.e import transfer as T
from primordial.score import transfer_b as TB


def _perms(d, k=6, seed=20260916):
    rng = random.Random(seed)
    out = [list(reversed(d)), sorted(d), sorted(d, reverse=True)]
    for _ in range(k):
        s = list(d)
        rng.shuffle(s)
        out.append(s)
    return out


def test_mc_branch_p_is_bitwise_order_invariant_at_the_gate_probe_vector():
    d = [((-1) ** i) * (0.25 + 0.5 * i) for i in range(32)]           # A's repro, BUILD_R8 gate probe
    assert T.signflip_method(len(d)).startswith("montecarlo")           # the branch D25 is about
    p = T.signflip_p(d)
    assert 0 < p < 1
    assert all(T.signflip_p(s) == p for s in _perms(d))


def test_mc_branch_invariance_holds_near_alpha_and_just_above_the_exact_cutoff():
    for n, loc in ((21, 0.35), (32, 0.36), (40, 0.30)):
        d = np.random.Generator(np.random.PCG64(n)).normal(loc, 1.0, n).tolist()
        assert T.signflip_method(n).startswith("montecarlo")
        p = T.signflip_p(d)
        assert all(T.signflip_p(s) == p for s in _perms(d)), n


def test_the_judge_gives_the_implementation_p_for_every_order():
    """Judge and experimenter must never disagree silently: TB delegates, and does so on permuted input too."""
    d = np.random.Generator(np.random.PCG64(7)).normal(0.3, 1.0, 32).tolist()
    p = T.signflip_p(d)
    assert all(TB.signflip_p(s) == p for s in _perms(d))
    assert "from primordial.cohorts.e.transfer import signflip_p" in open(TB.__file__, encoding="utf-8").read()


def test_exact_branch_values_are_unchanged():
    assert T.signflip_method(20) == "exact"
    assert T.signflip_p([1.0] * 8) == 1 / 256 and T.signflip_p([-1.0] * 8) == 1.0
    assert TB.signflip_p([1.0, 2.0, 3.0]) == 0.125
    assert T.signflip_p([1.0] * 32) == 1 / (T.SIGNFLIP_DRAWS + 1)        # the MC floor survives canonical order


def test_ndarray_and_list_inputs_agree():
    d = np.random.Generator(np.random.PCG64(9)).normal(0.1, 1.0, 24)
    assert T.signflip_p(d) == T.signflip_p(d.tolist()) == T.signflip_p(d[::-1].copy())
