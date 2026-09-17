"""M1 floors: the batched constant / random policies agree with the wforge reference world."""
import numpy as np

from primordial.metric import floors as F
from primordial.qd import e4_run as E4


def test_all_actions_is_exhaustive_and_ordered():
    a = F.all_actions(3)
    assert a.shape == (512, 3) and len({tuple(r) for r in a}) == 512
    assert a[0].tolist() == [0, 0, 0] and a[1].tolist() == [0, 0, 1] and a[-1].tolist() == [7, 7, 7]


def _wforge_const(spec, act, seeds):
    g = np.broadcast_to(np.asarray(act, np.int32)[None, None, :], (spec.T, spec.S, spec.W)).copy()
    return sum(int(np.clip(E4.wforge_replay(spec, g, int(s))[1], 0, None).sum()) for s in seeds) / len(seeds)


def test_const_scores_match_wforge():
    spec = E4.Spec(4)
    seeds = F.HELD64[:3]
    acts = np.array([[0] * spec.W, [1] * spec.W, [7] + [0] * (spec.W - 1), [3] * spec.W], np.int32)
    got = F.const_scores(spec, acts, seeds)
    want = [_wforge_const(spec, a, seeds) for a in acts]
    assert np.allclose(got, want)
    assert len(set(np.round(got, 6))) > 1                 # the planted actions are not all the same score


def test_const_scores_chunking_is_invisible(monkeypatch):
    spec = E4.Spec(4)
    acts = F.all_actions(spec.W)[::37]
    whole = F.const_scores(spec, acts, F.TRAIN8)
    monkeypatch.setattr(F, "MAX_ENVS", 24)                 # 3 policies per chunk
    assert np.array_equal(F.const_scores(spec, acts, F.TRAIN8), whole)


def test_random_policy_is_seeded():
    spec = E4.Spec(4)
    a = F.random_scores(spec, F.HELD64[:4], [0, 1])
    b = F.random_scores(spec, F.HELD64[:4], [0, 1])
    assert np.array_equal(a, b)
