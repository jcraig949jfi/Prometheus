"""END-TO-END ATLAS CALIBRATION on PLANTED toys (instrument calibration, NOT discovery).

  python -m atlas.calibration --toy GRADED --part atlas|qual|arms|scale|scale2     (from roles/Aphrodite/beta04)
  python -m atlas.calibration --summary
Each part is one process (<= 15 CPU-min), writes atlas/calibration/<TOY>_<part>.json; --summary aggregates them into
atlas/ATLAS_CALIBRATION_RESULT.json.

Frozen-parameter CANDIDATES used here (not frozen; coordinator decision): base budget B = 5,000 search charges (1x),
scaling 4x = 20,000 and 16x = 80,000; burst L = 10; mutator max_fill 3 / max_size 16; CRN seeds 0-7 (arms), 0-3
(scaling); random-control calibration seeds 1000-1002; descriptor for the archive arms D-BEH (the only candidate that
qualified on any toy; arms guided by it on a toy where it FAILED qualification are labelled INSTRUMENT_UNVALIDATED).
"""
import argparse
import json
import os
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
from tfs1.enum import Enumerator, canon_comm      # noqa: E402
from tfs1.membrane import flip_test              # noqa: E402
from tfs1 import core as C                       # noqa: E402

from . import arms as A                          # noqa: E402
from . import descriptors as D                   # noqa: E402
from . import measure as M                       # noqa: E402
from . import toys                               # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "calibration"
B = 5000
SCALES = (1, 4, 16)
ARM_SEEDS = tuple(range(8))
SCALE_SEEDS = tuple(range(4))
CAL_SEEDS = (1000, 1001, 1002)
DESC = "D-BEH"
LABEL = toys.LABEL


def _dump(name, obj):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def _load(name):
    p = OUT / name
    return json.loads(p.read_text()) if p.exists() else None


def part_atlas(toy):
    T, lib = toys.all_toys()[toy]
    t0 = time.process_time()
    rec = M.atlas(T, lib, seeds=ARM_SEEDS, enum_budget=16 * B * 4, enum_max_size=7, density_max_n=7, robust_n=1000)
    rec["classification_at_B"] = {str(b): M.classify(rec, b) for b in (B,)}
    rec["label"] = LABEL
    rec["cpu_s_total"] = round(time.process_time() - t0, 1)
    _dump("%s_atlas.json" % toy, rec)
    return rec


def part_qual(toy):
    T, lib = toys.all_toys()[toy]
    t0 = time.process_time()
    q = D.qualify(T, T["witness"], lib)
    q["cpu_s"] = round(time.process_time() - t0, 1)
    q["label"] = LABEL
    _dump("%s_qual.json" % toy, q)
    return q


def _watch(toy):
    a = _load("%s_atlas.json" % toy)
    if not a or not a.get("route"):
        return None
    w = {}
    for rname, r in a["route"].items():
        for s in r["steps"]:
            w[C.to_str(canon_comm(C.parse(s["program"])))] = rname
    return w


def _slim(r):
    keep = ("arm", "seed", "budget", "credit", "descriptor", "hit", "hit_charge", "program", "n_false_hits",
            "first_false_hits", "archive", "ledger", "first_visit_route", "archive_assisted_discovery",
            "autonomous_competence", "final_evaluation", "decision_log_sha256", "cpu_s")
    out = {k: r.get(k) for k in keep}
    m = r["mechanisms"]
    out["mechanisms"] = {"qualified_skeletons": m["qualified_skeletons"], "qualified_genotypes":
                         m["qualified_genotypes"], "cert_patterns_seen": m["cert_patterns_seen"]}
    return out


def _arms_set(K3, K2):
    return [("A-FRESH", None, "exact"), ("A-CHAIN", None, "exact"), ("B1-RETAIN", None, "exact"),
            ("B2-DESCSEL", DESC, "exact"), ("B3-CELLADMIT", DESC, "exact"), ("C3-RAND", "RAND:%d" % K3, "exact"),
            ("C2-RAND", "RAND:%d" % K2, "exact"), ("A-CHAIN", None, "partial"), ("A-CHAIN", None, "none")]


def part_arms(toy):
    T, lib = toys.all_toys()[toy]
    E = Enumerator(lib)
    t0 = time.process_time()
    cal3 = A.calibrate_random_k(T, lib, "B3-CELLADMIT", DESC, B, CAL_SEEDS, E=E)
    cal2 = A.calibrate_random_k(T, lib, "B2-DESCSEL", DESC, B, CAL_SEEDS, E=E)
    watch = _watch(toy)
    rows = {}
    for arm, desc, cr in _arms_set(cal3["K"], cal2["K"]):
        key = arm if cr == "exact" else "%s[%s]" % (arm, cr)
        rows[key] = []
        for sd in ARM_SEEDS:
            r = A.run_arm(T, lib, arm, sd, B, descriptor=desc, watch=watch, E=E, credit=cr)
            rows[key].append(_slim(r))
        print(toy, key, [x["hit_charge"] for x in rows[key]], flush=True)
    cost = {k: [x["hit_charge"] if x["hit"] else B for x in v] for k, v in rows.items()}
    contrasts = {}
    for a, b, what in (("B1-RETAIN", "A-FRESH", "retention"), ("B2-DESCSEL", "B1-RETAIN", "descriptor selection"),
                       ("B3-CELLADMIT", "B1-RETAIN", "cell admission"), ("B3-CELLADMIT", "C3-RAND",
                                                                         "descriptor vs random cells (admission)"),
                       ("B2-DESCSEL", "C2-RAND", "descriptor vs random cells (selection)"),
                       ("A-CHAIN", "A-FRESH", "no restarts"), ("A-CHAIN[partial]", "A-CHAIN", "partial credit"),
                       ("A-CHAIN", "A-CHAIN[none]", "feedback used (credit-guided vs credit-blind drift)")):
        ft = flip_test([x - y for x, y in zip(cost[b], cost[a])])       # positive = a cheaper than b
        ft.pop("diffs", None)
        contrasts["%s vs %s" % (a, b)] = {"factor": what, "hits": [sum(x["hit"] for x in rows[a]),
                                                                    sum(x["hit"] for x in rows[b])], **ft}
    emp = M.classify_empirical(cost, B)
    qual = _load("%s_qual.json" % toy)
    validated = bool(qual and DESC in qual.get("qualified", []))
    res = {"toy": toy, "family_id": T["family_id"], "label": LABEL, "budget_1x": B, "burst_L": A.DEFAULT_BURST,
           "descriptor": DESC, "descriptor_qualified_on_this_toy": validated,
           "descriptor_arm_status": "VALIDATED" if validated else "INSTRUMENT_UNVALIDATED",
           "random_control_calibration": {"C3": cal3, "C2": cal2}, "rows": rows, "censored_cost": cost,
           "one_factor_contrasts_exact_signflip": contrasts, "empirical_flags": emp,
           "hits_by_arm": {k: sum(x["hit"] for x in v) for k, v in rows.items()},
           "autonomous_by_arm": {k: sum(bool(x["autonomous_competence"]) for x in v) for k, v in rows.items()},
           "cpu_s": round(time.process_time() - t0, 1)}
    _dump("%s_arms.json" % toy, res)
    return res


def novel_mechanisms(skeletons) -> int:
    """Count of NEW certified mechanisms: qualified skeletons in discovery order whose primitive SET is not a superset
    of an earlier qualified primitive set (neutral padding such as (add 0 .) only adds primitives, so it is not
    counted again). Raw distinct skeletons are reported beside it."""
    seen, n = [], 0
    for sk, _c in sorted(skeletons.items(), key=lambda kv: (kv[1], kv[0])):
        ps = frozenset(x.rstrip("0123456789") for x in sk.split(",") if x)
        if any(p <= ps for p in seen):
            continue
        seen.append(ps)
        n += 1
    return n


SCALE_GROUPS = {"scale": (("A-FRESH", None), ("A-CHAIN", None), ("B1-RETAIN", None)),
                "scale2": (("B3-CELLADMIT", DESC), ("C3-RAND", "RAND")) }


def part_scale(toy, group="scale"):
    T, lib = toys.all_toys()[toy]
    E = Enumerator(lib)
    arms_res = _load("%s_arms.json" % toy)
    K3 = arms_res["random_control_calibration"]["C3"]["K"] if arms_res else 500
    t0 = time.process_time()
    out = {}
    for arm, desc in SCALE_GROUPS[group]:
        desc = "RAND:%d" % K3 if desc == "RAND" else desc
        out[arm] = {}
        for m in SCALES:
            rows = []
            for sd in SCALE_SEEDS:
                r = A.run_arm(T, lib, arm, sd, B * m, descriptor=desc, stop_on_hit=False, E=E, final_eval=False)
                mech = r["mechanisms"]
                rows.append({"seed": sd, "first_qualified_charge": r["hit_charge"],
                             "qualified_skeletons": len(mech["qualified_skeletons"]),
                             "novel_mechanisms": novel_mechanisms(mech["qualified_skeletons"]),
                             "skeleton_first_charges": dict(sorted(mech["qualified_skeletons"].items(),
                                                                   key=lambda kv: kv[1])[:20]),
                             "qualified_genotypes": mech["qualified_genotypes"],
                             "cert_patterns_seen": mech["cert_patterns_seen"],
                             "realised_cells": r["archive"]["realised_cells"]})
            n = len(rows)
            out[arm][str(m)] = {"budget": B * m, "success": sum(r["first_qualified_charge"] is not None for r in rows),
                                "seeds": n, "rows": rows,
                                "new_certified_mechanisms_per_1k_charges":
                                    round(sum(r["novel_mechanisms"] for r in rows) / n / (B * m) * 1000, 4),
                                "mean_novel_mechanisms": round(sum(r["novel_mechanisms"] for r in rows) / n, 2),
                                "raw_qualified_skeletons_per_1k_charges":
                                    round(sum(r["qualified_skeletons"] for r in rows) / n / (B * m) * 1000, 4),
                                "mean_cert_patterns": round(sum(r["cert_patterns_seen"] for r in rows) / n, 1)}
        print(toy, arm, {m: (v["success"], v["new_certified_mechanisms_per_1k_charges"]) for m, v in out[arm].items()},
              flush=True)
    res = {"toy": toy, "label": LABEL, "scales": SCALES, "base_budget": B, "seeds": SCALE_SEEDS, "arms": out,
           "note": "stop_on_hit=False: runs continue after the first qualified program to count distinct certified "
                   "mechanisms (skeleton = multiset of base primitives of the expanded program).",
           "cpu_s": round(time.process_time() - t0, 1)}
    _dump("%s_%s.json" % (toy, group), res)
    return res


D1_LADDER = (("D1-chain_strict", None), ("D1-chain_neutral", None), ("D1-X1", DESC), ("D1-X2", DESC),
             ("D1-X3", DESC), ("D1-X3G", "RAND"))
D1_CONTRASTS = (("C1", "D1-chain_neutral", "D1-chain_strict", "NEUTRAL ACCEPTANCE"),
                ("C2", "D1-X1", "D1-chain_neutral", "RETENTION"),
                ("C3", "D1-X2", "D1-X1", "RARELY-VISITED (count) SELECTION"),
                ("C4", "D1-X3", "D1-X2", "ADMISSION OF WORSE genomes into NEW cells"),
                ("C5", "D1-X3", "D1-X3G", "BEHAVIOUR-CELL STRUCTURE vs matched structure-free archive"))


def run_ladder(T, lib, seeds, budget, E=None, extra=(("A-CHAIN", None, "none"), ("A-CHAIN", None, "partial"))):
    """The C-013 D1 one-factor ladder on one task (+ the credit-blind and partial-credit chains)."""
    E = E or Enumerator(lib)
    cal = A.calibrate_random_k(T, lib, "D1-X3", DESC, budget, CAL_SEEDS, E=E)
    rows = {}
    for arm, desc in D1_LADDER:
        desc = "RAND:%d" % cal["K"] if desc == "RAND" else desc
        rows[arm] = [_slim(A.run_arm(T, lib, arm, sd, budget, descriptor=desc, E=E)) for sd in seeds]
    for arm, desc, cr in extra:
        rows["%s[%s]" % (arm, cr)] = [_slim(A.run_arm(T, lib, arm, sd, budget, descriptor=desc, E=E, credit=cr))
                                      for sd in seeds]
    cost = {k: [x["hit_charge"] if x["hit"] else budget for x in v] for k, v in rows.items()}
    con = {}
    for cid, a, b, what in D1_CONTRASTS:
        ft = flip_test([y - x for x, y in zip(cost[a], cost[b])])     # positive = a cheaper than b
        ft.pop("diffs", None)
        con[cid] = {"contrast": "%s vs %s" % (a, b), "isolates": what,
                    "hits": [sum(x["hit"] for x in rows[a]), sum(x["hit"] for x in rows[b])],
                    **{k: ft[k] for k in ("better", "worse", "tied", "p_one_sided", "p_two_sided")}}
    cost["A-CHAIN"] = cost["D1-chain_neutral"]
    return {"budget": budget, "seeds": list(seeds), "X3G_calibration": cal, "rows": rows, "censored_cost": cost,
            "contrasts_C1_C5": con, "hits_by_arm": {k: sum(x["hit"] for x in v) for k, v in rows.items()},
            "autonomous_by_arm": {k: sum(bool(x["autonomous_competence"]) for x in v) for k, v in rows.items()},
            "empirical_flags": M.classify_empirical(cost, budget),
            "attribution": "ladder derived from Nyx's design (3318a2098) via C-013 D1 (Palamedes); mapped to TFS-1"}


def part_ladder(toy):
    T, lib = toys.all_toys()[toy]
    t0 = time.process_time()
    res = run_ladder(T, lib, ARM_SEEDS, B)
    qual = _load("%s_qual.json" % toy)
    res.update({"toy": toy, "label": LABEL, "descriptor": DESC,
                "descriptor_arm_status": "VALIDATED" if (qual and DESC in qual.get("qualified", []))
                else "INSTRUMENT_UNVALIDATED", "cpu_s": round(time.process_time() - t0, 1)})
    for k, v in res["hits_by_arm"].items():
        print(toy, k, v, flush=True)
    _dump("%s_ladder.json" % toy, res)
    return res


def summary():
    out = {"label": LABEL, "base_budget": B, "toys": {}}
    for toy in ("TOY-D2", "GRADED", "DESERT", "CREDIT"):
        a, q, r, s, s2, lad = (_load("%s_%s.json" % (toy, p)) for p in ("atlas", "qual", "arms", "scale", "scale2",
                                                                         "ladder"))
        if s and s2:
            s = {**s, "arms": {**s["arms"], **s2["arms"]}, "cpu_s": s["cpu_s"] + s2["cpu_s"]}
        row = {}
        if a:
            row["existence"] = a["existence"]["exists"]
            row["enum_hitting_cost_by_seed"] = [x["hit_charge"] for x in a["hitting_cost_enumeration"]]
            row["enum_false_hits_by_seed"] = [x["n_false_hits"] for x in a["hitting_cost_enumeration"]]
            row["witness_rank_by_seed"] = {k: v.get("rank") for k, v in a["revisitability"]["witness_rank_by_seed"]
                                           .items()}
            row["classification"] = M.classify(a, B, arm_results=r["hits_by_arm"] if r else None)
            row["route_canonical"] = [(x["program"], x["exact"], x["partial"], x.get("p_eff"))
                                      for x in a["route"]["canonical"]["steps"]]
            row["density_viable_share_by_size"] = {x["size"]: x.get("viable_share") for x in a["density"]}
            row["witness_robustness"] = a["robustness"][0]
            row["atlas_cpu_s"] = a["cpu_s_total"]
        if q:
            row["descriptor_qualification"] = {n: {k: q["descriptors"][n].get(k) for k in
                                                   ("R1_separation", "R1c_given_trace_differs", "R2_invariance",
                                                    "granularity_cells_per_genotype", "verdict")}
                                               for n in ("D-BEH", "D-CERT", "D-RES", "C-FIT", "GENO", "TRACE")}
            row["qual_controls_ok"] = q["controls_ok"]
        if r:
            row["arms_hits_of_8"] = r["hits_by_arm"]
            row["arms_autonomous_of_8"] = r["autonomous_by_arm"]
            row["arms_median_censored_cost"] = {k: sorted(v)[len(v) // 2] for k, v in r["censored_cost"].items()}
            row["contrasts"] = {k: {kk: v[kk] for kk in ("factor", "hits", "better", "worse", "tied", "p_one_sided")}
                                for k, v in r["one_factor_contrasts_exact_signflip"].items()}
            row["descriptor_arm_status"] = ("VALIDATED" if (q and DESC in q.get("qualified", []))
                                            else "INSTRUMENT_UNVALIDATED")
            row["empirical_flags"] = M.classify_empirical(r["censored_cost"], B)
            row["random_K"] = {k: v["K"] for k, v in r["random_control_calibration"].items()}
            row["arms_cpu_s"] = r["cpu_s"]
        if s:
            row["scaling_success_and_new_mechanism_rate_per_1k"] = {arm: {m: (v["success"], v["new_certified_mechanisms_per_1k_charges"])
                                    for m, v in d.items()} for arm, d in s["arms"].items()}
            row["scale_cpu_s"] = s["cpu_s"]
        if lad:
            row["d1_ladder_hits_of_8"] = lad["hits_by_arm"]
            row["d1_ladder_contrasts"] = lad["contrasts_C1_C5"]
            row["d1_ladder_empirical_flags"] = M.classify_empirical(lad["censored_cost"], B)
            row["d1_ladder_descriptor_status"] = row.get("descriptor_arm_status")
            row["d1_X3G_K"] = lad["X3G_calibration"]["K"]
        out["toys"][toy] = row
    out["pilot"] = {}
    for p in sorted(OUT.glob("PILOT_*.json")):
        d = json.loads(p.read_text())
        a, q, lad = d["atlas"], d["qualification"], d["ladder"]
        out["pilot"][a["family_id"]] = {
            "task_sha256": d["task_sha256"], "witness_size": a["existence"].get("size_promoted"),
            "exists": a["existence"].get("exists"),
            "enum_hits_by_seed_at_80k": [x["hit_charge"] for x in a["hitting_cost_enumeration"]],
            "enum_false_hits": [x["n_false_hits"] for x in a["hitting_cost_enumeration"]],
            "witness_rank_bracket_seed0": a.get("revisitability", {}).get("witness_rank_by_seed", {}).get("0"),
            "lattice": {k: a.get("lattice", {}).get(k) for k in ("size", "n_paths", "paths_truncated",
                                                                    "any_intermediate_with_exact_credit")},
            "route_classification": M.classify(a, B),
            "ladder_hits_of_4": lad["hits_by_arm"], "ladder_flags": M.classify_empirical(lad["censored_cost"], B),
            "descriptor_verdicts": {n: q["descriptors"][n].get("verdict") for n in ("D-BEH", "D-CERT", "D-RES")},
            "descriptor_R1": {n: q["descriptors"][n].get("R1_separation") for n in ("D-BEH", "D-CERT", "D-RES",
                                                                                   "TRACE")},
            "qual_pairs": [q["pairs_R1"], q["pairs_R2"]], "qual_controls_ok": q["controls_ok"],
            "cpu_s": {"atlas": d["atlas_cpu_s"], "qual": d["qual_cpu_s"], "ladder": d["ladder_cpu_s"],
                      "total": d["cpu_s"]}}
    (HERE / "ATLAS_CALIBRATION_RESULT.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str))
    print(json.dumps(out, indent=1, default=str)[:6000])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--toy")
    ap.add_argument("--part", choices=("atlas", "qual", "arms", "scale", "scale2", "ladder"))
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    if a.summary:
        summary()
    else:
        if a.part in SCALE_GROUPS:
            part_scale(a.toy, a.part)
        else:
            {"atlas": part_atlas, "qual": part_qual, "arms": part_arms, "ladder": part_ladder}[a.part](a.toy)
