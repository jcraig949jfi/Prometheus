import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from comp import CompWorld
from belinst import end_state_hash
from prometheus.z80atlas.world import World, Config
from prometheus.z80atlas import coupling_campaign as CC, vm


def _cfg(tapes, coupling="ON"):
    d = dict(CC.COMMON, **CC.V3, **CC.K["K16"]); d.update(coupling=coupling, init_tapes=tuple(tapes), ticks=120, cells=144)
    return Config(**d)


def test_comp_invariance_and_hybrid_anatomy():
    F = CC.fixtures("INC", 5)
    cfg = _cfg([F["REP"], F["HYB"]])
    a = World(cfg, 5); a.run(); w = CompWorld(cfg, 5); w.run()
    assert end_state_hash(a) == end_state_hash(w)
    hyb = bytes.fromhex(F["HYB"]) + bytes(64 - len(bytes.fromhex(F["HYB"])))
    assert w.is_comp(hyb) and w.func(hyb)
    cc = w.critical_comp(hyb); rc = w.critical(hyb)
    assert any(hyb[p] == vm.IN_A for p in cc) and any(hyb[p] == vm.OUT_A for p in cc)
    assert any(hyb[p] == vm.LDIR for p in rc)
    s = w.comp_summary()
    assert s["C"].get("joint_keep", 0) > 0
    if "dominant" in s:
        assert "transplant1" in s["dominant"]["ccrit_founder_mech"]          # the HYB founder supplies the task code
