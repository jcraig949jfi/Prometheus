import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent.parent / "bel48h_2026-10-08" / "tools"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from halves import HalvesWorld
from belinst import end_state_hash
from prometheus.z80atlas import vm, coupling_campaign as CC
from prometheus.z80atlas.world import World, Config


def _cfg(task, ticks=60):
    d = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); d.update(coupling="ON", task=task, init="SEEDED_REPLICATOR", ticks=ticks, cells=64)
    return Config(**d)


def test_halves_classification_and_invariance():
    w = HalvesWorld(_cfg("COND_MULTI"), 3)
    pad = lambda b: bytes(b[:64]) + bytes(max(0, 64 - len(b)))
    rep = vm.replicator(64)
    assert w.halves(pad(vm.hybrid_relocated(rep, vm.witness_cond_multi()))) == "BOTH"
    assert w.halves(pad(vm.hybrid_relocated(rep, vm.witness_echo()))) == "LO"
    assert w.halves(pad(rep)) == "NONE"
    w1 = HalvesWorld(_cfg("COND_ONE"), 3)
    assert w1.halves(pad(vm.hybrid_relocated(rep, vm.witness_inc()))) == "HI"
    a = World(_cfg("COND_ONE"), 11); a.run(); b = HalvesWorld(_cfg("COND_ONE"), 11, census_every=20); b.run()
    assert end_state_hash(a) == end_state_hash(b)
    assert len(b.census) >= 1


def test_light_halves_is_invariant_and_censuses():
    from light_halves import LightHalvesWorld
    a = World(_cfg("COND_ONE", ticks=60), 21); a.run(); b = LightHalvesWorld(_cfg("COND_ONE", ticks=60), 21, census_every=20); b.run()
    assert end_state_hash(a) == end_state_hash(b) and len(b.census) >= 1


def test_first_both_recorded_from_seeded_composite():
    d = dict(CC.COMMON, **CC.V3, **CC.K["K40"])
    h = (vm.hybrid_relocated(vm.replicator(64), vm.witness_cond_one()) + bytes(64))[:64].hex()
    d.update(coupling="ON", task="COND_ONE", init_tapes=[h], init_draws="PAIRED", ticks=40, cells=64)
    w = HalvesWorld(Config(**d), 4, census_every=20); w.run()
    fb = w.first_both
    assert fb is not None and fb["via"] in ("birth", "census") and fb["anatomy"]["ccrit"] and 0 in fb["origin_ticks"]
