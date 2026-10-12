"""S1 law search and gates L1-L4 (roles/Cosmos/c3/S1_PREREG_LAW.md s4) on a MAPS.json.

  python -m prometheus.cosmos.c3.law <maps_dir>
Target: FUNCTIONAL (1) vs not (0); INDETERMINATE worlds excluded (reported). Families are the lineages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.miner import Miner, balanced_acc, default_workers, fit_thresholds, law_from_json

TERMS = ("sR", "sF", "rR", "rF", "kq")


def design(rows: List[Dict[str, Any]]):
    X = {k: np.array([r["coords"][k] for r in rows], float) for k in TERMS}
    y = np.array([int(r["class"] == "FUNCTIONAL") for r in rows])
    g = np.array([r["family"] for r in rows])
    return X, y, g


def lolo_single(X, y, g, key: str) -> Dict[str, float]:
    out = {}
    for f in sorted(set(g)):
        tr, te = g != f, g == f
        _, t, d = fit_thresholds(X[key][tr][:, None], y[tr])
        pred = (X[key][te] <= t[0]) if d[0] > 0 else (X[key][te] >= t[0])
        out[f] = float(balanced_acc(pred, y[te]))
    return out


def lolo_knn(X, y, g, k: int = 5) -> Dict[str, float]:
    Z = np.stack([X[t] for t in TERMS], 1)
    Z = (Z - Z.mean(0)) / np.where(Z.std(0) > 0, Z.std(0), 1)
    out = {}
    for f in sorted(set(g)):
        tr, te = g != f, g == f
        d = ((Z[te][:, None, :] - Z[tr][None, :, :]) ** 2).sum(-1)
        pred = y[tr][np.argsort(d, 1)[:, :k]].mean(1) >= 0.5
        out[f] = float(balanced_acc(pred, y[te]))
    return out


def analyse(maps: Path) -> Dict[str, Any]:
    M = json.loads((maps / "MAPS.json").read_text(encoding="utf-8"))
    rows = [r for r in M["rows"] if r["class"] != "INDETERMINATE"]
    excluded = [r for r in M["rows"] if r["class"] == "INDETERMINATE"]
    X, y, g = design(rows)
    miner = Miner(X, y, g, terminals=TERMS)
    res = miner.mine(n_perm=19, workers=default_workers())
    out: Dict[str, Any] = {"n_rows": len(rows), "n_indeterminate": len(excluded),
                           "class_counts": {f: {c: sum(1 for r in M["rows"] if r["family"] == f and r["class"] == c)
                                                for c in ("NONE", "PASSIVE", "FUNCTIONAL", "INDETERMINATE", "INCOHERENT")}
                                            for f in sorted(set(r["family"] for r in M["rows"]))},
                           "mine": {k: res[k] for k in ("verdict", "p_null", "best_score", "top") if k in res}}
    base = {"sF_only": lolo_single(X, y, g, "sF"), "sR_only": lolo_single(X, y, g, "sR"), "knn5": lolo_knn(X, y, g)}
    out["baselines"] = base
    if res["verdict"] != "CANDIDATE":
        out["gates"] = {"L1": "FAIL (no law: %s)" % res.get("reason", res["verdict"]), "L2": "NOT REACHED",
                        "L3": "NOT REACHED", "L4": "NOT REACHED"}
        return out
    law = res["law"]
    out["law"] = law
    fb = law["fold_ba"]
    worst, mean = min(fb.values()), float(np.mean(list(fb.values())))
    out["gates"] = {}
    out["gates"]["L1"] = "PASS" if (worst >= 0.80 and res["p_null"] <= 0.05) else "FAIL (worst %.3f p %.3f)" % (worst, res["p_null"])
    b_sf = float(np.mean(list(base["sF_only"].values())))
    b_knn = float(np.mean(list(base["knn5"].values())))
    out["gates"]["L2"] = "PASS" if (mean >= b_sf + 0.03 and mean >= b_knn and mean > 0.5) else \
        "FAIL (law %.3f vs sF-only %.3f, knn %.3f)" % (mean, b_sf, b_knn)
    out["gates"]["L3"] = "PASS" if all(v >= 0.75 for v in fb.values()) else "FAIL (%s)" % fb
    L = law_from_json(law)
    hy = [r for r in M["hybrid"] if r["class"] != "INDETERMINATE"]
    if hy:
        Xh = {k: np.array([r["coords"][k] for r in hy], float) for k in TERMS}
        yh = np.array([int(r["class"] == "FUNCTIONAL") for r in hy])
        ph = L.predict(Xh)
        ok = int((ph == (yh == 1)).sum())
        out["hybrid"] = [{"params": r["params"], "k": r["k"], "class": r["class"], "pred": int(p)} for r, p in zip(hy, ph)]
        out["gates"]["L4"] = "PASS" if ok >= 10 and len(hy) >= 10 else "FAIL (%d/%d correct)" % (ok, len(hy))
    else:
        out["gates"]["L4"] = "NOT REACHED (hybrid all INDETERMINATE)"
    return out


if __name__ == "__main__":
    d = Path(sys.argv[1])
    r = analyse(d)
    (d / "LAW.json").write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("n_rows", "n_indeterminate", "class_counts", "gates", "baselines")}, indent=1, default=str))
    print("LAW", r.get("law", {}).get("law"), "| fold BA", r.get("law", {}).get("fold_ba"), "| p", r["mine"]["p_null"])
