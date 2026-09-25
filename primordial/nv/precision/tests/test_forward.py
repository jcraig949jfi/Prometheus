"""P2: the precision gene's forward against the fp64 brain oracle, and the controls it must catch."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from primordial.brain import genomes as gm  # noqa: E402
from primordial.nv.precision import forward as pf  # noqa: E402

DEVICES = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])


def _case(family, D=12, n=512, seed=0):
    rng = np.random.default_rng(seed)
    fam = gm.FAMILIES[family](D)
    g1 = fam.one(fam.init(rng, 1), 0)
    obs = rng.integers(0, 65536, (n, D), dtype=np.int64).astype(np.uint16)
    return fam, g1, obs, fam.ref_logits(g1, obs)


def test_gene_maps_every_byte_to_a_precision():
    assert [pf.gene_to_precision(i) for i in range(5)] == list(pf.PRECISIONS)
    assert pf.gene_to_precision(255) in pf.PRECISIONS


def test_unknown_precision_raises():
    fam, g1, obs, _ = _case("linear", n=4)
    with pytest.raises(ValueError):
        pf.precision_logits("linear", g1, obs, "fp4")


@pytest.mark.parametrize("family", pf.FAMILIES)
def test_bytes_shrink_with_precision(family):
    b = {p: pf.nbytes(family, 12, p) for p in pf.PRECISIONS}
    assert b["fp32"] == gm.FAMILIES[family](12).nbytes + 1
    assert b["fp16"] == b["bf16"] < b["fp32"]
    assert b["int8"] == b["fp8_sim"] < b["fp16"]


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("family", pf.FAMILIES)
def test_fp32_matches_oracle_on_clear_rows(family, device):
    fam, g1, obs, ref = _case(family)
    r = pf.exactness(family, g1, obs, "fp32", device, ref=ref)
    assert r["n_clear"] > 400
    assert r["agree_clear"] >= 0.998
    assert r["max_logit_err"] < 1e-3


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("family", pf.FAMILIES)
@pytest.mark.parametrize("precision", pf.PRECISIONS)
def test_every_precision_runs_and_beats_the_cheat(family, precision, device):
    fam, g1, obs, ref = _case(family)
    honest = pf.exactness(family, g1, obs, precision, device, ref=ref)
    cheat = pf.exactness(family, g1, obs, precision, device, cheat=True, ref=ref)
    assert honest["agree_clear"] > 0.8, honest
    assert cheat["agree_clear"] < honest["agree_clear"] - 0.2, (honest, cheat)


def test_linear_int8_cuda_kernel_equals_integer_emulation():
    if not torch.cuda.is_available():
        pytest.skip("needs cuda")
    fam, g1, obs, _ = _case("linear", n=256)
    a = pf.precision_logits("linear", g1, obs, "int8", "cuda")
    b = pf.precision_logits("linear", g1, obs, "int8", "cpu")
    assert pf.substrate("linear", "int8", "cuda") == "int8_intmm"
    np.testing.assert_allclose(a, b, rtol=1e-6, atol=1e-6)      # same integers, fp32 scales on two devices
    assert (a.argmax(1) == b.argmax(1)).all()
