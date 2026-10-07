"""B28 -- do evolved content-sensing foragers TRANSFER across worlds? (evaluation only, single process)

Elites: B26/B27 content-sensing elites (P-boom 2504/2505/2506, B-scatter 2701/2702/2703, C6-unable 2703). Worlds:
the three NOCLOCK worlds where content sensing evolved. Each cell: elite reward on that world, minus that world's
best constant program ("lift"). Home diagonal vs off-diagonal.
PREDICTION (before running): mean off-diagonal lift <= .3 x mean home lift (rules are world-tuned), but >= 1 elite
keeps a positive lift (>= .05) on every world (a general "stop where food" rule).
"""
import json
from pathlib import Path

from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest, score
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b27_noclock_generality import load_world

OUT = Path(__file__).resolve().parent / "results"
WORLDS = {"P-boom": "P-boom_K_D_persist_s3", "B-scatter": "B-scatter.T000.d_horizon", "C6-unable": "C6-unable.T3"}


def main():
    b25 = json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"]
    b27 = json.loads((OUT / "B27_result.json").read_text(encoding="utf-8"))["rows"]
    elites = {"P-boom_%d" % r["seed"]: ("P-boom", r["elite_manifest"]) for r in b25 if r.get("arm") == "NOCLOCK" and r["seed"] in (2504, 2505, 2506)}
    short = {v: k for k, v in WORLDS.items()}
    for r in b27:
        if r.get("content_sensing"):
            elites["%s_%d" % (short[r["world"]], r["seed"])] = (short[r["world"]], r["elite_manifest"])
    worlds = {k: load_world(v) for k, v in WORLDS.items()}
    base = {k: max(score(constant_manifest(c, w.K), NoClock(w), s) for c in CONSTS) for k, (w, s) in worlds.items()}
    rows = []
    for en, (home, m) in elites.items():
        row = {"elite": en, "home": home}
        for wk, (w, s) in worlds.items():
            row[wk] = round(score(m, NoClock(w), s) - base[wk], 4)
        rows.append(row); print(json.dumps(row), flush=True)
    homeL = [r[r["home"]] for r in rows]
    offL = [r[k] for r in rows for k in WORLDS if k != r["home"]]
    summ = {"constant_baselines": {k: round(v, 4) for k, v in base.items()}, "mean_home_lift": round(sum(homeL) / len(homeL), 4),
            "mean_off_lift": round(sum(offL) / len(offL), 4),
            "general_elites": [r["elite"] for r in rows if all(r[k] >= .05 for k in WORLDS)]}
    print(json.dumps(summ))
    (OUT / "B28_result.json").write_text(json.dumps({"probe": "B28", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
