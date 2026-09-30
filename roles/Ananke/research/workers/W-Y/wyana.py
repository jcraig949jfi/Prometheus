"""W-Y analysis: follow effects, 99% pair bootstrap, frozen PLAN s3 decision (+ addendum A2).
python wyana.py <tag> [...] -> out/summary_<tag>.json/.txt"""
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


def follow_table(ns0, arm, y, scored, trials):
    Mw, nt = ns0.shape
    tr = np.zeros(nt, bool)
    tr[list(trials)] = True
    A, B = slice(0, None, 2), slice(1, None, 2)
    corr = np.sign(ns0) == y
    ran = arm != NOT_RUN
    elig = corr[A] & corr[B] & scored[A] & scored[B] & ran[A] & ran[B] & tr[None]
    sg = np.sign(arm)
    fA = (sg[A] == np.sign(ns0[B])) & (sg[A] != 0)
    fB = (sg[B] == np.sign(ns0[A])) & (sg[B] != 0)
    return elig, (fA.astype(float) + fB) / 2


def _q(v):
    return float(np.quantile(v, ALPHA / 2)), float(np.quantile(v, 1 - ALPHA / 2))


def stratum(raw, arms, oi, trials, kp="KP7", shuffle_seed=None, seed=0):
    ns0, y, sc = raw["normal_s0"], raw["y"], raw["scored"]
    armS = raw["arm_s0"][:, oi]                                   # [A, M, nt]
    elig = None
    for a in range(len(arms)):
        el, _ = follow_table(ns0, armS[a], y, sc, trials)
        elig = el if elig is None else (elig & el)
    if shuffle_seed is not None:
        # MF-SHUF (addendum A3): one permutation of eligible pair-trials applied to all arms' outcomes
        idx = np.argwhere(elig)
        perm = idx[np.random.default_rng(1000 + shuffle_seed).permutation(len(idx))]
        armS = armS.copy()
        for w in (0, 1):
            src = armS[:, 2 * perm[:, 0] + w, perm[:, 1]]
            armS[:, 2 * idx[:, 0] + w, idx[:, 1]] = src
    F = {lab: follow_table(ns0, armS[a], y, sc, trials)[1] for a, lab in enumerate(arms)}
    n_p = elig.sum(1).astype(float)
    n = int(n_p.sum())
    res = {"n": n}
    if n < MIN_ELIGIBLE:
        return res
    P = len(n_p)
    S = np.stack([np.where(elig, F[lab], 0).sum(1) for lab in arms])     # [A, P]
    pt = S.sum(1) / n
    ik, ifl, ij = arms.index(kp), arms.index("FLA"), arms.index("KP7+FLA")
    rng = np.random.default_rng(seed)
    bs = np.empty((N_BOOT, len(arms)))
    for b in range(N_BOOT):
        w = np.bincount(rng.integers(P, size=P), minlength=P).astype(float)
        bs[b] = S @ w / (w @ n_p)
    for a, lab in enumerate(arms):
        lo, hi = _q(bs[:, a])
        res[lab] = {"e": float(pt[a]), "lo": lo, "hi": hi}
    d_pt = pt[ij] - max(pt[ik], pt[ifl])
    d_bs = bs[:, ij] - np.maximum(bs[:, ik], bs[:, ifl])
    lo, hi = _q(d_bs)
    res["diff"] = {"e": float(d_pt), "lo": lo, "hi": hi}
    d2 = bs[:, arms.index("KPALL")] - bs[:, ik]
    lo2, hi2 = _q(d2)
    res["kpall_minus_kp"] = {"e": float(pt[arms.index("KPALL")] - pt[ik]), "lo": lo2, "hi": hi2}
    return res


def informative(t):
    return t.get("n", 0) >= MIN_ELIGIBLE and (t["SITE_R"]["e"] >= 0.50 or t["FLA"]["e"] >= 0.50)


def classify(t, kp="KP7"):
    """Frozen PLAN s3 (order per addendum A2)."""
    if t.get("n", 0) < MIN_ELIGIBLE:
        return "UNDEFINED"
    if not informative(t):
        return "NOT-INFORMATIVE"
    k, d = t[kp], t["diff"]
    if k["lo"] > 0.20 and d["e"] >= 0.10 and d["lo"] > 0:
        return "KP7 IS THE READOUT HALF"
    if k["lo"] > 0.20 and d["lo"] <= 0 <= d["hi"]:
        return "KP7 REDUNDANT"
    if k["hi"] < 0.05:
        return "KP7 NOT A CARRIER"
    return "UNRESOLVED"


def load_raw(tag):
    d = dict(np.load(OUT / f"raw_{tag}.npz"))
    meta = json.loads((OUT / f"meta_{tag}.json").read_text())
    return d, meta


def summarize(tag, kp="KP7", shuffle_seed=None, write=True, quiet=False):
    raw, meta = load_raw(tag)
    arms = meta["arms"]
    Pd, per = int(raw["Pd"]), int(raw["update_period"])
    trials = [int(k) for k in raw["trials"]]
    out = {"tag": tag, "spec": meta["spec"], "M": meta["M"], "ns": meta["ns"], "kp_arm": kp,
           "shuffle_seed": shuffle_seed, "strata": {}}
    lines = [f"{tag} spec {meta['spec']} M {meta['M']} ns {meta['ns']} kp-arm {kp} shuffle {shuffle_seed}"]
    for oi, o in enumerate(raw["offsets"].tolist()):
        for lab, trs in (("q0", [k for k in trials if (k * Pd + o) % per == 0]),
                         ("q1", [k for k in trials if (k * Pd + o) % per == 1]), ("pooled", trials)):
            t = stratum(raw, arms, oi, trs, kp=kp, shuffle_seed=shuffle_seed)
            t["class"] = classify(t, kp) if lab != "pooled" else "(not a decision stratum)"
            t["o"], t["lab"], t["trials"] = o, lab, trs
            tsel = np.zeros(raw["cen_kp7_diff"].shape[-1], bool)
            tsel[trs] = True
            for c in ("kp7_diff", "kp_any_diff", "fla_diff", "inbox_diff", "S_diff"):
                t[f"cen_{c}"] = float(raw[f"cen_{c}"][oi][:, tsel].mean())
            t["cen_kp_slot_diff"] = raw["cen_kp_slot_diff"][oi][:, tsel].mean((0, 1)).round(3).tolist()
            out["strata"][f"o{o}{lab}"] = t
            if t["n"] < MIN_ELIGIBLE:
                lines.append(f"o{o:<2} {lab:6} n {t['n']:4d} UNDEFINED")
                continue
            ef = lambda k: f"{t[k]['e']:.2f}[{t[k]['lo']:.2f},{t[k]['hi']:.2f}]"
            lines.append(f"o{o:<2} {lab:6} n {t['n']:4d} {t['class']:24s} | " + " ".join(
                f"{a} {ef(a)}" for a in arms) + f" | diff {ef('diff')} | KPALL-KP {ef('kpall_minus_kp')}"
                + f" | cen kp7 {t['cen_kp7_diff']:.2f} kpany {t['cen_kp_any_diff']:.2f} fla {t['cen_fla_diff']:.2f}"
                + f" inbox {t['cen_inbox_diff']:.2f} S {t['cen_S_diff']:.2f}")
    out["overall"] = overall(out)
    lines.append(f"OVERALL {out['overall']}")
    if write:
        sfx = ("" if kp == "KP7" else f"_{kp}") + ("" if shuffle_seed is None else f"_shuf{shuffle_seed}")
        (OUT / f"summary_{tag}{sfx}.json").write_text(json.dumps(out, indent=1, default=float))
        (OUT / f"summary_{tag}{sfx}.txt").write_text("\n".join(lines) + "\n")
    if not quiet:
        print("\n".join(lines))
    return out


def overall(out):
    cls = {k: t["class"] for k, t in out["strata"].items() if t["lab"] != "pooled"
           and t["class"] not in ("UNDEFINED", "NOT-INFORMATIVE")}
    if not cls:
        return {"class": "NO INFORMATIVE STRATUM", "strata": cls}
    s = set(cls.values())
    return {"class": s.pop() if len(s) == 1 else "MIXED", "strata": cls}


if __name__ == "__main__":
    for tg in sys.argv[1:]:
        summarize(tg)
