"""W4 probe (forensic, analytic, 1 core, seconds). From the frozen A19/C2 artifacts:
(1) how much information a donor trace carries (the only input an endogenous outer loop
may read); (2) how transfer capability splits between the INHERITED library (START) and
the one-generation improver product (SELECTED - START); (3) what a PRISTINE-start donor
produces (the starting point of any imp@k chain).  Runs no search.
Output: w4_probe_trace_budget.json"""
import json, statistics as st, collections
from pathlib import Path
A = Path(__file__).resolve().parents[3] / "engine" / "A19_C2"
D = [json.loads(l) for l in open(A / "A18_DONORS_2026-09-28.jsonl")]
T = [json.loads(l) for l in open(A / "A18_TRANSFER_2026-09-28.jsonl")]
out = {"trace": {}, "transfer_cells_solved": {}, "pristine_donor": {}}
for k in ("classes", "n_derived", "n_composed_candidates"):
    v = [d[k] for d in D]
    out["trace"][k] = {"median": st.median(v), "mean": round(st.mean(v), 2),
                       "zeros": sum(x == 0 for x in v), "n": len(v)}
out["trace"]["observed_families_of_4"] = dict(collections.Counter(len(d["observed_families"]) for d in D))
out["trace"]["menu_size_median"] = st.median(len(d["selection_table"]) for d in D)
out["trace"]["selected_origin"] = dict(collections.Counter(str(d.get("selected_origin")) for d in D))
agg = collections.defaultdict(collections.Counter)
for r in T:
    for c in r["cells"]:
        agg[r["arm"]]["n"] += 1
        for k in ("PRISTINE", "START", "SELECTED"):
            agg[r["arm"]][k] += c[k]["charge"] < 250000
for a, c in agg.items():
    c = dict(c); c["inherited_gain"] = c["START"] - c["PRISTINE"]; c["improver_gain"] = c["SELECTED"] - c["START"]
    out["transfer_cells_solved"][a] = c
P = [d for d in D if d["arm"] == "P"]
out["pristine_donor"] = {"n": len(P), "derived_total": sum(d["n_derived"] for d in P),
                         "selected_non_inherited": sum(d["selected"] != "INHERITED" for d in P),
                         "observed_families": [len(d["observed_families"]) for d in P]}
json.dump(out, open(Path(__file__).with_name("w4_probe_trace_budget.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
