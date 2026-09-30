"""D003-09 / H-D3-35: does a learning-time / lifetime proxy predict whether in-life learning pays in WTP-03 worlds?

NOT RUN by the author (read-only worker, no code execution). Inputs, all at commit b960d1a42600:
  ensorain/runs/wtp03/waveA.json   (keys used: "admitted"[i]["g"]["time"]["lifetime"], ["g"]["learning"]["lr"],
                                    ["pre"]["learning_pays"], ["pre"]["rate_learner"/"rate_trivial"/"rate_oracle"],
                                    ["pre"]["updates"], ["root"]; field names from ensorain/wtp3/preflight3.py:267-277
                                    and ensorain/wtp3/analyze3.py:20-27)
  ensorain/runs/wtp03/waveB.json   (keys used: [i]["ratios"]["learn_over_change"], ["life_real"]["updates"/"steps"],
                                    ["root"]; field names from ensorain/wtp3/campaign3.py:148-192)
Stdlib + numpy only.

CAVEAT built into the design (read from code, not from data): preflight3.py:169 computes the G3 economy and the
`learning_pays` flag over Lc = min(lifetime, 600) steps. For any world with lifetime > 600, `learning_pays` cannot
depend on lifetime. The script therefore reports the fraction of admitted worlds with lifetime <= 600; if that
fraction is small, this data set CANNOT test the H-D3-35 claim and a new experiment is needed (see REPORT.md s6).

Decision rule (stated before any output exists):
  SUPPORT   if AUC(proxy -> learning_pays) >= 0.75 with a founder-clustered bootstrap 95% CI lower bound > 0.60,
            for the proxy updates_per_step (learning opportunities per unit life), AND it beats
            AUC(lifetime alone) and AUC(lr alone) by >= 0.05.
  REFUTE    if every proxy's CI contains 0.5.
  UNDECIDED otherwise, or if n_lifetime_le_600 / n_admitted < 0.2 (instrument cannot see the ratio).
"""
import json
import sys

import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."


def load(p):
    with open(f"{ROOT}/{p}") as f:
        return json.load(f)


def auc(x, y):
    x, y = np.asarray(x, float), np.asarray(y, bool)
    pos, neg = x[y], x[~y]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(gt / (len(pos) * len(neg)))


def cluster_boot(x, y, roots, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    x, y, roots = np.asarray(x, float), np.asarray(y, bool), np.asarray(roots)
    uniq = np.unique(roots)
    idx = {r: np.where(roots == r)[0] for r in uniq}
    out = []
    for _ in range(B):
        pick = np.concatenate([idx[r] for r in rng.choice(uniq, len(uniq))])
        a = auc(x[pick], y[pick])
        if a == a:
            out.append(a)
    return (float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))) if out else (None, None)


def main():
    A = load("ensorain/runs/wtp03/waveA.json")
    adm = A["admitted"]
    rows = []
    for a in adm:
        g, pre = a["g"], a.get("pre", {})
        T = g["time"]["lifetime"]
        lr = g.get("learning", {}).get("lr")
        rows.append(dict(root=a.get("root"), T=T, lr=lr, pays=bool(pre.get("learning_pays")),
                         upd=pre.get("updates"),
                         gap=(min(pre["rate_oracle"]) - max(pre["rate_trivial"]))
                         if pre.get("rate_oracle") and pre.get("rate_trivial") else None))
    n = len(rows)
    y = [r["pays"] for r in rows]
    roots = [r["root"] for r in rows]
    res = dict(n_admitted=n, n_pays=int(sum(y)),
               n_lifetime_le_600=sum(r["T"] <= 600 for r in rows),
               n_founders=len(set(roots)))
    proxies = {
        "lifetime": [r["T"] for r in rows],
        "lr": [r["lr"] if r["lr"] is not None else np.nan for r in rows],
        "lr_x_lifetime": [(r["lr"] or np.nan) * r["T"] for r in rows],
        "updates_per_step": [(r["upd"] / r["T"]) if r["upd"] else np.nan for r in rows],
        "info_gap": [r["gap"] if r["gap"] is not None else np.nan for r in rows],
    }
    for k, v in proxies.items():
        v = np.asarray(v, float)
        ok = ~np.isnan(v)
        yy, rr = np.asarray(y)[ok], np.asarray(roots)[ok]
        res[f"auc_{k}"] = auc(v[ok], yy)
        res[f"auc_{k}_ci"] = cluster_boot(v[ok], yy, rr)
        res[f"n_{k}"] = int(ok.sum())
    # Wave B: the only "ratio" the collider actually logged is updates / drift_period (campaign3.py:165),
    # i.e. learning time / WORLD-CHANGE time, not / lifetime. Report its relation to life_frac for completeness.
    try:
        Bw = load("ensorain/runs/wtp03/waveB.json")
        lo = [r["ratios"]["learn_over_change"] for r in Bw if r.get("ratios")]
        res["waveB_n_with_ratios"] = len(lo)
        res["waveB_learn_over_change_nonzero"] = int(sum(1 for v in lo if v))
    except Exception as ex:  # noqa: BLE001
        res["waveB_error"] = repr(ex)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
