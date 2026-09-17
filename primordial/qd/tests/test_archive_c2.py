"""C2 (round 3, builder G): sampler_seed mandatory in every archive constructor; elites saved per run
seed and replayable. Needs the lane E substrate on 127.0.0.1:6394 (skip otherwise)."""
import numpy as np
import pytest
import redis

from primordial.qd import archive as A
from primordial.qd.e2_run import LineageArchive
from primordial.qd.stubworld import GLEN, NKWorld, mutate, random_genomes


@pytest.fixture
def r():
    c = redis.Redis(host="127.0.0.1", port=6394)
    try:
        c.ping()
    except redis.ConnectionError:
        pytest.skip("lane E substrate not running on 6394")
    return c


@pytest.mark.parametrize("cls", [A.LuaArchive, A.RacyArchive, LineageArchive])
def test_archive_without_seed_raises(r, cls):
    with pytest.raises(TypeError):
        cls(r, "test-c2-noseed", GLEN)
    with pytest.raises(ValueError, match="mandatory"):
        cls(r, "test-c2-noseed", GLEN, None)
    with pytest.raises(ValueError, match="mandatory"):
        cls(r, "test-c2-noseed", GLEN, sampler_seed=None)


def test_unseeded_label_is_explicit_and_not_replayable(r):
    assert not A.LuaArchive(r, "test-c2-u", GLEN, A.UNSEEDED).replayable
    assert A.LuaArchive(r, "test-c2-s", GLEN, 5).replayable
    assert A.LuaArchive(r, "test-c2-s", GLEN, np.array([7, 1], np.uint64)).replayable   # no elementwise compare
    with pytest.raises(ValueError, match="not UNSEEDED"):
        A.LuaArchive(r, "test-c2-s", GLEN, "seed-42")


def _qd(r, run, run_seed, sampler_seed, gens=12, batch=128):
    """A small seeded QD loop on the NK stub world: the whole run is a function of its two seeds."""
    a = A.LuaArchive(r, run, GLEN, sampler_seed=sampler_seed)
    a.clear()
    rng = np.random.Generator(np.random.PCG64(run_seed))
    world = NKWorld()
    for gen in range(gens):
        parents = a.sample(batch)
        kids = random_genomes(rng, batch) if len(parents) == 0 else mutate(rng, parents, 0.05)
        f, c = world.evaluate(kids)
        meta = np.stack([np.zeros(batch, np.uint32), np.full(batch, gen, np.uint32)], axis=1)
        a.insert(c, f, kids, meta)
    return a


def test_replay_same_seeds_gives_byte_identical_elites(r, tmp_path):
    docs = []
    for i, run in enumerate(("test-c2-rep-a", "test-c2-rep-b")):
        a = _qd(r, run, run_seed=3, sampler_seed=[11, 3])
        path = tmp_path / f"rs3-{i}.json"
        docs.append(A.save_elites(a, path, run_seed=3))
        a.clear()
    ea, eb = docs[0]["elites"], docs[1]["elites"]
    assert len(ea) > 20 and ea == eb
    body = lambda p: p.read_text(encoding="utf-8").replace("test-c2-rep-a", "RUN").replace("test-c2-rep-b", "RUN")
    assert body(tmp_path / "rs3-0.json") == body(tmp_path / "rs3-1.json")
    assert docs[0]["replayable"] is True and docs[0]["sampler_seed"] == [11, 3]
    other = _qd(r, "test-c2-rep-c", run_seed=3, sampler_seed=[11, 4])
    assert A.save_elites(other, tmp_path / "rs3-c.json", run_seed=3)["elites"] != ea   # the seed matters
    other.clear()


def test_saved_elites_restore_into_a_fresh_archive(r, tmp_path):
    a = _qd(r, "test-c2-sv", run_seed=5, sampler_seed=5)
    A.save_elites(a, tmp_path / "e" / "rs5.json", run_seed=5)
    want = a.dump()
    a.clear()
    doc = A.load_elites(tmp_path / "e" / "rs5.json")
    b = A.LuaArchive(r, "test-c2-sv2", GLEN, sampler_seed=5)
    b.clear()
    assert A.restore_elites(b, doc) == len(want)
    assert b.dump() == want
    with pytest.raises(ValueError, match="glen"):
        A.restore_elites(A.LuaArchive(r, "test-c2-sv3", GLEN + 4, sampler_seed=5), doc)
    b.clear()
