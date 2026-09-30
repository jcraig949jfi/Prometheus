"""W-X REL5 analysis: FC tables (Wilson 99%) for H2/H0/ZW, degeneracy counters, PLAN s4 decision (frozen rule).
Usage: python analyze5.py  -> out/analysis.txt, out/analysis.json"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import degen as dg  # noqa: E402
import run5  # noqa: E402

FC_MAX = 0.01
AB = {"FLIP_REL": "F", "NO_EFFECT_REL": "N", "CHANCE_REL": "C"}

R, cpu = {}, 0.0
for f in sorted((HERE / "out").glob("fc_w*.json")):
    r = json.load(open(f))
    cpu += r.pop("_cpu_s_total", 0.0)
    R.update(r)
missing = [run5.key(pt) for pt in run5.POINTS if run5.key(pt) not in R]

lines, js = [], {"points": {}, "missing": missing, "cpu_s": cpu}
fails = {c: [] for c in dg.CANDS}
sanity = []
for pt in run5.POINTS:
    k = run5.key(pt)
    if k not in R:
        continue
    v = R[k]
    n = v["n"]
    row = {"n": n, "stage2": v["stage2"], "fc": {}, "deg": v["deg"]}
    for c in dg.CANDS:
        row["fc"][c] = {}
        for vv in dg.VS:
            x = v["k"][c][vv]
            lo, hi = dg.wilson(x, n)
            row["fc"][c][vv] = [x, x / n, lo, hi]
            if x / n > FC_MAX:
                fails[c].append((k, vv, x / n))
    for vv in dg.VS:
        if v["k"]["H0"][vv] > v["k"]["H2"][vv]:
            sanity.append((k, vv, v["k"]["H0"][vv], v["k"]["H2"][vv]))
    js["points"][k] = row

hdr = f"{'point':22s} {'n':>6s}  " + "  ".join(f"{c}:F N C (% [W99])".ljust(64) for c in dg.CANDS)
for c in dg.CANDS:
    lines.append(f"\n== {c} FC per point, %, [Wilson 99%] (F=FLIP@z-1/2, N=NO_EFFECT@z+1/2, C=CHANCE max) ==")
    for k, row in js["points"].items():
        cells = "  ".join(f"{AB[vv]} {row['fc'][c][vv][1]*100:.2f} [{row['fc'][c][vv][2]*100:.2f},"
                          f"{row['fc'][c][vv][3]*100:.2f}]" for vv in dg.VS)
        lines.append(f"{k:22s} n={row['n']:6d}{'*' if row['stage2'] else ' '} {cells}")
lines.append("\n== degeneracy (grid data): per truth z: mean sd*=0 share | datasets any | datasets >=0.5% | "
             "H2!=H0 | ZW!=H0 ==")
for k, row in js["points"].items():
    s = "   ".join(f"z{z}: {d['share_sum']/row['n']:.1e} {d['any']} {d['ge_tail']} {d['diff_H2']} {d['diff_ZW']}"
                   for z, d in row["deg"].items())
    lines.append(f"{k:22s} n={row['n']:6d} {s}")

h2_pass = not fails["H2"] and not missing
zw_fails = bool(fails["ZW"])
sanity_ok = not sanity
if missing:
    dec = "INCOMPLETE"
elif not zw_fails:
    dec = "UNINFORMATIVE (ZW control did not fail): do not promote"
elif h2_pass and sanity_ok:
    dec = "PROMOTE H2"
elif not h2_pass:
    dec = "DO NOT PROMOTE H2; promote REL3 (H0) with documented high-accuracy power blind spot"
else:
    dec = "SANITY FAILED (H0 FC > H2 FC somewhere): do not promote; report"
js.update({"fails": fails, "sanity_violations": sanity, "decision": dec})
lines.append(f"\nFC > 1% : H2 {len(fails['H2'])}, H0 {len(fails['H0'])}, ZW {len(fails['ZW'])} point-verdicts")
for c in dg.CANDS:
    for f_ in fails[c]:
        lines.append(f"  {c} {f_[0]} {AB[f_[1]]} {f_[2]*100:.3f}%")
lines.append(f"sanity H0 <= H2 at every point-verdict: {sanity_ok} ({len(sanity)} violations)")
lines.append(f"missing points: {missing}")
lines.append(f"DECISION (PLAN s4): {dec}")
lines.append(f"grid CPU s: {cpu:.0f}")
(HERE / "out" / "analysis.txt").write_text("\n".join(lines) + "\n")
json.dump(js, open(HERE / "out" / "analysis.json", "w"))
print("\n".join(lines[-8 - sum(len(v) for v in fails.values()):]))
