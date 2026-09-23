"""C1 F adjudication (roles/Cosmos/campaigns/c1/PREREG.md s2): BOTH frozen laws on sealed F.

  python -m prometheus.cosmos.c1f <c0b_out_dir> <c1_out_dir>
Law A = the C0b law (v3); law B = the C1 survivor (v4). Each law's predictions are receipted in its
own store before the F worlds run (broker.adjudicate). G6F on law B only.
"""
from __future__ import annotations

import json
import math
import sqlite3
import statistics
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos import broker
from prometheus.cosmos.sampler import feats
from prometheus.cosmos.store import Store

COMMITMENT_F = "5e0064901277ef9e48571906dab60f998ad924b16a46bdb316d0db46bc504946"


def _visible(store_dir: Path):
    db = sqlite3.connect(str(store_dir / "cwe.sqlite"))
    q = ("SELECT n.coords_v1, r.verdict FROM runs r JOIN nodes n ON n.world_id = r.world_id "
         "WHERE (r.purpose = 'main' OR r.purpose LIKE 'attack:%' OR r.purpose = 'costline') AND r.replicate = 0")
    return [{"coords": json.loads(c), "y": int(v == "PAYS")} for c, v in db.execute(q)]


def _baselines(vis):
    Zt = feats([r["coords"] for r in vis])
    yt = np.array([r["y"] for r in vis])
    rate = float(yt.mean())

    def knn(X):
        Zq = feats([{k: X[k][i] for k in ("C", "N", "K", "G")} for i in range(len(X["C"]))])
        d = ((Zq[:, None, :] - Zt[None, :, :]) ** 2).sum(-1)
        return yt[np.argsort(d, 1)[:, :5]].mean(1) >= 0.5
    return {"majority_visible": lambda X: np.full(len(X["C"]), rate >= 0.5), "knn5_visible": knn}


def main(c0b: str, c1: str) -> dict:
    out = {}
    base = _baselines(_visible(Path(c1) / "store"))
    for tag, d in (("A_c0b_v3", Path(c0b)), ("B_c1_v4", Path(c1))):
        st = Store(d / "store")
        fr = [l for l in st.laws() if l["freeze_hash"]]
        if not fr:
            out[tag] = {"verdict": "NOT REACHED (no frozen law)"}
            continue
        res = broker.adjudicate(st, fr[-1]["law_id"], COMMITMENT_F, baselines=base, holdout="F")
        res["verdict"] = "PASS" if (res["law_ba"] >= 0.80 and res["law_ba"] >= res["baselines"]["knn5_visible"]["ba"] - 0.05) else "FAIL"
        out[tag] = res
    if "law_ba" in out.get("B_c1_v4", {}) and "law_ba" in out.get("A_c0b_v3", {}):
        out["H1"] = "HELD" if out["B_c1_v4"]["law_ba"] > out["A_c0b_v3"]["law_ba"] else "LOST"
    if "law_ba" in out.get("B_c1_v4", {}):
        st = Store(Path(c1) / "store")
        fr = [l for l in st.laws() if l["freeze_hash"]][-1]
        g6 = broker.intervene_fresh(st, fr["law_id"], COMMITMENT_F, salt="G6F", holdout="F")
        rows = [r for r in g6["rows"] if r["f_hi"] and r["f_obs_hi"]]
        law_err = statistics.mean(abs(math.log2(r["f_obs_hi"] / r["f_hi"])) for r in rows) if rows else float("inf")
        best = min((statistics.mean(abs(math.log2(r["f_obs_hi"] / c)) for r in rows), c) for c in [2 ** (k / 4) for k in range(-8, 25)]) if rows else (float("inf"), None)
        g6.update({"law_mean_abs_log2_err_hi": law_err, "best_constant": best[1], "best_constant_mean_abs_log2_err": best[0]})
        g6["G6F"] = "PASS" if (len(g6["rows"]) >= 12 and g6["direction_ok"] >= 10 and law_err <= 0.5 and law_err <= best[0] - 0.3) else "FAIL"
        out["G6F"] = g6
    (Path(c1) / "C1F.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "rows"} if isinstance(v, dict) else v) for k, v in out.items()},
                     indent=1, default=str))
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
