import numpy as np

from primordial.brain import plastic as pl


def test_round_without_charge_preserves_function():
    rng = np.random.default_rng(0)
    cores = pl.random_target(4, 3, rng)
    X = rng.integers(0, 16, size=(500, 4))
    out, _ = pl.tt_round([c.copy() for c in cores], lam=0.0, rmax=99)
    assert np.allclose(pl.tt_eval(out, X), pl.tt_eval(cores, X), atol=1e-10)


def test_sigma_squared_is_mse_units_and_rounding_finds_true_rank():
    rng = np.random.default_rng(1)
    for r in (1, 2, 5):
        cores = pl.random_target(4, r, rng)
        T = pl.tt_full(cores)
        assert abs(np.mean(T ** 2) - 1.0) < 1e-9
        sig = pl.bond_sigmas(T)
        assert all(abs((s ** 2).sum() - 1.0) < 1e-9 for s in sig)
        grown = pl.grow([c.copy() for c in cores], 3, 12, rng, scale=1e-7)
        out, s2 = pl.tt_round(grown, lam=1e-4, rmax=12)
        assert pl.ranks(out) == [r, r, r]
        assert np.allclose(s2[1][:r], sig[1][:r], atol=1e-5)


def test_als_recovers_low_rank_target():
    rng = np.random.default_rng(2)
    tgt = pl.random_target(4, 2, rng)
    X = rng.integers(0, 16, size=(6000, 4))
    y = pl.tt_eval(tgt, X)
    b = pl.PlasticTTBrain(d=4, rank0=3, seed=0)
    for _ in range(15):
        pl.als_sweep(b.cores, X, y, ridge=1e-6)
        b.cores, _ = pl.tt_round(b.cores, 0.0, 99)
    Xt = rng.integers(0, 16, size=(2000, 4))
    assert np.mean((pl.tt_eval(b.cores, Xt) - pl.tt_eval(tgt, Xt)) ** 2) < 1e-3


def test_leak_brain_reacts_to_flag_honest_does_not():
    rng = np.random.default_rng(3)
    tgt = pl.random_target(4, 2, rng)
    traces = {}
    for cls in (pl.PlasticTTBrain, pl.LeakTTBrain):
        for shift in (0, 3):
            b = cls(d=4, seed=0)
            rs = []
            for t in range(12):
                g = np.random.default_rng([9, t])
                X = g.integers(0, 16, size=(256, 4), dtype=np.uint8)
                y = pl.tt_eval(tgt, X)
                b.observe_flag((t + shift) // 6)
                b.adapt_batch(X, y, b.predict(X))
                rs.append(tuple(pl.ranks(b.cores)) + (b.surprised,))
            traces[(cls.__name__, shift)] = rs
    assert traces[("PlasticTTBrain", 0)] == traces[("PlasticTTBrain", 3)]
    assert traces[("LeakTTBrain", 0)] != traces[("LeakTTBrain", 3)]
