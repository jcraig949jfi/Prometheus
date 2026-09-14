"""F8: FusedRollout built from the (world id, seed) table cache is bytes-equal to the cold
per-env build and at least 5x faster."""
from __future__ import annotations

import time

import numpy as np
import pytest

from primordial.fabric import worldcache as wc


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(wc, "DIR", tmp_path / "wc")
    monkeypatch.setenv("PM_WORLDCACHE", "1")
    wc.clear_memory()
    yield tmp_path / "wc"
    wc.clear_memory()


def _cold_env_arrays(bs, P, seeds):
    """The pre-F8 FusedRollout.__init__ arrays, computed per env."""
    seeds_env = np.tile(np.asarray(seeds, np.int64), P)
    return wc.cold_tables(bs.mech, bs.wid, seeds_env)


def _specs():
    from primordial.qd import e5_run as E5
    from primordial.qd import e7_run as E7
    g7 = E7.G7(4, "linear")
    return [("tt_digits", E5.BrainSpec(4), None), ("linear", g7.spec, g7)]


@pytest.mark.parametrize("which", [0, 1])
def test_cached_build_is_bytes_equal_and_runs_identically(cache_dir, which):
    from primordial.qd import e5_run as E5
    from primordial.soup.b6.fused import FusedRollout
    fam, bs, g7 = _specs()[which]
    P, seeds = 6, np.array([9100, 9101, 9107, 9100, 9230], np.int64)      # includes a repeated seed
    regs, stoch, corr = _cold_env_arrays(bs, P, seeds)
    for attempt in ("cold", "memory", "disk"):
        if attempt == "disk":
            wc.clear_memory()
            assert any(cache_dir.glob("*.npz"))
        fr = FusedRollout(bs, P, seeds, family=fam)
        assert fr.regs0.tobytes() == regs.tobytes() and fr.regs0.dtype == regs.dtype
        assert fr.st_stoch0.tobytes() == stoch.tobytes() and fr.st_stoch0.dtype == np.uint64
        assert fr.st_corr0.tobytes() == corr.tobytes() and fr.st_corr0.shape == corr.shape
    rng = np.random.default_rng(3)
    g = E5.init_brains(rng, bs, P) if g7 is None else g7.init(rng, P)
    wc.clear_memory()
    fit_a, cells_a, done_a, _, _ = FusedRollout(bs, P, seeds, family=fam).run(g)
    import primordial.soup.b6.fused as F
    orig = F.worldcache.tables
    try:
        F.worldcache.tables = wc.cold_tables                                 # force the uncached path
        fit_b, cells_b, done_b, _, _ = FusedRollout(bs, P, seeds, family=fam).run(g)
    finally:
        F.worldcache.tables = orig
    assert np.array_equal(fit_a, fit_b) and np.array_equal(cells_a, cells_b) and np.array_equal(done_a, done_b)


def test_mechanics_digest_separates_worlds_sharing_an_id(cache_dir):
    import dataclasses
    from primordial.qd import e5_run as E5
    bs = E5.BrainSpec(4)
    other = dataclasses.replace(bs.mech, n_regs=bs.mech.n_regs + 1)
    assert wc.mech_digest(other) != wc.mech_digest(bs.mech)
    r1, _, _ = wc.tables(bs.mech, bs.wid, [9100])
    r2, _, _ = wc.tables(other, bs.wid, [9100])
    assert r1.shape[1] + 1 == r2.shape[1]


def test_cached_build_is_at_least_5x_faster_than_cold(cache_dir):
    from primordial.qd import e5_run as E5
    from primordial.soup.b6.fused import FusedRollout
    bs = E5.BrainSpec(4)
    P, seeds = 128, np.arange(9100, 9228, dtype=np.int64)
    FusedRollout(bs, 2, seeds)                                              # fills the cache
    t = time.perf_counter()
    _cold_env_arrays(bs, P, seeds)
    cold = time.perf_counter() - t
    warm = min(_timed(lambda: FusedRollout(bs, P, seeds)) for _ in range(3))
    assert cold / warm >= 5, (cold, warm)


def _timed(f):
    t = time.perf_counter()
    f()
    return time.perf_counter() - t
