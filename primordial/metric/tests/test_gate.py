"""M1 gate floor: the batched gate scorer agrees with const_scores at the extremes and with the
production closed-loop scorer (E7.rollout on an A=2 linear genome) on mixed gates."""
import numpy as np
import pytest

from primordial.brain import genomes as gm
from primordial.metric import floors as F
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7


def _gates(feat, thr, dr, act):
    return {"feat": np.array(feat), "thr": np.array(thr, np.int64), "dir": np.array(dr),
            "act": np.array(act, np.int32)}


def test_always_and_never_gates_equal_constant_policies():
    spec = E4.Spec(4)
    act = [[1, 2, 3], [7, 0, 0]]
    seeds = F.HELD64[:4]
    always = F.gate_scores(spec, _gates([0, 3], [0, 0], [1, 1], act), seeds)        # obs >= 0 always
    never = F.gate_scores(spec, _gates([0, 3], [0, 0], [-1, -1], act), seeds)       # obs < 0 never
    assert np.array_equal(always, F.const_scores(spec, np.array(act), seeds))
    assert np.array_equal(never, F.const_scores(spec, np.zeros((2, 3), np.int32), seeds))


def _rollout_gate(gs, f, thr, dr, act, seeds):
    """The same gate as an A=2 linear brain: logit1 - logit0 = dir * (obs_f - thr + 0.5)."""
    g7 = E7.G7(gs, "linear")
    g7.fam = gm.FAMILIES["linear"](g7.D, 2)
    g7.pb, g7.cb = g7.fam.nbytes, 2 * g7.W
    W = np.zeros((1, g7.D, 2), np.float32)
    b = np.zeros((1, 2), np.float32)
    W[0, f, 1] = dr * 65535.0
    b[0, 1] = dr * (32768.0 - thr)
    C = np.zeros((1, 2, g7.W), np.uint8)
    C[0, 1] = act
    return E7.rollout(g7, ((W, b), C), seeds)[0][0] / len(seeds)


@pytest.mark.parametrize("gs", [4, 3])
def test_mixed_gates_equal_the_closed_loop_scorer(gs):
    spec = E4.Spec(gs)
    g = F.gate_candidates(spec)
    rng = np.random.default_rng(gs)
    idx = rng.choice(len(g["feat"]), size=6, replace=False)
    seeds = F.HELD64[:4]
    got = F.gate_scores(spec, F._pick(g, idx), seeds)
    want = [_rollout_gate(gs, int(g["feat"][i]), int(g["thr"][i]), int(g["dir"][i]), g["act"][i], seeds) for i in idx]
    assert np.allclose(got, want)
    assert len(set(np.round(got, 6))) > 1


def test_candidates_use_train_quantiles_and_skip_the_abstain_action():
    spec = E4.Spec(3)
    g = F.gate_candidates(spec)
    assert not (g["act"] == 0).all(1).any()
    assert (g["thr"] > 0).all()          # thr 0 = always/never on, i.e. a constant or abstain (v1 defect)
    assert len(g["feat"]) % (8 ** spec.W - 1) == 0
    assert set(np.unique(g["dir"])) == {-1, 1}
