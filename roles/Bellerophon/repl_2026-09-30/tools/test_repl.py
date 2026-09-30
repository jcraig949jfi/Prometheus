"""E-BEL-REPL-01 positive controls (PREREG s5 G0): run before any production run; all must pass.
    python -m pytest -q roles/Bellerophon/repl_2026-09-30/tools/test_repl.py
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3])); sys.path.insert(0, str(HERE))
from prometheus.z80atlas import vm  # noqa: E402
from prometheus.z80atlas.world import Config  # noqa: E402
import state_free as SF  # noqa: E402
import repl_run as RR  # noqa: E402
import repl_analysis as RA  # noqa: E402
from pilot_worlds import CELL  # noqa: E402

CFG = Config(**CELL, ticks=10)


def test_planted_state_free_replicator_profiles_state_free():
    t = vm.replicator(CFG.L).ljust(CFG.L, b"\0")            # sets S, T, C explicitly: needs no entry state
    p = SF.profile(t, CFG)
    assert p["class"] == "STATE_FREE"
    assert all(SF.competent(t, CFG, e)[0] for e in ("R3", "R4"))


def test_planted_zero_dependent_copier_profiles_zero_dependent():
    t = bytes([vm.LD_T_n, CFG.L, vm.LD_C_n, CFG.L, vm.LDIR, vm.HALT]).ljust(CFG.L, b"\0")   # copies from S: needs S == 0
    assert SF.profile(t, CFG)["class"] == "ZERO_DEPENDENT"


def test_every_production_founder_is_zero_dependent_under_both_batteries():
    for h in RR.founders():
        t = bytes.fromhex(h)
        assert SF.profile(t, CFG)["class"] == "ZERO_DEPENDENT"
        assert not (SF.competent(t, CFG, "R3")[0] and SF.competent(t, CFG, "R4")[0])


def _cp(tick, free, fG, Gs, fFM=0, FMs=0.0, alt=0, altG=0):
    return {"tick": tick, "alive": 100, "distinct": 10, "L_share": 0.0, "G_share": Gs, "free": free, "free_in_L": 0,
            "free_in_G": fG, "free_alt": alt, "free_alt_in_L": 0, "free_alt_in_G": altG, "FM_share": FMs, "free_in_FM": fFM}


def test_event_detector_fires_and_refuses_on_planted_records():
    fire = {"checkpoints": [_cp(0, 0, 0, 1.0), _cp(100, 5, 4, 0.6, 4, 0.6, 2, 2), _cp(200, 0, 0, 0.6)]}
    s = RA.score(fire)
    assert s["event"] and s["event_FM"] and s["event_alt"] and s["persisting"]
    low_share = {"checkpoints": [_cp(100, 5, 5, 0.4)]}
    assert not RA.score(low_share)["event"] and RA.score(low_share)["replacement"]
    outside = {"checkpoints": [_cp(100, 5, 3, 0.9)]}                  # 3/5 < 80% carried by G
    assert not RA.score(outside)["event"]
    none = {"checkpoints": [_cp(100, 0, 0, 1.0)]}
    assert not RA.score(none)["event"] and not RA.score(none)["replacement"]


def test_fisher_matches_a_known_value():
    # 8/200 vs 0/100: P(X >= 8) = C(200,8)/C(300,8)
    import math
    assert abs(RA.fisher_one_sided(8, 200, 0, 100) - math.comb(200, 8) / math.comb(300, 8)) < 1e-12
    assert RA.fisher_one_sided(0, 200, 5, 100) == 1.0
