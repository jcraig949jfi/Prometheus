"""EXP-01 analysis exactly as preregistered (roles/Cosmos/c4/prereg/EXP-01_LOCAL_DISCOVERY.md).

    python -m prometheus.cosmos.c4.exp01_analyse <rows.jsonl> [labels A|B]
"""
from __future__ import annotations

import json
import sys
from collections import Counter

import numpy as np

from prometheus.cosmos.c4 import stats as S

_CACHE: dict = {}

DET = ("FUNCTIONAL", "PASSIVE", "NONE")


def l0001_score(c, k):
    lam, eta, gam = c["lam"], c["eta"], c["gamma"]
    l2 = min(max(lam, 1e-9), 0.999999) ** 2
    sig = gam * l2 ** (k + 1)
    noi = eta * sum(l2 ** i for i in range(k + 1)) + gam * sum(l2 ** i for i in range(1, k + 1))
    return float(np.log(max(sig, 1e-300)) - np.log(max(noi, 1e-300)))


def l0003_scores(rows, cache=None):
    """C4-L-0003 (prereg ADDENDUM 1): recompute the LOCAL one-step description per world from its stored spec."""
    from prometheus.cosmos.c4 import exp01 as E
    from prometheus.cosmos.c4.sysid_local import LocalProbe, lgss_discriminability, local_lgss
    out = []
    for r in rows:
        key = r["world_id"]
        if cache is not None and key in cache:
            L = cache[key]
        else:
            sys_, task = E.build(r["family"], r["knobs"], r["k"])
            L = local_lgss(LocalProbe(sys_, task.n_symbols, seed=int(key[:8], 16)))
            if cache is not None:
                cache[key] = L
        out.append(float(np.log(max(lgss_discriminability(L, 4, r["k"]), 1e-300))))
    return np.array(out)


def _best_threshold(s, y):
    cand = np.unique(s)
    if len(cand) == 0:
        return np.inf
    best, bt = -1.0, cand[0]
    for t in cand:
        b = S.ba(y, (s > t).astype(int))
        if not np.isnan(b) and b > best:
            best, bt = b, t
    return bt


def _feat(r):
    c = r["coords"]
    f = lambda v: np.log(max(v, 1e-9))
    return [f(min(c["lam"], 0.999999)), f(c["eta"]), f(c["gamma"]), c["vis"], r["k"]]


def lofo(rows, y, fam):
    """Held-out-family predictions for every rule."""
    n = len(rows)
    pred = {k: np.zeros(n, int) for k in ("L0001", "L0002", "L0003", "T2a", "T0")}
    s1 = np.array([l0001_score(r["coords"], r["k"]) for r in rows])
    s3 = l0003_scores(rows, _CACHE)
    X2 = np.array([_feat(r) for r in rows], float)
    kk = np.array([r["k"] for r in rows], float)
    for f in np.unique(fam):
        tr, te = fam != f, fam == f
        th = _best_threshold(s1[tr], y[tr])
        pred["L0001"][te] = (s1[te] > th).astype(int)
        th3 = _best_threshold(s3[tr], y[tr])
        pred["L0003"][te] = (s3[te] > th3).astype(int)
        mu, sd = X2[tr].mean(0), X2[tr].std(0) + 1e-9
        Z = np.hstack([np.ones((n, 1)), (X2 - mu) / sd])
        if not tr.any():
            continue
        b, _ = S._logit_fit(Z[tr], y[tr].astype(float), ridge=1e-2)
        pred["L0002"][te] = (Z[te] @ b > 0).astype(int)
        Zk = np.stack([np.ones(n), kk], 1)
        b, _ = S._logit_fit(Zk[tr], y[tr].astype(float), ridge=1e-2)
        pred["T2a"][te] = (Zk[te] @ b > 0).astype(int)
        pred["T0"][te] = int(y[tr].mean() >= .5)
    pred["T3"] = np.array([int(r["T3"] == "FUNCTIONAL") for r in rows])
    return pred, s1


def analyse(path, labels="A"):
    rows = [json.loads(x) for x in open(path) if x.strip()]
    out = {"n_rows": len(rows), "labels": labels, "classes": {}, "excluded": {}}
    for fam in sorted({r["family"] for r in rows}):
        out["classes"][fam] = dict(Counter(r["A"] for r in rows if r["family"] == fam))
    if labels == "A":
        keep = [r for r in rows if r["A"] in DET]
        y = np.array([int(r["A"] == "FUNCTIONAL") for r in keep])
    else:
        keep = [r for r in rows if r["A"] in DET]
        y = np.array([int(r["B"]) for r in keep])
    out["excluded"] = dict(Counter(r["family"] for r in rows if r["A"] not in DET))
    fam = np.array([r["family"] for r in keep])
    pred, s1 = lofo(keep, y, fam)
    out["per_family_BA"] = {}
    for f in np.unique(fam):
        m = fam == f
        out["per_family_BA"][str(f)] = {k: S.ba(y[m], p[m]) for k, p in pred.items()} | {
            "n": int(m.sum()), "functional": int(y[m].sum())}
    out["within_uplift"] = {k: S.within_family_uplift(y, pred[k], pred["T2a"], fam)
                            for k in ("L0001", "L0002", "L0003", "T3")}
    out["within_uplift_vs_T3"] = {k: S.within_family_uplift(y, pred[k], pred["T3"], fam)["U"]
                                  for k in ("L0001", "L0002", "L0003")}
    out["AB_agreement"] = {str(f): float(np.mean([(r["A"] == "FUNCTIONAL") == bool(r["B"]) for r in keep
                                                  if r["family"] == f])) for f in np.unique(fam)}
    u = out["within_uplift"]["L0001"]
    per = u["per_family"]
    below = sum(1 for v in per.values() if v < 0)
    kill = (u["U"] < 0.05) or (below >= 2)
    l2_gap = out["within_uplift"]["L0002"]["U"] - u["U"]
    u3 = out["within_uplift"]["L0003"]
    kill3 = (u3["U"] < 0.05) or (sum(1 for v in u3["per_family"].values() if v < 0) >= 2)
    out["prereg_decision_L0003"] = {"verdict": "KILLED" if kill3 else "SURVIVED_PROVISIONAL", "U_vs_T2a": u3["U"],
                                    "families_below_T2a": sum(1 for v in u3["per_family"].values() if v < 0)}
    out["prereg_decision"] = {
        "H-LOCAL": "KILLED" if kill else ("INCONCLUSIVE (L-0002 >> L-0001)" if l2_gap >= 0.10 else "SURVIVED_PROVISIONAL"),
        "L0001_U_vs_T2a": u["U"], "families_below_T2a": below, "L0002_minus_L0001": l2_gap,
        "sediment_alone_fails": bool(per.get("sediment", 0) < 0 and all(v >= 0 for f, v in per.items() if f != "sediment")),
    }
    return out


if __name__ == "__main__":
    print(json.dumps(analyse(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "A"), indent=1, default=float))
