#!/usr/bin/env python
"""E4 -- smoothness is not navigability. Frozen by FREEZE_E4.txt.
Pure analysis of E2's frozen table; no new measurement."""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

e2 = json.loads((HERE/"results"/"e2_arena.json").read_text(encoding="utf-8"))
cells = {f"{c['substrate']}|{c['operator']}": c for c in e2["cells"]}

def sm(c):
    Q = c["Q"]
    return {"SM1_middle_mass": Q["q4_middle_mass"],
            "SM2_magnitude_smoothness": 1.0 - Q["q5_median_nonzero_d"],
            "SM3_band_rate": Q["q3_band_rate"]}

P1 = cells["P1-BLOCKS|SWEEP-ALL"]; N1 = cells["N1-SMOOTH-UNREACHABLE|SWEEP-ALL"]
N2 = cells["N2-HASH|SWEEP-ALL"]
s1, s2 = sm(P1), sm(N1)
c1 = {k: {"P1": s1[k], "N1": s2[k], "abs_diff": round(abs(s1[k]-s2[k]), 6),
          "pass": bool(abs(s1[k]-s2[k]) <= 0.02)} for k in s1}

nv = {"NV1_q10_own_target": {
        "P1_on_T9": P1["per_target"]["T9_P1_TARGET"]["q10_reach_improve_at1"],
        "N1_on_T10": N1["per_target"]["T10_N1_TARGET"]["q10_reach_improve_at1"]},
      "NV2_q11_drift_own_target": {
        "P1_on_T9": P1["per_target"]["T9_P1_TARGET"]["q11_drift"],
        "N1_on_T10": N1["per_target"]["T10_N1_TARGET"]["q11_drift"]}}
for k, v in nv.items():
    a, b = list(v.values())[0], list(v.values())[1]
    v["abs_diff"] = round(abs(a-b), 4); v["separates"] = bool(abs(a-b) >= 0.50)

out = {"experiment": "E4", "freeze": "FREEZE_E4.txt",
       "E4-C1_no_smoothness_stat_separates_P1_N1": {
           "per_statistic": c1, "pass": bool(all(v["pass"] for v in c1.values()))},
       "E4-C2_some_navigability_stat_separates": {
           "per_statistic": nv, "pass": bool(any(v["separates"] for v in nv.values()))},
       "E4-C3_quadrants": {
           "smooth_navigable": ["P1-BLOCKS (designed)"],
           "smooth_non_navigable": ["N1-SMOOTH-UNREACHABLE (designed)"],
           "discontinuous_non_navigable": ["N2-HASH (designed)"],
           "discontinuous_navigable": "EMPTY AT E4 -- empirical cell, candidates CIRCUIT and DNF, filled only by E5 search outcomes",
           "designed_smoothness_values": {"P1": s1, "N1": s2, "N2": sm(N2)}}}
out["pass"] = bool(out["E4-C1_no_smoothness_stat_separates_P1_N1"]["pass"]
                   and out["E4-C2_some_navigability_stat_separates"]["pass"])
out["verdict"] = ("SMOOTHNESS_IS_NOT_NAVIGABILITY" if out["pass"]
                  else "E4_KILL_CONTROL_PAIR_NOT_IDENTICAL")
(HERE/"results"/"e4_smoothness.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("--- E4-C1: does any smoothness statistic separate P1 from N1? ---")
for k, v in c1.items():
    print(f"  {k:26s} P1={v['P1']:.4f} N1={v['N1']:.4f} |diff|={v['abs_diff']:.6f} "
          f"{'blind (PASS)' if v['pass'] else 'SEPARATES (KILL)'}")
print("--- E4-C2: does a navigability statistic separate them? ---")
for k, v in nv.items():
    print(f"  {k:26s} diff={v['abs_diff']:.4f} {'SEPARATES' if v['separates'] else 'blind'}")
print(f"\nVERDICT: {out['verdict']}")
