import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from reach import ReachWorld, copy_extent
from belinst import end_state_hash
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import World, Config

BASE = dict(world="GRID", spatial="WELL_MIXED", reproduction="ENDOGENOUS_COPY", physics="v2", ticks=80, cells=144, budget=256)


def test_reach_on_seeded_world_and_invariance():
    cfg = Config(**dict(BASE, init="SEEDED_REPLICATOR"))
    a = World(cfg, 2); a.run(); w = ReachWorld(cfg, 2); w.run()
    assert end_state_hash(a) == end_state_hash(w)
    r = w.reach_summary()
    assert r["how"] == "FOUNDER_seed" and r["ldir_critical"] and r["minimal_core_func"]
    assert r["n_founder_events"] == 1 and r["n_novel_events"] == 0 and r["relocated_founder_bytes"] == 0
    assert r["portability"] == 1.0 or r["portability"] > 0.5
    assert copy_extent(vm.replicator(64), cfg) == 64 and copy_extent(bytes(64), cfg) == 0
