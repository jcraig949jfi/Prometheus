"""B34 -- the deciding comparison for B32: world-distribution elites vs world-SPECIFIC elites on UNFILTERED worlds.

B33 showed B32's held-out contrast was inflated by the held-out filter; on 40 unfiltered family worlds the margin over
ONE specific elite was only +.01-.02. B34 widens both sides:
  DIST     all B32 + B32rep elites (16 seeds)
  SPECIFIC every content-sensing specific elite available: B25 NOCLOCK 2504/2505/2506 (P-boom), B27 B-scatter
           2701/2702/2703, B27 C6-unable 2703
on the SAME 40 unfiltered worlds (family_world(("unfiltered", i)), as B33). Per world: mean DIST lift - mean SPECIFIC
lift; paired sign test across worlds (two-sided, exact binomial).
PREDICTION (before running, after B33): mean paired difference in [-.01, +.03] and sign test p > .05 -- i.e. no
reliable advantage of world-distribution training over specific training on unfiltered family worlds.
"""
import json
from math import comb
from pathlib import Path

from archaeon.beta.b32_world_distribution import family_world, lift

OUT = Path(__file__).resolve().parent / "results"


def sign_test(diffs):
    pos = sum(d > 0 for d in diffs); neg = sum(d < 0 for d in diffs); n = pos + neg
    k = min(pos, neg)
    p = sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n * 2 if n else 1.0
    return pos, neg, min(1.0, p)


def main():
    dist = []
    for f in ("B32_result.json", "B32rep_result.json"):
        d = json.loads((OUT / f).read_text(encoding="utf-8"))
        dist += [r["elite_manifest"] for r in d["rows"] if "elite_manifest" in r]
    b25 = {r["seed"]: r for r in json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"] if r.get("arm") == "NOCLOCK"}
    b27 = json.loads((OUT / "B27_result.json").read_text(encoding="utf-8"))["rows"]
    spec = [b25[s]["elite_manifest"] for s in (2504, 2505, 2506)] + [r["elite_manifest"] for r in b27 if r.get("content_sensing")]
    worlds = [family_world(("unfiltered", i)) for i in range(40)]
    rows, diffs = [], []
    for i, (w, s) in enumerate(worlds):
        dl = [lift(m, w, s) for m in dist]; sl = [lift(m, w, s) for m in spec]
        md, ms = sum(dl) / len(dl), sum(sl) / len(sl)
        diffs.append(md - ms)
        rows.append({"world": i, "R": w.w.R, "features": w.w.features, "dist_mean": round(md, 4), "spec_mean": round(ms, 4)})
    pos, neg, p = sign_test(diffs)
    summ = {"n_dist": len(dist), "n_spec": len(spec), "n_worlds": len(worlds),
            "mean_dist_lift": round(sum(r["dist_mean"] for r in rows) / len(rows), 4),
            "mean_spec_lift": round(sum(r["spec_mean"] for r in rows) / len(rows), 4),
            "mean_paired_diff": round(sum(diffs) / len(diffs), 4), "sign_pos": pos, "sign_neg": neg, "sign_p": round(p, 4)}
    print(json.dumps(summ))
    (OUT / "B34_result.json").write_text(json.dumps({"probe": "B34", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
