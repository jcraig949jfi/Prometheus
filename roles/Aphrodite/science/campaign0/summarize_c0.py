"""Campaign 0 verdict from rows (PREREG_C0 sections 4-7). TIER 2. Reads ledgers/c0_rows.jsonl only."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from assay import PLANTED  # noqa: E402

L_DIR = HERE / ("ledgers_quick" if "--quick" in sys.argv else "ledgers")


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    rows = [json.loads(x) for x in (L_DIR / "c0_rows.jsonl").read_text(encoding="utf-8").splitlines() if x]
    g = defaultdict(list)
    for r in rows:
        g[(r["tag"], r["world"], r["L"], r["analysis"])].append(r)
    out = {"per_world": {}, "mde": {}, "sensitivity": {}, "misspecified": {}}

    def stats(rs, wk):
        n = len(rs)
        rec = sum(r["recovered"] for r in rs)
        planted = PLANTED[wk]
        amb = sum(r["ambiguous"] for r in rs)
        fp = sum(bool(set(r["flags"]) - planted) for r in rs)
        fn = sum(bool(planted - set(r["flags"])) for r in rs)
        lo, hi = wilson(rec, n)
        return {"n": n, "recovery": rec / n, "wilson": [round(lo, 4), round(hi, 4)],
                "reliable": (rec / n >= 0.90 and lo >= 0.85), "ambiguous": amb / n,
                "false_positive_flag_rate": fp / n, "false_negative_flag_rate": fn / n,
                "fp_wilson_upper": round(wilson(fp, n)[1], 4)}

    worlds = sorted({r["world"] for r in rows if r["tag"] == "main"})
    Ls = sorted({r["L"] for r in rows})
    for wk in worlds:
        out["per_world"][wk] = {str(L): stats(g[("main", wk, L, "primary")], wk) for L in Ls}
        rel = [L for L in Ls if out["per_world"][wk][str(L)]["reliable"]]
        out["per_world"][wk]["smallest_reliable_L"] = min(rel) if rel else None
        for an in ("boot", "delta0.02", "delta0.05", "noholm", "pseudo"):
            out["sensitivity"].setdefault(an, {})[wk] = {
                str(L): round(stats(g[("main", wk, L, an)], wk)["recovery"], 4) for L in Ls}
        out["misspecified"][wk] = {str(L): stats(g[("mis", wk, L, "primary")], wk) for L in Ls}
    for s in sorted({r["world"] for r in rows if r["tag"] == "mde"}, key=float):
        out["mde"][s] = {str(L): round(sum(r["recovered"] for r in g[("mde", s, L, "primary")])
                                        / max(1, len(g[("mde", s, L, "primary")])), 4) for L in Ls}
    mde = {}
    for L in Ls:
        ok = [float(s) for s in out["mde"] if float(s) > 0 and out["mde"][s][str(L)] >= 0.80]
        mde[str(L)] = min(ok) if ok else None
    out["mde_logit_by_L"] = mde
    b0 = 0.35
    out["mde_points_by_L"] = {L: (None if v is None else round(1 / (1 + math.exp(-(math.log(b0 / (1 - b0)) + v))) - b0, 4))
                              for L, v in mde.items()}
    null_ok = all(out["per_world"][wk][str(L)]["fp_wilson_upper"] <= 0.10 for wk in ("W6", "W9") for L in Ls)
    all_rel = all(out["per_world"][wk]["smallest_reliable_L"] is not None for wk in worlds)
    fragile = {}
    for an in ("boot", "delta0.02", "delta0.05", "noholm"):
        for wk in worlds:
            for L in Ls:
                d = abs(out["sensitivity"][an][wk][str(L)] - out["per_world"][wk][str(L)]["recovery"])
                if d > 0.10:
                    fragile.setdefault(wk, []).append(f"{an}@L{L}: {d:+.3f}")
    out["fragile"] = fragile
    out["PASS"] = bool(null_ok and all_rel)
    out["pass_parts"] = {"every_world_reliable_at_some_L": all_rel, "null_fp_upper_le_0.10_every_L_W6_W9": null_ok}
    (L_DIR / "C0_VERDICT.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    for wk in worlds:
        pw = out["per_world"][wk]
        print(wk, " ".join(f"L{L}:{pw[str(L)]['recovery']:.3f}{'*' if pw[str(L)]['reliable'] else ''}"
                           f"(amb {pw[str(L)]['ambiguous']:.2f},fp {pw[str(L)]['false_positive_flag_rate']:.2f})"
                           for L in Ls), "min_L", pw["smallest_reliable_L"])
    print("MDE logit", mde, "points", out["mde_points_by_L"])
    print("PASS", out["PASS"], out["pass_parts"])
    print("fragile", fragile)


if __name__ == "__main__":
    main()
