"""Lane E archive tests; need the private substrate on 127.0.0.1:6394 (skip otherwise)."""
import numpy as np
import pytest
import redis

from primordial.qd.archive import UNSEEDED as A_UNSEEDED, LuaArchive, RacyArchive, serial_reference
from primordial.qd.stubworld import GLEN, NKWorld, mutate, random_genomes


@pytest.fixture
def r():
    c = redis.Redis(host="127.0.0.1", port=6394)
    try:
        c.ping()
    except redis.ConnectionError:
        pytest.skip("lane E substrate not running on 6394")
    return c


def _offers(seed, n):
    rng = np.random.Generator(np.random.PCG64(seed))
    g = mutate(rng, random_genomes(rng, n), 0.2)
    f, c = NKWorld().evaluate(g)
    return c, f, g, np.zeros((n, 2), np.uint32)


@pytest.mark.parametrize("cls", [LuaArchive, RacyArchive])
def test_serial_insert_equals_reference(r, cls):
    a = cls(r, "test-ser", GLEN, sampler_seed=1)
    a.clear()
    c, f, g, m = _offers(1, 5000)
    for i in range(0, 5000, 700):  # uneven batches
        a.insert(c[i:i + 700], f[i:i + 700], g[i:i + 700], m[i:i + 700])
    got = {k: v[:2] for k, v in a.dump().items()}
    assert got == serial_reference(c, f, g)
    a.clear()


def test_tie_break_is_smaller_genome_regardless_of_order(r):
    a = LuaArchive(r, "test-tie", GLEN, sampler_seed=1)
    hi = np.array([[0x80, 0, 0, 0, 0, 0, 0, 1]], np.uint8)  # u32 chunk > 2^31: signedness trap
    lo = np.array([[0x7F, 0xFF, 0, 0, 0, 0, 0, 0]], np.uint8)
    for order in ([hi, lo], [lo, hi]):
        a.clear()
        for g in order:
            a.insert(np.array([5], np.uint32), np.array([100], np.int32), g, np.zeros((1, 2), np.uint32))
        assert a.dump()[5][1] == lo.tobytes()
    a.clear()


def test_seeded_sample_reproduces_and_stays_in_archive(r):
    c, f, g, m = _offers(3, 400)
    got = []
    for run in ("test-seed-a", "test-seed-b"):
        a = LuaArchive(r, run, GLEN, sampler_seed=[7, 1])
        a.clear()
        a.insert(c[:200], f[:200], g[:200], m[:200])      # different insertion batching, same final state
        a.insert(c[200:], f[200:], g[200:], m[200:])
        got.append(np.concatenate([a.sample(64), a.sample(64)]))
        stored = {v[1] for v in a.dump().values()}
        assert all(row.tobytes() in stored for row in got[-1])
        a.clear()
    assert np.array_equal(got[0], got[1])
    b = LuaArchive(r, "test-seed-c", GLEN, sampler_seed=[7, 2])
    b.clear()
    b.insert(c, f, g, m)
    assert not np.array_equal(np.concatenate([b.sample(64), b.sample(64)]), got[0])
    assert len({row.tobytes() for row in got[0]}) > 16      # spread over cells, not one cell
    b.clear()


def test_seeded_sample_empty_archive(r):
    a = LuaArchive(r, "test-seed-empty", GLEN, sampler_seed=1)
    a.clear()
    assert a.sample(8).shape == (0, GLEN)


def test_sample_returns_archive_genomes(r):
    a = LuaArchive(r, "test-smp", GLEN, sampler_seed=A_UNSEEDED)
    a.clear()
    c, f, g, m = _offers(2, 300)
    a.insert(c, f, g, m)
    s = a.sample(64)
    stored = {v[1] for v in a.dump().values()}
    assert s.shape == (64, GLEN) and all(row.tobytes() in stored for row in s)
    a.clear()
