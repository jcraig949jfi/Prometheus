"""Tabulate Task 1 (FLIP_CHANGE on the record) -> out/t1_table.md"""
import json, numpy as np, pathlib
O = pathlib.Path(__file__).parent / "out"
R = []
for c in (0, 1): R += json.load(open(O / f"t1_record_{c}of2.json"))["rows"]
B = {(r["cell"], r["program"]): r for r in json.load(open(O / "t1_balanced.json"))["rows"]}
L = ["| cell | kind | M | rec held | acc [lo99] | same | changed [lo99, hi99] | FLIP_CHANGE | pattern |", "|---|---|---|---|---|---|---|---|---|"]
def pat(r):
    if r["same"] > .8 and r["chg"] < .2: return "TEACHER-COPY (ans=y_prev)"
    if r["chg"] > .6 and r["same"] < .45: return "ANTI-COPY (ans=-y_prev)"
    if r["lo99"] > .5 and r["chg"] <= .55 and r["same"] - r["chg"] > .1: return "COPY-CLASS (overall>.5 from same-cue)"
    if r["lo99"] > .5: return "above chance, symmetric"
    return "chance"
for r in sorted(R, key=lambda r: -r["acc"]):
    L.append(f"| {r['cell'][:8]} | {r['kind'][:3]} | {r['M']} | {r['held_rec']:.3f} | {r['acc']:.3f} [{r['lo99']:.3f}] | {r['same']:.3f} | {r['chg']:.3f} [{r['chg_lo99']:.3f}, {r['chg_hi99']:.3f}] | {'PASS' if r['chg_lo99'] > .55 else 'fail'} | {pat(r)} |")
L += ["", "Controls and balanced accuracy (32 pairs):", "| cell | program | acc [lo99] | same | changed [lo99] | B=(same+chg)/2 [lo99, hi99] | FLIP_CHANGE | B>.75 cert |", "|---|---|---|---|---|---|---|---|"]
for (c, p), r in B.items():
    L.append(f"| {c[:8]} | {p} | {r['acc']:.3f} [{r['lo99']:.3f}] | {r['same']:.3f} | {r['chg']:.3f} [{r['chg_lo99']:.3f}] | {r['bal']:.3f} [{r['bal_lo99']:.3f}, {r['bal_hi99']:.3f}] | {'PASS' if r['chg_lo99'] > .55 else 'fail'} | {'PASS' if r['bal_lo99'] > .75 else 'fail'} |")
a = np.array([r["acc"] for r in R]); s = np.array([r["same"] for r in R]); ch = np.array([r["chg"] for r in R])
ev = np.array([r["kind"] == "evolve" for r in R])
summ = {"n": len(R), "evolve": int(ev.sum()), "transfer": int((~ev).sum()),
        "M64_bit_match": f"{sum(1 for r in R if r['match'])}/{sum(1 for r in R if r['M'] == 64)}",
        "overall_lo99_gt_.5": [r["cell"][:8] for r in R if r["lo99"] > .5],
        "flip_change_pass": [r["cell"][:8] for r in R if r["chg_lo99"] > .55],
        "chg_quantiles_evolve": np.quantile(ch[ev], [0, .1, .25, .5, .75, .9, 1]).round(3).tolist(),
        "same_quantiles_evolve": np.quantile(s[ev], [0, .1, .25, .5, .75, .9, 1]).round(3).tolist(),
        "acc_gt_.5_evolve_mean_same_chg": [round(s[ev & (a > .5)].mean(), 4), round(ch[ev & (a > .5)].mean(), 4), int((ev & (a > .5)).sum())],
        "patterns": {}}
for r in R: summ["patterns"][pat(r)] = summ["patterns"].get(pat(r), 0) + 1
pe = {}
for r in R:
    if r["kind"] == "evolve": pe[pat(r)] = pe.get(pat(r), 0) + 1
summ["patterns_evolve"] = pe
(O / "t1_table.md").write_text("\n".join(L) + "\n\nSummary: " + json.dumps(summ, indent=1) + "\n")
print(json.dumps(summ, indent=1))
