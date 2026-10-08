"""B38 -- named-world transfer of world-distribution elites (readout for B37 vs B35).

Lift (reward minus best constant) of each elite on the three named NOCLOCK worlds -- P-boom_K_D_persist_s3,
B-scatter.T000.d_horizon, C6-unable.T3 -- none of which was in any training distribution; plus the blind twin.
Groups: B35 echo-free (delayed off in training), B37 echo-free + wide (delayed allowed).
"""
import json
import sys
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b26_word_ablation import Ablate
from archaeon.beta.b27_noclock_generality import load_world
from archaeon.beta.b32_world_distribution import lift
from archaeon.beta.b23b_composed_world_audit import score

OUT = Path(__file__).resolve().parent / "results"
NAMED = {"P-boom": "P-boom_K_D_persist_s3", "B-scatter": "B-scatter.T000.d_horizon", "C6-unable": "C6-unable.T3"}


def main():
    worlds = {k: (NoClock(load_world(v)[0]), load_world(v)[1]) for k, v in NAMED.items()}
    groups = {"B35_echofree": "B32echofree_result.json", "B37_wide": "B32echofree_wide_result.json"}
    out = {}
    for g, f in groups.items():
        rows = [r for r in json.loads((OUT / f).read_text(encoding="utf-8"))["rows"] if "elite_manifest" in r]
        per = []
        for r in rows:
            m = r["elite_manifest"]
            per.append({"seed": r["seed"], **{k: {"lift": round(lift(m, w, s), 4), "input_use": round(score(m, w, s) - score(m, Ablate(w, "all"), s), 4)}
                                              for k, (w, s) in worlds.items()}})
        out[g] = {"elites": per, "mean_lift": {k: round(sum(e[k]["lift"] for e in per) / len(per), 4) for k in NAMED},
                  "n_positive_ge_.03": {k: sum(e[k]["lift"] >= .03 for e in per) for k in NAMED}}
        print(g, json.dumps({k: out[g][k] for k in ("mean_lift", "n_positive_ge_.03")}), flush=True)
    (OUT / "B38_result.json").write_text(json.dumps({"probe": "B38", **out}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
