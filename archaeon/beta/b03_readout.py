"""B03 readout: did the search do ANYTHING after generation 0?

Observed while B03 ran (2026-10-07 ~00:29Z): per seed, the three arms often finish with the SAME held-out score to 4
digits. Hypothesis: the final elite IS a generation-0 organism (elitism keeps it; no child ever beats it), so the
arms never differed. Checks per cell: (1) is the final elite's genome present in the cell's generation 0;
(2) generation of the last improvement of the training best; (3) training best at gen 0 vs final.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2
from archaeon.wse.evolve import gen0

OUT = Path(__file__).resolve().parent / "results"


def main(argv):
    b = json.loads((OUT / "B03_result.json").read_text(encoding="utf-8"))
    g0cache, rows = {}, []
    for r in b["rows"]:
        s = r["seed"]
        if s not in g0cache:
            g0cache[s] = {tuple(o["manifest"]["genome"]) for o in gen0(CAMPAIGN_SEED, s, 200, FOUNDRY_C2)}
        m = r.get("final_manifest") or r.get("summit_manifest")
        tb = r["trace_best"]
        last_imp = max((i for i in range(1, len(tb)) if tb[i] > max(tb[:i])), default=0)
        rows.append({"arm": r["arm"], "seed": s, "elite_in_gen0": tuple(m["genome"]) in g0cache[s],
                     "best_g0": tb[0], "best_final": tb[-1], "max_train_best": max(tb), "last_improvement_gen": last_imp,
                     "final_heldout": r.get("final_heldout"), "summit": r["first_summit_gen"]})
    summ = {}
    for a in ("BASE", "HEAVY", "RELOC"):
        rr = [x for x in rows if x["arm"] == a]
        summ[a] = {"n": len(rr), "elite_in_gen0": sum(x["elite_in_gen0"] for x in rr),
                   "mean_best_g0": round(sum(x["best_g0"] for x in rr) / len(rr), 4),
                   "mean_max_train_best": round(sum(x["max_train_best"] for x in rr) / len(rr), 4),
                   "median_last_improvement_gen": sorted(x["last_improvement_gen"] for x in rr)[len(rr) // 2],
                   "summits": sum(x["summit"] is not None for x in rr)}
    print(json.dumps(summ, indent=1))
    (OUT / "B03_readout.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
