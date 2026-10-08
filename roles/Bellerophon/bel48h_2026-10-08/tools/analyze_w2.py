"""BEL-48H Window 2 analysis (rules frozen in BEL_48H_PREREG.md s4; this file committed before the W2 results were read).

    python3 analyze_w2.py RESULTS.jsonl EVENTS_DIR OUT.json PLAN.json

Unit = run. Wilson 95% intervals for proportions; Fisher exact (one-sided) where the prereg says so."""
import gzip
import json
import math
import pathlib
import sys
from collections import Counter, defaultdict


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def fisher_greater(a, b, c, d):
    """one-sided P(X >= a) for the 2x2 [[a, b], [c, d]] (row 1 = test group, col 1 = success)."""
    n1, n2, k = a + b, c + d, a + c
    def h(x):
        return math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n1 + n2, k)
    return round(sum(h(x) for x in range(a, min(n1, k) + 1)), 6)


def multi_source(ff):
    an = (ff or {}).get("anatomy") or {}
    return an.get("n_origins", 0) >= 2


def main(res_path, ev_dir, out_path):
    R = [json.loads(l) for l in open(res_path)]
    voids = [r for r in R if r.get("void")]
    R = [r for r in R if not r.get("void")]
    plan = {p["id"]: p for p in json.load(open(PLAN))} if PLAN else {}
    for r in R:
        r["_cfg"] = plan.get(r["id"], {}).get("cfg", {"cells": 256})
    out = {"n_results": len(R) + len(voids), "voids": len(voids)}
    # ---- H1 -----------------------------------------------------------------------------------------------------------
    H1 = [r for r in R if r["lane"] == "H1"]
    cells = defaultdict(list)
    for r in H1:
        cells[r["cell"]].append(r)
    h1 = {}
    born_all = with_ff_all = 0
    for c, rs in sorted(cells.items()):
        ff = [r["heredity"]["first_func"] for r in rs if r["heredity"]["first_func"]]
        hows = Counter(f["how"] for f in ff)
        born = sum(1 for f in ff if f["how"].startswith("BORN_"))
        born_all += born; with_ff_all += len(ff)
        ca = sum(1 for f in ff if f["how"] == "BORN_ASSEMBLY" and multi_source(f))
        ms = sum(1 for f in ff if multi_source(f))
        reach = [r.get("reach") or {} for r in rs if (r.get("reach") or {}).get("how")]
        H = Counter()
        for r in rs:
            H.update(r["heredity"]["H"])
        dom = [r["heredity"].get("dominant_func") for r in rs if r["heredity"].get("dominant_func")]
        h1[c] = {"runs": len(rs), "extinct": sum(r["summary"]["extinct"] for r in rs), "with_first_func": len(ff),
                 "first_func_how": dict(hows), "born_share": [born, len(ff)], "multi_source_first_func": ms,
                 "born_assembly_multi_source": ca, "func_birth_classes_pooled": dict(H),
                 "runs_with_causal_assembly": sum(1 for r in rs if r["heredity"]["H"].get("causal_assembly", 0) > 0),
                 "dominant_func_runs": len(dom),
                 "dominant_n_origins": Counter(d.get("n_origins") for d in dom),
                 "dominant_novel_kinds": dict(sum((Counter(d.get("critical_novel_kinds") or {}) for d in dom), Counter())),
                 "reach_n": len(reach),
                 "reach_n_origin_events": Counter(x.get("n_origin_events") for x in reach),
                 "reach_ldir_critical": sum(1 for x in reach if x.get("ldir_critical")),
                 "reach_zero_to_halt_func": sum(1 for x in reach if x.get("func_zero_to_halt")),
                 "reach_undefined_halt_func": sum(1 for x in reach if x.get("func_undefined_halt")),
                 "reach_minimal_core_func": sum(1 for x in reach if x.get("minimal_core_func")),
                 "reach_portability_mean": round(sum(x.get("portability", 0) for x in reach) / len(reach), 3) if reach else None,
                 "reach_ramp_any_partial": sum(1 for x in reach if x.get("ramp_any_partial")),
                 "reach_chain_above_contemporaries_median": sorted(x["chain_frac_above_contemporaries"] for x in reach if x.get("chain_frac_above_contemporaries") is not None)[len(reach) // 2] if reach else None}
    out["H1"] = h1
    out["W2-P1"] = {"born": born_all, "with_first_func": with_ff_all, "share": round(born_all / with_ff_all, 4) if with_ff_all else None,
                    "wilson": wilson(born_all, with_ff_all),
                    "holds": (born_all / with_ff_all >= 0.9) if with_ff_all else "NOT_TESTABLE"}
    pk = "ENDOGENOUS_PARTIAL/Z80_64/WELL_MIXED"; ck = "ENDOGENOUS_COPY/Z80_64/WELL_MIXED"
    if pk in h1 and ck in h1 and h1[pk]["with_first_func"] >= 5 and h1[ck]["with_first_func"] >= 5:
        a = h1[pk]["multi_source_first_func"]; b = h1[pk]["with_first_func"] - a
        c_ = h1[ck]["multi_source_first_func"]; d = h1[ck]["with_first_func"] - c_
        p = fisher_greater(a, b, c_, d)
        out["W2-P2"] = {"partial": [a, a + b], "copy": [c_, c_ + d], "p_one_sided": p, "holds": p < 0.05}
    else:
        out["W2-P2"] = {"holds": "NOT_TESTABLE", "partial_ff": h1.get(pk, {}).get("with_first_func"), "copy_ff": h1.get(ck, {}).get("with_first_func")}
    # ---- H2 -----------------------------------------------------------------------------------------------------------
    H2 = [r for r in R if r["lane"] == "H2"]
    arms = defaultdict(list)
    for r in H2:
        arms[r["arm"]].append(r)
    h2 = {}
    for arm, rs in sorted(arms.items()):
        h2[arm] = {"runs": len(rs), "func_any": sum(1 for r in rs if r["heredity"]["first_func"]),
                   "causal_assembly_runs": sum(1 for r in rs if r["heredity"]["H"].get("causal_assembly", 0) > 0),
                   "first_func_how": dict(Counter((r["heredity"]["first_func"] or {}).get("how") for r in rs)),
                   "func_alive_end_runs": sum(1 for r in rs if r["heredity"]["func_alive"] > 0)}
    # attribution of the first CAUSAL assembly per run (events files)
    attr = defaultdict(lambda: Counter())
    herit = defaultdict(lambda: [0, 0])
    for arm in ("AB", "A"):
        for r in arms.get(arm, []):
            f = pathlib.Path(ev_dir) / (r["id"] + ".jsonl.gz")
            if not f.exists():
                continue
            evs = [json.loads(l) for l in gzip.open(f, "rt")]
            first = next((e for e in evs if e.get("causal_assembly")), None)
            if first is None:
                continue
            tape = bytes.fromhex(first["tape"])
            mech_at = {}
            for kind, fid, pos_or_tick, p in first.get("origins_raw", []):
                mech_at[p] = ("F", kind, fid)
            # LD T,64 = 0x08 0x40 critical pair; LDIR = 0x15
            fm = {}
            for kind, fid, x, p in first.get("origins_raw", []):
                fm[p] = kind if kind != "F" else "F:%s" % fid
            founders_mech = first.get("critical_founder_mech") or []
            ldt = [p for p in first["critical"] if tape[p] == 0x08 and p + 1 < len(tape) and tape[p + 1] == 0x40]
            ldir = [p for p in first["critical"] if tape[p] == 0x15]
            def mech_of(p):
                for kind, fid, x, q in first.get("origins_raw", []):
                    if q == p:
                        return "novel_" + kind if kind != "F" else r_founder_mech(r, fid, first)
                return "?"
            attr[arm]["runs"] += 1
            attr[arm]["ldT_from_A"] += any(mech_of(p) == "transplant0" for p in ldt)
            ldir_m = Counter(mech_of(p) for p in ldir)
            attr[arm]["ldir_from_B"] += ldir_m.get("transplant1", 0) > 0 if arm == "AB" else 0
            attr[arm]["ldir_from_init_random"] += ldir_m.get("init", 0) > 0
            attr[arm]["ldir_from_novel"] += any(k.startswith("novel_") for k in ldir_m)
            herit[arm][1] += 1
            herit[arm][0] += r["heredity"]["event_alive_descendants"].get(str(first["i"]), 0) > 0
    out["H2"] = h2
    out["H2_attribution_first_causal_assembly"] = {k: dict(v) for k, v in attr.items()}
    ab = attr.get("AB", Counter())
    out["W2-P3"] = {"ldT_from_A": [ab.get("ldT_from_A", 0), ab.get("runs", 0)], "ldir_from_B": [ab.get("ldir_from_B", 0), ab.get("runs", 0)],
                    "holds": (ab.get("runs", 0) > 0 and ab["ldT_from_A"] / ab["runs"] >= 0.9 and ab["ldir_from_B"] / ab["runs"] < 0.5) if ab.get("runs") else "NOT_TESTABLE"}
    out["W2-P4"] = {arm: {"alive_descendants": v, "share": round(v[0] / v[1], 3) if v[1] else None} for arm, v in herit.items()}
    out["W2-P4"]["holds"] = all(v[1] and v[0] / v[1] >= 0.5 for v in herit.values()) if herit else "NOT_TESTABLE"
    cab = arms.get("COPY_AB", [])
    out["W2-P5"] = {"zero_causal_assembly_runs": sum(1 for r in cab if r["heredity"]["H"].get("causal_assembly", 0) == 0), "runs": len(cab),
                    "holds": sum(1 for r in cab if r["heredity"]["H"].get("causal_assembly", 0) == 0) >= 95 if cab else "NOT_TESTABLE"}
    out["W2-P6"] = {arm: {"func_any": h2.get(arm, {}).get("func_any"), "runs": h2.get(arm, {}).get("runs")} for arm in ("B", "none")}
    out["W2-P6"]["holds"] = all((h2.get(a, {}).get("func_any") or 0) <= 5 for a in ("B", "none"))
    json.dump(out, open(out_path, "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in out if k.startswith("W2-")}, indent=1, default=str))


def r_founder_mech(r, fid, ev):
    """founder mechanism from the founder id: World.next_id starts at 1 and init slots are spawned in order k, so
    id = k + 1; slot k < max(1, n_fill // 4) is a transplant with index k % len(init_tapes) (world._init_population;
    verified for 256 cells: ids 1..32 alternate transplant0/transplant1, 33.. are init)."""
    cfg = r["_cfg"]
    ntx = len(cfg.get("init_tapes") or [])
    nfill = max(1, cfg["cells"] // 2)
    k = fid - 1
    if k < 0 or k >= nfill:
        return "not_founder"
    if ntx and k < max(1, nfill // 4):
        return "transplant%d" % (k % ntx)
    return "init"


if __name__ == "__main__":
    PLAN = sys.argv[4] if len(sys.argv) > 4 else None
    main(*sys.argv[1:4])
