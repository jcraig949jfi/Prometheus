"""C0e: adjudicate the already-frozen C0b law on the second sealed universe E
(roles/Cosmos/campaigns/c0e/PREREG.md).

  python -m prometheus.cosmos.c0e <c0b_campaign_out_dir>
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

COMMITMENT_E = "d17ace6e6f9171da49afab4a6c9626cfd1d998ae9e5c9cfdc14837dc319e7528"


def visible_rows(store_dir: Path):
    db = sqlite3.connect(str(store_dir / "cwe.sqlite"))
    q = ("SELECT n.coords_v1, r.verdict FROM runs r JOIN nodes n ON n.world_id = r.world_id "
         "WHERE (r.purpose = 'main' OR r.purpose LIKE 'attack:%') AND r.replicate = 0")
    return [{"coords": json.loads(c), "y": int(v == "PAYS")} for c, v in db.execute(q)]


def main(c0b_out: str) -> dict:
    out = Path(c0b_out)
    st = Store(out / "store")
    frozen = [l for l in st.laws() if l["freeze_hash"]]
    assert len(frozen) == 1
    law_id = frozen[0]["law_id"]
    vis = visible_rows(out / "store")
    rate = float(np.mean([r["y"] for r in vis]))
    Zt = feats([r["coords"] for r in vis])
    yt = np.array([r["y"] for r in vis])

    def knn(X):
        Zq = feats([{k: X[k][i] for k in ("C", "N", "K", "G")} for i in range(len(X["C"]))])
        d = ((Zq[:, None, :] - Zt[None, :, :]) ** 2).sum(-1)
        return yt[np.argsort(d, 1)[:, :5]].mean(1) >= 0.5

    base = {"majority_visible": lambda X: np.full(len(X["C"]), rate >= 0.5), "knn5_visible": knn}
    g5 = broker.adjudicate(st, law_id, COMMITMENT_E, baselines=base, holdout="E")
    g5["verdict"] = "PASS" if (g5["law_ba"] >= 0.80 and g5["law_ba"] >= g5["baselines"]["knn5_visible"]["ba"] - 0.05) else "FAIL"
    g6 = broker.intervene_fresh(st, law_id, COMMITMENT_E, salt="G6E", holdout="E")
    rows = [r for r in g6["rows"] if r["f_hi"] and r["f_obs_hi"]]
    law_err = statistics.mean(abs(math.log2(r["f_obs_hi"] / r["f_hi"])) for r in rows) if rows else float("inf")
    consts = [2 ** (k / 4) for k in range(-8, 25)]
    best_c, best_err = None, float("inf")
    for c in consts:
        e = statistics.mean(abs(math.log2(r["f_obs_hi"] / c)) for r in rows) if rows else float("inf")
        if e < best_err:
            best_c, best_err = c, e
    g6["law_mean_abs_log2_err_hi"] = law_err
    g6["best_constant"] = best_c
    g6["best_constant_mean_abs_log2_err"] = best_err
    g6["G6E"] = "PASS" if (len(g6["rows"]) >= 12 and g6["direction_ok"] >= 10 and law_err <= 0.5
                           and law_err <= best_err - 0.3) else "FAIL"
    st.receipts.append("c0e_verdicts", {"G5E": g5["verdict"], "G6E": g6["G6E"], "law_id": law_id})
    st.commit()
    res = {"G5E": g5, "G6E": g6, "receipt_chain_ok": st.receipts.verify() is None}
    (out / "C0E.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps({"G5E": {k: v for k, v in g5.items() if k != "rows"},
                      "G6E": {k: v for k, v in g6.items() if k != "rows"},
                      "chain": res["receipt_chain_ok"]}, indent=1, default=str))
    return res


if __name__ == "__main__":
    main(sys.argv[1])
