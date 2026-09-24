"""Readout for the P-boom pursuit (code; the preregistered statistic in boom.py's docstring): per arm, the spike rate =
archived generations whose reward_max rose by >= 2/16 over the previous archived generation, per 100 archived
generations; the reverted share; the population_shift series summary; the reward median trajectory. Prints and writes
design/BOOM_READOUT_<stamp>.json. No interpretation is written here.

    python -m archaeon.frontier.design.boom_readout
"""
from __future__ import annotations

import glob
import gzip
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from archaeon.frontier.design.measurement import max_spike, BAND     # noqa: E402

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs" / "P-boom"


def main() -> int:
    arms = defaultdict(list)
    for rp in sorted(glob.glob(str(RUNS / "*" / "RECEIPT.json"))):
        r = json.loads(Path(rp).read_text(encoding="utf-8"))
        if r.get("status") != "DONE":
            continue
        eid = r["experiment_id"]; arm = eid.split("/")[1]; arm = arm[:-3] if arm[-3:-1] == "_s" and arm[-1].isdigit() else arm
        obs = []; shifts = []; nominated = 0; scopes = defaultdict(int)
        for c in r["chunks"]:
            p = Path(rp).parent / ("chunk_%03d.json.gz" % c["chunk"])
            with gzip.open(p, "rt", encoding="utf-8") as f:
                d = json.load(f)
            obs += d["out"]["observations"]
            for fz in d["out"]["freezes"]:
                nominated += 1 if fz.get("nominated") else 0; scopes[fz["scope"]] += 1
            m = c.get("measurements", {})
            shifts += [x["shift"] for x in m.get("population_shift", [])]
        obs.sort(key=lambda o: o["generation"])
        spikes = max_spike({"observations": obs})
        n_arch = max(1, len(obs))
        meds = [o["reward_median"] for o in obs]; maxs = [o["reward_max"] for o in obs]
        arms[arm].append({"experiment": eid, "archived_generations": n_arch, "spikes": len(spikes), "spike_rate_per_100": round(100 * len(spikes) / n_arch, 2),
                          "reverted_share": round(sum(1 for s in spikes if s["reverted_within_4"]) / max(1, len(spikes)), 3),
                          "median_first_last": [round(meds[0], 3), round(meds[-1], 3)] if meds else None, "max_mean": round(sum(maxs) / len(maxs), 3) if maxs else None,
                          "max_max": round(max(maxs), 3) if maxs else None, "shift_mean": round(sum(shifts) / len(shifts), 3) if shifts else None,
                          "shift_max": round(max(shifts), 3) if shifts else None, "nominated_freezes": nominated, "freeze_scopes": dict(scopes), "evaluations": r["evaluations"]})
    out = {"schema": "archaeon.frontier.boom_readout.v1", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "arms": arms,
           "summary": {arm: {"runs": len(v), "spike_rate_per_100_mean": round(sum(x["spike_rate_per_100"] for x in v) / len(v), 2),
                             "max_mean": round(sum(x["max_mean"] or 0 for x in v) / len(v), 3), "median_last_mean": round(sum((x["median_first_last"] or [0, 0])[1] for x in v) / len(v), 3)} for arm, v in arms.items()}}
    p = HERE / ("BOOM_READOUT_%s.json" % time.strftime("%Y-%m-%dT%H%MZ", time.gmtime()))
    p.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(out["summary"], indent=1)); print("written", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
