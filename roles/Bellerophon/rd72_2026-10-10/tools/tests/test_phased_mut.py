import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent.parent / "bel48h_2026-10-08" / "tools"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from phased_mut import PhasedMutWorld
from light_halves import LightHalvesWorld
from belinst import end_state_hash
from prometheus.z80atlas import coupling_campaign as CC
from prometheus.z80atlas.world import Config


def _cfg():
    d = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); d.update(coupling="ON", task="COND_ONE", init="SEEDED_REPLICATOR", ticks=60, cells=64)
    return Config(**d)


def test_identical_before_switch_and_switches():
    a = LightHalvesWorld(_cfg(), 9, census_every=20); a.run()
    b = PhasedMutWorld(_cfg(), 9, switch=10 ** 6, phase2="VLOW", census_every=20); b.run()
    assert end_state_hash(a) == end_state_hash(b)
    c = PhasedMutWorld(_cfg(), 9, switch=30, phase2="VLOW", census_every=20); c.run()
    assert c.cfg.mutation_rate == "VLOW" and c.cfg.mut_rate == 0.0005 and end_state_hash(c) != end_state_hash(a)
