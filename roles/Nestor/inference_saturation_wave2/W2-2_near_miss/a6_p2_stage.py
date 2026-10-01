"""W2-2 a6: P2 implanted panels (X-P2-BRIDGE, X-P2-REGSTATE, C-ZERO-SPECIFIC): is time-to-first-copy (S1 epoch) an
early-warning observable for S5, and do S2 (first certified founder birth) / founder_ages add anything? Read-only.
Also W1 X-DD-ESTABLISH: founder-lineage births vs early live-L. python -B a6_p2_stage.py -> a6_p2_stage.json
"""
import json, glob, pathlib
HERE = pathlib.Path(__file__).resolve().parent
P2 = HERE.parents[1] / "campaigns" / "npe-p2-endogenous-heredity-2026-09-27"
W1 = HERE.parents[1] / "campaigns" / "npe-w1-donor-discovery-2026-09-26" / "x_dd_establish" / "results"
out = {}
rows = []
for exp, arm_key in (("x_p2_bridge", "state"), ("x_p2_regstate", "policy"), ("c_zero_specific", "policy")):
    for f in glob.glob(str(P2 / exp / "results" / "*.json")):
        r = json.load(open(f))
        rows.append(dict(exp=exp, arm=r[arm_key], cell=r["cell"], donor=r["donor"], S1=r["S1"], S2=r["S2"], S5=bool(r["S5"]),
                         depth=r["depth"], anc0=r["anc0"], ages=r.get("founder_ages"), births_L=r.get("births_L"), causal_L=r.get("causal_L")))
def scr(pool, pred, name):
    tp = sum(pred(r) and r["S5"] for r in pool); fn = sum((not pred(r)) and r["S5"] for r in pool)
    fp = sum(pred(r) and not r["S5"] for r in pool); tn = sum((not pred(r)) and not r["S5"] for r in pool)
    return dict(name=name, n=len(pool), tp=tp, fn=fn, fp=fp, tn=tn, hit=round(tp / (tp + fn), 3) if tp + fn else None,
                false_alarm=round(fp / (fp + tn), 3) if fp + tn else None)
S = []
for k in (0, 3, 10, 30):
    S.append(scr(rows, lambda r, k=k: r["S1"] is not None and r["S1"] <= k, f"all panels: S1 <= {k}"))
    S.append(scr([r for r in rows if r["S1"] is not None], lambda r, k=k: r["S1"] <= k, f"copied at all: S1 <= {k}"))
for k in (3, 10, 30):
    S.append(scr([r for r in rows if r["S1"] is not None], lambda r, k=k: r["S2"] is not None and r["S2"] <= k, f"copied at all: S2 (certified founder birth) <= {k}"))
out["screens"] = S
# S1 timing among S5 vs not, per experiment
out["S1_by_outcome"] = {}
for exp in ("x_p2_bridge", "x_p2_regstate", "c_zero_specific"):
    for s5 in (True, False):
        v = sorted(r["S1"] for r in rows if r["exp"] == exp and r["S5"] == s5 and r["S1"] is not None)
        out["S1_by_outcome"][f"{exp}_S5={s5}"] = dict(n=len(v), median=v[len(v) // 2] if v else None, max=max(v) if v else None,
                                                     share_le10=round(sum(x <= 10 for x in v) / len(v), 3) if v else None)
# founder_ages (bridge): age distribution of founder copies, S5 vs not
ag = {True: [], False: []}
for r in rows:
    if r["ages"]:
        ag[r["S5"]] += r["ages"]
out["founder_ages"] = {str(k): dict(n=len(v), hist={a: v.count(a) for a in sorted(set(v))}) for k, v in ag.items()}
# W1 establish: founder-lineage births histogram and early live-L
W = [json.load(open(f)) for f in glob.glob(str(W1 / "*.json"))]
out["w1_lineage_births_sorted"] = sorted(r["lineage_births"] for r in W)
big = lambda r: r["lineage_births"] >= 100
first = lambda r: r["checks"][0][1] if r["checks"] else 0
W = [r for r in W if r["status"] != "NO_D0"]
out["w1_screens"] = []
for k in (5, 10, 20):
    tp = sum(first(r) >= k and big(r) for r in W); fn = sum(first(r) < k and big(r) for r in W)
    fp = sum(first(r) >= k and not big(r) for r in W); tn = sum(first(r) < k and not big(r) for r in W)
    out["w1_screens"].append(dict(name=f"live L at first 20-epoch check >= {k} -> founder lineage >= 100 births", tp=tp, fn=fn, fp=fp, tn=tn))
out["w1_comp_collapse_in_takeovers"] = [(r["cell"], r["seed"], r["lineage_births"], max(c[2] for c in r["checks"]), sum(c[2] == 0 for c in r["checks"]), len(r["checks"]))
                                        for r in W if big(r)]
json.dump(out, open(HERE / "a6_p2_stage.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "founder_ages"}, indent=0)[:5000]); print(out["founder_ages"])
