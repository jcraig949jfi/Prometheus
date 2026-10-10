import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent.parent / "bel48h_2026-10-08" / "tools"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from intervene import InterveneWorld
from light_halves import LightHalvesWorld
from belinst import end_state_hash
from prometheus.z80atlas import vm, coupling_campaign as CC
from prometheus.z80atlas.world import Config


def _cfg(ticks=60):
    d = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); d.update(coupling="ON", task="COND_ONE", init="SEEDED_REPLICATOR", ticks=ticks, cells=64)
    return Config(**d)


def test_none_is_identical_and_actions_apply():
    a = LightHalvesWorld(_cfg(), 5, census_every=20); a.run()
    b = InterveneWorld(_cfg(), 5, at=30, action="NONE", census_every=20); b.run()
    assert end_state_hash(a) == end_state_hash(b) and b.intervention["action"] == "NONE"
    echo = vm.hybrid_relocated(vm.replicator(64), vm.witness_echo()).hex()
    c = InterveneWorld(_cfg(), 5, at=30, action="IMPLANT", tapes=[echo], n_implant=8, census_every=20); c.step_until = None; c.run()
    assert c.intervention["affected"] > 0 and end_state_hash(c) != end_state_hash(a)
    d = InterveneWorld(_cfg(), 5, at=30, action="REMOVE_CLASS", classes=("NONE",), census_every=20); d.run()
    assert d.intervention["affected"] == d.intervention["class_count"] > 0
    e = InterveneWorld(_cfg(), 5, at=30, action="REMOVE_SHAM", classes=("LO", "BOTH"), census_every=20); e.run()
    assert e.intervention["affected"] == e.intervention["class_count"]
