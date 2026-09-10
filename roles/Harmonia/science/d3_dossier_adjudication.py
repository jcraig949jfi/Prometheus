"""Adjudicate the D3 live dossier: two artifacts in series.  Harmonia 2026-09-10.

v0 (concatenated denominator) -> v1 (pooled-within) -> v1 + detrended.
Run from the repo root:
    python roles/Harmonia/science/d3_dossier_adjudication.py
"""
from __future__ import annotations
import json, math, sys

DOSSIER = "archaeon/docs/h0h5/D3_LIVE_DOSSIER_2026-09-10.json"
LO, HI = 1 / 3.0, 3.0


def seq(r): return int(r["anchors"]["committed_seq"])
def var(v):
    m = sum(v) / len(v)
    return sum((x - m) ** 2 for x in v) / (len(v) - 1)


def pearson(x, y):
    n = len(x); mx = sum(x) / n; my = sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def detrended_var(R):
    """Residual variance after removing a linear trend in commit order.
    A trajectory is not a sample: within-region variance conflates dispersion
    with drift, and D3's null assumes exchangeable rows."""
    x = [seq(r) for r in R]; y = [r["metric"] for r in R]; n = len(x)
    mx = sum(x) / n; my = sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0 or n <= 2:
        return var(y)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    res = [c - (my + b * (a - mx)) for a, c in zip(x, y)]
    return sum(r * r for r in res) / (n - 2)


def main():
    d = json.load(open(DOSSIER, encoding="utf-8"))
    print("d3.v0 %s ; d3.v1 %s ; eligible %s"
          % (d["v0"]["fires"], d["v1"]["fires"], d["v0"]["eligible"]))

    fires = {f["region"]: f for f in d["upper_fires_v0"] + d["fires_v0"]
             if f.get("v1_fires")}
    surv = 0
    print("\nregion                dir     v1 ratio   detrended   survives?")
    for reg, f in sorted(fires.items()):
        R = f["region_rows"]
        nbs = [n for n in f["neighbours"] if n.get("rows")]
        if not nbs:
            continue
        den = sum(len(n["rows"]) - 2 for n in nbs)
        if den <= 0:
            continue
        vnb = sum((len(n["rows"]) - 2) * detrended_var(n["rows"]) for n in nbs) / den
        if vnb <= 0:
            continue
        ratio = detrended_var(R) / vnb
        hit = ratio < LO or ratio > HI
        surv += hit
        print("%-20s %-6s %8.4f   %9.4f   %s"
              % (reg[:18], "UPPER" if "HIGHER" in f["direction"] else "lower",
                 f["v1"]["ratio"], ratio, "YES" if hit else "no -- vanishes"))
    print("\n%d of %d v1 fires survive detrending" % (surv, len(fires)))

    seen, rs = set(), []
    for f in d["upper_fires_v0"] + d["fires_v0"]:
        for n_ in f["neighbours"]:
            if n_["region"] not in seen and n_.get("rows") and len(n_["rows"]) >= 8:
                seen.add(n_["region"]); rs.append(n_["rows"])
    r = [abs(pearson([seq(x) for x in R], [x["metric"] for x in R])) for R in rs]
    print("\nEXCHANGEABILITY: %d neighbour regions, mean |r(committed_seq, metric)| "
          "= %.3f" % (len(rs), sum(r) / len(r)))
    print("Both D3 nulls were calibrated on I.I.D. draws. They do not apply here.")


if __name__ == "__main__":
    sys.exit(main())
