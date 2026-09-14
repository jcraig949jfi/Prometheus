"""Lane D signal world, codes, probe and channel. Channel tests need 127.0.0.1:6393 (skip otherwise)."""
import numpy as np
import pytest
import redis

from primordial.lingua import signal as S


def _exact(k, enc, dec, a, b, d):
    c, y, bits, ent = S.evaluate(np.array([k]), np.asarray(enc)[None], np.asarray(dec)[None],
                                 np.arange(256), a, b, d)
    return float(c[0]), float(y[0]), float(bits[0]), int(ent[0])


@pytest.mark.parametrize("m", range(1, 9))
def test_hand_code_hits_the_formula(m):
    k, enc, dec = S.hand_code(m)
    c, y, bits, ent = _exact(k, enc, dec, 0.3, 0.01, 1.0)
    kk = 0 if m == 1 else int(np.ceil(np.log2(m)))
    assert y == pytest.approx(m / 8) and ent == m
    assert c == pytest.approx(0.3 * kk * (m - 1) / 8 + 0.01 * m + (1 - m / 8))


def test_no_random_or_mutated_genome_beats_the_analytic_bound():
    rng = np.random.default_rng(0)
    k, enc, dec = S.random_genomes(rng, 256)
    for _ in range(20):
        k, enc, dec = S.mutate(rng, k, enc, dec, p_compact=0.5)
    for a, b in [(0.0, 0.0), (0.3, 0.01), (1.5, 0.0)]:
        cost = S.evaluate(k, enc, dec, np.arange(256), a, b, 1.0)[0]
        assert cost.min() >= S.analytic_optimum(a, b, 1.0)[1] - 1e-9


def test_compact_preserves_behaviour():
    rng = np.random.default_rng(1)
    k, enc, dec = S.random_genomes(rng, 16)
    before = np.take_along_axis(dec, enc, 1)
    for i in range(16):
        S._compact(enc, dec, i)
    assert (np.take_along_axis(dec, enc, 1) == before).all()


def test_mi_of_hand_codes():
    assert S.mi_bucket(S.hand_code(8)[1]) == pytest.approx(3.0)
    assert S.mi_low(S.hand_code(8)[1]) == pytest.approx(0.0, abs=1e-12)
    assert S.mi_bucket(np.arange(256)) == pytest.approx(3.0) and S.mi_low(np.arange(256)) == pytest.approx(5.0)


def test_probe_flags_leak_not_honest():
    seeds = np.arange(256)
    rng = np.random.default_rng(2)
    honest = S.scramble_probe(*S.hand_code(8), seeds, 32, rng)
    leak = S.scramble_probe(*S.hand_code(1), seeds, 32, rng, leak=True)
    assert honest["norm_drop"] > 0.8 and not honest["flagged_leak"]
    assert leak["y"] == 1.0 and leak["flagged_leak"]


def test_np_world_conserves_charge():
    seeds = np.arange(64)
    res = S.run_world(*S.hand_code(8), seeds, 32, S.NpChannel(64, 2, 8), y_int=3)
    assert S.conservation_violations(res, 8, 2, 3) == 0


@pytest.fixture
def r():
    c = redis.Redis(host="127.0.0.1", port=6393)
    try:
        c.ping()
    except redis.ConnectionError:
        pytest.skip("lane D substrate not running on 6393")
    return c


def test_lua_equals_np_and_cheats_break_conservation(r):
    from primordial.lingua.channel import LuaChannel
    seeds = np.arange(64)
    code = S.hand_code(8)
    ref_ch = S.NpChannel(64, 2, 8)
    ref = S.run_world(*code, seeds, 32, ref_ch, y_int=3)
    assert ref_ch.unaffordable > 0            # the cheats below are exercised
    got = S.run_world(*code, seeds, 32, LuaChannel(r, "test-d1:h", 64, 2, 8), y_int=3)
    assert got["hashes"] == ref["hashes"]
    for cheat in ("free_unaffordable", "undercharge"):
        bad = S.run_world(*code, seeds, 32, LuaChannel(r, f"test-d1:{cheat}", 64, 2, 8, cheat), y_int=3)
        assert S.conservation_violations(bad, 8, 2, 3) > 0
