"""B26 -- what do the B25 NOCLOCK elites SENSE? Per-observation-word ablation (attack before naming).

For each B25 elite (both arms), on its own world: reward with every observation word intact; with ALL words zeroed
(blind twin); and with ONE word index zeroed at a time. Word layout on NOCLOCK: [pool0, pool1, pool2, cell0, cell1,
cell2, hazard, signal]; on CLOCK the same preceded by [tick, pos]. A word is SENSED if zeroing it drops reward by
>= .05. PREDICTION (before running): >= 3/6 NOCLOCK elites sense at least one pool word; CLOCK elites sense tick/pos.
"""
import json
from pathlib import Path

from archaeon.beta.b23b_composed_world_audit import score
from archaeon.beta.b25_noclock_world import NoClock, load

OUT = Path(__file__).resolve().parent / "results"


class Ablate:
    def __init__(self, w, idx):
        self.w = w; self.K = w.K; self.idx = idx; self.features = getattr(w, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def observe(self, st):
        chs = self.w.observe(st)
        return [[0 if (self.idx == "all" or i == self.idx) else x for i, x in enumerate(ch)] for ch in chs]


def main():
    world, seed, _ = load()
    d = json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))
    rows = []
    for r in d["rows"]:
        if "elite_manifest" not in r:
            continue
        w = NoClock(world) if r["arm"] == "NOCLOCK" else world
        names = (["tick", "pos"] if r["arm"] == "CLOCK" else []) + ["pool0", "pool1", "pool2", "cell0", "cell1", "cell2", "hazard", "signal"]
        base = score(r["elite_manifest"], w, seed)
        blind = score(r["elite_manifest"], Ablate(w, "all"), seed)
        drops = {names[i]: round(base - score(r["elite_manifest"], Ablate(w, i), seed), 4) for i in range(len(names))}
        rows.append({"arm": r["arm"], "seed": r["seed"], "elite": round(base, 4), "blind": round(blind, 4),
                     "sensed": [k for k, v in drops.items() if v >= .05], "drops": drops})
        print(json.dumps(rows[-1]), flush=True)
    (OUT / "B26_result.json").write_text(json.dumps({"probe": "B26", "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
