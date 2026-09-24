"""DEEP FRONTIER -- preregistered adaptive compute allocation (directive s10). Frozen here before any
run; changing these rules is a charter change (s12) and needs the operator.

POOLS and FLOORS (shares of the campaign's evaluation budget per allocation EPOCH)
    EXPLORATION   initial .40   floor .20
    EXPLOITATION  initial .40   ceiling .60
    AUDIT         initial .20   floor .15      (controls, replays, falsification, calibration, random audits;
                                                REVISIT items are charged to AUDIT)
EPOCH = 1e5 evaluations (the first tranche ceiling, D6-005) or 24 h of wall, whichever first.

INFORMATION YIELD per pool per epoch (counted from the registry's events, never from a score):
    Y = corroborated_events + new_phenomenon_families + blind_spots_with_new_positive_control
        + interpretations_overturned + retirements_with_reopen              (per 1e5 evaluations)
    corroborated_event = an admitted-detector firing that reproduced under replay A and survived at least
    one control (B/C/D/E/F/G) in a descendant transformation.
ADAPTATION (multiplicative, bounded, once per epoch):
    share'_p = share_p * (1 + 0.25 * sign(Y_p - median(Y)))   for p in {EXPLORATION, EXPLOITATION}
    then clamp to the floors/ceiling and renormalise with AUDIT held at max(.15, its previous share);
    no share may move by more than .10 per epoch. AUDIT never adapts downward below .15 and never
    adapts upward on yield (audits are not rewarded for finding things).
ANTI-COLLAPSE (s15): if the share of EXPLOITATION items descending from ONE lineage exceeds .50 of
    the pool for two epochs, the next epoch's EXPLORATION share is raised by .10 (within bounds) and a
    "distant reopen" item is pushed: a world at bin >= 7 from an unused generator seed range plus an
    unlabeled schedule.
RELEVANCE FLOOR for retirement condition C: an effect bounded within +-1/16 (the band) on the
    lineage's primary observable by >= 3 independent controlled descendants.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

HERE = Path(__file__).resolve().parent
RULES = {
    "schema": "archaeon.frontier.allocation.v1",
    "initial": {"EXPLORATION": 0.40, "EXPLOITATION": 0.40, "AUDIT": 0.20},
    "floors": {"EXPLORATION": 0.20, "AUDIT": 0.15}, "ceilings": {"EXPLOITATION": 0.60},
    "epoch": {"evaluations": 100000, "wall_hours": 24},
    "yield_terms": ["corroborated_events", "new_phenomenon_families", "blind_spots_with_new_positive_control", "interpretations_overturned", "retirements_with_reopen"],
    "step": 0.25, "max_move": 0.10, "anti_collapse": {"single_lineage_share": 0.50, "epochs": 2, "exploration_boost": 0.10, "reopen_bin_min": 7},
    "relevance_floor_band": 1 / 16, "relevance_floor_controls": 3,
}


def adapt(shares: Dict[str, float], yields: Dict[str, float], collapse_flag: bool = False) -> Dict[str, float]:
    s = dict(shares)
    ys = sorted(yields.get(p, 0.0) for p in ("EXPLORATION", "EXPLOITATION", "AUDIT"))
    med = ys[len(ys) // 2]
    for p in ("EXPLORATION", "EXPLOITATION"):
        y = yields.get(p, 0.0); sign = 1 if y > med else (-1 if y < med else 0)
        target = s[p] * (1 + RULES["step"] * sign)
        target = max(s[p] - RULES["max_move"], min(s[p] + RULES["max_move"], target))
        s[p] = target
    if collapse_flag:
        s["EXPLORATION"] = min(1.0, s["EXPLORATION"] + RULES["anti_collapse"]["exploration_boost"])
    s["EXPLORATION"] = max(RULES["floors"]["EXPLORATION"], s["EXPLORATION"])
    s["EXPLOITATION"] = min(RULES["ceilings"]["EXPLOITATION"], s["EXPLOITATION"])
    s["AUDIT"] = max(RULES["floors"]["AUDIT"], shares.get("AUDIT", 0.2))
    tot = s["EXPLORATION"] + s["EXPLOITATION"]
    rest = 1.0 - s["AUDIT"]
    s["EXPLORATION"], s["EXPLOITATION"] = round(rest * s["EXPLORATION"] / tot, 4), round(rest * s["EXPLOITATION"] / tot, 4)
    s["AUDIT"] = round(1.0 - s["EXPLORATION"] - s["EXPLOITATION"], 4)
    return s


def write_frozen(path: Path = HERE / "ALLOCATION_RULES_frozen.json") -> Path:
    import hashlib
    body = json.dumps(RULES, indent=1, sort_keys=True)
    rec = dict(RULES); rec["digest"] = "sha256:" + hashlib.sha256(body.encode()).hexdigest()
    path.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    p = write_frozen()
    print("frozen", p)
    print("adapt example", adapt(RULES["initial"], {"EXPLORATION": 3, "EXPLOITATION": 1, "AUDIT": 0}))
    print("collapse example", adapt(RULES["initial"], {"EXPLORATION": 0, "EXPLOITATION": 5, "AUDIT": 0}, collapse_flag=True))
