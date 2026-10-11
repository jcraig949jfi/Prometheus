import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent.parent / "bel48h_2026-10-08" / "tools"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from paired_pay import PairedPayWorld
from light_halves import LightHalvesWorld
from belinst import end_state_hash
from prometheus.z80atlas import vm, coupling_campaign as CC
from prometheus.z80atlas.world import Config
L = 64


def _cfg(arm, tape, ticks=60):
    d = dict(CC.COMMON, **CC.V3, **CC.K["K40"])
    d.update(coupling=arm, task="COND_ONE", init_tapes=[tape.hex()], init_draws="PAIRED", ticks=ticks, cells=64, spatial="LOCAL", lifespan=40)
    return Config(**d)


def pad(b):
    return bytes(b[:L]) + bytes(max(0, L - len(b)))


ECHO = pad(vm.hybrid_relocated(vm.replicator(L), vm.witness_echo()))
W0 = pad(vm.hybrid_relocated(vm.replicator(L), vm.witness_cond_one()))


def test_off_is_identical():
    a = LightHalvesWorld(_cfg("OFF", ECHO), 3, census_every=20); a.run()
    b = PairedPayWorld(_cfg("OFF", ECHO), 3, census_every=20); b.run()
    assert end_state_hash(a) == end_state_hash(b)


def test_half_solver_unpaid_composite_paid():
    e = PairedPayWorld(_cfg("ON", ECHO, 30), 4, census_every=10); e.run()
    assert e.pp["pp_correct"] > 0 and e.pp["pp_denied"] >= 0.9 * e.pp["pp_correct"]
    k = LightHalvesWorld(_cfg("ON", ECHO, 30), 4, census_every=10); k.run()
    assert k.ledger.t["earned_bonus"] > 0 and e.ledger.t["earned_bonus"] < 0.2 * k.ledger.t["earned_bonus"]
    w = PairedPayWorld(_cfg("ON", W0, 30), 4, census_every=10); w.run()
    assert w.pp["pp_correct"] > 0 and w.pp["pp_denied"] <= 0.3 * w.pp["pp_correct"] and w.ledger.t["earned_bonus"] > 0
