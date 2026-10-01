"""PLAN s5: apply the frozen REL2 rule to W-O's 733 re-run verdicts (saved data only).
Inputs: W-O out/rerun_table.csv (rel = W-N certificate at M=512, n512 = normal CI, K);
P = 256 for every arm (checked in LOG A0/A6 against rerun_s*.jsonl).
Writes out/rel2_table.csv, out/apply_summary.json; prints transition tables."""
import collections
import csv
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import swap_rel2 as s2  # noqa: E402

TAB = s2.load_table()
WO = HERE.parent / "W-O" / "out"
rows = list(csv.DictReader(open(WO / "rerun_table.csv")))
assert len(rows) == 733
P = 256
out = []
for r in rows:
    n = json.loads(r["n512"])
    s = json.loads(r["s512"])
    K = int(r["K"])
    lab = s2.label(r["rel"], n[1], P, K, dz=TAB[f"P{P}_K{K}"])
    y = {k: r[k] for k in ("vid", "source", "specimen", "family", "arm", "timing", "offset", "single", "rel",
                           "rel_gated", "K", "z", "census", "fS")}
    y.update(n_m=n[0], n_lo=n[1], n_hi=n[2], s_m=s[0], s_lo=s[1], s_hi=s[2], one_minus_n=1 - n[0],
             rel2=lab["label"], rel2_strict=lab["strict"], NE="|".join(lab["NE"]),
             p_min_F=lab["p_min"]["FLIP_REL"], p_min_N=lab["p_min"]["NO_EFFECT_REL"],
             p_min_C=lab["p_min"]["CHANCE_REL"])
    out.append(y)
with open(HERE / "out" / "rel2_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)

ORDER = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL", "INDETERMINATE", "NOT_ELIGIBLE")


def wilson(k, n, z=2.5758):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def cluster_ci(sub, cls, key="rel2", B=2000, seed=0):
    spec = sorted({r["specimen"] for r in sub})
    by = {s: [r for r in sub if r["specimen"] == s] for s in spec}
    k = np.array([sum(r[key] == cls for r in by[s]) for s in spec], float)
    n = np.array([len(by[s]) for s in spec], float)
    idx = np.random.default_rng(seed).integers(0, len(spec), (B, len(spec)))
    ps = k[idx].sum(1) / n[idx].sum(1)
    return (round(float(np.quantile(ps, .005)), 3), round(float(np.quantile(ps, .995)), 3))


def matrix(sub, rowkey, colkey="rel2"):
    c = collections.Counter((r[rowkey], r[colkey]) for r in sub)
    rk = sorted({r[rowkey] for r in sub})
    return {a: {b: c[(a, b)] for b in ORDER if c[(a, b)]} for a in rk}


S = {"n": len(out)}
S["marginal_rel2"] = {v: {"k": sum(r["rel2"] == v for r in out),
                          "wilson99": wilson(sum(r["rel2"] == v for r in out), len(out)),
                          "cluster99": cluster_ci(out, v)} for v in ORDER}
S["marginal_strict"] = {v: sum(r["rel2_strict"] == v for r in out) for v in ORDER}
S["abs_x_rel2"] = matrix(out, "single")
S["wn_gated_x_rel2"] = matrix(out, "rel_gated")
S["wn_ungated_x_rel2"] = matrix(out, "rel")
S["wn_gated_x_strict"] = matrix(out, "rel_gated", "rel2_strict")
S["abs_x_strict"] = matrix(out, "single", "rel2_strict")
S["NE_patterns"] = dict(collections.Counter((r["rel2"], r["NE"]) for r in out))
S["NE_patterns"] = {f"{a} [NE:{b}]": n for (a, b), n in sorted(S["NE_patterns"].items())}
ch = [r for r in out if r["single"] == "CHANCE"]
S["absCHANCE_x_rel2"] = {v: {"k": sum(r["rel2"] == v for r in ch), "wilson99": wilson(sum(r["rel2"] == v for r in ch), len(ch)),
                             "cluster99": cluster_ci(ch, v)} for v in ORDER}
S["absCHANCE_n"] = len(ch)
the42 = [r for r in out if r["single"] == "CHANCE" and r["rel_gated"] == "FLIP_REL"]
the53 = [r for r in out if r["single"] == "CHANCE" and r["rel"] == "FLIP_REL" and r["rel_gated"] == "NOT_ELIGIBLE"]
S["n42"] = len(the42)
S["the42_rel2"] = dict(collections.Counter(r["rel2"] for r in the42))
S["the42_strict"] = dict(collections.Counter(r["rel2_strict"] for r in the42))
S["the53_rel2"] = dict(collections.Counter(r["rel2"] for r in the53))
S["the53_strict"] = dict(collections.Counter(r["rel2_strict"] for r in the53))
for name, grp in (("the42", the42), ("the53", the53)):
    S[f"{name}_by_family"] = dict(collections.Counter(r["family"] for r in grp))
    S[f"{name}_by_arm"] = dict(collections.Counter(r["arm"] for r in grp))
    S[f"{name}_by_source"] = dict(collections.Counter(r["source"] for r in grp))
    S[f"{name}_specimens"] = dict(collections.Counter(r["specimen"] for r in grp))
    S[f"{name}_n_lo_range"] = (min(r["n_lo"] for r in grp), max(r["n_lo"] for r in grp)) if grp else None
    S[f"{name}_z_range"] = (min(float(r["z"]) for r in grp), max(float(r["z"]) for r in grp)) if grp else None
json.dump(S, open(HERE / "out" / "apply_summary.json", "w"), indent=1)
for k, v in S.items():
    print(k, json.dumps(v))
print("\nTHE 42 (abs CHANCE, W-N gated FLIP_REL):")
for r in sorted(the42, key=lambda r: (r["specimen"], r["source"], r["arm"], int(r["offset"]))):
    print(f"{r['vid']} {r['source']} {r['specimen'][:8]} {r['family']:5s} {r['arm']:15s} {r['timing'] or '-':5s} "
          f"o{r['offset']:>3s} K{r['K']} n={r['n_m']:.3f}[{r['n_lo']:.3f},{r['n_hi']:.3f}] "
          f"s={r['s_m']:.3f}[{r['s_lo']:.3f},{r['s_hi']:.3f}] 1-n={r['one_minus_n']:.3f} z={float(r['z']):+.2f} "
          f"census={r['census']:15s} REL2={r['rel2']} strict={r['rel2_strict']}")
print("\nTHE 53 (abs CHANCE, ungated FLIP_REL, W-N gated NOT_ELIGIBLE):")
for r in sorted(the53, key=lambda r: (r["specimen"], r["source"], r["arm"], int(r["offset"]))):
    print(f"{r['vid']} {r['source']} {r['specimen'][:8]} {r['family']:5s} {r['arm']:15s} {r['timing'] or '-':5s} "
          f"o{r['offset']:>3s} K{r['K']} n={r['n_m']:.3f}[{r['n_lo']:.3f}] s={r['s_m']:.3f}[{r['s_lo']:.3f},{r['s_hi']:.3f}] "
          f"z={float(r['z']):+.2f} REL2={r['rel2']} strict={r['rel2_strict']}")
