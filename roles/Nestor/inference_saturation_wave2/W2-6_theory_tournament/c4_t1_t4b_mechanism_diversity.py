"""W2-6 check C4 (T1/T3 vs T4(b)): do state-free genomes from INDEPENDENT runs converge on one address-sourcing mechanism
(T4(b): a shared mechanism transmitted as a unit) or on diverse constant-loading solutions (T1/T3 convergence)?

Read-only over ../../inference_harvest_2026-09-30/forensics/core_map.json (FOR panel; no VM calls).
Mechanism class of a genome = (copy op, passing side, how E/DE is sourced, how L/HL is sourced), read from FOR's dynamic
backward slice of the copy operands (slice_instr) and trace:
  E source: '11' (LD DE,nn) | '1E' (LD E,n) | 'REG' (neither immediate in the slice: register-derived chain)
  L source: '21' (LD HL,nn) | '2E' (LD L,n) | 'REG'
Independent origins = distinct origin runs (each run's genomes counted once, by its modal class); the 8 epoch-700
16000006 genomes form one run. E4's frozen kill uses ">= 3 distinct classes across >= 6 origins in different runs" as its
first conjunct (the second conjunct, transmission as a unit, needs CVT-R and is NOT tested here).
Output: c4_t1_t4b_mechanism_diversity.json
"""
import collections
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
rows = json.load(open(FOR / "core_map.json"))["rows"]


def cls(r):
    si = set(r.get("slice", {}).get("slice_instr", []))
    e = "11" if "11" in si else "1E" if "1E" in si else "REG"
    l = "21" if "21" in si else "2E" if "2E" in si else "REG"
    t = r.get("trace", {})
    return (t.get("copy_op"), t.get("side"), e, l)


out = {}
for lab, sel in (("SF", lambda r: r.get("state_free") and r["vm"] == "DENSE"),
                 ("SD", lambda r: r.get("competent") and not r.get("state_free") and r["vm"] == "DENSE")):
    g = [r for r in rows if sel(r)]
    byrun = collections.defaultdict(list)
    for r in g:
        run = "16000006_e700" if r["src"] != "corpus" else r["origin_run"] + "|" + r["cell"]
        byrun[run].append(cls(r))
    modal = {k: collections.Counter(v).most_common(1)[0][0] for k, v in byrun.items()}
    cc = collections.Counter(modal.values())
    top_share = cc.most_common(1)[0][1] / len(modal)
    # Simpson diversity (prob. two random independent runs share a class)
    n = len(modal)
    share_prob = sum(c * (c - 1) for c in cc.values()) / (n * (n - 1)) if n > 1 else None
    out[lab] = {"genomes": len(g), "independent_runs": n, "distinct_classes": len(cc),
                "class_counts_by_run": {"|".join(map(str, k)): v for k, v in cc.most_common()},
                "modal_class_share": round(top_share, 3), "P_two_runs_share_class": round(share_prob, 3),
                "E_source_by_run": dict(collections.Counter(k[2] for k in modal.values())),
                "L_source_by_run": dict(collections.Counter(k[3] for k in modal.values())),
                "copy_op_by_run": dict(collections.Counter(k[0] for k in modal.values())),
                "side_by_run": dict(collections.Counter(k[1] for k in modal.values()))}
out["E4_first_conjunct_met_for_SF"] = out["SF"]["distinct_classes"] >= 3 and out["SF"]["independent_runs"] >= 6
(HERE / "c4_t1_t4b_mechanism_diversity.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
