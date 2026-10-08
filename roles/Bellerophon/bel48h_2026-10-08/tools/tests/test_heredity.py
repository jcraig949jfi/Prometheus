"""Controls for the W2 heredity instrument."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from heredity import HeredityWorld
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import Config

BASE = dict(world="GRID", spatial="LOCAL", reproduction="ENDOGENOUS_PARTIAL", physics="v2", ticks=60, cells=16, budget=256)


def _w(**kw):
    w = HeredityWorld(Config(**dict(BASE, **kw)), 9); return w


def test_critical_set_of_reference_replicator():
    w = _w()
    # LD T,64 (2 bytes), LDIR and HALT: without HALT execution slides into its own copy and then into the input bytes
    assert w.critical(vm.replicator(64) + bytes(56)) == [2, 3, 6, 7]


def test_planted_assembly_is_causal_and_attributed_to_both_parents():
    w = _w(); w.cells = [None] * 16
    writer = bytearray(64); code = bytes([vm.LD_S_n, 20, vm.LD_T_n, 64, vm.LD_C_n, 2, vm.LDIR, vm.HALT]); writer[:len(code)] = code
    writer[20:22] = bytes([vm.LD_T_n, 64])                                   # the 2 bytes it copies
    target = bytearray(64); target[:3] = bytes([vm.LD_A_n, 1, vm.LDIR])
    a = w._spawn(0, writer, None, "init"); b = w._spawn(1, target, None, "init")
    for o in (a, b):
        w.tags[o.id] = [o.id * 64 + i for i in range(64)]; w.shadow[o.id] = bytes(o.tape); w.founder_mech[o.id] = "init"
    assert not w.func(bytes(writer)) and not w.func(bytes(target))
    mem, tr = w._execute(a, b.tape, [1]); a.tape = bytearray(mem[:64])
    w._apply_reproduction(a, 1, mem, tr)
    c = w.cells[1]
    assert w.func(bytes(c.tape))
    ev = w.h_events[-1]
    assert ev["class"] == "ASSEMBLY" and ev["causal_assembly"] is True
    assert ev["critical"] == [0, 1, 2] and ev["critical_vec"] == "WWT"
    assert ev["critical_founders"] == sorted([a.id, b.id])                    # two founder organisms built the machine
    assert w.tags[c.id][0] == a.id * 64 + 20 and w.tags[c.id][2] == b.id * 64 + 2   # exact source positions


def test_seeded_replicator_world_is_copy_heredity():
    w = HeredityWorld(Config(**dict(BASE, reproduction="ENDOGENOUS_COPY", init="SEEDED_REPLICATOR", cells=144, ticks=80, spatial="WELL_MIXED")), 4)
    w.run(); h = w.heredity_summary()
    assert h["first_func"]["how"] == "FOUNDER_seed"
    assert h["H"].get("func_birth_COPY", 0) > 0 and h["H"].get("causal_assembly", 0) == 0
    assert set(h["dominant_func"]["critical_founder_mech"]) <= {"seed"}


def test_in_place_mutation_gets_a_novel_tag():
    w = _w(); w.cells = [None] * 16
    o = w._spawn(0, bytearray(64), None, "init"); w.tags[o.id] = [o.id * 64 + i for i in range(64)]; w.shadow[o.id] = bytes(64)
    o.tape[5] = 0x15
    t = w._synced(o.id, bytes(o.tape))
    assert t[5] < 0 and w.novel_kind[t[5]][0] == "n" and t[4] == o.id * 64 + 4
