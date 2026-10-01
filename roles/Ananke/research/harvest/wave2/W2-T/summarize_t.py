"""W2-T step 4: apply W2-O's section-5 checklist to every C1 NULL evolve cell and tabulate.
Inputs: out/cells.json, out/audit_*.jsonl (engine replays), out/lcwake_null_*.json (combined bound),
        W2-O/out/reach_census.json (cross-check), C1 rows (curve max_acc, plant).
Classes (first match wins, W2-O order): BROKEN > TRUNCATED > CAPPED > DEGRADED > INERT > FLAT > ADMISSIBLE.
  BROKEN    known-answer gate fails (held acc/lo99/hi99/tel; + zero_comm/comm_delta/final on the full subsample),
            or a break guard fires (G1-G5, G7, G9, G10, G11), or direct G8 overlap, or wake recompute != engine.
  TRUNCATED patched G12 fires (normal arm only) AND first-half per-pair accuracy lo99 > .5.
  CAPPED    combined light-cone+wake bound < .60 (H-PLANT/W2-O cap threshold).   MARGINAL flag: .60 <= bound < .75.
  DEGRADED  >= 1 held world with no sensor->actuator path (W2-O item 6).
  INERT     readout dead (S0 == 0 at every scored readout) in >= 48/64 worlds (75%).
  FLAT      training max_acc over all generations <= .5.
Strict ADMISSIBLE excludes MARGINAL; lenient includes MARGINAL."""
import json, gzip, glob, math, pathlib, collections
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
R = {}
for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    r = json.loads(l)
    R[r["cell_id"]] = r
cells = json.load(open(HERE / "out/cells.json"))
A = {}
for f in sorted(glob.glob(str(HERE / "out/audit_b*.jsonl"))):
    for l in open(f):
        d = json.loads(l)
        A[d["cell"]] = d
L = {}
for f in sorted(glob.glob(str(HERE / "out/lcwake_null_*.json"))):
    for o in json.load(open(f))["rows"]:
        L[o["cell"]] = o
RC = {x["cell"]: x for x in json.load(open(HERE.parent / "W2-O/out/reach_census.json"))["rows"]}
BREAK = {"G1_PHYSICS_PROVENANCE", "G2_TOPOLOGY_PROVENANCE", "G3_SENSE_LIVE", "G4_MIRROR_INVARIANT",
         "G5_CONDITION_PROVENANCE", "G7_CRN_PAIRING", "G8_HELD_DISJOINT", "G9_GENOME_PROVENANCE",
         "G10_SCORER_SELFTEST", "G11_TRANSPORT_LIVE"}
ORDER = ("BROKEN", "TRUNCATED", "CAPPED", "DEGRADED", "INERT", "FLAT", "ADMISSIBLE")


def cp(k, n, a=0.05):
    """two-sided 95% Clopper-Pearson via bisection on the binomial cdf."""
    def cdf(x, p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))
    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) else (lo, m)
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - cdf(k - 1, p) < a / 2)
    upper = 1.0 if k == n else solve(lambda p: cdf(k, p) > a / 2)
    return round(lower, 4), round(upper, 4)


rows = []
missing = []
for c in cells:
    cid = c["cell"]
    r = R[cid]
    a, lw = A.get(cid), L.get(cid)
    if a is None or lw is None:
        missing.append(cid)
        continue
    f = a["feasibility"]
    flags = []
    brk = sorted(set(a["alarms_held"]) & BREAK) + sorted(set(a.get("alarms_final", [])) & BREAK)
    if a["G8_direct_overlap"]:
        brk.append("G8_direct")
    if not a["gate_pass"]:
        brk.append("gate_held")
    if a["full"] and not a["final_gate"][2]:
        brk.append("gate_final")
    if not f["wake_recompute_matches_engine"]:
        brk.append("wake_recompute")
    g12 = "G12_STATE_LIVE" in a["alarms_held"]
    trunc = g12 and a["half_lo99"][0] > 0.5
    cb = lw["held_exact"]["bound"]
    lc_opt = lw["held_opt"]["bound"]
    maxacc = max(x["max_acc"] for x in r["result"]["curve"])
    inert = a["readout_dead_worlds"] >= 48
    flat = maxacc <= 0.5
    if brk:
        cls = "BROKEN"
    elif trunc:
        cls = "TRUNCATED"
    elif cb < 0.60:
        cls = "CAPPED"
    elif f["impossible_worlds"] > 0:
        cls = "DEGRADED"
    elif inert:
        cls = "INERT"
    elif flat:
        cls = "FLAT"
    else:
        cls = "ADMISSIBLE"
    marginal = 0.60 <= cb < 0.75
    pl = r["result"].get("plant") or {}
    rows.append({
        "cell": cid, "family": c["family"], "full": c["full"], "class": cls, "marginal": marginal,
        "break": brk, "G12_normal": g12, "half_acc": [round(x, 3) for x in a["half_acc"]],
        "held": round(r["result"]["held"]["acc"], 4), "held_lo99": round(r["result"]["held"]["lo99"], 4),
        "topology": r["physics"]["topology"], "update_mode": r["physics"]["update_mode"],
        "update_p": r["physics"]["update_p"], "d": r["env"]["d"], "delta": r["env"]["delta"],
        "lc_census": lw["lc_census"], "lc_held_opt": round(lc_opt, 4), "combined_bound": round(cb, 4),
        "combined_bound_score_seeds": round(lw["score_exact"]["bound"], 4),
        "wake_ceiling_W2O": round(f["ceiling_info_mean"], 4), "impossible_worlds": f["impossible_worlds"],
        "impossible_worlds_W2O_census": RC.get(cid, {}).get("impossible"),
        "readout_dead": a["readout_dead_worlds"], "worlds_emitting": a["worlds_emitting"],
        "max_acc_any_gen": round(maxacc, 4), "selector_invisible": maxacc < 0.57,
        "G0": "G0_DEGENERATE_CONTROL" in a["alarms_held"], "G6": "G6_CONTROL_DISTINGUISHABLE" in a["alarms_held"],
        "flags": {"inert": inert, "flat": flat, "capped": cb < 0.60, "degraded": f["impossible_worlds"] > 0},
        "plant": pl.get("plant"), "plant_acc": pl.get("acc"),
        "cpu_s": a["compute"]["cpu_s"]})

fams = ("XOR", "FLIP", "RELAY", "MAJ", "HOLD")
table = {}
for fam in fams + ("C1_NULL_4FAM",):
    rr = [x for x in rows if (x["family"] == fam if fam != "C1_NULL_4FAM" else x["family"] != "HOLD")]
    if not rr:
        continue
    t = {k: sum(x["class"] == k for x in rr) for k in ORDER}
    t["n"] = len(rr)
    t["ADMISSIBLE_strict(no MARGINAL)"] = sum(x["class"] == "ADMISSIBLE" and not x["marginal"] for x in rr)
    t["MARGINAL_among_ADMISSIBLE"] = sum(x["class"] == "ADMISSIBLE" and x["marginal"] for x in rr)
    t["flag_counts(non-exclusive)"] = {k: sum(x["flags"][k] for x in rr) for k in ("capped", "degraded", "inert", "flat")}
    t["flag_marginal"] = sum(x["marginal"] for x in rr)
    t["flag_selector_invisible(max_acc<.57)"] = sum(x["selector_invisible"] for x in rr)
    t["G12_normal_fired"] = sum(x["G12_normal"] for x in rr)
    t["ADMISSIBLE_with_plant_acc_ge_.60"] = sum(x["class"] == "ADMISSIBLE" and (x["plant_acc"] or 0) >= 0.60 for x in rr)
    fs = [x for x in rr if x["full"]]
    kb = sum(x["class"] == "BROKEN" for x in fs)
    t["full_subsample"] = {"n": len(fs), "broken": kb, "ci95": cp(kb, len(fs)) if fs else None}
    t["admissible_frac_strict"] = round(t["ADMISSIBLE_strict(no MARGINAL)"] / len(rr), 4)
    t["admissible_frac_lenient"] = round(t["ADMISSIBLE"] / len(rr), 4)
    t["admissible_frac_lenient_ci95"] = cp(t["ADMISSIBLE"], len(rr))
    table[fam] = t
# light-cone question: cells H-PLANT bounds at 1.0 (lc_census, its own seeds) that drop below .75 with exact wake
lcq = {}
for fam in ("XOR", "FLIP", "RELAY"):
    rr = [x for x in rows if x["family"] == fam and x["lc_census"] is not None and x["lc_census"] >= 1.0]
    lcq[fam] = {"lc_census_eq_1": len(rr),
                "combined_lt_.75_held_seeds": sum(x["combined_bound"] < 0.75 for x in rr),
                "combined_lt_.75_score_seeds": sum(x["combined_bound_score_seeds"] < 0.75 for x in rr),
                "combined_lt_.60_held_seeds": sum(x["combined_bound"] < 0.60 for x in rr),
                "min_combined": min((x["combined_bound"] for x in rr), default=None)}
for fam in ("MAJ", "HOLD"):
    rr = [x for x in rows if x["family"] == fam]
    lcq[fam] = {"lc_held_opt_eq_1(no H-PLANT census)": sum(x["lc_held_opt"] >= 1.0 for x in rr),
                "combined_lt_.75": sum(x["combined_bound"] < 0.75 for x in rr),
                "combined_lt_.60": sum(x["combined_bound"] < 0.60 for x in rr),
                "min_combined": min((x["combined_bound"] for x in rr), default=None)}
# MAJ: drop of the bound compared with the opt (always-awake) cone among cells where opt cone == full-info ceiling
xs = [x for x in rows if x["family"] != "MAJ" and x["lc_census"] is not None]
lcq["held_vs_score_seed_lc_agree(opt)"] = sum(abs(x["lc_held_opt"] - x["lc_census"]) < 0.02 for x in xs), len(xs)
summ = {"table": table, "lightcone_wake": lcq, "missing": missing, "n_rows": len(rows),
        "cpu_s_audit": round(sum(x["cpu_s"] for x in rows), 1),
        "admissible_cells": sorted([(x["family"], x["cell"], x["held"], x["combined_bound"], x["marginal"],
                                     x["plant_acc"]) for x in rows if x["class"] == "ADMISSIBLE"])}
(HERE / "out/table_t.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))
print(json.dumps({k: v for k, v in summ.items() if k != "admissible_cells"}, indent=1))
print("ADMISSIBLE cells:", len(summ["admissible_cells"]))
