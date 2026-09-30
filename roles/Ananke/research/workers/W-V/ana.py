"""W-V analysis: follow effects, pair bootstrap, pivot contrast, frozen classification (PLAN s2-s3).
python ana.py <tag> [<tag> ...]  -> out/summary_<tag>.json/.txt"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
NOT_RUN = -(2 ** 40)
MIN_ELIGIBLE = 20
N_BOOT = 2000
ALPHA = 0.01
K5 = 5


def follow_table(ns0, arm_s0, y, scored, trials):
    """-> elig [P, nt] bool, f [P, nt] pair-mean follow (NaN where not eligible)."""
    Mw, nt = ns0.shape
    tr = np.zeros(nt, bool)
    tr[list(trials)] = True
    A, B = slice(0, None, 2), slice(1, None, 2)
    corr = np.sign(ns0) == y
    ran = arm_s0 != NOT_RUN
    elig = corr[A] & corr[B] & scored[A] & scored[B] & ran[A] & ran[B] & tr[None]
    sg = np.sign(arm_s0)
    fA = (sg[A] == np.sign(ns0[B])) & (sg[A] != 0)
    fB = (sg[B] == np.sign(ns0[A])) & (sg[B] != 0)
    f = np.where(elig, (fA.astype(float) + fB) / 2, np.nan)
    return elig, f


def _q(v):
    return float(np.quantile(v, ALPHA / 2)), float(np.quantile(v, 1 - ALPHA / 2))


def stratum(raw, oi, trials, permute_votes=False, seed=0):
    """Stats for offset index oi over `trials`. Returns table dict for classify()."""
    arms = list(raw["arms"])
    ns0, y, sc = raw["normal_s0"], raw["y"], raw["scored"]
    P = ns0.shape[0] // 2
    F = {}
    elig0 = None
    for ai, lab in enumerate(arms):
        el, f = follow_table(ns0, raw["arm_s0"][ai, oi], y, sc, trials)
        F[lab] = f
        elig0 = el if elig0 is None else (elig0 & el)
    n_p = elig0.sum(1).astype(float)                   # eligible pair-trials per pair
    n = int(n_p.sum())
    res = {"n": n}
    if n < MIN_ELIGIBLE:
        return res
    sums = {lab: np.where(elig0, F[lab], 0).sum(1) for lab in arms}
    for j in range(K5):
        sums[f"drop{j}"] = sums["ALL5"] - sums[f"c{j}"]
    # pivot contrast (world A votes; y_A correct)
    v = raw["votes"][0::2]                              # [P, nt, K]
    yA = y[0::2]
    if permute_votes:
        rng0 = np.random.default_rng(seed + 1)
        idx = np.argwhere(elig0)
        perm = idx[rng0.permutation(len(idx))]
        v2 = v.copy()
        v2[idx[:, 0], idx[:, 1]] = v[perm[:, 0], perm[:, 1]] * (yA[perm[:, 0], perm[:, 1]] * yA[idx[:, 0], idx[:, 1]])[:, None]
        v = v2
    agree = v == yA[..., None]
    nag = agree.sum(-1)
    piv = (nag == 3)[..., None] & agree                 # [P, nt, K]
    fs = np.stack([F[f"s{j}"] for j in range(K5)], -1)  # [P, nt, K]
    e3 = elig0[..., None]
    pv_s = np.where(e3 & piv, fs, 0).sum((1, 2))
    pv_n = (e3 & piv).sum((1, 2)).astype(float)
    np_s = np.where(e3 & ~piv, fs, 0).sum((1, 2))
    np_n = (e3 & ~piv).sum((1, 2)).astype(float)
    keys = list(sums)
    S = np.stack([sums[k] for k in keys])               # [nk, P]
    pt = S.sum(1) / n
    rng = np.random.default_rng(seed)
    bs = []
    bpiv = []
    for _ in range(N_BOOT):
        w = np.bincount(rng.integers(P, size=P), minlength=P).astype(float)
        d = w @ n_p
        bs.append(S @ w / d)
        a, b = w @ pv_n, w @ np_n
        bpiv.append((w @ pv_s) / a - (w @ np_s) / b if a > 0 and b > 0 else np.nan)
    bs = np.array(bs)
    for i, k in enumerate(keys):
        lo, hi = _q(bs[:, i])
        if k.startswith("drop"):
            res.setdefault("drop", {})[int(k[4:])] = {"e": float(pt[i]), "lo": lo, "hi": hi}
        else:
            res[k] = {"e": float(pt[i]), "lo": lo, "hi": hi}
    bpiv = np.array(bpiv)
    bpiv = bpiv[~np.isnan(bpiv)]
    if pv_n.sum() > 0 and np_n.sum() > 0 and len(bpiv):
        D = pv_s.sum() / pv_n.sum() - np_s.sum() / np_n.sum()
        lo, hi = _q(bpiv)
        res["piv"] = {"D": float(D), "lo": lo, "hi": hi, "n_piv": int(pv_n.sum()), "n_non": int(np_n.sum()),
                      "f_piv": float(pv_s.sum() / pv_n.sum()), "f_non": float(np_s.sum() / np_n.sum())}
    else:
        res["piv"] = {"D": float("nan"), "lo": float("nan"), "hi": float("nan")}
    E = res["ALL5"]["e"]
    se = sum(res[f"s{j}"]["e"] for j in range(K5))
    res["additivity"] = se / E if E > 0 else None
    res["share"] = [res[f"s{j}"]["e"] / se if se > 0 else None for j in range(K5)]
    return res


def classify(t):
    """Frozen PLAN s3. -> (class, set)."""
    if t.get("n", 0) < MIN_ELIGIBLE:
        return ("UNDEFINED", ())
    E = t["ALL5"]["e"]
    if E < 0.50:
        return ("NOT-INFORMATIVE", ())
    s = [t[f"s{j}"] for j in range(K5)]
    c = [t[f"c{j}"] for j in range(K5)]
    C = tuple(j for j in range(K5) if s[j]["lo"] >= 0.03 or t["drop"][j]["lo"] >= 0.03)
    for js in range(K5):
        if (s[js]["e"] / E >= 0.70 and c[js]["e"] / E <= 0.30
                and all(s[i]["hi"] <= 0.10 for i in range(K5) if i != js)):
            return ("DICTATOR", (js,))
    pv = t["piv"]
    if (all(x["lo"] >= 0.03 for x in s) and max(x["e"] for x in s) / E <= 0.50
            and min(x["e"] for x in c) / E >= 0.60 and pv["D"] >= 0.50 and pv["lo"] > 0):
        return ("MAJORITY", C)
    if 1 <= len(C) <= 2:
        return ("SUBSET", C)
    if len(C) >= 3:
        return ("DISTRIBUTED-NONMAJ", C)
    return ("REDUNDANT-JOINT", ())


def load_raw(tag):
    d = dict(np.load(OUT / f"raw_{tag}.npz"))
    meta = json.loads((OUT / f"meta_{tag}.json").read_text())
    d["arms"] = meta["arms"]
    return d, meta


def summarize(tag, permute_votes=False):
    raw, meta = load_raw(tag)
    Pd = int(raw["Pd"])
    trials = [int(k) for k in raw["trials"]]
    out = {"tag": tag, "spec": meta["spec"], "M": meta["M"], "ns": meta["ns"], "permute_votes": permute_votes,
           "sensor_dist_modal": np.median(raw["sdist"], 0).tolist(),
           "sensor_dist_all_same": bool((raw["sdist"] == raw["sdist"][0]).all()), "strata": {}}
    lines = [f"{tag} spec {meta['spec']} M {meta['M']} ns {meta['ns']} permute_votes {permute_votes}",
             f"sensor ring distance to readout (modal) {out['sensor_dist_modal']} all worlds same: {out['sensor_dist_all_same']}"]
    for oi, o in enumerate(raw["offsets"].tolist()):
        for lab, trs in (("pooled", trials), ("q0", [k for k in trials if (k * Pd + o) % 2 == 0]),
                         ("q1", [k for k in trials if (k * Pd + o) % 2 == 1])):
            t = stratum(raw, oi, trs, permute_votes=permute_votes)
            cl = classify(t)
            t["class"] = [cl[0], list(cl[1])]
            t["trials"] = trs
            t["o"], t["lab"] = o, lab
            out["strata"][f"o{o}{lab}"] = t
            if t["n"] < MIN_ELIGIBLE:
                lines.append(f"o{o:<2} {lab:6} n {t['n']:4d} UNDEFINED")
                continue
            ef = lambda k: f"{t[k]['e']:.2f}[{t[k]['lo']:.2f},{t[k]['hi']:.2f}]"
            pv = t["piv"]
            lines.append(
                f"o{o:<2} {lab:6} n {t['n']:4d} {cl[0]}{list(cl[1]) if cl[1] else ''} | ALL5 {ef('ALL5')} FLA {ef('FLA')}"
                f" | single " + " ".join(f"s{j} {ef(f's{j}')}" for j in range(K5))
                + " | compl " + " ".join(f"c{j} {t[f'c{j}']['e']:.2f}" for j in range(K5))
                + (f" | A {t['additivity']:.2f}" if t["additivity"] is not None else " | A -"))
            lines[-1] += (f" | piv D {pv['D']:.2f}[{pv['lo']:.2f},{pv['hi']:.2f}] f_piv {pv.get('f_piv', float('nan')):.2f}"
                          f" f_non {pv.get('f_non', float('nan')):.2f}")
    suffix = "_perm" if permute_votes else ""
    (OUT / f"summary_{tag}{suffix}.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / f"summary_{tag}{suffix}.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return out


def verdict(out, offsets=None, primary=("q0", "q1")):
    """PLAN s3 champion verdict over informative defined strata (primary = phase strata)."""
    cls = []
    for key, t in out["strata"].items():
        o, lab = t["o"], t["lab"]
        if lab not in primary or (offsets is not None and o not in offsets):
            continue
        if t["class"][0] in ("UNDEFINED", "NOT-INFORMATIVE"):
            continue
        cls.append((key, t["class"][0], tuple(t["class"][1])))
    if not cls:
        return "NO-INFLIGHT-SENSOR-CARRIER", cls
    names = [c[1] for c in cls]
    best = max(set(names), key=names.count)
    if names.count(best) >= (2 / 3) * len(names):
        return best, cls
    return "MIXED-BY-STRATUM", cls


if __name__ == "__main__":
    for tg in sys.argv[1:]:
        o = summarize(tg)
        print("VERDICT", tg, verdict(o))
