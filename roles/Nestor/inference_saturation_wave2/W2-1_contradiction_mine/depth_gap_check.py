"""W2-1 check F: is the depth gap (no single-founder run ends at depth 22-161, U-N4) a general property, and does
world depth track time-since-acquisition (turnover reading) in spontaneous-acquisition runs?
Read-only over C-A3-INTERNALIZE (144 runs) and X-A3-FAIR (144 runs) results. Spearman via ranks (no scipy needed)."""
import json, pathlib
N = pathlib.Path(__file__).resolve().parents[2] / "campaigns/npe-arc3-2026-09-28"
def ranks(x):
    o = sorted(range(len(x)), key=lambda i: x[i]); r = [0.0] * len(x); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and x[o[j + 1]] == x[o[i]]: j += 1
        for k in range(i, j + 1): r[o[k]] = (i + j) / 2
        i = j + 1
    return r
def spearman(a, b):
    ra, rb = ranks(a), ranks(b); n = len(a); ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb)); va = sum((x - ma) ** 2 for x in ra); vb = sum((y - mb) ** 2 for y in rb)
    return cov / (va * vb) ** 0.5
out = {}
ca3 = [json.loads(p.read_text()) for p in sorted((N / "c_a3_internalize/results").glob("*.json"))]
d = [r["depth"] for r in ca3]
out["C-A3"] = {"n": len(d), "depth>=20": sum(x >= 20 for x in d), "in_gap_22_161": sum(22 <= x <= 161 for x in d),
               "gt161": sum(x > 161 for x in d)}
pairs = [(2000 - r["d0_epoch"], r["depth"]) for r in ca3 if r.get("d0_epoch") is not None and r["depth"] >= 20]
out["C-A3"]["spearman_depth_vs_time_since_D0_runaways"] = (round(spearman([p[0] for p in pairs], [p[1] for p in pairs]), 3), len(pairs))
for w in ("CARRIED", "ZERO", "CONST5A"):
    rows = [json.loads(p.read_text()) for p in sorted((N / "x_a3_fair/results").glob(w + "_*.json"))]
    d = [r["depth"] for r in rows]
    pr = []
    for r in rows:
        f = next((c["epoch"] for c in r["checkpoints"] if c["donors"] > 0), None)
        if f is not None and r["depth"] >= 20:
            pr.append((2000 - f, r["depth"]))
    out["FAIR_" + w] = {"n": len(d), "depth>=20": sum(x >= 20 for x in d), "in_gap_22_161": sum(22 <= x <= 161 for x in d),
                        "gt161": sum(x > 161 for x in d),
                        "spearman_depth_vs_time_since_first_donor_runaways": (round(spearman([p[0] for p in pr], [p[1] for p in pr]), 3) if len(pr) > 2 else None, len(pr))}
for k, v in out.items(): print(k, v)
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
