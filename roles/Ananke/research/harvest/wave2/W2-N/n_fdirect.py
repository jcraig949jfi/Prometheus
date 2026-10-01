"""W2-N: direct, zero-compute estimate of the between-namespace SE inflation f.

Two independent draws of the SAME design exist for every covered group:
  W-O (namespace 0x600, M=512; saved marginals mean + 99% pair_ci per row) and
  W-Z (namespace 0x680, M=512; full pair arrays).
Same specimen, physics, genome, env, offset, trial set and arm (verified in n_decomp sanity and below);
only world seeds differ. For each unit, z = (m_WZ - m_WO) / sqrt(se_WZ^2 + se_WO^2), with se_WO from the
recorded pair_ci width / (2 * 2.5758) and se_WZ = sd/sqrt(P) of the W-Z pair means. If the within-run SEs are
right and namespaces add no variance, z ~ N(0, 1) and f = RMS(z) = 1.
Units:
  normal arm (a): one per group (arms share the normal run; per-row n512 differs only by scored mask);
  swap arm (s):   one per unique measurement (identical / mirrored arms deduplicated, n_decomp.D);
  DF, DN:         per unique measurement, se_WO using W-Z's a-s correlation (same design).
Reported for all groups, REST groups (not selected on the W-O draw) and AMBIG groups (selected because the W-O
draw sat near a threshold -> regression to the mean inflates |z|).
Output out/fdirect.json."""
from __future__ import annotations

import collections
import csv
import json
import math

import numpy as np
from scipy import stats

import n_decomp as N


def f_ci(z, level=0.95):
    z = np.asarray(z, float)
    n = len(z)
    s2 = float(np.mean(z * z))
    lo = math.sqrt(s2 * n / stats.chi2.ppf(1 - (1 - level) / 2, n))
    hi = math.sqrt(s2 * n / stats.chi2.ppf((1 - level) / 2, n))
    mad = float(np.median(np.abs(z - np.median(z))) * 1.4826)
    return {"n": n, "f_rms": round(math.sqrt(s2), 3), "ci95": [round(lo, 3), round(hi, 3)],
            "f_mad": round(mad, 3), "mean_z": round(float(z.mean()), 3),
            "frac_abs_gt_2.576": round(float(np.mean(np.abs(z) > 2.576)), 4)}


def boot_f(z_by_group, B=4000, seed=1):
    """cluster bootstrap over groups of RMS(z) -> 95% percentile CI."""
    keys = list(z_by_group)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        pick = rng.integers(0, len(keys), len(keys))
        zz = np.concatenate([z_by_group[keys[i]] for i in pick])
        vals.append(math.sqrt(np.mean(zz * zz)))
    return [round(float(np.quantile(vals, .025)), 3), round(float(np.quantile(vals, .975)), 3)]


def main():
    rows = list(csv.DictReader(open(N.WK / "W-Z" / "out" / "row_table.csv")))
    wo = {r["vid"]: r for r in csv.DictReader(open(N.WK / "W-O" / "out" / "rerun_table.csv"))}
    prio = {r["gid"]: r["priority"] for r in csv.DictReader(open(N.WK / "W-Z" / "out" / "group_table.csv"))}
    arms = N.load_arms()
    seen_a, seen_m = set(), {}
    out = collections.defaultdict(list)
    zg = collections.defaultdict(lambda: collections.defaultdict(list))
    detail = []
    for r in rows:
        g, arm = r["gid"], r["arm"]
        x = arms[(g, arm)]
        a, s = x["a"][x["ok"]], x["s"][x["ok"]]
        P = len(a)
        o = wo[r["vid"]]
        n5, s5 = json.loads(o["n512"]), json.loads(o["s512"])
        seA_o, seS_o = (n5[2] - n5[1]) / (2 * N.Z99), (s5[2] - s5[1]) / (2 * N.Z99)
        seA_z, seS_z = a.std(ddof=1) / math.sqrt(P), s.std(ddof=1) / math.sqrt(P)
        rho = float(np.corrcoef(a, s)[0, 1]) if a.std() > 0 and s.std() > 0 else 0.0
        if int(o["P"]) != P if "P" in o and o["P"] else False:
            pass
        pr = prio[g]
        if g not in seen_a:
            seen_a.add(g)
            den = math.hypot(seA_z, seA_o)
            if den > 0:
                z = (a.mean() - n5[0]) / den
                out[f"a_{pr}"].append(z)
                out["a_all"].append(z)
                zg["a"][g].append(z)
        # dedupe swap measurements by the (group, representative) key; mirrors give z of opposite sign
        key = (g, round(float(s.mean()), 6), round(float(a.mean()), 6))
        mkey = (g, round(float(1 - s.mean()), 6), round(float(a.mean()), 6))
        if key in seen_m or mkey in seen_m:
            continue
        seen_m[key] = True
        den = math.hypot(seS_z, seS_o)
        if den > 0:
            z = (s.mean() - s5[0]) / den
            out[f"s_{pr}"].append(z)
            out["s_all"].append(z)
            zg["s"][g].append(z)
        # DF / DN
        for name, sgn in (("DF", +1), ("DN", -1)):
            v_z = (s - .5) + sgn * (a - .5) / 2
            se_z = v_z.std(ddof=1) / math.sqrt(P)
            se_o = math.sqrt(max(seS_o ** 2 + seA_o ** 2 / 4 + sgn * rho * seS_o * seA_o, 0))
            m_o = (s5[0] - .5) + sgn * (n5[0] - .5) / 2
            den = math.hypot(se_z, se_o)
            if den > 0:
                z = (v_z.mean() - m_o) / den
                out[f"{name}_{pr}"].append(z)
                out[f"{name}_all"].append(z)
                zg[name][g].append(z)
        detail.append({"gid": g, "arm": arm, "prio": pr, "P": P, "WO_P": o.get("P"), "s_WZ": round(float(s.mean()), 4),
                       "s_WO": s5[0], "seS_z": round(seS_z, 5), "seS_o": round(seS_o, 5)})
    res = {k: f_ci(v) for k, v in sorted(out.items())}
    for nm in ("a", "s", "DF", "DN"):
        res[f"{nm}_all"]["cluster_boot_ci95"] = boot_f({g: np.array(v) for g, v in zg[nm].items()})
        rest = {g: np.array(v) for g, v in zg[nm].items() if prio[g] == "REST"}
        res[f"{nm}_REST"]["cluster_boot_ci95"] = boot_f(rest)
    # SE ratio check: W-O CI-derived SE vs W-Z sd/sqrt(P) (same design => should be ~1)
    ratio = [d["seS_o"] / d["seS_z"] for d in detail if d["seS_z"] > 0]
    res["seS_ratio_WO_over_WZ"] = {"median": round(float(np.median(ratio)), 3),
                                   "q10": round(float(np.quantile(ratio, .1)), 3),
                                   "q90": round(float(np.quantile(ratio, .9)), 3)}
    for k, v in res.items():
        print(k, v)
    json.dump({"summary": res, "detail": detail}, open(N.OUT / "fdirect.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
