"""B71a -- choose a THIRD world for the niche replication, from OUTSIDE the C6 named set (packet S3; evaluation only).

Candidates are procedural worlds from the B32 family generator (b32.family_world: C6 procedural generator with
resources + locality forced and delayed actions off), with COUPLING forced on, R >= 3 and K >= 2.
For each candidate:
- teeth: hand generalist (b29.generalist) solo vs mean of 4 copies concurrent (B64 regime-aware evaluator);
- competence: generalist lift over the best constant.
A world qualifies if copies earn <= .6x solo (competition bites) and the generalist lift is >= .05 (there is
something to forage). The first qualifier in key order is chosen, fixed BEFORE any evolution run, and its params are
written to results/B71_world.json.
"""
import copy
import json
import sys
from pathlib import Path

from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b29_leave_one_world_out import generalist
from archaeon.beta.b32_world_distribution import family_world
from archaeon.beta.b64_niche_replication import group_rewards
from archaeon.campaign6.worlds.runtime import ComposedWorld

OUT = Path(__file__).resolve().parent / "results"


def candidate(i):
    w, s = family_world(("b71", i, 0))
    p = copy.deepcopy(w.w.params); p["coupling"] = {"on": True}
    return NoClock(ComposedWorld(p)), s, p


def main(argv):
    n = int(argv[0]) if argv else 40
    rows = []; chosen = None
    for i in range(n):
        w, s, p = candidate(i)
        if w.w.R < 3:
            continue
        g = generalist(w.w.R)
        solo = group_rewards([g], w, s, 16)[0]
        cop = sum(group_rewards([g] * 4, w, s, 16)) / 4
        const = max(group_rewards([constant_manifest(c, w.K)], w, s, 16)[0] for c in CONSTS)
        row = {"i": i, "R": w.w.R, "L": w.w.L, "K": w.K, "features": w.w.features, "solo": round(solo, 4), "copies": round(cop, 4),
               "ratio": round(cop / solo, 3) if solo else None, "lift": round(solo - const, 4)}
        row["qualifies"] = bool(solo and cop / solo <= .6 and solo - const >= .05)
        rows.append(row); print(json.dumps(row), flush=True)
        if row["qualifies"] and chosen is None:
            chosen = {"i": i, "seed": s, "params": p}
    (OUT / "B71_scan.json").write_text(json.dumps({"rows": rows}, indent=1), encoding="utf-8")
    if chosen:
        (OUT / "B71_world.json").write_text(json.dumps(chosen, indent=1), encoding="utf-8")
    print("chosen", chosen and chosen["i"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
