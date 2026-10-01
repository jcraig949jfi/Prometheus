"""W2-27: re-derive W2-8 D10 from committed C-A3-INTERNALIZE and X-MAT-INTERNALIZE records. Read-only."""
import json, pathlib, math
from fractions import Fraction
HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[1] / "campaigns"
CI = CAMP / "npe-arc3-2026-09-28" / "c_a3_internalize" / "results"
XM = CAMP / "npe-frontier-2026-09-30" / "x_mat_internalize" / "results"

def fisher_2x2(a, b, c, d):
    """two-sided Fisher exact (sum of probs <= p_obs), rows=cells, cols=event/non-event"""
    n1, n2, k = a + b, c + d, a + c
    N = n1 + n2
    def p(x): return math.comb(n1, x) * math.comb(n2, k - x) / math.comb(N, k)
    po = p(a)
    lo, hi = max(0, k - n2), min(k, n1)
    return sum(p(x) for x in range(lo, hi + 1) if p(x) <= po * (1 + 1e-9))

def cond(c):
    return c["free"] > 0 and c["free_in_L"] >= 0.8 * c["free"] and c["L_share"] >= 0.5

recs = {p.stem: json.loads(p.read_text()) for p in sorted(CI.glob("*.json"))}
allL = set(); endL = set(); n_cp = 0
rows = []
for k, r in recs.items():
    cps = r["checkpoints"]; n_cp += len(cps)
    allL |= {c["L_share"] for c in cps}
    d0_not = bool(r["d0_free"]) and not any(r["d0_free"])
    if not d0_not: continue
    last = next((c for c in reversed(cps) if c["free"] > 0), None)
    if last is None: continue
    endL.add(last["L_share"])
    fin = cps[-1]
    a = cond(last)
    b = cond(fin)                                   # final checkpoint (== last-with-free iff fin.free>0)
    first = next((i for i, c in enumerate(cps) if cond(c)), None)
    if first is None:
        cmaj = False; frac = None; ever = False; consec = False; Lfix = False
    else:
        tail = cps[first:]
        nh = sum(cond(c) for c in tail)
        frac = Fraction(nh, len(tail)); cmaj = nh * 2 > len(tail); ever = True
        consec = any(cond(cps[i]) and cond(cps[i + 1]) for i in range(len(cps) - 1))
        Lfix = all(c["L_share"] >= 0.5 for c in tail)       # L keeps >=50% from first crossing to the end
    # W2-8's own "majority": final free>0, final L>=0.5, free >= 0.5*competent at final
    w28maj = a and fin["free"] > 0 and fin["L_share"] >= 0.5 and fin["free"] >= 0.5 * fin["competent"]
    # red-team-sensible: condition at final OR (L still >=50% at final and free present in >=1 of last 3 cps)
    last3 = cps[-3:]
    d_recent = a and fin["L_share"] >= 0.5 and any(c["free"] > 0 for c in last3)
    rows.append(dict(run=k, cell=r["cell"], seed=r["seed"], n_cp=len(cps), last_free_epoch=last["epoch"],
        L_at_last=last["L_share"], free_last=last["free"], fil_last=last["free_in_L"],
        final_epoch=fin["epoch"], final_L=fin["L_share"], final_free=fin["free"], final_comp=fin["competent"],
        a=a, b=b, c_frac=str(frac) if frac is not None else None, c=cmaj, ever=ever, consec2=consec,
        Lhold=Lfix, w28maj=w28maj, d_recent=d_recent,
        clause_equiv=(last["free_in_L"] == last["free"]) == (last["L_share"] >= 0.5),
        traj=[(c["epoch"], c["L_share"], c["competent"], c["free"], c["free_in_L"]) for c in cps]))

def count(key):
    ev = [x for x in rows if x[key]]
    f = sum(x["cell"] == "ffa6" for x in ev); s = sum(x["cell"] == "7ae3" for x in ev)
    return dict(n=len(ev), ffa6=f, s7ae3=s, fisher_p=round(fisher_2x2(f, 72 - f, s, 72 - s), 4),
                runs=[x["run"] for x in ev])

readings = {"a_as_coded": "a", "b_final_checkpoint": "b", "c_majority_after_first_crossing": "c",
            "c2_W2-8_majority_free>=half_competent_at_final": "w28maj", "d1_ever_any_checkpoint": "ever",
            "d2_two_consecutive_checkpoints": "consec2", "d3_a_and_L>=0.5_held_from_first_crossing_to_end": None,
            "d4_a_and_final_L>=0.5_and_free_in_last3": "d_recent"}
for x in rows: x["d3"] = x["a"] and x["Lhold"]
readings["d3_a_and_L>=0.5_held_from_first_crossing_to_end"] = "d3"
out = {"n_files": len(recs), "n_checkpoints": n_cp, "distinct_L_all_checkpoints": len(allL),
       "eligible_runs": len(rows), "distinct_L_at_endpoint_eligible": sorted(endL),
       "clause_equiv_all_eligible": all(x["clause_equiv"] for x in rows),
       "clause_equiv_failures": [x["run"] for x in rows if not x["clause_equiv"]],
       "readings": {k: count(v) for k, v in readings.items()}, "rows": rows}

# 27000053 (red-team example)
r53 = recs.get("ffa6_27000053")
out["ffa6_27000053"] = {"d0_free": r53["d0_free"], "max_free": max(c["free"] for c in r53["checkpoints"]),
                        "L": [c["L_share"] for c in r53["checkpoints"]]}
# runs with intermediate L at any checkpoint among those ever reaching L>=0.5
reach = [k for k, r in recs.items() if any(c["L_share"] >= 0.5 for c in r["checkpoints"])]
inter = [k for k in reach if any(0 < c["L_share"] < 1 and abs(c["L_share"] - 0.6641) > 1e-4 for c in recs[k]["checkpoints"])]
out["runs_reaching_L50"] = len(reach); out["of_which_intermediate_L"] = len(inter)

# X-MAT: X over free_L at every checkpoint with free_L orgs
xm = {}
for p in sorted(XM.glob("*.json")):
    r = json.loads(p.read_text())
    ser = []
    for t in r["tags"]:
        n = t["free_L"]; att = n["ENDO"] + n["XENO"]
        if n["orgs"] > 0:
            ser.append(dict(epoch=t["epoch"], orgs=n["orgs"], X=round(n["XENO"] / att, 4) if att else None,
                            att=round(att / n["bytes"], 3), MUT=round(n["MUT"] / n["bytes"], 3)))
    fin = r["record"]["checkpoints"][-1]
    xm[p.stem] = dict(replay_identical=r["replay_identical"], record_matches_ci=r["record"] == recs[p.stem],
                      series=ser, final_epoch=fin["epoch"], final_free_L_orgs=r["tags"][-1]["free_L"]["orgs"])
out["xmat"] = xm
(HERE / "rederive.json").write_text(json.dumps(out, indent=1))
for k, v in out.items():
    if k not in ("rows", "xmat", "readings"): print(k, v)
for k, v in out["readings"].items(): print(k, v)
