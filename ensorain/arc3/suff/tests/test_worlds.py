"""The answer key must be verified before any learner is scored against it."""
import numpy as np

from ensorain.arc3.suff.worlds import W0, W1, W2, W5, even_process, golden_mean, simple_nonunifilar_source, logloss


def test_even_and_golden_mean_bayes_hits_entropy_rate():
    # both have entropy rate h_mu = 2/3 bit/symbol (Crutchfield-Feldman); the Bayes log-loss must converge to it
    for w in (even_process(), golden_mean()):
        x = w.sample(60000, np.random.default_rng(1))
        ll = logloss(w.bayes(x)[1000:], x[1000:])
        assert abs(ll - 2 / 3) < 0.01, (w.name, ll)


def test_even_process_has_no_finite_window():
    # after a long block of 1s, the next-symbol probability depends on the parity of the run: not on any fixed window
    w = even_process()
    x = np.array([0] + [1] * 20 + [1])            # run of 21 ones after a 0
    p_odd = w.bayes(np.array([0] + [1] * 21))[-1]
    p_even = w.bayes(np.array([0] + [1] * 22))[-1]
    assert abs(p_odd[1] - p_even[1]) > 0.4


def test_w1_bayes_is_calibrated_and_beats_plugin_early():
    rng = np.random.default_rng(2)
    lls, pl = [], []
    for _ in range(300):
        w = W1()
        x = w.sample(20, rng)
        lls.append(logloss(w.bayes(x), x))
        n1 = np.concatenate([[0], np.cumsum(x)[:-1]])
        n = np.arange(20)
        p = np.clip(np.where(n > 0, n1 / np.maximum(n, 1), 0.5), 0.01, 0.99)
        pl.append(logloss(np.stack([1 - p, p], 1), x))
    assert np.mean(lls) < np.mean(pl)


def test_w2_bayes_approaches_its_entropy_rate():
    w = W2(2)
    rng = np.random.default_rng(3)
    x = w.sample(40000, rng)
    early = logloss(w.bayes(x)[:500], x[:500])
    late = logloss(w.bayes(x)[-5000:], x[-5000:])
    assert late <= early + 0.01


def test_sns_is_nonunifilar_and_bayes_below_iid():
    w = simple_nonunifilar_source()
    x = w.sample(40000, np.random.default_rng(4))
    ll = logloss(w.bayes(x), x)
    p1 = x.mean()
    iid = -(p1 * np.log2(p1) + (1 - p1) * np.log2(1 - p1))
    assert ll < iid - 0.01


def test_w5_bayes_is_exact_lookup():
    w = W5(n_keys=200, V=8)
    st = w.sample(5000, np.random.default_rng(5))
    P = w.bayes(st)
    y = w.targets(st)
    certain = P.max(1) == 1.0
    assert np.all(P[certain].argmax(1) == y[certain])      # a seen key: the prediction is exact
    assert np.allclose(P[~certain], 1 / 8)


def test_stat_learner_equals_bayes_at_true_order():
    """STAT(k) with the KT estimator IS the Bayes predictor of W2(k) (Beta(.5,.5) prior): excess must be ~0."""
    from ensorain.arc3.suff.learners import STAT, VERB_SUM
    w = W2(2)
    x = w.sample(3000, np.random.default_rng(7))
    b = logloss(w.bayes(x), x)
    assert abs(logloss(STAT(2).run(x)[0], x) - b) < 1e-9
    assert abs(logloss(VERB_SUM(10 ** 6, 2).run(x)[0], x) - b) < 1e-9     # unbounded verbatim + readout = the same
