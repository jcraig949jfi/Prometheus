import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from origin import OriginWorld
from belinst import end_state_hash
from prometheus.z80atlas.world import World, Config

BASE = dict(world="GRID", spatial="WELL_MIXED", physics="v2", ticks=120, cells=144, budget=256)


def test_origin_hook_invariance():
    for repro in ("ENDOGENOUS_PARTIAL", "ENDOGENOUS_COPY", "PAIR_EXECUTION"):
        cfg = Config(**dict(BASE, reproduction=repro))
        a = World(cfg, 17); a.run(); w = OriginWorld(cfg, 17); w.run(); w.origin_summary(); w.reach_summary()
        assert end_state_hash(a) == end_state_hash(w), repro


def test_mutation_completing_a_replicator_is_caught():
    from prometheus.z80atlas import vm
    cfg = Config(**dict(BASE, reproduction="ENDOGENOUS_COPY", ticks=5))
    w = OriginWorld(cfg, 3)
    o = next(x for x in w.cells if x is not None)
    broken = bytearray(vm.replicator(64) + bytes(56)); broken[6] = 0x00      # LDIR knocked out
    o.tape = broken; w.tags[o.id] = [o.id * 64 + i for i in range(64)]; w.shadow[o.id] = bytes(broken)
    old = bytes(broken); fixed = bytearray(broken); fixed[6] = vm.LDIR
    w.origin_event = None
    w._check_origin(o, old, bytes(fixed), "MUTATION", [6])
    e = w.origin_event
    assert e["kind"] == "MUTATION" and e["necessary_changed"] == [6] and e["revert_all_func"] is False
