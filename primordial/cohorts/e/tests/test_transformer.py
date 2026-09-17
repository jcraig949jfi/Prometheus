import numpy as np

from primordial.brain import genomes as gm
from primordial.cohorts.e import transformer as TR
from primordial.qd import e7_run as E7


def test_param_count_and_bytes_follow_shapes():
    f = TR.Transformer(8, 8)
    d, h, D, A = 8, 16, 8, 8
    assert f.nf == d + D * d + 4 * d * d + d * h + h + h * d + d + d * A + A
    assert f.nbytes == 4 * f.nf
    gt = TR.GT(4)
    assert gt.glen == (gt.pb + 8 * gt.W + 3) // 4 * 4 and gt.glen % 4 == 0


def test_pack_unpack_roundtrip():
    gt = TR.GT(4)
    g = gt.init(np.random.default_rng(0), 5)
    raw = gt.pack(g)
    g2 = gt.unpack(raw)
    assert np.array_equal(gt.pack(g2), raw)


def test_batched_forward_matches_float64_reference_on_clear_rows():
    rng = np.random.default_rng(1)
    f = TR.Transformer(8, 8)
    g = f.init(rng, 4)
    obs = rng.integers(0, 65536, (64, 8))
    gidx = np.repeat(np.arange(4), 16)
    fast = f.forward(g, obs, gidx)
    mm = clear = 0
    for p in range(4):
        rows = gidx == p
        ref = f.ref_logits(f.one(g, p), obs[rows])
        ok = gm.clear_rows(ref)
        clear += ok.sum()
        mm += ((ref.argmax(1) != fast[rows]) & ok).sum()
        assert np.allclose(ref, f.logits(g, obs[rows], gidx[rows]), rtol=1e-4, atol=1e-4)
    assert clear > 48 and mm == 0


def test_cheat_changes_actions():
    rng = np.random.default_rng(2)
    f = TR.Transformer(8, 8)
    g = f.init(rng, 8)
    obs = rng.integers(0, 65536, (256, 8))
    gidx = np.repeat(np.arange(8), 32)
    assert (f.forward(g, obs, gidx) != f.forward(g, obs, gidx, cheat=True)).mean() > 0.05


def test_rollout_and_oracles_through_e7():
    gt = TR.GT(4)
    g = gt.init(np.random.default_rng(3), 4)
    seeds = E7.HELD8[:2]
    fit, cells, _, _ = E7.rollout(gt, g, seeds)
    assert fit.shape == (4,) and cells.shape == (4,)
    wo = E7.world_oracle(gt, g, seeds)
    assert wo["elites_failing"] == 0
    assert E7.world_oracle(gt, g, seeds, "skip_lin")["elites_failing"] >= 3
    bo = E7.brain_oracle(gt, g, seeds)
    assert bo["mismatched_rows"] == 0 and bo["clear_rows"] > 0
