import numpy as np

from primordial.brain import affine_plastic as ap


def test_inv_odd_exact_on_every_odd_residue():
    d = np.arange(1, 1 << 16, 2)
    assert np.all((ap.inv_odd(d) * d) & ap.MASK == 1)


def test_fit_recovers_exact_affine_map_clean_and_with_30pct_corrupted_targets():
    rng = np.random.default_rng(0)
    X = rng.integers(0, 1 << 16, size=(1024, 5))
    for s_t, a_t, c_t in [(2, 40503, 17), (0, 1, 0), (4, 25033, 999)]:
        y = (a_t * X[:, s_t] + c_t) & ap.MASK
        assert ap.fit_affine(X, y, rng)[:3] == (s_t, a_t, c_t)
        yc = y.copy()
        bad = rng.random(len(y)) < 0.3
        yc[bad] = rng.integers(0, 1 << 16, bad.sum())
        s, a, c, sup = ap.fit_affine(X, yc, rng)
        assert (s, a, c) == (s_t, a_t, c_t) and 0.6 < sup < 0.8


def _drive(cls, shift):
    rng = np.random.default_rng(5)
    b = cls(seed=1)
    trace = []
    for t in range(24):
        X = rng.integers(0, 1 << 16, size=(256, 3))
        a = 40503 if (t // 8) % 2 == 0 else (1 << 16) - 40503           # the B-world flip a -> M - a
        y = (a * X[:, 1] + 7) & ap.MASK
        b.observe_flag((t + shift) // 8)
        b.adapt_batch(X, y)
        trace.append((b.surprised, b.model))
    return trace


def test_honest_learner_detects_flips_and_ignores_flag_leak_learner_does_not():
    honest0, honest3 = _drive(ap.PlasticAffine, 0), _drive(ap.PlasticAffine, 3)
    assert honest0 == honest3                                            # flag-shift invariant
    assert [t for t, (s, _) in enumerate(honest0) if s] == [0, 8, 16]    # first fit + both flips, on the tick
    assert honest0[8][1] == (1, (1 << 16) - 40503, 7)
    leak0, leak3 = _drive(ap.LeakAffine, 0), _drive(ap.LeakAffine, 3)
    assert leak0 != leak3                                                # the probe sees the leak
