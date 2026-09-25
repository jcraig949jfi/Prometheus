"""Regression (C-R5-AP-01 fitness recount oracle): offer-time fitness must use the declared decoder act = cb[sym] % 8,
so a genome scores the same from raw codebook bytes as after a pack/unpack round trip."""
import numpy as np

import primordial.cohorts.c.r5_ap01_tt_digits_d1_cpu_ttl_lua as M


def test_raw_codebook_bytes_score_as_their_packed_genome():
    rng = np.random.Generator(np.random.PCG64(5))
    p, cb = M.FAM.init(rng, 32), rng.integers(0, 256, (32, 8))
    assert (cb >= 8).any()
    fit_raw = M.evaluate(p, cb)[0]
    fit_packed = M.evaluate(*M.unpack(M.pack(p, cb)))[0]
    assert np.array_equal(fit_raw, fit_packed)


def test_actions_are_in_range():
    rng = np.random.Generator(np.random.PCG64(6))
    p, cb = M.FAM.init(rng, 8), rng.integers(0, 256, (8, 8))
    _, act = M.tables(p, cb)
    assert act.min() >= 0 and act.max() < M.A
