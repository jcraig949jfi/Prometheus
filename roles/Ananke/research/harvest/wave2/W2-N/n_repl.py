"""W2-N: direct between-namespace inflation f from the fresh-namespace replicates (n_runs.py).

Per group g and statistic X in {a, s, DF, DN} (pair means of the run arm), namespace draws j:
  0x680 prefix (first 128 pairs of the W-Z arrays; KA-verified equal to a fresh M=256 run in 0x680),
  0x4e01, 0x4e02, 0x4e03 (fresh, M=256), and 0x600 (W-O, M=512, saved marginals; DF/DN SE uses W-Z's a-s corr).
Q_g = sum_j w_j (m_j - m_w)^2, w_j = 1/SE_j^2  ~  f^2 chi2_{n_g - 1} if the within-run SEs are right and the
namespace adds nothing. f^2 = sum_g Q_g / sum_g (n_g - 1); 95% CI from chi2 on the pooled df.
Within-namespace control: 0x680 prefix vs 0x680 second half (pairs 128..255), same Q with 1 df per group.
Output out/repl.json"""
from __future__ import annotations

import csv
import json
import math

import numpy as np
from scipy import stats

import n_decomp as N

GROUPS = [("2a776b0a3245a735", "inbox", "flipped"), ("6edf00dccf85ffd6", "inbox", "flipped"),
          ("48c5f7d48604ca8b", "site_all", "flipped"), ("047aa8ed8357fa1c", "channel_all", "stable"),
          ("b7e296268480ebee", "inbox", "stable"), ("561ed71c41350fe1", "site_all", "stable")]
FRESH = ("4e01", "4e02", "4e03")


def dec(A):
    A = A.astype(float)
    A[A == 255] = np.nan
    return A / 4


def pm(At, St):
    both = ~np.isnan(At) & ~np.isnan(St)
    with np.errstate(all="ignore"):
        a = np.nanmean(np.where(both, At, np.nan), 1)
        s = np.nanmean(np.where(both, St, np.nan), 1)
    ok = ~np.isnan(a) & ~np.isnan(s)
    return a[ok], s[ok]


def stats_of(a, s):
    P = len(a)
    out = {}
    for nm, v in (("a", a), ("s", s), ("DF", (s - .5) + (a - .5) / 2), ("DN", (s - .5) - (a - .5) / 2)):
        out[nm] = (float(v.mean()), float(v.std(ddof=1) / math.sqrt(P)))
    return out


def Q(draws):
    m = np.array([d[0] for d in draws])
    w = 1 / np.array([d[1] for d in draws]) ** 2
    mw = (w * m).sum() / w.sum()
    return float((w * (m - mw) ** 2).sum()), len(draws) - 1


def ci(Qs, dfs):
    q, d = sum(Qs), sum(dfs)
    f2 = q / d
    return {"f": round(math.sqrt(f2), 3), "df": d,
            "ci95": [round(math.sqrt(q / stats.chi2.ppf(.975, d)), 3), round(math.sqrt(q / stats.chi2.ppf(.025, d)), 3)],
            "p_f_eq_1_upper": round(float(stats.chi2.sf(q, d)), 4)}


def main():
    rows = list(csv.DictReader(open(N.WK / "W-Z" / "out" / "row_table.csv")))
    wo = {r["vid"]: r for r in csv.DictReader(open(N.WK / "W-O" / "out" / "rerun_table.csv"))}
    res = {"groups": []}
    acc = {k: {nm: ([], []) for nm in ("a", "s", "DF", "DN")} for k in ("ns", "ns_noWO", "within")}
    for g, arm, kind in GROUPS:
        z = np.load(N.WK / "W-Z" / "out" / "pairs" / f"{g}.npz")
        At, St = dec(z[f"a__{arm}"]), dec(z[f"s__{arm}"])
        a1, s1 = pm(At[:128], St[:128])
        a2, s2 = pm(At[128:], St[128:])
        aF, sF = pm(At, St)
        rho = float(np.corrcoef(aF, sF)[0, 1])
        draws = {"0x680a": stats_of(a1, s1)}
        half2 = stats_of(a2, s2)
        for ns in FRESH:
            r = np.load(N.OUT / "runs" / f"{g}_{arm}_{ns}_M256.npz")
            draws[f"0x{ns}"] = stats_of(*pm(dec(r["a"]), dec(r["s"])))
        vid = next(r["vid"] for r in rows if r["gid"] == g and r["arm"] == arm)
        n5, s5 = json.loads(wo[vid]["n512"]), json.loads(wo[vid]["s512"])
        sa, ss = (n5[2] - n5[1]) / (2 * N.Z99), (s5[2] - s5[1]) / (2 * N.Z99)
        draws["0x600(M512)"] = {"a": (n5[0], sa), "s": (s5[0], ss),
                                "DF": ((s5[0] - .5) + (n5[0] - .5) / 2, math.sqrt(ss * ss + sa * sa / 4 + rho * ss * sa)),
                                "DN": ((s5[0] - .5) - (n5[0] - .5) / 2, math.sqrt(ss * ss + sa * sa / 4 - rho * ss * sa))}
        rec = {"gid": g, "arm": arm, "kind": kind, "draws": draws, "half2_0x680": half2, "Q": {}}
        for nm in ("a", "s", "DF", "DN"):
            q, d = Q([v[nm] for v in draws.values()])
            q2, d2 = Q([v[nm] for k, v in draws.items() if k != "0x600(M512)"])
            q3, d3 = Q([draws["0x680a"][nm], half2[nm]])
            acc["ns"][nm][0].append(q); acc["ns"][nm][1].append(d)
            acc["ns_noWO"][nm][0].append(q2); acc["ns_noWO"][nm][1].append(d2)
            acc["within"][nm][0].append(q3); acc["within"][nm][1].append(d3)
            rec["Q"][nm] = {"ns": round(q, 3), "df": d, "ratio": round(q / d, 3), "within": round(q3, 3)}
        res["groups"].append(rec)
        print(g[:8], kind, arm, {nm: rec["Q"][nm]["ratio"] for nm in rec["Q"]})
    res["f"] = {k: {nm: ci(*v[nm]) for nm in v} for k, v in acc.items()}
    # pooled over the two label statistics (DF, DN): conservative df (they are correlated) = DF df
    for k in acc:
        q = [a + b for a, b in zip(acc[k]["DF"][0], acc[k]["DN"][0])]
        d = acc[k]["DF"][1]
        f2 = sum(q) / (2 * sum(d))
        res["f"][k]["DF+DN_pooled"] = {"f": round(math.sqrt(f2), 3), "df_conservative": sum(d),
                                       "ci95": [round(math.sqrt(sum(q) / 2 / stats.chi2.ppf(.975, sum(d))), 3),
                                                round(math.sqrt(sum(q) / 2 / stats.chi2.ppf(.025, sum(d))), 3)]}
    for k, v in res["f"].items():
        print(k, json.dumps(v))
    json.dump(res, open(N.OUT / "repl.json", "w"), indent=1)


if __name__ == "__main__":
    main()
