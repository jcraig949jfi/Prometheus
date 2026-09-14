import numpy as np
import pytest

from primordial.brain import genomes as gm
from primordial.brain.tt_policy import TTPolicy, ref64_logits


def _batch(fam, P=5, n=300, seed=0):
    rng = np.random.default_rng(seed)
    g = fam.init(rng, P)
    obs = rng.integers(0, 65536, size=(n, fam.D), dtype=np.int64)
    gidx = rng.integers(0, P, size=n)
    return g, obs, gidx


@pytest.mark.parametrize("name", list(gm.FAMILIES))
def test_batched_forward_matches_reference(name):
    fam = gm.FAMILIES[name](D=5, A=8)
    g, obs, gidx = _batch(fam)
    got = fam.forward(g, obs, gidx)
    checked = 0
    for p in range(len(g[0])):
        rows = np.flatnonzero(gidx == p)
        ref = fam.ref_logits(fam.one(g, p), obs[rows])
        ok = gm.clear_rows(ref)
        assert np.array_equal(got[rows][ok], ref.argmax(1)[ok])
        checked += ok.sum()
    assert checked > 250


@pytest.mark.parametrize("name", list(gm.FAMILIES))
def test_cheat_forward_is_caught(name):
    fam = gm.FAMILIES[name](D=5, A=8)
    g, obs, gidx = _batch(fam, seed=1)
    bad = fam.forward(g, obs, gidx, cheat=True)
    mism = 0
    for p in range(len(g[0])):
        rows = np.flatnonzero(gidx == p)
        ref = fam.ref_logits(fam.one(g, p), obs[rows]).argmax(1)
        mism += int((bad[rows] != ref).sum())
    assert mism > 30


@pytest.mark.parametrize("name", list(gm.FAMILIES))
def test_pack_roundtrip_and_charge(name):
    fam = gm.FAMILIES[name](D=5, A=8)
    g, _, _ = _batch(fam, P=3)
    B = fam.pack(g)
    assert B.shape == (3, fam.nbytes) and B.dtype == np.uint8
    for x, y in zip(g, fam.unpack(B)):
        assert np.array_equal(x, y)


def test_tt_digits_agrees_with_lane_c_policy_oracle():
    fam = gm.TTDigits(D=3, A=8)
    g, obs, _ = _batch(fam, P=1, n=200, seed=2)
    al, G, Wo = fam.one(g, 0)
    pol = TTPolicy(al.astype(np.float64), G.astype(np.float64), Wo.astype(np.float64))
    ref = ref64_logits(pol, obs.astype(np.uint16))
    ok = gm.clear_rows(ref)
    assert np.array_equal(fam.forward(g, obs, np.zeros(200, int))[ok], ref.argmax(1)[ok])


def test_sizes_are_ordered_smallest_first():
    D = 6
    sizes = [gm.FAMILIES[n](D).nbytes for n in ("linear", "lut_top", "tt_feat", "tt_digits")]
    assert sizes == sorted(sizes)
