"""ROBUST01 stage 1 reducer: discovery at LADDER01 geometry G1 under aeth01.op_xor_fold vs the frozen contest law.

    python r01_reduce_s1.py --fold-dir D --rules RULES.json --out REDUCTION_S1.json [--backend gpu]

(Run directly, not through r01_run.py: it reads the contest units first, then installs the fold law itself.)

One code path counts both laws. CONTEST counts come from REACH01's own G1 units and certificates (LADDER01 seeds 0-7
plus x4 seeds 8-39) and must reproduce REACH01's published numbers before anything is decided (REPRODUCTION gate).
Per seed and arm:
  COMBINE        the search found >= 1 COMBINE candidate
  COMPOSE        >= 1 certified candidate (cap 10 per unit, discovery order) is COMPOSE
  AUTO_COMPOSE   >= 1 certified candidate is COMPOSE and AUTONOMOUS (r3_certify's definitions, unchanged)
  AUTO_ANY       >= 1 certified candidate is AUTONOMOUS
  GEN_COMPOSE    >= 1 AUTO_COMPOSE candidate is also COMBINE on the held-out alphabet IN_H (fold only)
Fold-only diagnostics for every certified candidate: the invariance check (energy-field contest events; seed
identity), held-out rung, distinct outputs. INSTRUMENT gate: every candidate with zero energy-field contest events
must have seeds_identical and position_combine_frac in {0, 1}.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fold_physics as FP  # noqa: E402

DATA = "C:/Prometheus-data/aether_reach01"
CONTEST_DIRS = (os.path.join(DATA, "LADDER01", "search"), os.path.join(DATA, "LADDERx4", "search"))
SEEDS = range(40)
# REACH01 72H_SYNTHESIS / R3_LADDER01_RESULT, G1, pooled over seeds 0-39.
CONTEST_PUBLISHED = {"C": {"COMBINE": 7, "COMPOSE": 3, "AUTO_COMPOSE": 0, "AUTO_ANY": 1},
                     "A": {"COMBINE": 0, "COMPOSE": 0, "AUTO_COMPOSE": 0, "AUTO_ANY": 0}}


def load_units(dirs):
    units = {}
    for d in dirs:
        for path in glob.glob(os.path.join(d, "G1_*_s*.json")):
            if path.endswith("_cert.json"):
                continue
            u = json.load(open(path))
            cert = path[:-5] + "_cert.json"
            u["_dir"] = d
            u["_certs"] = json.load(open(cert))["certified"] if os.path.exists(cert) else None
            units[(u["arm"], u["seed"])] = u
    return units


def seed_flags(u):
    certs = u["_certs"] or []
    return {"COMBINE": u["combine_distinct"] > 0,
            "COMPOSE": any(c["COMPOSE"] for c in certs),
            "AUTO_COMPOSE": any(c["COMPOSE"] and c["AUTONOMOUS"] for c in certs),
            "AUTO_ANY": any(c["AUTONOMOUS"] for c in certs)}


def count(units, arm, key):
    return sum(1 for s in SEEDS if (arm, s) in units and units[(arm, s)]["_flags"][key])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold-dir", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--backend", default="gpu")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.rules))["stage1"]

    contest = load_units(CONTEST_DIRS)
    for u in contest.values():
        u["_flags"] = seed_flags(u)
    repro = {arm: {k: count(contest, arm, k) for k in CONTEST_PUBLISHED[arm]} for arm in "CA"}
    repro_ok = repro == CONTEST_PUBLISHED and all((arm, s) in contest and contest[(arm, s)]["_certs"] is not None
                                                  for arm in "CA" for s in SEEDS)

    FP.install()
    import r01_lib as L
    import r3_frontier as F
    F.set_geom("G1")
    fold = load_units([a.fold_dir])
    missing = [(arm, s) for arm in "CA" for s in SEEDS if (arm, s) not in fold or fold[(arm, s)]["_certs"] is None]
    stamped = all(u.get("robust01", {}).get("semantics_id") == FP.SEMANTICS_ID for u in fold.values())
    violations, cands = [], []
    for (arm, s), u in sorted(fold.items()):
        u["_flags"] = seed_flags(u)
        u["_flags"]["GEN_COMPOSE"] = False
        if not u["_certs"]:
            continue
        z = np.load(os.path.join(u["_dir"], u["combine_npz"]))
        by_hash = {str(h): z["patches"][i] for i, h in enumerate(z["hashes"])}
        for c in u["_certs"]:
            p = by_hash[c["hash"]]
            inv = L.invariance_check(p)
            held = L.rung(L.table(p, a.backend, L.IN_H))
            row = {"arm": arm, "seed": s, "hash": c["hash"], "found_at_eval": c["found_at_eval"],
                   "COMPOSE": c["COMPOSE"], "AUTONOMOUS": c["AUTONOMOUS"],
                   "position_combine_frac": c["position_combine_frac"], "a_only": c["a_only"], "b_only": c["b_only"],
                   "shared": c["shared"], "Na": c["Na"], "Nb": c["Nb"],
                   "energy_multi": inv["energy_multi"], "template_multi": inv["template_multi"],
                   "seeds_identical": inv["seeds_identical"], "heldout_rung": held,
                   "distinct_outputs": L.n_distinct(np.array(inv["table"], np.uint8))}
            cands.append(row)
            if inv["energy_multi"] == 0 and not (inv["seeds_identical"]
                                                 and c["position_combine_frac"] in (0.0, 1.0)):
                violations.append(row)
            if c["COMPOSE"] and c["AUTONOMOUS"] and held == 2:
                u["_flags"]["GEN_COMPOSE"] = True

    keys = ("COMBINE", "COMPOSE", "AUTO_COMPOSE", "AUTO_ANY", "GEN_COMPOSE")
    table = {}
    for law, units in (("fold", fold), ("contest", contest)):
        for arm in "CA":
            for k in keys:
                if law == "contest" and k == "GEN_COMPOSE":
                    continue
                n = count(units, arm, k)
                table["%s_%s_%s" % (law, arm, k)] = {"k": n, "n": len(SEEDS), "wilson95": L.wilson(n, len(SEEDS))}

    k_auto = table["fold_C_AUTO_COMPOSE"]["k"]
    k_comp = table["fold_C_COMPOSE"]["k"]
    k_gen = table["fold_C_GEN_COMPOSE"]["k"]
    if missing:
        disp = "INCOMPLETE"
    elif not repro_ok:
        disp = "REDUCER_DEFECT"
    elif violations or not stamped:
        disp = "INSTRUMENT_DEFECT"
    elif k_auto >= R["common_min"]:
        disp = "ROBUST_COMPOSITION_COMMON"
    elif k_auto >= R["discoverable_min"]:
        disp = "ROBUST_COMPOSITION_DISCOVERABLE"
    elif k_auto >= 1:
        disp = "ROBUST_COMPOSITION_RARE"
    elif k_comp >= 1:
        disp = "COMPOSITION_STILL_FRAGILE"
    else:
        disp = "NO_COMPOSITION"
    qualifier = None
    if disp.startswith("ROBUST_COMPOSITION"):
        qualifier = "HELDOUT_GENERAL" if k_gen >= R["heldout_general_min"] else "HELDOUT_NOT_GENERAL"
    nonauto = [c for c in cands if not c["AUTONOMOUS"]]
    res = {"schema": "aether.robust01.s1.reduction.v1", "semantics_id": FP.SEMANTICS_ID,
           "disposition": disp, "qualifier": qualifier, "rules": R,
           "reproduction": {"counts": repro, "published": CONTEST_PUBLISHED, "ok": repro_ok},
           "missing_units": missing, "all_units_stamped": stamped, "instrument_violations": violations,
           "table": table,
           "nonautonomous_with_energy_contests": [sum(1 for c in nonauto if c["energy_multi"] > 0), len(nonauto)],
           "fold_seed_flags": {"%s_s%d" % k: u["_flags"] for k, u in sorted(fold.items())},
           "candidates": cands}
    json.dump(res, open(a.out + ".partial", "w"), indent=1)
    os.replace(a.out + ".partial", a.out)
    print(json.dumps({k: res[k] for k in ("disposition", "qualifier", "reproduction")}, indent=1))
    for k, v in table.items():
        print(k, v["k"], "/", v["n"], v["wilson95"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
