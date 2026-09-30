"""Register-world axis (2026-09-30, E-BEL-REPL-01): ZERO is the historical physics; CARRIED / RANDOM are declared worlds."""
import random

from prometheus.z80atlas import vm
from prometheus.z80atlas.world import Config, World

L = 64


def _mem(tape, partner=b""):
    m = bytearray(256); m[:len(tape)] = tape; m[L:L + len(partner)] = partner
    return m


def test_zero_entry_equals_default_on_random_tapes():
    rng = random.Random(7)
    for _ in range(300):
        tape = bytes(rng.randrange(256) for _ in range(L)); part = bytes(rng.randrange(256) for _ in range(L))
        ins = [rng.randrange(256) for _ in range(4)]
        m1, m2 = _mem(tape, part), _mem(tape, part)
        t1 = vm.execute(m1, L, 0, 256, ins)
        t2 = vm.execute(m2, L, 0, 256, ins, regs=(0, 0, 0, 0, 0, 0, False, False))
        assert m1 == m2 and t1.outputs == t2.outputs and t1.steps == t2.steps and t1.writes == t2.writes
        assert t1.win_prov == t2.win_prov and t1.regs_out == t2.regs_out


def test_regs_out_recorded_and_entry_state_matters():
    # "LD T,L ; LD C,8 ; LDIR ; HALT" never sets S: it copies from S, so it is a self-copier only from S == 0
    tape = bytes([vm.LD_T_n, L, vm.LD_C_n, 8, vm.LDIR, vm.HALT])
    m0 = _mem(tape); t0 = vm.execute(m0, L, 0, 256, [])
    assert m0[L:L + 6] == tape and t0.regs_out[4] == 8          # S advanced by the 8 copied bytes
    m5 = _mem(tape); vm.execute(m5, L, 0, 256, [], regs=(0, 0, 0, 0, 0x20, 0, False, False))
    assert m5[L:L + 6] != tape                                   # a nonzero entry S breaks the copy


def test_to_dict_omits_default_axis():
    assert "reg_world" not in Config().to_dict()
    assert Config(reg_world="CARRIED").to_dict()["reg_world"] == "CARRIED"


def _cfg(w):
    return Config(world="SOUP", reproduction="ENDOGENOUS_COPY", physics="v2", cells=64, ticks=30, reg_world=w)


def test_carried_keeps_exit_registers_and_is_deterministic():
    a = World(_cfg("CARRIED"), 11); a.run()
    b = World(_cfg("CARRIED"), 11); b.run()
    assert a.summary([o for o in a.cells if o]) == b.summary([o for o in b.cells if o])
    assert any(o is not None and o.regs is not None for o in a.cells)


def test_random_world_uses_its_own_rng_and_is_deterministic():
    a = World(_cfg("RANDOM"), 3); b = World(_cfg("RANDOM"), 3)
    assert a.reg_rng is not a.rng
    a.run(); b.run()
    assert a.summary([o for o in a.cells if o]) == b.summary([o for o in b.cells if o])
    assert all(o is None or o.regs is None for o in a.cells)      # RANDOM stores nothing on organisms


def test_zero_world_never_stores_registers():
    w = World(_cfg("ZERO"), 5); w.run()
    assert all(o is None or o.regs is None for o in w.cells) and w.reg_rng is None


# ---- added after the post-merge review (Fabric tsk-c26c09590d3b): kill the mutations the first tests missed ----

def test_entry_state_round_trips_every_register_in_order():
    m = bytearray(256); m[0] = vm.HALT
    e = (1, 2, 3, 4, 5, 6, True, False)
    assert vm.execute(m, L, 0, 16, [], regs=e).regs_out == e
    e2 = (9, 8, 7, 6, 5, 4, False, True)
    assert vm.execute(bytearray(m), L, 0, 16, [], regs=e2).regs_out == e2


def test_random_world_never_consumes_the_world_rng():
    w = World(_cfg("RANDOM"), 3)
    o = next(x for x in w.cells if x is not None)
    before = w.rng.getstate(); rb = w.reg_rng.getstate()
    got = [w._entry_regs(o) for _ in range(5)]
    assert w.rng.getstate() == before and w.reg_rng.getstate() != rb
    assert all(g is not None and len(g) == 8 for g in got) and len(set(got)) > 1


def test_carried_newborn_inherits_overwritten_occupant_registers():
    w = World(_cfg("CARRIED"), 21)
    idx = [i for i, x in enumerate(w.cells) if x is not None]
    parent, occ, j = w.cells[idx[0]], w.cells[idx[1]], idx[1]
    occ.regs = (7, 7, 7, 7, 7, 7, True, True)
    mem, tr = w._execute(parent, occ.tape, [0] * 16)
    w._register_offspring(j, bytearray(parent.tape), parent, "ENDOGENOUS_COPY", 1.0, tr, replaced=occ)
    assert w.cells[j] is not occ and w.cells[j].regs == (7, 7, 7, 7, 7, 7, True, True)


def test_carried_pair_execution_stores_executor_exit_registers_only():
    cfg = Config(world="SOUP", reproduction="PAIR_EXECUTION", physics="v2", cells=64, ticks=5, reg_world="CARRIED")
    w = World(cfg, 4)
    idx = [i for i, x in enumerate(w.cells) if x is not None]
    a, b = w.cells[idx[0]], w.cells[idx[1]]
    a.regs = (1, 1, 1, 1, 1, 1, False, False); b.regs = (2, 2, 2, 2, 2, 2, True, True)
    mem, tr = w._pair_execute(a, b, [0] * 16)
    assert a.regs == tr.regs_out and b.regs == (2, 2, 2, 2, 2, 2, True, True)


def test_external_carried_newborn_inherits_and_separated_is_refused():
    import pytest
    with pytest.raises(ValueError):
        World(Config(layout="SEPARATED", reg_world="CARRIED"), 1)
    cfg = Config(world="SOUP", reproduction="EXTERNAL", physics="v2", cells=64, ticks=5, reg_world="CARRIED")
    w = World(cfg, 2)
    for i in range(len(w.cells)):
        if w.cells[i] is None:
            w._spawn(i, w._random_tape(), None, "init")          # a full grid: every EXTERNAL birth overwrites an occupant
        w.cells[i].regs = (3, 3, 3, 3, 3, 3, False, True)
    occupied_before = {i for i, o in enumerate(w.cells) if o is not None}
    ids_before = {o.id for o in w.cells if o is not None}
    w._external_reproduce()
    born = [(i, o) for i, o in enumerate(w.cells) if o is not None and o.id not in ids_before]
    assert born and all(i in occupied_before for i, _ in born)
    for i, o in born:
        assert o.regs == ((3, 3, 3, 3, 3, 3, False, True) if i in occupied_before else None)


def test_origin_record_carries_entry_registers_only_off_default():
    for wname, seed in (("CARRIED", 11), ("ZERO", 11)):
        w = World(_cfg(wname), seed); w.run()
        f = w.first_self_replication
        if f is not None:
            assert ("entry_regs" in f) == (wname != "ZERO")
