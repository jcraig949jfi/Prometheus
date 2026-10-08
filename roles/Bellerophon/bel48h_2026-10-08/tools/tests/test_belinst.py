"""Self-falsification of the BEL-48H instrument: it must not change dynamics (invariance), it must detect real
replication (positive), reject non-replication (negative) and reject the historical cheat specimens (cheat)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from belinst import DualWorld, Func, end_state_hash
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import World, Config

BASE = dict(world="GRID", spatial="LOCAL", reproduction="ENDOGENOUS_COPY", physics="v2", ticks=120, cells=144, budget=256)


def test_invariance_random_and_seeded():
    for repro in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "PAIR_EXECUTION", "OVERWRITE", "CONSTRUCTIVE"):
        for init in ("RANDOM", "SEEDED_REPLICATOR"):
            cfg = Config(**dict(BASE, reproduction=repro, init=init))
            a = World(cfg, 11); a.run(); b = DualWorld(cfg, 11); b.run()
            assert end_state_hash(a) == end_state_hash(b), (repro, init)


def test_func_positive_negative_cheat():
    cfg = Config(**BASE)
    f = Func(cfg)
    assert f(vm.replicator(64))                                                    # positive
    assert not f(bytes(64))                                                         # negative: all NOP
    assert not f(bytes.fromhex("1500" + "ff") + bytes(61))                          # cheat: bare LDIR
    assert not f(bytes([0x07, 63, 0x08, 0, 0x03, 128, 0x15, 0xFF]) + bytes(56))     # cheat: self-smear
    assert not f(bytes([0x01, 0x77, 0x08, 70, 0x11, 0xFF]) + bytes(58))             # cheat: 1-byte capture
    cfgc = Config(**dict(BASE, representation="VM_COPY"))
    assert Func(cfgc)(vm.replicator_copyall(64))


def test_seeded_world_produces_trb_and_random_cheat_does_not():
    w = DualWorld(Config(**dict(BASE, init="SEEDED_REPLICATOR")), 3); w.run()
    s = w.dual_summary()
    assert s["B"]["trb"] > 0 and s["trb_max_depth"] >= 3
    w2 = DualWorld(Config(**dict(BASE, init_tapes=(bytes([0x07, 63, 0x08, 0, 0x03, 128, 0x15, 0xFF]).hex(),))), 3); w2.run()
    assert w2.dual_summary()["B"].get("trb", 0) == 0


def test_driver_finish_equals_run_and_lockstep_controls():
    import bel48h_driver as D
    cfg = Config(**dict(BASE, reproduction="ENDOGENOUS_PARTIAL"))
    a = World(cfg, 21); a.run()
    b = World(cfg, 21)
    for _ in range(7):
        D._step_once(b)
    D._finish(b)
    assert end_state_hash(a) == end_state_hash(b)
    d = dict(BASE); rep = vm.replicator(64).hex()
    r = D._run_one({"id": "x", "kind": "lockstep", "seed": 5, "cfg": dict(d, init_draws="PAIRED"), "cfg_b": dict(d, init_draws="PAIRED")})
    assert r["init_rng_equal"] and r["rng_div_tick"] is None and r["pop_div_tick"] is None      # identical arms never diverge
    r2 = D._run_one({"id": "y", "kind": "lockstep", "seed": 5, "cfg": dict(d, init_draws="PAIRED", init_tapes=[rep]), "cfg_b": dict(d, init_draws="PAIRED")})
    assert r2["init_rng_equal"] and r2["pop_div_tick"] == 1
    r3 = D._run_one({"id": "z", "kind": "lockstep", "seed": 5, "cfg": dict(d, init_tapes=[rep]), "cfg_b": dict(d)})
    assert not r3["init_rng_equal"]
