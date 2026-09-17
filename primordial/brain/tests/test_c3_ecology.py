import numpy as np

from primordial.brain import c3_ecology as c3


def test_pack_roundtrip_and_bits8_size():
    rng = np.random.default_rng(0)
    T = rng.standard_normal(c3.SHAPE)
    blob, _, _ = c3.fit_bits(T, 8)
    assert len(blob) > 65536                      # the uint16 shape field would have overflowed here
    rec = c3.decode(blob)
    assert np.max(np.abs(rec - T)) <= (T.max() - T.min()) / 255 / 2 + 1e-9


def test_dense_and_tt_full_rank_exact_from_bytes():
    rng = np.random.default_rng(1)
    T = c3.standardize(rng.standard_normal(c3.SHAPE))
    blob = c3.pack("dense", [T.astype(np.float32)])
    assert np.mean((c3.decode(blob) - T) ** 2) < 1e-12
    blob, _, _ = c3.fit_tt(c3.make_targets(0)["separable_decay"], 16)
    assert np.mean((c3.decode(blob) - c3.make_targets(0)["separable_decay"]) ** 2) < 1e-10


def test_program_search_finds_in_space_target_exactly():
    T = c3.make_targets(0)["program_in"]
    blob, _, flops = c3.fit_program(T)
    assert len(blob) <= 64 and flops == 5
    assert np.mean((c3.decode(blob) - T) ** 2) < 1e-12


def test_cheat_ref_is_flagged_and_honest_is_not():
    T = c3.make_targets(0)["tt_rank2"]
    blob, predict, _ = c3.CheatRef(T).fit()
    var = T.var()
    rel_b = np.mean((c3.decode(blob) - T) ** 2) / var
    rel_m = np.mean((predict() - T) ** 2) / var
    assert c3.mismatch(rel_b, rel_m)
    blob, predict, _ = c3.fit_tt(T, 2)
    rel_b = np.mean((c3.decode(blob) - T) ** 2) / var
    rel_m = np.mean((predict() - T) ** 2) / var
    assert not c3.mismatch(rel_b, rel_m)


def test_c3b_program_fit_on_constant_targets_does_not_divide_by_zero():
    from primordial.brain import c3b_learn as L
    idx = np.arange(64)
    y = np.full(64, 0.25)
    blob = L.fit_program(idx, y, np.zeros(c3.SHAPE))
    assert np.allclose(c3.decode(blob), 0.25, atol=1e-6)


def test_pareto_basic():
    pts = [{"rep": "a", "bytes": 1, "rel_mse": 1.0}, {"rep": "b", "bytes": 2, "rel_mse": 0.5},
           {"rep": "c", "bytes": 3, "rel_mse": 0.6}]
    assert c3.pareto(pts, ("bytes", "rel_mse")) == ["a", "b"]
