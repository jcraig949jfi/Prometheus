"""C4: variable-length genomes in the archive. Needs the lane E substrate on 127.0.0.1:6394 (skip otherwise)."""
import itertools

import numpy as np
import pytest
import redis

from primordial.qd import archive as A
from primordial.qd.stubworld import GLEN, NKWorld, mutate, random_genomes


@pytest.fixture
def r():
    c = redis.Redis(host="127.0.0.1", port=6394)
    try:
        c.ping()
    except redis.ConnectionError:
        pytest.skip("lane E substrate not running on 6394")
    return c


def _meta(n):
    return np.zeros((n, 2), np.uint32)


def test_five_byte_genome_round_trips(r, tmp_path):
    a = A.VarArchive(r, "test-c4-rt", 16, sampler_seed=3)
    a.clear()
    g = bytes([1, 2, 3, 4, 5])
    assert a.insert([7], [42], [g], _meta(1)) == 1
    assert a.dump()[7][:2] == (42, g)
    assert a.sample(4) == [g] * 4
    A.save_elites(a, tmp_path / "rs0.json", run_seed=0)
    a.clear()
    b = A.VarArchive(r, "test-c4-rt", 16, sampler_seed=3)
    assert A.restore_elites(b, A.load_elites(tmp_path / "rs0.json")) == 1
    assert b.dump()[7][:2] == (42, g)
    b.clear()


def test_mixed_lengths_total_order_is_arrival_independent(r):
    # equal fitness in one cell: prefix (shorter wins), signedness trap (0x80 > 0x7f), different lengths
    offers = [b"\x01\x02\x00", b"\x01\x02", b"\x80", b"\x7f\xff\xff\xff\xff", b"\x01\x02\x00\x00\x00"]
    want = min(offers)
    assert want == b"\x01\x02"
    a = A.VarArchive(r, "test-c4-ord", 8, sampler_seed=1)
    for perm in itertools.permutations(range(len(offers)), len(offers)):
        if perm[0] > 1:            # 48 of the 120 orders is plenty
            continue
        a.clear()
        for i in perm:             # one offer per call: the server-side compare decides
            a.insert([5], [100], [offers[i]], _meta(1))
        assert a.dump()[5][1] == want
    a.clear()
    a.insert([5] * len(offers), [100] * len(offers), offers, _meta(len(offers)))   # client-side reduce agrees
    assert a.dump()[5][1] == want
    a.insert([5], [101], [b"\xff" * 8], _meta(1))                                  # fitness still wins first
    assert a.dump()[5][:2] == (101, b"\xff" * 8)
    a.clear()


def test_lengths_outside_bounds_raise(r):
    a = A.VarArchive(r, "test-c4-bad", 4, sampler_seed=1)
    with pytest.raises(ValueError, match="outside"):
        a.insert([1], [1], [b""], _meta(1))
    with pytest.raises(ValueError, match="outside"):
        a.insert([1], [1], [b"12345"], _meta(1))


def test_old_fixed_length_archive_still_loads_and_orders_the_same(r):
    rng = np.random.Generator(np.random.PCG64(4))
    g = mutate(rng, random_genomes(rng, 3000), 0.2)
    f, c = NKWorld().evaluate(g)
    old = A.LuaArchive(r, "test-c4-old", GLEN, sampler_seed=1)
    old.clear()
    old.insert(c[:1500], f[:1500], g[:1500], _meta(1500))
    v = A.VarArchive(r, "test-c4-old", GLEN, sampler_seed=1)          # same run key: the old archive
    assert v.dump() == old.dump()
    assert all(len(x) == GLEN for x in v.sample(32))
    v.insert(c[1500:], f[1500:], [row.tobytes() for row in g[1500:]], _meta(1500))
    assert {k: x[:2] for k, x in v.dump().items()} == A.serial_reference(c, f, g)
    old.clear()
