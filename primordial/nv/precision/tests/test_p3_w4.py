"""P3: the closed-loop precision wrapper against lane E's committed E9 numbers (needs pm-data elites)."""
import numpy as np
import pytest

pytest.importorskip("torch")

from primordial.nv.precision import p3_w4 as P3  # noqa: E402

needs_elites = pytest.mark.skipif(not (P3.E9_HOT / "full_w4_linear_r0_top.npy").exists(),
                                  reason="E9 elites not in pm-data on this host")


def test_wrapper_delegates_oracle_and_rejects_bad_precision():
    from primordial.brain import genomes as gm
    fam = gm.FAMILIES["linear"](8)
    w = P3.PrecisionFamily(fam, "fp16")
    g = fam.init(np.random.default_rng(0), 3)
    obs = np.random.default_rng(1).integers(0, 65536, (30, 8)).astype(np.uint16)
    gidx = np.repeat(np.arange(3), 10)
    a = w.forward(g, obs, gidx)
    assert a.shape == (30,) and a.dtype == np.int64
    np.testing.assert_array_equal(w.ref_logits(w.one(g, 1), obs), fam.ref_logits(fam.one(g, 1), obs))
    with pytest.raises(ValueError):
        P3.PrecisionFamily(fam, "fp4").forward(g, obs, gidx)


@needs_elites
@pytest.mark.parametrize("fam", ["linear", "tt_feat"])
def test_fp32_reproduces_e9_held64_on_seed0(fam):
    r = P3.evaluate(fam, 0, "fp32", oracle=False)
    assert r["held64_per_seed"] == P3.e9_held64(fam, 0)


@needs_elites
def test_cheat_is_caught_by_the_on_policy_oracle():
    honest = P3.evaluate("linear", 0, "fp32")
    cheat = P3.evaluate("linear", 0, "fp32", cheat=True)
    assert honest["agree_clear"] >= 0.99
    assert cheat["agree_clear"] < 0.9
