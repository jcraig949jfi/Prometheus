"""Tables for L4 (reads L4_rows.json only)."""
import json, statistics as S
from collections import Counter
d = json.load(open("L4_rows.json")); rows = d["rows"]
lab = [r for r in rows if r["labelled"]]; unl = [r for r in rows if not r["labelled"]]
def q(xs):
    xs = sorted(xs); n = len(xs)
    return "n=%d min %.3f q1 %.3f med %.3f q3 %.3f max %.3f" % (n, xs[0], xs[n//4], S.median(xs), xs[(3*n)//4], xs[-1]) if xs else "n=0"
print("== P1 ruler reproducibility")
mm = [r for r in rows if r["structural"]["ruler_class_now"] != r["then"]["founder_class"]]
print("class mismatches: %d / %d" % (len(mm), len(rows)))
for r in mm[:10]: print("  ", r["id"], r["then"]["founder_class"], "->", r["structural"]["ruler_class_now"])
ex_mm = [r for r in lab if sorted(r["causal"]["exact_inputs_zero"]) != sorted(r["then"]["founder_exact_inputs"])[:16]]
print("exact-input-set mismatches (labelled, first 16 compared): %d / %d" % (len(ex_mm), len(lab)))
for r in ex_mm[:5]: print("  ", r["id"], r["then"]["founder_exact_inputs"][:10], r["causal"]["exact_inputs_zero"][:10])
print("\n== P2 verdicts"); print(d["summary"]["by"] if "by" in d["summary"] else d["summary_by_class"]["by"])
print("\n== P3 mechanism (labelled)")
print("T:", q([r["causal"]["transmission"] for r in lab]))
print("bits:", q([r["causal"]["bits_transmitted"] for r in lab]))
print("T<0.6:", [(r["id"], r["then"]["founder_class"], r["causal"]["transmission"]) for r in lab if r["causal"]["transmission"] < 0.6])
print("offset k:", Counter(r["causal"]["offset_k"] for r in lab))
print("intervention env:", Counter(r["causal"]["intervention_env"] for r in lab))
print("behaviour pass rate:", Counter(r["behavioural"]["pass_rate"] for r in lab))
print("\n== P4 heredity share, empty neighbour, uniform inputs")
for cls in ("EXACT_GATED", "NEAR_COPIER"):
    rs = [r for r in lab if r["then"]["founder_class"] == cls]
    print(cls, "heredity_share:", q([r["causal"]["heredity_share_zero"] for r in rs]))
    print(cls, "n_birth_inputs:", q([r["causal"]["n_birth_inputs_zero"] for r in rs]))
    print(cls, "n_copier_inputs:", q([r["causal"]["n_copier_inputs_zero"] for r in rs]))
    print(cls, "n_exact_inputs:", q([r["causal"]["n_exact_inputs_zero"] for r in rs]))
    print(cls, "mean_birth_fid (now, isolation):", q([r["causal"]["mean_birth_fid_zero"] for r in rs]))
    print(cls, "world mean fid (then, births-weighted):", q([r["then"]["world_mean_fid_births_weighted"] for r in rs]))
    print(cls, "world exact share (then):", q([r["then"]["world_exact_births"]/r["then"]["world_births"] for r in rs]))
print("\n== gate width by environment (labelled): median copier-grade inputs per env / share of objects passing")
envs = d["neighbour_names"]
for e in envs:
    w = [r["causal"]["gate_width_by_env"][e] for r in lab]
    z = [r["causal"]["gate_width_by_env"]["zero"] for r in lab]
    print("  %-6s med %5.1f  pass %2d/%d  narrower-than-zero %2d  wider %2d" % (e, S.median(w), sum(x > 0 for x in w), len(w),
          sum(a < b for a, b in zip(w, z)), sum(a > b for a, b in zip(w, z))))
print("\n== P5 unlabelled controls")
print(Counter(r["now"] for r in unl))
for r in unl:
    if r["now"] not in ("UNLABELLED_STRUCTURE_WITHOUT_BEHAVIOUR", "UNLABELLED_LABEL_PROVENANCE_ONLY"):
        print(json.dumps({k: r[k] for k in ("id", "then", "structural", "behavioural", "causal", "now")}, indent=None)[:3000])
