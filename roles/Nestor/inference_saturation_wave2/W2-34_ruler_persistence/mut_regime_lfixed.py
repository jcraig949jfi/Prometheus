"""W2-34 sensitivity for mut_regime.py: restrict both reference classes to L-fixed intervals (L_share == 1.0 at the start),
the regime run 52 is in after 1100, and widen the level window to 0.35-0.72. Reads mut_regime.json. python -B mut_regime_lfixed.py"""
import json, pathlib, statistics as st
HERE = pathlib.Path(__file__).resolve().parent
d = json.loads((HERE / "mut_regime.json").read_text())
rows = [x for x in d["all_rows"] if x["run"] != 27000052 and x["L0"] == 1.0 and 0.35 <= x["m0"] <= 0.72]
out = {}
for k in ("BLANK", "COMP", "MIXED"):
    xs = [x for x in rows if x["cls"] == k]
    out[k] = {"n": len(xs), "runs": sorted({x["run"] for x in xs}),
              "mean_dm": round(st.mean(x["dm"] for x in xs), 4) if xs else None,
              "max_dm": max((x["dm"] for x in xs), default=None),
              "frac_dm_ge_0.023": round(sum(x["dm"] >= 0.0232 for x in xs) / len(xs), 3) if xs else None}
out["r52_post_dm"] = [x["dm"] for x in d["r52_post_1600"]["intervals"]]
(HERE / "mut_regime_lfixed.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
# 4-interval consecutive blocks within L-fixed COMP runs (any level >= 0.35), against run 52's post-1600 mean
allr = [x for x in d["all_rows"] if x["run"] != 27000052 and x["L0"] == 1.0 and x["cls"] == "COMP"]
by = {}
for x in sorted(allr, key=lambda x: (x["run"], x["t0"])):
    by.setdefault(x["run"], []).append(x)
blocks = [v[i:i + 4] for v in by.values() for i in range(len(v) - 3) if v[i + 3]["t0"] - v[i]["t0"] == 300]
ms = sorted(st.mean(x["dm"] for x in bk) for bk in blocks)
pm = st.mean(out["r52_post_dm"])
out["Lfixed_COMP_blocks_any_level"] = {"runs": sorted(by), "n_blocks": len(ms), "max_block_mean": round(ms[-1], 4),
                                       "P(block_mean >= r52_post)": round(sum(m >= pm for m in ms) / len(ms), 3)}
(HERE / "mut_regime_lfixed.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out["Lfixed_COMP_blocks_any_level"], indent=1))
