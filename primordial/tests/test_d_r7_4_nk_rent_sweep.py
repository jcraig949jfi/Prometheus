"""D-R7-4: the sweep rule, the LAMBDA-parameterised reference, and the half_rent exemption (the runs are the job's)."""
import numpy as np

from primordial.cohorts.d import r7_4_nk_rent_sweep as D
from primordial.fabric import rows as R


def runs(active_by_lambda, n=32):
    keys = [(f, rs) for f in D.FAMILIES for rs in range(8)][:n]
    return {L: {k: {"best_active": a(i) if callable(a) else a, "best_net": 1, "best_raw_nk": 1, "qd_score": 1,
                    "coverage": 0.5, "archive_cells": 2, "elites_mismatched": 0,
                    "offers_audited": 1 if i == 0 else 0, "offers_mismatched": 0}
                for i, k in enumerate(keys)}
            for L, a in active_by_lambda.items()}


def test_rent_binds():
    got, st = D.decide(True, True, runs({0: 8, 16384: 8, 131072: 6}))
    assert got == "RENT_BINDS" and st["shrink_streams"] == 32 and st["median_best_active"]["131072"] == 6.0


def test_rent_inert():
    got, st = D.decide(True, True, runs({0: 8, 16384: 8, 131072: 8}))
    assert got == "RENT_INERT" and st["shrink_streams"] == 0


def test_mixed_when_median_moves_but_few_streams_shrink():
    a = lambda i: 6 if i < 12 else 8                      # median 8 at the top lambda, 12 streams shrink
    assert D.decide(True, True, runs({0: 8, 16384: 8, 131072: a}))[0] == "MIXED"
    b = lambda i: 6 if i < 20 else 8                      # 20 shrink: below BINDS, above INERT
    assert D.decide(True, True, runs({0: 8, 16384: 8, 131072: b}))[0] == "MIXED"


def test_indeterminate():
    assert D.decide(False, True, runs({0: 8, 16384: 8, 131072: 6}))[0] == "INDETERMINATE"
    assert D.decide(True, False, runs({0: 8, 16384: 8, 131072: 6}))[0] == "INDETERMINATE"
    assert D.decide(True, True, runs({0: 8, 131072: 6}))[0] == "INDETERMINATE"


def test_eval_ref_charges_lambda_per_active_instruction():
    world = D.NKWorld()
    g = np.random.Generator(np.random.PCG64(3)).integers(0, 256, (64, D.GLEN), dtype=np.uint8)
    active = D.C2.decode_ref(g)[1].astype(np.int64)
    net0 = D.eval_ref(world, g, 0)[0].astype(np.int64)
    net_l = D.eval_ref(world, g, 16384)[0].astype(np.int64)
    assert np.array_equal(net0 - net_l, 16384 * active)
    assert np.array_equal(D.eval_ref(world, g, 16384, cheat=2)[0].astype(np.int64), net0 - 8192 * active)
    assert np.array_equal(D.eval_ref(world, g, 0, cheat=2)[0], D.eval_ref(world, g, 0)[0])   # exempt at 0


def test_half_rent_control_is_exempt_only_at_lambda_zero():
    world = D.NKWorld()
    honest = lambda L: (lambda g, cheat=0: D.eval_ref(world, g, L, cheat))   # honours the cheat flag, as C's Lua does
    out = D.cheat_controls(honest(0), world, 0)
    assert out["honest"]["ok"] and out["skip_last"]["ok"]
    assert out["half_rent"]["exempt"] and out["half_rent"]["ok"] and out["half_rent"]["mismatch_share"] == 0.0
    out16 = D.cheat_controls(honest(16384), world, 16384)
    assert not out16["half_rent"]["exempt"] and out16["half_rent"]["ok"] and out16["skip_last"]["ok"]
    blind = lambda g, cheat=0: D.eval_ref(world, g, 16384, 0)                # an evaluator that ignores the cheat flag
    out_blind = D.cheat_controls(blind, world, 16384)
    assert out_blind["honest"]["ok"] and not out_blind["skip_last"]["ok"] and not out_blind["half_rent"]["ok"]


def test_emitted_status_is_writable_by_the_rowwriter():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in R.STATUSES
