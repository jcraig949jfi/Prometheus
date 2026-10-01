"""W2-37 a1: K1 verdict (R2, Newcombe hybrid score, C-/C+) + descriptive R1, R3; cap-censoring diagnostics. -> a1_analysis.json"""
import json, pathlib
from collections import Counter
from newcombe import newcombe, verdict, wilson
HERE = pathlib.Path(__file__).resolve().parent


def load(tag):
    rows = {}
    for l in open(HERE / ("runs_%s.jsonl" % tag)):
        r = json.loads(l); rows[r["s"]] = r
    ss = sorted(rows)
    k = 0
    while k < len(ss) and ss[k] == 50000 + k:   # contiguous prefix
        k += 1
    return [rows[s] for s in ss[:k]], len(rows)


Fd, nF_all = load("FIELD"); Rd, nR_all = load("FREE")
cap = lambda r: r["stop"] == "free_cap256"


def R2(r, plus):  return (r["maxA"] >= 40 and r["B"] >= 27) or (plus and cap(r))
def R1(r, plus):  return r["Bxk"] >= 27 or (plus and cap(r))
def E(r, plus):   return R1(r, plus)
def S3(r, plus):  return r["Bxk"] >= 163 or (plus and cap(r) and r["Bxk"] >= 27)


def rate(xs):
    x, n = sum(xs), len(xs)
    lo, hi = wilson(x, n) if n else (None, None)
    return {"x": x, "n": n, "p": round(x / n, 4) if n else None, "wilson": [round(lo, 4), round(hi, 4)] if n else None}


def diff(fx, rx):
    x1, n1, x2, n2 = sum(fx), len(fx), sum(rx), len(rx)
    if not n1 or not n2:
        return None
    d, lo, hi = newcombe(x1, n1, x2, n2)
    return {"d": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "hw": round((hi - lo) / 2, 4), "verdict_at_0.05": verdict(lo, hi)}


out = {"n_FIELD": len(Fd), "n_FIELD_file": nF_all, "n_FREE": len(Rd), "n_FREE_file": nR_all,
       "stops": {"FIELD": Counter(r["stop"] for r in Fd), "FREE": Counter(r["stop"] for r in Rd)},
       "cpu_s": {"FIELD": round(sum(r["cpu_s"] for r in Fd), 1), "FREE": round(sum(r["cpu_s"] for r in Rd), 1)}}
k1 = {}
for plus, tag in ((False, "C-"), (True, "C+")):
    f = [R2(r, False) for r in Fd]; g = [R2(r, plus) for r in Rd]
    k1[tag] = {"FIELD": rate(f), "FREE": rate(g), "diff": diff(f, g)}
vs = [k1[t]["diff"]["verdict_at_0.05"] for t in ("C-", "C+")]
k1["K1_VERDICT"] = "PASSED" if all(v == "PASSED" for v in vs) else "KILLED" if all(v == "KILLED" for v in vs) else "UNRESOLVED"
out["K1_R2"] = k1
desc = {}
for plus, tag in ((False, "C-"), (True, "C+")):
    f1 = [R1(r, False) for r in Fd]; g1 = [R1(r, plus) for r in Rd]
    fe = [r for r in Fd if E(r, False)]; ge = [r for r in Rd if E(r, plus)]
    f3 = [S3(r, False) for r in fe]; g3 = [S3(r, plus) for r in ge]
    desc[tag] = {"R1": {"FIELD": rate(f1), "FREE": rate(g1), "diff": diff(f1, g1)},
                 "R3": {"FIELD": rate(f3), "FREE": rate(g3), "diff": diff(f3, g3)}}
out["descriptive"] = desc
# R3 on B (not B_xk) for comparability with W2-22's primary
out["descriptive_R3_on_B_Cminus"] = {"FIELD": rate([r["B"] >= 163 for r in Fd if r["B"] >= 27]),
                                     "FREE": rate([r["B"] >= 163 for r in Rd if r["B"] >= 27])}
caps = [r for r in Rd if cap(r)]
out["cap_diag"] = {"n_cap": len(caps), "cap_B_lt_27": sum(r["B"] < 27 for r in caps),
                   "cap_B_lt_27_values": sorted(r["B"] for r in caps if r["B"] < 27),
                   "cap_epochs": sorted(r["epochs"] for r in caps)}
for tag, D in (("FIELD", Fd), ("FREE", Rd)):
    occ = [r for r in D if r["maxA"] >= 40]
    out.setdefault("flood", {})[tag] = {"maxA_ge_40": len(occ), "of_which_B_lt_27": sum(r["B"] < 27 for r in occ),
                                        "maxA_ge_40_rate": rate([r["maxA"] >= 40 for r in D])}
    out.setdefault("B27_without_maxA40", {})[tag] = sum(r["B"] >= 27 and r["maxA"] < 40 for r in D)
    out.setdefault("kin_share_in_B", {})[tag] = round(sum(r["kin"] for r in D) / max(1, sum(r["B"] for r in D)), 4)
# pooled with W2-22 (consistency only; W2-22 predates freeze)
W = HERE.parent / "W2-22_second_regime"
wf = [json.loads(l) for l in open(W / "runs_FIELD.jsonl")]; wr = [json.loads(l) for l in open(W / "runs_FREE.jsonl")]
wf = [r for r in wf if r.get("mech") is None]
out["W2-22_same_rule_Cminus_Cplus"] = {t: diff([R2(r, False) for r in wf], [R2(r, p) for r in wr]) for t, p in (("C-", False), ("C+", True))}
json.dump(out, open(HERE / "a1_analysis.json", "w"), indent=1, default=dict)
print(json.dumps(out, indent=1, default=dict))
