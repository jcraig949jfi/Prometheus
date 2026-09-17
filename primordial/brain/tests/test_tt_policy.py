import numpy as np
import pytest

from primordial.brain import tt_policy as tt
from primordial.core.contract import Brain

try:
    import torch
    HAVE_CUDA = torch.cuda.is_available()
except ImportError:
    HAVE_CUDA = False

CPU = list(tt.CPU_HONEST)
GPU = list(tt.GPU_HONEST) if HAVE_CUDA else []


def test_digits_roundtrip():
    obs = np.array([[0, 1, 0xABCD, 65535]], np.uint16)
    d = tt.digits(obs)
    assert d.shape == (1, 16)
    assert d[0, 8:12].tolist() == [0xA, 0xB, 0xC, 0xD]
    back = (d.reshape(1, 4, 4).astype(np.int64) * np.array([4096, 256, 16, 1])).sum(-1)
    assert back.tolist() == obs.tolist()


@pytest.mark.parametrize("name", CPU + GPU)
def test_additive_positive_control_exact(name):
    rng = np.random.default_rng(0)
    f = rng.integers(-8, 9, size=(8, 16, 8)).astype(np.float64)
    p = tt.additive_policy(f, r=12)
    obs = rng.integers(0, 65535, size=(300, 2), dtype=np.uint16, endpoint=True)
    exact = tt.additive_logits(f, obs)
    be = tt.make(name, p)
    try:
        assert np.array_equal(be.logits(obs), exact)
    except NotImplementedError:
        a = be.to_numpy(be.run(be.prepare(obs)))
        top2 = np.sort(exact, 1)[:, -2:]
        clear = (top2[:, 1] - top2[:, 0]) > 0.5
        assert np.array_equal(a[clear], exact.argmax(1)[clear])
    finally:
        be.close()


@pytest.mark.parametrize("name", CPU + GPU)
def test_random_policy_matches_float64_oracle(name):
    p = tt.random_policy(obs_dim=4, r=16, A=8, seed=3)
    obs = np.random.default_rng(1).integers(0, 65535, size=(257, 4), dtype=np.uint16, endpoint=True)
    ref = tt.ref64_logits(p, obs)
    be = tt.make(name, p)
    try:
        a = be.to_numpy(be.run(be.prepare(obs)))
        top2 = np.sort(ref, 1)[:, -2:]
        clear = (top2[:, 1] - top2[:, 0]) > 2e-2
        assert np.array_equal(a[clear], ref.argmax(1)[clear])
    finally:
        be.close()


def test_cheat_skip_half_fails_oracle():
    p = tt.random_policy(obs_dim=4, r=16, A=8, seed=3)
    obs = np.random.default_rng(1).integers(0, 65535, size=(512, 4), dtype=np.uint16, endpoint=True)
    ref = tt.ref64_logits(p, obs)
    a = tt.make("cheat_skip_half", p).run(obs)
    assert (a != ref.argmax(1)).mean() > 0.5


def test_brain_protocol():
    p = tt.random_policy(obs_dim=2, r=4, A=8, seed=0)
    b = tt.TTPolicyBrain(p, backend="np_bucket")
    assert isinstance(b, Brain)
    acts, msg = b.act(np.zeros((3, 2, 2), np.uint16), None)
    assert acts.shape == (3, 2, 1) and acts.dtype == np.int32 and msg is None
    assert b.cost()["flops_per_act"] == 8 * 16 + 4 * 8
