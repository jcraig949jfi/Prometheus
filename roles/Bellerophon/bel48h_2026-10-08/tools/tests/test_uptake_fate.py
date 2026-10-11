import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from uptake_fate import UptakeFateWorld
from origin import OriginWorld
from belinst import end_state_hash
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import Config


def test_invariance_and_break_detection():
    cfg = Config(reproduction="ENDOGENOUS_PARTIAL", physics="v2", cells=64, ticks=40, spatial="WELL_MIXED")
    a = OriginWorld(cfg, 7); a.run(); b = UptakeFateWorld(cfg, 7); b.run()
    assert end_state_hash(a) == end_state_hash(b)
    w = UptakeFateWorld(Config(reproduction="ENDOGENOUS_PARTIAL", physics="v2", cells=16, ticks=5), 3); w.cells = [None] * 16
    code = bytes([vm.LD_S_n, 64, vm.LD_T_n, 32, vm.LD_C_n, 2, vm.LDIR, vm.HALT])   # imports 2 partner bytes over own 32-33
    t = bytearray(64); t[:len(code)] = code; t[32] = vm.LDIR                         # own LDIR at 32 will be overwritten...
    a_ = w._spawn(0, t, None, "init"); p_ = w._spawn(1, bytearray([0xAA, 0xBB]) + bytearray(62), None, "init")
    for o in (a_, p_):
        w.tags[o.id] = [o.id * 64 + i for i in range(64)]; w.shadow[o.id] = bytes(o.tape)
    w._execute(a_, p_.tape, [1])
    assert w.UF["uptake_events"] == 1 and w.UF["ldir_lost"] == 1
