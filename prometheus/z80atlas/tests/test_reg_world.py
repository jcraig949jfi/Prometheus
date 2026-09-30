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
