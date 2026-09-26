"""RIE-01 instrument tests: regime RNG isolation/determinism, exposure accounting, case-0 equivalence, replay identity, controls,
promotion score reads observable classes only."""
from __future__ import annotations

import copy

import pytest

from archaeon.lineage import core as LC
from archaeon.rie import physics as P
from archaeon.rie import campaign as CP
from archaeon.rie.world import run_world, world_score


class _Count:
    def __init__(self): self.n = 0
    def randbelow(self, k): self.n += 1; return 0
    def next_u32(self): self.n += 1; return 0


@pytest.mark.parametrize("reg", P.REGIMES)
def test_regime_is_deterministic_and_never_touches_world_rng(reg):
    w = LC.World("t", 2, ("t.w", 0), ("t.m", 0), lambda *a: [(0,)]); cw, cm = _Count(), _Count(); w.rng, w.mrng = cw, cm; w.genomes[3] = bytes(range(32))
    f = P.make_inputs(reg, "rie01.test")
    for e in range(40):
        a = f(w, 3, e); assert a == f(w, 3, e) and len(a) == P.NC and all(0 <= c[0] <= 255 for c in a)
    assert cw.n == 0 and cm.n == 0


def test_exposure_accounting_exact():
    for inf in ("BELOW", "REPLACE"):
        r = run_world({"regime": "SPARSE", "inflow": inf, "topology": "GRID", "substrate": "z80", "T": 520}, 4)
        assert r["exposure_ok"] and r["arrivals"] == r["expected_arrivals"] > 0


def test_case0_equivalence_and_replay_identity():
    from archaeon.z80atlas.census import copier_census as C
    spec = {"regime": "LOCAL", "inflow": "REPLACE", "topology": "WELL_MIXED", "substrate": "vmcopy", "T": 450}; tapes = [bytes.fromhex(C.SPECIMEN)] * 1500
    a = run_world(spec, 5, tapes=iter(tapes), all_cases=True); b = run_world(spec, 5, tapes=iter(tapes)); c = run_world(spec, 5, tapes=iter(tapes))
    assert a["births"] == b["births"] > 0 and a["telemetry"] == b["telemetry"]
    strip = lambda r: {k: v for k, v in r.items() if k != "wall_s"}
    assert strip(b) == strip(c)


def test_controls_pass():
    assert all(CP.controls(0).values())


def test_grammar_is_full_factorial():
    assert len(CP.CELLS) == 96 and len({tuple(sorted(c.items())) for c in CP.CELLS}) == 96


def test_promotion_score_ignores_tapes():
    r = {"coexistence_episodes": 1, "glins": {1: {"established": True, "inserted": False, "mechanism": "EXACT_GATED_COPIER", "liberation": False, "acquisition": False,
                                                  "foreign_executor_role": False, "founder_tape": "aa" * 32, "dominant_genome": "bb" * 32}}}
    r2 = copy.deepcopy(r); r2["glins"][1]["founder_tape"] = "cc" * 32; r2["glins"][1]["dominant_genome"] = "dd" * 32
    assert world_score(r) == world_score(r2) == 2.0
