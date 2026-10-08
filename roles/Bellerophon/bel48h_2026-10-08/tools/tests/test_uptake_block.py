import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from uptake_block import UptakeBlockWorld
from origin import OriginWorld
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import Config


def test_uptake_is_reverted_and_counted():
    cfg = Config(reproduction="ENDOGENOUS_PARTIAL", physics="v2", cells=16, ticks=5)
    for W, expect_in in ((OriginWorld, True), (UptakeBlockWorld, False)):
        w = W(cfg, 3); w.cells = [None] * 16
        code = bytes([vm.LD_S_n, 64, vm.LD_T_n, 32, vm.LD_C_n, 4, vm.LDIR, vm.HALT])          # copy partner[0:4] into own 32..35
        t = bytearray(64); t[:len(code)] = code
        a = w._spawn(0, t, None, "init"); b = w._spawn(1, bytearray([0xAA, 0xBB, 0xCC, 0xDD]) + bytearray(60), None, "init")
        for o in (a, b):
            w.tags[o.id] = [o.id * 64 + i for i in range(64)]; w.shadow[o.id] = bytes(o.tape)
        mem, tr = w._execute(a, b.tape, [1])
        assert (bytes(mem[32:36]) == bytes([0xAA, 0xBB, 0xCC, 0xDD])) == expect_in, W.__name__
    assert w.O["blocked_bytes"] == 4


def test_block_world_identical_without_uptake():
    from belinst import end_state_hash
    cfg = Config(reproduction="ENDOGENOUS_COPY", init="SEEDED_REPLICATOR", physics="v2", cells=64, ticks=30, spatial="WELL_MIXED")
    a = OriginWorld(cfg, 5); a.run(); b = UptakeBlockWorld(cfg, 5); b.run()
    if b.O.get("blocked_bytes", 0) == 0:
        assert end_state_hash(a) == end_state_hash(b)
