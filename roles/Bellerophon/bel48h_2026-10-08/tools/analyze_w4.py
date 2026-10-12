"""BEL-48H Window 4 analysis (rules: BEL_48H_PREREG.md s5; committed before W4 runs).

    python3 analyze_w4.py RESULTS.jsonl OUT.json"""
import json
import math
import sys
from collections import Counter, defaultdict

from analyze_w1 import mcnemar_exact
from analyze_w2 import fisher_greater, wilson


def paired(xs, ys):
    """amendment 2: arms sharing a seed are paired; exact McNemar on seed-pairs (x only, y only)."""
    a = {r["seed"]: r["comp"]["comp_func_alive"] > 0 for r in xs}; b = {r["seed"]: r["comp"]["comp_func_alive"] > 0 for r in ys}
    common = set(a) & set(b)
    xo = sum(1 for s in common if a[s] and not b[s]); yo = sum(1 for s in common if b[s] and not a[s])
    return {"pairs": len(common), "only_first": xo, "only_second": yo, "p_two_sided": mcnemar_exact(xo, yo)}


def mann_whitney_less(x, y):
    """one-sided P(X < Y) normal approximation; returns (U, z, p)."""
    n1, n2 = len(x), len(y)
    allv = sorted([(v, 0) for v in x] + [(v, 1) for v in y])
    ranks = {}
    i = 0
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]:
            j += 1
        for k in range(i, j):
            ranks.setdefault(allv[k][0], (i + j + 1) / 2)
        i = j
    r1 = sum(ranks[v] for v in x)
    u = r1 - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2; sd = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z = (u - mu) / sd if sd else 0.0
    p = 0.5 * math.erfc(-z / math.sqrt(2))
    return round(u, 1), round(z, 3), round(p, 6)


def cls_repair(dom):
    rm = set(dom.get("rcrit_founder_mech") or []); cm = set(dom.get("ccrit_founder_mech") or [])
    if "transplant0" in rm and "transplant1" in cm:
        return "CROSS_LINEAGE"
    if (rm | cm) and (rm | cm) <= {"transplant1"}:
        return "SINGLE_LINEAGE_BAD"
    if (rm | cm) and (rm | cm) <= {"transplant0"}:
        return "SINGLE_LINEAGE_REP"
    return "OTHER"


def main(res_path, out_path):
    R = [json.loads(l) for l in open(res_path)]
    voids = [r for r in R if r.get("void")]
    R = [r for r in R if not r.get("void")]
    out = {"n_results": len(R) + len(voids), "voids": len(voids)}
    end = lambda r: r["comp"]["comp_func_alive"] > 0
    by = defaultdict(list)
    for r in R:
        by[(r["lane"], r["arm"])].append(r)
    tab = {"%s/%s" % k: {"runs": len(v), "comp_sr_end": sum(map(end, v)), "wilson": wilson(sum(map(end, v)), len(v)),
                         "extinct": sum(r["summary"]["extinct"] for r in v)} for k, v in sorted(by.items())}
    out["table"] = tab
    on, off = by[("M1", "ON")], by[("M1", "OFF")]
    a = sum(map(end, on)); c = sum(map(end, off))
    p = fisher_greater(a, len(on) - a, c, len(off) - c) if on and off else None
    rate_on = a / len(on) if on else 0; rate_off = c / len(off) if off else 0
    out["W4-P1"] = {"mcnemar_paired": paired(on, off), "ON": [a, len(on)], "OFF": [c, len(off)], "p_one_sided": p,
                    "verdict": "HOLDS" if p is not None and p < 0.05 else ("FALSIFIED" if rate_on <= rate_off + 0.02 else "SIGNAL_WEAK")}
    m2 = {arm: by[("M2", arm)] for arm in ("ON", "OFF", "SHUFFLED")}
    k = {arm: sum(map(end, v)) for arm, v in m2.items()}
    ps = {}
    for ctl in ("OFF", "SHUFFLED"):
        ps[ctl] = fisher_greater(k["ON"], len(m2["ON"]) - k["ON"], k[ctl], len(m2[ctl]) - k[ctl]) if m2["ON"] and m2[ctl] else None
    srt = sorted(ps.items(), key=lambda x: x[1] if x[1] is not None else 1)
    holm = {}
    for i, (ctl, pv) in enumerate(srt):
        holm[ctl] = None if pv is None else round(min(1.0, pv * (len(srt) - i)), 6)
    out["W4-P2"] = {"mcnemar_paired": {ctl: paired(m2["ON"], m2[ctl]) for ctl in ("OFF", "SHUFFLED")},
                    "counts": {a_: [k[a_], len(v)] for a_, v in m2.items()}, "p": ps, "p_holm": holm,
                    "holds": all(v is not None and v < 0.05 for v in holm.values())}
    doms = [r["comp"]["dominant"] for r in on if end(r) and r["comp"].get("dominant")]
    out["W4-P3"] = {"classes": dict(Counter(cls_repair(d) for d in doms)), "n": len(doms)}
    out["W4-P3"]["modal"] = Counter(cls_repair(d) for d in doms).most_common(1)[0][0] if doms else None
    out["W4-P3"]["holds"] = out["W4-P3"]["modal"] == "SINGLE_LINEAGE_BAD" if doms else "NOT_TESTABLE"
    def tl(rs):
        xs = []
        for r in rs:
            C = r["comp"]["C"]
            n = C.get("from_comp_func", 0)
            if n >= 20:
                xs.append(C.get("task_loss", 0) / n)
        return xs
    x_on, x_off = tl(on), tl(off)
    out["W4-P4"] = {"n_on": len(x_on), "n_off": len(x_off),
                    "median_on": sorted(x_on)[len(x_on) // 2] if x_on else None, "median_off": sorted(x_off)[len(x_off) // 2] if x_off else None}
    if len(x_on) >= 10 and len(x_off) >= 10:
        u, z, pp = mann_whitney_less(x_on, x_off)
        out["W4-P4"].update({"U": u, "z": z, "p_one_sided": pp, "holds": pp < 0.05})
    else:
        out["W4-P4"]["holds"] = "DESCRIPTIVE (fewer than 10 qualifying runs per arm)"
    d2 = [r["comp"]["dominant"] for r in m2["ON"] if end(r) and r["comp"].get("dominant")]
    nov = sum(1 for d in d2 if any(kk in ("n", "c") for kk in (d.get("ccrit_novel") or {})))
    out["W4-P5"] = {"novel_in_ccrit": [nov, len(d2)], "holds": (nov / len(d2) >= 0.8) if d2 else "NOT_TESTABLE",
                    "ccrit_founder_mech": dict(Counter(m for d in d2 for m in (d.get("ccrit_founder_mech") or [])))}
    # descriptive: task loss / joint keep pooled per arm, first competent SR timing
    desc = {}
    for kk, v in by.items():
        C = Counter()
        for r in v:
            C.update(r["comp"]["C"])
        ft = [r["comp"]["first_comp_sr"]["tick"] for r in v if r["comp"].get("first_comp_sr")]
        desc["%s/%s" % kk] = {"C": dict(C), "first_comp_sr_ticks_median": sorted(ft)[len(ft) // 2] if ft else None, "n_first": len(ft)}
    out["descriptive"] = desc
    json.dump(out, open(out_path, "w"), indent=1, default=str)
    print(json.dumps({k_: out[k_] for k_ in out if k_.startswith("W4-") or k_ == "table"}, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
