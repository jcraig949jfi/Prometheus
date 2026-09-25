"""Boundary criterion, verdicts, classification and spec determinism."""
from __future__ import annotations

import numpy as np

from prometheus.ananke import campaign as C


def rows(family, dial, base, means, reps=3, noise=0.01, seed=0):
    g = np.random.default_rng(seed)
    out = []
    for li, m in enumerate(means):
        for r in range(reps):
            out.append({"env": {"family": family}, "kind": "evolve",
                        "extra": {"transect": dial, "level_index": li, "base": base, "rep": r},
                        "result": {"held": {"acc": float(m + g.normal(0, noise))}}})
    return out


CFG = C.CampaignConfig()


def test_sharp_jump_is_candidate_smooth_ramp_is_not():
    sharp = rows("RELAY", "loss", 0, [0.9, 0.9, 0.52, 0.5])
    ramp = rows("RELAY", "noise", 0, [0.9, 0.8, 0.7, 0.6, 0.5])       # smooth amplifier null
    flat = rows("RELAY", "fanout", 0, [0.5, 0.5, 0.5, 0.5])
    found = C.detect_boundaries(CFG, sharp + ramp + flat)
    dials = {f["dial"] for f in found}
    assert dials == {"loss"}
    assert found[0]["between"] == [1, 2] and found[0]["jump"] < 0


def test_noisy_jump_below_3se_is_not_candidate():
    noisy = rows("RELAY", "loss", 0, [0.62, 0.50], reps=3, noise=0.15, seed=3)
    assert not C.detect_boundaries(CFG, noisy)


def test_supported_needs_fresh_seed_and_orthogonal_offset():
    b0 = rows("HOLD", "decay_shift", 0, [0.95, 0.95, 0.5, 0.5])
    b1 = rows("HOLD", "decay_shift", 1, [0.9, 0.5, 0.5, 0.5])        # jump one level earlier: within +-1
    cands = C.detect_boundaries(CFG, b0 + b1)
    fresh = rows("HOLD", "decay_shift", 0, [0.97, 0.96, 0.52, 0.49], seed=9)
    v = C.boundary_verdicts(CFG, cands, fresh)
    lab = {(x["base"]): x["label"] for x in v}
    assert lab[0] == "PHASE_BOUNDARY_SUPPORTED"
    assert lab[1] == "PHASE_BOUNDARY_CANDIDATE"          # its own fresh-seed rerun is absent
    v2 = C.boundary_verdicts(CFG, cands, [])
    assert all(x["label"] == "PHASE_BOUNDARY_CANDIDATE" for x in v2)


def test_classify_signal_and_comm():
    row = {"env": {"family": "RELAY"}, "result": {"held": {"lo99": 0.58, "comm_delta_lo99": 0.05},
                                                  "twin": {"beyond_hop": 1.0}}}
    lab = C.classify(row, CFG)
    assert lab["SIGNAL"] and lab["COMM_DEPENDENT"] and not lab["LOCAL_ONLY"] and lab["REACH_BEYOND_HOP"]
    row["result"]["held"]["comm_delta_lo99"] = 0.0
    assert C.classify(row, CFG)["LOCAL_ONLY"]
    row["result"]["held"]["lo99"] = 0.55                 # exactly at the margin is NOT a signal
    assert not C.classify(row, CFG)["SIGNAL"]


def test_wave_A_specs_deterministic_and_valid():
    cfg = C.CampaignConfig(a_cells=40)
    a, b = C.wave_A(cfg, []), C.wave_A(cfg, [])
    assert [C.cell_id(x) for x in a] == [C.cell_id(x) for x in b]
    assert len({C.cell_id(x) for x in a}) == 40
    fams = [x["env"]["family"] for x in a]
    assert all(fams.count(f) == 8 for f in cfg.families)


def test_wave_A0_and_living_draw():
    cfg = C.CampaignConfig(a0_cells=20, a_cells=10)
    a0 = C.wave_A0(cfg)
    assert len({C.cell_id(x) for x in a0}) == 20 and all(x["kind"] == "census" for x in a0)
    fake = []
    for x in a0:
        x = dict(x, cell_id=C.cell_id(x))
        x["result"] = {"plant": {"acc": 1.0}, "gen0": {"frac_sensitive_any": 0.0}}
        fake.append(x)
    a1 = C.wave_A(cfg, fake)
    from_living = [x for x in a1 if "from_living_A0" in x["extra"]]
    assert len(from_living) == 5 and len(a1) == 10
