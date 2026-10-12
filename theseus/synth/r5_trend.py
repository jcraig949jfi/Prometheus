"""R5-by-generation statistics for ecology runs (THESEUS-28 / -27 frozen definitions).

rho  = Spearman(generation, R5) over viable DEEP + VERY_DEEP children
medD = median R5 of those children
Bootstrap (1000) CIs; for a pair of runs, CIs of the differences (OFF/ALT minus ON/BASE).
"""
import json
import sys

import numpy as np

from . import battery as bt

DEEP = ("DEEP", "VERY_DEEP")


def r5(fp):
    r = np.asarray(fp)[bt.N_DESC:]
    return float(((r > 0.05) & (r < 0.9)).mean())


def rows_for(tag):
    fps = {}
    for l in open(f"theseus/fingerprints/{tag}.jsonl", encoding="utf-8"):
        x = json.loads(l)
        fps[x["id"]] = x["fp"]
    out = []
    for l in open(f"theseus/entities/{tag}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("kind") == "mechanism" and e.get("lane") in DEEP and e.get("viable") and e["id"] in fps:
            out.append((e["generation"], r5(fps[e["id"]])))
    return np.array(out, float)


def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def stats(a, rng, n=1000):
    rho = spearman(a[:, 0], a[:, 1])
    med = float(np.median(a[:, 1]))
    br, bm = [], []
    for _ in range(n):
        s = a[rng.integers(len(a), size=len(a))]
        br.append(spearman(s[:, 0], s[:, 1]))
        bm.append(float(np.median(s[:, 1])))
    return {"n": len(a), "rho": rho, "rho_ci95": [float(np.percentile(br, 2.5)), float(np.percentile(br, 97.5))],
            "medD": med, "medD_ci95": [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
            "max_generation": float(a[:, 0].max()), "_br": br, "_bm": bm}


def compare(base_tag, alt_tag, seed=20261008):
    rng = np.random.default_rng(seed)
    A, B = rows_for(base_tag), rows_for(alt_tag)
    sa, sb = stats(A, rng), stats(B, rng)
    dr = np.array(sb.pop("_br")) - np.array(sa.pop("_br"))
    dm = np.array(sb.pop("_bm")) - np.array(sa.pop("_bm"))
    return {"base": base_tag, "alt": alt_tag, "base_stats": sa, "alt_stats": sb,
            "rho_alt_minus_base": sb["rho"] - sa["rho"],
            "rho_diff_ci95": [float(np.percentile(dr, 2.5)), float(np.percentile(dr, 97.5))],
            "medD_alt_minus_base": sb["medD"] - sa["medD"],
            "medD_diff_ci95": [float(np.percentile(dm, 2.5)), float(np.percentile(dm, 97.5))]}


if __name__ == "__main__":
    out = compare(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3:
        json.dump(out, open(sys.argv[3], "w"), indent=1)
    print(json.dumps(out, indent=1))
