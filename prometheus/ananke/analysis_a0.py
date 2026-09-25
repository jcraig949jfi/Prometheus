"""PTE-C1 A0 interaction analysis (roles/Ananke/pte/ANALYSIS_PLAN_C1_A0.md).

Declared at commit time, AFTER A0 closed and BEFORE any rung distribution
beyond the per-family marginal counts was inspected:

  binarisation   L1  gen0.frac_sensitive_any >= 0.30  (the PREREG living threshold)
                 L2  gen0.frac_contrast_pos >= 2/64   (>= 2 random genomes whose
                     actuator S0 moves with the target at readout). Proxy caveat:
                     a genome whose actuator diverges between twins WITHOUT tracking
                     the target still scores > 0 about half the time, so L2 measures
                     "input causally reaches the readout" at ~half sensitivity to
                     untargeted divergence -- distal influence, not target-aligned
                     transport. HOLD's L2 is local by design; FLIP's includes the
                     local teacher path (plan s5) and is not interpreted as distal.
                 L2' plant.acc >= 0.75
  split          FIT = cell_id first hex digit 0-7, CONFIRM = 8-f
  models         (a) one-hot single dials, L2-regularised logistic regression (C=1)
                 (b) (a) + log ratios R_time R_surv R_mem R_band R_clock + topology x fanout
                 (c) depth-3 decision tree on raw dials + ratios (min_samples_leaf 20)
  criterion      a ratio "explains" a rung iff AUC_conf(b) - AUC_conf(a) >= 0.02 AND a
                 depth-1 stump on that ratio fitted separately on FIT and on CONFIRM puts
                 its threshold within one A0 level-step (same quantile bin of 10) on both.
  null           (b) refitted with family labels permuted within topology.

    python -m prometheus.ananke.analysis_a0 --cells <cells.jsonl> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier, export_text

from .campaign import DIALS, ENV_DIALS

RUNGS = {
    "L1": lambda r: r["result"]["gen0"]["frac_sensitive_any"] >= 0.30,
    "L2": lambda r: r["result"]["gen0"]["frac_contrast_pos"] >= 2 / 64,
    "L2p": lambda r: r["result"]["plant"]["acc"] >= 0.75,
}
RATIOS = ("R_time", "R_surv", "R_mem", "R_band", "R_clock")


def hops(ph, d):
    if ph["topology"] in ("torus", "ring"):
        return max(1, math.ceil(d / ph["radius"]))
    return max(1, d)


def ratios(r):
    ph, env, lv = r["physics"], r["env"], r["levels"]
    fam = env["family"]
    d = env["d"]
    budget = env["gap"] if fam == "HOLD" else env["delta"]
    h = 0 if fam == "HOLD" else hops(ph, d)
    per_hop = min(ph["radius"], d) if ph["topology"] in ("torus", "ring") else 1
    R = {"torus": 2 * ph["radius"] * (ph["radius"] + 1), "ring": 2 * ph["radius"],
         "random": ph["k_random"], "smallworld": 4, "global": ph["fanout"]}[ph["topology"]]
    fan = R if (ph["dest_mode"] == "all" and ph["topology"] != "global") else ph["fanout"]
    surv = (1 - ph["loss"]) ** (max(h, 1) if ph["loss_per_hop"] else 1)
    rate = (1 / ph["update_period"]) if ph["update_mode"] == "sync" else ph["update_p"]
    mem = (2 ** ph["decay_shift"]) if ph["decay_shift"] > 0 else 1e3
    out = {
        "R_time": (ph["lat_base"] + ph["lat_hop"] * per_hop + ph["lat_jitter"]) * max(h, 0) / budget,
        "R_surv": fan * surv * (1 + ph["dup"]),
        "R_mem": mem / budget,
        "R_band": 0.0 if ph["cap"] == 0 else fan * R / ph["cap"],
        "R_clock": rate * env["cue_len"],
    }
    return {k: float(np.log1p(v)) for k, v in out.items()}


def features(rows, with_ratios):
    cols = []
    for dial, levels in list(DIALS.items()) + list(ENV_DIALS.items()):
        for lv in levels:
            cols.append((dial, lv))
    X = np.zeros((len(rows), len(cols)), dtype=float)
    for i, r in enumerate(rows):
        for j, (dial, lv) in enumerate(cols):
            v = r["levels"].get(dial, r["env_levels"].get(dial))
            X[i, j] = float(v == lv)
    names = [f"{d}={v}" for d, v in cols]
    if with_ratios:
        rt = np.array([[ratios(r)[k] for k in RATIOS] for r in rows])
        topo = [r["physics"]["topology"] for r in rows]
        fan = np.array([np.log2(r["physics"]["fanout"]) for r in rows])
        tf = np.stack([fan * (np.array(topo) == t) for t in DIALS["topology"]], 1)
        X = np.concatenate([X, rt, tf], 1)
        names += list(RATIOS) + [f"topo={t}*log2fanout" for t in DIALS["topology"]]
    return X, names


def auc(model, X, y):
    if len(set(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, model.predict_proba(X)[:, 1]))


def stump_threshold(x, y):
    t = DecisionTreeClassifier(max_depth=1, min_samples_leaf=20).fit(x[:, None], y)
    return float(t.tree_.threshold[0]) if t.tree_.node_count > 1 else float("nan")


def analyse(rows):
    fit = [r for r in rows if int(r["cell_id"][0], 16) < 8]
    conf = [r for r in rows if int(r["cell_id"][0], 16) >= 8]
    res = {"n_fit": len(fit), "n_conf": len(conf)}
    for rung, fn in RUNGS.items():
        yf = np.array([fn(r) for r in fit])
        yc = np.array([fn(r) for r in conf])
        out = {"pos_rate_fit": float(yf.mean()), "pos_rate_conf": float(yc.mean())}
        if yf.sum() < 10 or (~yf).sum() < 10:
            out["status"] = "INDETERMINATE: fewer than 10 positives or negatives in FIT"
            res[rung] = out
            continue
        Xa_f, _ = features(fit, False)
        Xa_c, _ = features(conf, False)
        Xb_f, nb = features(fit, True)
        Xb_c, _ = features(conf, True)
        ma = LogisticRegression(C=1.0, max_iter=3000).fit(Xa_f, yf)
        mb = LogisticRegression(C=1.0, max_iter=3000).fit(Xb_f, yf)
        tr = DecisionTreeClassifier(max_depth=3, min_samples_leaf=20, random_state=0).fit(Xb_f, yf)
        out.update(auc_single=auc(ma, Xa_c, yc), auc_ratios=auc(mb, Xb_c, yc), auc_tree=auc(tr, Xb_c, yc))
        out["tree"] = export_text(tr, feature_names=nb, decimals=2)
        # per-ratio: stump thresholds on each half, quantile-bin agreement
        per = {}
        rf = np.array([[ratios(r)[k] for k in RATIOS] for r in fit])
        rc = np.array([[ratios(r)[k] for k in RATIOS] for r in conf])
        allv = np.concatenate([rf, rc])
        for j, k in enumerate(RATIOS):
            tf, tc = stump_threshold(rf[:, j], yf), stump_threshold(rc[:, j], yc)
            edges = np.unique(np.quantile(allv[:, j], np.linspace(0, 1, 11)))
            bf, bc = np.searchsorted(edges, tf), np.searchsorted(edges, tc)
            # single-ratio added value: (a) + this ratio only
            Xk_f = np.concatenate([Xa_f, rf[:, j:j + 1]], 1)
            Xk_c = np.concatenate([Xa_c, rc[:, j:j + 1]], 1)
            mk = LogisticRegression(C=1.0, max_iter=3000).fit(Xk_f, yf)
            gain = auc(mk, Xk_c, yc) - out["auc_single"]
            per[k] = {"thr_fit": tf, "thr_conf": tc, "bin_fit": int(bf), "bin_conf": int(bc),
                      "auc_gain": float(gain),
                      "EXPLAINS": bool(gain >= 0.02 and abs(int(bf) - int(bc)) <= 1)}
        out["ratios"] = per
        # null: family permuted within topology
        g = np.random.default_rng(0)
        perm = list(fit)
        by = {}
        for i, r in enumerate(perm):
            by.setdefault(r["physics"]["topology"], []).append(i)
        yperm = yf.copy()
        for idx in by.values():
            yperm[idx] = g.permutation(yf[idx])
        mn = LogisticRegression(C=1.0, max_iter=3000).fit(Xb_f, yperm)
        out["auc_null_within_topology"] = auc(mn, Xb_c, yc)
        res[rung] = out
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(a.cells, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r["wave"] == "A0"]
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    result = {"per_family": {}, "pooled_comm_families": None}
    fams = sorted({r["env"]["family"] for r in rows})
    for fam in fams:
        result["per_family"][fam] = analyse([r for r in rows if r["env"]["family"] == fam])
    result["pooled_comm_families"] = analyse([r for r in rows if r["env"]["family"] in ("RELAY", "XOR", "MAJ")])
    # ladder counts: L1 -> L2 -> L2'
    lad = {}
    for fam in fams:
        rs = [r for r in rows if r["env"]["family"] == fam]
        l1 = np.array([RUNGS["L1"](r) for r in rs])
        l2 = np.array([RUNGS["L2"](r) for r in rs])
        l2p = np.array([RUNGS["L2p"](r) for r in rs])
        lad[fam] = {"n": len(rs), "L1": int(l1.sum()), "L2": int(l2.sum()), "L2p": int(l2p.sum()),
                    "L2_given_L1": float(l2[l1].mean()) if l1.any() else None,
                    "L2_given_notL1": float(l2[~l1].mean()) if (~l1).any() else None,
                    "L2p_given_L2": float(l2p[l2].mean()) if l2.any() else None}
    result["ladder"] = lad
    (out / "a0_interactions.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(lad, indent=1))
    for fam, r in result["per_family"].items():
        for rung in RUNGS:
            x = r[rung]
            if "auc_single" not in x:
                print(fam, rung, x.get("status"), f"pos {x['pos_rate_fit']:.3f}")
                continue
            ex = [k for k, v in x["ratios"].items() if v["EXPLAINS"]]
            print(f"{fam:5s} {rung:3s} pos {x['pos_rate_fit']:.3f} AUC single {x['auc_single']:.3f} "
                  f"+ratios {x['auc_ratios']:.3f} tree {x['auc_tree']:.3f} null {x['auc_null_within_topology']:.3f} "
                  f"EXPLAINS {ex}")


if __name__ == "__main__":
    main()
