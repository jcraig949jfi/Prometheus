"""Deterministic selection of the S1-A forensic replays: 64 frozen RANDOM-start runs per
non-pair reproduction physics, 256 in total.

Rule (fixed before any replay was run):
  * population = FROZEN_FUNNEL_RUNS.jsonl (every RANDOM-start run of the four physics);
  * strata = self_location x copy_primitive (3 x 2 = 6) within each physics;
  * quota = 64 split as evenly as possible: 10 each, and the 4 left over go to the four
    strata with the smallest sha256("<physics>|<stratum>"); a stratum with fewer runs
    than its quota gives the deficit to the next strata in that same hash order;
  * within a stratum, runs are taken in ascending sha256(run_id).
No outcome field is read. Output: REPLAY_SELECTION.json and replay_ids.txt.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PHYSICS = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE", "OVERWRITE")
PER = 64


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    rows = [json.loads(l) for l in open(HERE / "FROZEN_FUNNEL_RUNS.jsonl")]
    sel, report = [], {}
    for phys in PHYSICS:
        strata = {}
        for r in rows:
            if r["physics"] == phys:
                strata.setdefault("%s/%s" % (r["self_location"], r["copy_primitive"]), []).append(r)
        order = sorted(strata, key=lambda k: h(phys + "|" + k))
        quota = {k: PER // len(order) for k in order}
        for k in order[:PER - sum(quota.values())]:
            quota[k] += 1
        # redistribute any deficit in hash order
        deficit = 0
        for k in order:
            if len(strata[k]) < quota[k]:
                deficit += quota[k] - len(strata[k])
                quota[k] = len(strata[k])
        while deficit:
            moved = False
            for k in order:
                if deficit and len(strata[k]) > quota[k]:
                    quota[k] += 1
                    deficit -= 1
                    moved = True
            if not moved:
                break
        picked = []
        for k in order:
            picked += sorted(strata[k], key=lambda r: h(r["run_id"]))[:quota[k]]
        sel += picked
        report[phys] = {"quota": quota, "available": {k: len(v) for k, v in strata.items()},
                        "tiers": {t: sum(1 for r in picked if r["tier"] == t) for t in "SML"},
                        "run_ids": [r["run_id"] for r in picked]}
    (HERE / "REPLAY_SELECTION.json").write_text(json.dumps(
        {"rule": __doc__, "n": len(sel), "by_physics": report}, indent=1))
    (HERE / "replay_ids.txt").write_text("".join(r["run_id"] + "\n" for r in sel))
    for p, v in report.items():
        print(p, v["quota"], v["tiers"])
    print("total", len(sel))


if __name__ == "__main__":
    main()
